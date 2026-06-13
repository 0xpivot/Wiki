---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.10 Web Archive — Wayback Machine for Hidden Endpoints"
---

# 05.10 — Web Archive (Wayback Machine)

## What is it?

The Wayback Machine (web.archive.org) maintains archived snapshots of websites going back to 1996. For VAPT, it reveals: old API endpoints that still work, deleted pages with sensitive content, historical configurations, old JavaScript files with hardcoded credentials, and pages removed after a breach (which tell you about past incidents).

---

## Why Historical Archives Matter

```
COMMON FINDINGS FROM WAYBACK MACHINE:

1. OLD API ENDPOINTS (still functional!):
   2019 archive: /api/v1/users?debug=true
   → Endpoint deleted from docs but still in code!
   → Test if /api/v1/users?debug=true still works on live site!

2. DELETED ADMIN PANELS:
   2021 archive: /phpmyadmin/ → accessible!
   → Admin moved it but forgot to remove from server
   
3. OLD JAVASCRIPT WITH CREDENTIALS:
   2020 archive: app.min.js contains:
   var API_KEY = "hardcoded_key_here"; // TODO: remove before prod
   → Key might still be valid!
   
4. PAST BREACH INDICATORS:
   "Site unavailable for maintenance" → incident?
   Changed login page → breach response?
   Removed user data pages → privacy issue?
   
5. HIDDEN FUNCTIONALITY:
   Archived page shows beta feature that was "removed"
   → Feature might still be in code, just unlisted!
```

---

## Wayback Machine Tools

```bash
# BROWSE MANUALLY:
# https://web.archive.org/web/*/target.com/*
# Shows calendar of when snapshots were taken

# API ENDPOINT (CDX API — powerful!):
curl "https://web.archive.org/cdx/search/cdx?url=*.target.com/*&output=text&fl=original&collapse=urlkey"
# Returns all URLs ever archived for target.com!

# FILTER BY FILE TYPE:
# Find all archived PHP files:
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*&output=text&fl=original&collapse=urlkey&filter=original:.*\.php"

# Find all JS files:
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*&output=text&fl=original&collapse=urlkey&filter=original:.*\.js"

# Find admin/backup/config paths:
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*admin*&output=text&fl=original&collapse=urlkey"
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*backup*&output=text&fl=original&collapse=urlkey"
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*.bak&output=text&fl=original&collapse=urlkey"
curl "https://web.archive.org/cdx/search/cdx?url=target.com/*.env&output=text&fl=original&collapse=urlkey"

# WAYBACKURLS (specialized tool):
waybackurls target.com > wayback-urls.txt
echo target.com | waybackurls

# GAUA (Get All URLs — multiple sources including Wayback):
gau target.com > all-urls.txt
gau --subs target.com  # include subdomains
```

---

## Analyzing Historical URLs

```bash
# Get all unique paths from wayback:
waybackurls target.com | sort -u | tee all-paths.txt

# Extract unique directories:
cat all-paths.txt | grep -oP 'https?://[^/]+\K/[^?#]*' | sort -u

# Find interesting paths:
cat all-paths.txt | grep -iE "admin|backup|config|debug|test|old|dev|internal|secret|api/v[0-9]"

# Extract parameters to fuzz:
cat all-paths.txt | grep "?" | python3 -c "
import sys
from urllib.parse import urlparse, parse_qs
params = set()
for line in sys.stdin:
    q = parse_qs(urlparse(line.strip()).query)
    params.update(q.keys())
print('Found parameters:', params)
"

# Test if old endpoints still work:
cat old-endpoints.txt | httpx -status-code -title
# 200 on an "old" endpoint → still accessible!
# 403 on old admin endpoint → worth trying bypass!
```

---

## JavaScript File Analysis from Archives

```bash
# Download all historical JS files:
waybackurls target.com | grep "\.js$" | sort -u > js-files.txt

# Check each for secrets (using trufflehog-style scanning):
cat js-files.txt | while read url; do
  content=$(curl -s "$url")
  if echo "$content" | grep -qiE "api.?key|secret|password|token|credential"; then
    echo "INTERESTING: $url"
    echo "$content" | grep -iE "api.?key|secret|password|token|credential" | head -5
  fi
done

# Linkfinder on archived JS:
linkfinder.py -i https://web.archive.org/web/2023*/https://target.com/app.js -o cli

# SECRETFINDER:
SecretFinder.py -i js-files.txt -o secrets.txt
```

---

## GAU (Get All URLs)

```bash
# GAU aggregates multiple sources:
# Wayback Machine + Common Crawl + URLScan.io + Alien Vault OTX

gau target.com --subs > all-target-urls.txt

# Filter by type:
gau target.com --blacklist jpg,png,css,ttf,woff,gif,ico

# Interesting patterns:
cat all-target-urls.txt | grep -E "=http|=//|redirect|next|url|returnto" > redirect-params.txt
cat all-target-urls.txt | grep -E "id=|user=|account=" > idor-targets.txt
cat all-target-urls.txt | grep -E "\.php\?|\.asp\?|\.aspx\?" > server-side-scripts.txt
```

---

## Related Notes
- [[17 - JavaScript File Analysis]] — deeper JS analysis
- [[18 - API Discovery from JS Files]] — finding API endpoints in JS
- [[29 - Directory and File Bruteforcing]] — finding additional URLs
