---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.30 Parameter Discovery (Arjun, x8)"
---

# 05.30 — Parameter Discovery

## What is it?

Web applications often accept hidden parameters — query string or POST body parameters that aren't visible in the UI but are processed server-side. These can expose debug modes, hidden features, access control bypasses, injection points, and IDOR vulnerabilities. Parameter discovery is the process of finding these hidden parameters by fuzzing.

```
VISIBLE URL:
  https://target.com/api/user?id=123

HIDDEN PARAMETERS THAT MIGHT WORK:
  https://target.com/api/user?id=123&debug=true   → debug output!
  https://target.com/api/user?id=123&admin=true   → privilege escalation!
  https://target.com/api/user?id=123&format=json  → different response format
  https://target.com/api/user?id=123&source=internal → internal data?
  https://target.com/api/user?id=123&include=all  → more fields returned?

WHY THIS MATTERS:
  → Hidden parameters = more attack surface
  → debug=true → verbose errors → information disclosure
  → admin=true → auth bypass (if not validated!)
  → IDOR through extra parameters: user_id=456 vs id=123
```

---

## Arjun (Best Parameter Discovery Tool)

```bash
# INSTALL:
pip3 install arjun
# OR:
git clone https://github.com/s0md3v/Arjun.git

# BASIC GET PARAMETER SCAN:
arjun -u https://target.com/api/user

# POST PARAMETER SCAN:
arjun -u https://target.com/api/login -m POST

# JSON BODY PARAMETERS:
arjun -u https://target.com/api/user -m JSON

# MULTIPART FORM DATA:
arjun -u https://target.com/upload -m MULTIPART

# WITH HEADERS (authenticated):
arjun -u https://target.com/api/user \
  -H "Authorization: Bearer TOKEN" \
  -H "Cookie: session=ABCDEF"

# CUSTOM WORDLIST:
arjun -u https://target.com/api/user \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt

# SLOWER RATE (avoid detection):
arjun -u https://target.com/api/user --stable  # slower but more reliable
arjun -u https://target.com/api/user -d 2000   # 2 second delay between requests

# CHUNK SIZE (parameters per request):
arjun -u https://target.com/api/user -c 250   # send 250 params at once (faster)

# SAVE OUTPUT:
arjun -u https://target.com/api/user -oJ arjun-results.json

# BATCH SCAN (multiple URLs):
arjun -i urls.txt -oT arjun-all.txt

# EXAMPLE OUTPUT:
# [*] Scanning https://target.com/api/user
# [+] Parameters found: debug, admin, format, include, token
```

---

## x8 (Parameter Discovery with Change Detection)

```bash
# INSTALL:
cargo install x8
# OR download from: https://github.com/Sh1Yo/x8

# BASIC SCAN:
x8 -u "https://target.com/api/user" -w params.txt

# WITH BODY:
x8 -u "https://target.com/api/user" -X POST -w params.txt

# JSON:
x8 -u "https://target.com/api/user" \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"FUZZ":"test"}' \
  -w params.txt

# HEADER PARAMETERS:
x8 -u "https://target.com/api/user" \
  --headers \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt

# WITH COOKIES:
x8 -u "https://target.com/api/user" \
  -H "Cookie: session=ABCDEF" \
  -w params.txt

# SAVE:
x8 -u "https://target.com/api/user" -w params.txt -o results.txt
```

---

## Manual Parameter Discovery

### Mining from JavaScript Files

```bash
# EXTRACT PARAMETERS FROM JS FILES:
cat all-js.txt | \
  grep -oP '(?<=[?&])[a-zA-Z_][a-zA-Z0-9_]+(?==)' | \
  sort -u > js-params.txt

# FROM FETCH/AXIOS CALLS:
cat all-js.txt | \
  grep -oP '(?<=params:\s{0,5}{\s{0,5})[^}]+' | \
  grep -oP '[a-zA-Z_]+(?=:)' | sort -u

# FROM FORM FIELDS:
curl -s https://target.com | \
  grep -oP '(?<=name=")[^"]+' | sort -u
curl -s https://target.com | \
  grep -oP "(?<=name=')[^']+" | sort -u

# FROM WAYBACK MACHINE URLS (historical params!):
waybackurls target.com | \
  grep "?" | \
  python3 -c "
import sys
from urllib.parse import urlparse, parse_qs
params = set()
for line in sys.stdin:
    parsed = urlparse(line.strip())
    params.update(parse_qs(parsed.query).keys())
for p in sorted(params):
    print(p)
" > historical-params.txt
```

### GAU + Parameter Extraction

```bash
# GET ALL HISTORICAL URLS WITH PARAMS:
gau target.com | grep "?" | sort -u > gau-urls.txt

# EXTRACT PARAMETER NAMES:
cat gau-urls.txt | \
  python3 -c "
import sys
from urllib.parse import urlparse, parse_qs
params = set()
for line in sys.stdin:
    url = line.strip()
    parsed = urlparse(url)
    params.update(parse_qs(parsed.query).keys())
print('\n'.join(sorted(params)))
" > known-params.txt

# COMBINE WITH ARJUN:
arjun -u https://target.com/page \
  -w known-params.txt  # test historically known params on new endpoints!
```

---

## Wordlists for Parameter Discovery

```bash
# SECLISTS PARAMETER WORDLISTS:
ls /usr/share/wordlists/seclists/Discovery/Web-Content/ | grep -i param

# MOST USEFUL:
burp-parameter-names.txt       # 2,588 common Burp params
# Contains: debug, admin, token, key, secret, id, user, etc.

# BUILD CUSTOM LIST FROM RESPONSES:
# Take all parameter names you've seen on the target and create a custom list

# COMMON HIGH-VALUE PARAMS TO TEST MANUALLY:
HIGH_VALUE_PARAMS=(
  debug admin test internal dev
  verbose trace show_errors
  format output type
  include exclude fields select
  limit offset page size
  sort order by filter
  callback jsonp
  token key secret api_key
  lang locale version
  source origin ref
  preview draft mode
  role access level permission
  redirect next return_url
  action method operation
  id user_id account_id object_id
)
```

---

## Testing Found Parameters

```bash
# ONCE PARAMETER FOUND, TEST FOR VULNS:

# DEBUG PARAMETER:
curl "https://target.com/api/user?id=1&debug=true"
curl "https://target.com/api/user?id=1&debug=1"
curl "https://target.com/api/user?id=1&debug=on"
# → Verbose error output, internal paths, stack traces

# ADMIN/PRIVILEGE ESCALATION:
curl "https://target.com/api/user?id=1&admin=true"
curl "https://target.com/api/user?id=1&role=admin"
curl "https://target.com/api/user?id=1&is_admin=1"
# → Access to admin functionality?

# IDOR (change ID values):
curl "https://target.com/api/user?id=1"
curl "https://target.com/api/user?id=2"    # another user's data?
curl "https://target.com/api/user?id=0"    # edge case
curl "https://target.com/api/user?id=-1"   # negative
curl "https://target.com/api/user?id=1000000"  # large number

# SSRF (URL parameter):
curl "https://target.com/api/fetch?url=http://169.254.169.254/latest/meta-data/"
curl "https://target.com/api/fetch?redirect=http://evil.com"

# SQLi (ID parameters):
curl "https://target.com/api/user?id=1'"        # syntax error?
curl "https://target.com/api/user?id=1 AND 1=1" # boolean test

# PARAMETER POLLUTION (send same param twice):
curl "https://target.com/api/user?id=1&id=2"    # which one wins?
curl "https://target.com/api/user?admin=false&admin=true"
```

---

## URL Mining from Historical Sources

```bash
# COMPLETE PARAMETER DISCOVERY WORKFLOW:
TARGET="target.com"

# 1. Collect historical URLs:
echo "$TARGET" | waybackurls > wayback.txt
gau "$TARGET" >> wayback.txt
cat wayback.txt | sort -u > all-historical-urls.txt

# 2. Filter to URLs with parameters:
cat all-historical-urls.txt | grep "?" > parameterized-urls.txt

# 3. Extract unique parameter names:
cat parameterized-urls.txt | \
  python3 -c "
import sys
from urllib.parse import urlparse, parse_qs
params = set()
for line in sys.stdin:
    url = line.strip()
    try:
        parsed = urlparse(url)
        params.update(parse_qs(parsed.query).keys())
    except: pass
print('\n'.join(sorted(params)))
" > unique-params.txt

# 4. Combine with standard wordlist and deduplicate:
cat unique-params.txt /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt | \
  sort -u > combined-params.txt

# 5. Run arjun on each endpoint:
cat parameterized-urls.txt | \
  python3 -c "
import sys
from urllib.parse import urlparse
endpoints = set()
for line in sys.stdin:
    parsed = urlparse(line.strip())
    endpoints.add(f'{parsed.scheme}://{parsed.netloc}{parsed.path}')
print('\n'.join(endpoints))
" | while read endpoint; do
    arjun -u "$endpoint" -w combined-params.txt -oJ "arjun-$(echo $endpoint | md5sum | cut -d' ' -f1).json"
done
```

---

## Related Notes
- [[18 - API Discovery from JS Files]] — API endpoint discovery
- [[17 - JavaScript File Analysis]] — JS param mining
- [[29 - Directory and File Bruteforcing]] — path discovery
- [[10 - Web Archive Wayback Machine]] — historical URL sources
