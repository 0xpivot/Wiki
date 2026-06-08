---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.18 API Discovery from JS Files (LinkFinder, JSParser)"
---

# 05.18 — API Discovery from JS Files

## What is it?

Modern web applications (SPAs) define all their API routes client-side in JavaScript. Extracting API endpoints from bundled JavaScript files reveals the complete API surface — including endpoints that aren't visible in the UI, admin endpoints, debug endpoints, and old API versions.

---

## LinkFinder

```bash
# INSTALL:
git clone https://github.com/GerbenJavado/LinkFinder.git
pip3 install -r requirements.txt

# SCAN A JS FILE:
python3 linkfinder.py -i https://target.com/app.js -o cli

# CRAWL ENTIRE DOMAIN (follow JS includes):
python3 linkfinder.py -i https://target.com -d -o cli

# SAVE TO FILE:
python3 linkfinder.py -i https://target.com -d -o results.html

# SCAN LOCAL FILE:
python3 linkfinder.py -i ./downloaded-app.js -o cli

EXAMPLE OUTPUT:
  /api/v1/users
  /api/v1/admin/config
  /internal/debug/healthcheck
  /api/v2/payment/process
  https://api.external-service.com/v1/data
```

---

## JSParser

```bash
# INSTALL:
git clone https://github.com/nahamsec/JSParser.git
pip3 install -r requirements.txt

# RUN:
python3 handler.py

# SCAN:
# Browse to http://localhost:8008
# Enter URL of JS file → extracts all links/endpoints

# CLI mode:
python3 jsparser.py -u https://target.com/app.js

# BATCH MODE:
cat js-files.txt | while read url; do
  python3 jsparser.py -u "$url"
done | sort -u
```

---

## Manual Regex Extraction

```bash
# DOWNLOAD JS FILES:
curl -s https://target.com | \
  grep -oP '(?<=src=")[^"]+\.js(?:[^"]*)"' | \
  sed 's/"$//' | \
  while read js; do
    [ "${js:0:4}" = "http" ] || js="https://target.com$js"
    curl -s "$js" >> all-js.txt
  done

# EXTRACT ENDPOINT PATTERNS:
# REST API paths:
grep -oP '(?<=["`'"'"'])/api/[a-zA-Z0-9/_.-]+(?=["`'"'"'])' all-js.txt | sort -u

# Paths starting with /:
grep -oP '(?<=["`'"'"'])/[a-zA-Z][a-zA-Z0-9/_.-]{2,}(?=["`'"'"'])' all-js.txt | \
  grep -v "^//\|\.css\|\.js\|\.png\|\.jpg" | sort -u

# fetch() calls:
grep -oP "fetch\(['\"][^'\"]+['\"]" all-js.txt | sed 's/fetch(//; s/['\"]//g' | sort -u

# axios calls:
grep -oP "axios\.(get|post|put|delete|patch)\(['\"][^'\"]+['\"]" all-js.txt | \
  sed 's/axios\.[a-z]*(['"'"'"]//; s/['"'"'"]$//' | sort -u

# API base URL extraction:
grep -oP '(?<=["\x27])(https?://[a-zA-Z0-9.-]+/api[^"\x27]*)(?=["\x27])' all-js.txt | sort -u
```

---

## React/Angular/Vue Route Discovery

```bash
# REACT ROUTER (Routes define all pages):
grep -oP 'path=["'"'"'][^"'"'"']+["'"'"']' all-js.txt | sort -u
# path="/admin/users" → admin user management exists!
# path="/api/internal/:id" → internal API!

# ANGULAR ROUTES:
grep -oP '(?<=path: ["\x27])[^"'"'"']+' all-js.txt | sort -u

# VUE ROUTER:
grep -oP '(?<=path: ["\x27])/[^"'"'"']+' all-js.txt | sort -u

# NEXT.JS (pages directory maps to routes):
# Look for page components:
grep -oP "import.*from.*pages/[^'\"]*" all-js.txt | sort -u
# OR in sourcemap: find "pages/" filenames

# NUXT.JS (pages directory):
grep -oP '(?<=pages\/)[^"'"'"']+' all-js.txt | sort -u
```

---

## API Version Discovery

```bash
# FIND ALL API VERSIONS:
grep -oP '(?<=["\x27])/api/v\d+/[^"'"'"']+(?=["\x27])' all-js.txt | sort -u

# Common patterns:
/api/v1/users    → v1 endpoints
/api/v2/users    → v2 endpoints (is v1 still active? try it!)
/api/beta/       → beta endpoints (less secure!)
/api/internal/   → internal (shouldn't be in client-side JS!)

# Test old versions:
curl https://target.com/api/v1/admin
# If v2 has auth checks but v1 doesn't → auth bypass via v1!
```

---

## OpenAPI/Swagger Discovery via JS

```bash
# FIND SWAGGER/OPENAPI REFERENCES IN JS:
cat all-js.txt | grep -iE "swagger|openapi|api.?doc|api.?spec" | head -10

# Common swagger endpoints:
for path in \
  /swagger.json \
  /openapi.json \
  /api/swagger.json \
  /api/docs \
  /api/v1/docs \
  /v2/api-docs \
  /swagger-ui.html \
  /swagger/index.html \
  /api-docs; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
    [ "$code" = "200" ] && echo "FOUND: https://target.com$path"
done

# PARSE SWAGGER FOR ALL ENDPOINTS:
curl -s https://target.com/swagger.json | \
  python3 -c "
import json, sys
spec = json.load(sys.stdin)
for path, methods in spec.get('paths', {}).items():
    for method in methods.keys():
        print(f'{method.upper()} {path}')
" | sort
```

---

## Post-Discovery: Testing Found Endpoints

```bash
# TAKE ALL DISCOVERED ENDPOINTS AND TEST:
cat discovered-endpoints.txt | while read endpoint; do
  url="https://target.com${endpoint}"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "$code $url"
done | grep -v "^404" | sort

# TEST WITH DIFFERENT HTTP METHODS:
curl -X GET https://target.com/api/admin/users  → 403?
curl -X POST https://target.com/api/admin/users → 200? → auth bypass!
curl -X OPTIONS https://target.com/api/admin/users  → see allowed methods

# NUCLEI ON DISCOVERED ENDPOINTS:
cat discovered-endpoints.txt | \
  sed 's|^|https://target.com|' | \
  nuclei -t ~/nuclei-templates/ -o nuclei-results.txt
```

---

## Related Notes
- [[17 - JavaScript File Analysis]] — JS analysis and secrets
- [[29 - Directory and File Bruteforcing]] — additional endpoint discovery
- [[30 - Parameter Discovery]] — parameters on found endpoints
- [[Module 07 - API Security]] — API vulnerability testing
