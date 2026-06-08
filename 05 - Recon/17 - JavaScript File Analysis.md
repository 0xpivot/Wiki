---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.17 JavaScript File Analysis for Endpoints and Secrets"
---

# 05.17 — JavaScript File Analysis

## What is it?

JavaScript files shipped to browsers often contain API endpoints, authentication logic, feature flags, environment configs, and accidentally committed secrets. Analyzing JS files is one of the highest-yield recon techniques — especially for single-page applications (React, Angular, Vue) where all the application logic lives in JS.

---

## Why JS Files Are Goldmines

```
SINGLE-PAGE APPLICATIONS (React/Angular/Vue):
  ALL routing logic is in JavaScript!
  React Router: <Route path="/api/admin/users" component={AdminUsers}/>
  → Reveals admin endpoint even if it's "hidden" from UI!
  
SECRETS OFTEN FOUND:
  const API_KEY = "sk-live-xxxxx"         ← OpenAI/Stripe key!
  const GOOGLE_MAPS_KEY = "AIzaSy..."     ← Google Maps API key
  var AWS_ACCESS_KEY = "AKIAIOSFODNN7..."  ← AWS key! (still happens!)
  const DB_PASSWORD = "prod-password-123" ← Database password!
  var internalApiUrl = "http://10.10.10.5:8080/api" ← Internal endpoint!
  
FEATURE FLAGS AND DEBUG:
  const DEBUG_MODE = process.env.NODE_ENV === 'development'
  const ADMIN_FEATURE_ENABLED = true  ← hidden feature exposed!
```

---

## Finding and Downloading JS Files

```bash
# FROM BROWSER (DevTools → Sources tab):
# Paste into Sources filter to find all .js files

# FROM CURL (extract script tags):
curl -s https://target.com | \
  grep -oP 'src="[^"]*\.js[^"]*"' | \
  sed 's/src="//' | sed 's/"//' | \
  sed 's|^/|https://target.com/|' | sort -u

# WAYBACK MACHINE JS FILES:
waybackurls target.com | grep "\.js$" | sort -u

# GAU (get all URLs including JS):
gau target.com --blacklist css,png,jpg,gif,ico | grep "\.js"

# DOWNLOAD ALL JS FILES:
curl -s https://target.com | \
  grep -oP 'src="[^"]*\.js[^"]*"' | \
  sed 's/src="//' | sed 's/"//' | \
  while read js; do
    [ "${js:0:4}" = "http" ] || js="https://target.com$js"
    curl -s "$js" -o "js/$(basename $js)"
  done
```

---

## Extracting Endpoints from JS

```bash
# LINKFINDER (best tool for this):
python3 linkfinder.py -i https://target.com -d -o cli
# -d = crawl entire domain
python3 linkfinder.py -i https://target.com/app.js -o cli

# JSPARSER:
python3 jsparser.py -u https://target.com/app.js

# MANUAL GREP for common patterns:
cat app.js | grep -oP '(?<=["`'"'"'])/[a-zA-Z0-9/._-]+(?=["`'"'"'])'
# Finds: /api/users, /internal/admin, /v2/account, etc.

# FIND API ENDPOINTS:
cat app.js | grep -E '"(get|post|put|delete|patch).*api|fetch\(|axios\.' -i | head -20

# REGEX for common endpoint patterns:
grep -oP '(?<=["\x27])/[a-zA-Z0-9/_.-]{3,}(?=["\x27])' app.js | sort -u

# BEAUTIFUL SOUP (Python, if minified JS):
# Deobfuscate first → then grep
```

---

## Finding Secrets in JS

```bash
# SECRETFINDER:
python3 SecretFinder.py -i https://target.com -e -o cli
python3 SecretFinder.py -i app.js -o cli

# MANUAL PATTERNS:
cat app.js | grep -iE "api.?key|apikey|secret|password|token|credential|private.?key"
cat app.js | grep -oP "(AKIA[A-Z0-9]{16})"        # AWS Access Key ID
cat app.js | grep -oP "sk-(live|test)-[a-zA-Z0-9]+"  # Stripe
cat app.js | grep -oP "ghp_[a-zA-Z0-9]{36}"        # GitHub PAT
cat app.js | grep -oP "AIzaSy[a-zA-Z0-9_-]{33}"    # Google API key
cat app.js | grep -oP "[a-f0-9]{32,}"              # Generic hash/key

# TRUFFLEHOG on JS files:
trufflehog filesystem --directory ./js-files/

# GITLEAKS on JS directory:
gitleaks detect --source ./js-files/ --no-git

# SEMGREP (pattern-based):
semgrep --config "p/secrets" ./js-files/
```

---

## Deobfuscating Minified JavaScript

```bash
# PRETTIFY/BEAUTIFY:
# Online: https://beautifier.io/
# npm: 
npm install -g js-beautify
js-beautify app.min.js > app-pretty.js

# WEBPACK BUNDLE ANALYZER:
# If bundle.js → webpack bundle
# Look for map file: bundle.js.map (source map!)

# SOURCE MAPS (often left enabled!):
curl -s https://target.com/static/js/main.abc123.js.map
# Returns: original source code before bundling!
# Contains: original file names, original code!

# FIND SOURCE MAPS:
curl -sI https://target.com/app.js | grep "SourceMap"
# OR look at last line of JS file:
tail -1 app.js | grep "sourceMappingURL"
# //# sourceMappingURL=app.js.map  → source map exists!

# DOWNLOAD SOURCE MAPS:
curl -s https://target.com/app.js.map | python3 -m json.tool | head -50
# "sources": ["../src/components/AdminPanel.jsx", ...]
# → Original source file structure revealed!
# → Sometimes full original code in "sourcesContent"!
```

---

## Webpack Source Map Exploitation

```bash
# IF SOURCE MAP IS EXPOSED:
curl -s https://target.com/static/js/main.chunk.js.map > sourcemap.json

# UNPACK SOURCE MAP (get original files):
# Tool: sourcemapper
python3 sourcemapper.py sourcemap.json output_dir/
# → Creates directory with all original source files!
# → Now you have the actual React/Angular source code!
# → Look for: hardcoded credentials, admin routes, auth bypasses!
```

---

## Related Notes
- [[18 - API Discovery from JS Files]] — finding API endpoints
- [[10 - Web Archive Wayback Machine]] — historical JS files
- [[11 - GitHub Dorking for Secrets]] — secrets in code repos
- [[19 - Source Code Leakage]] — exposed .git directory
