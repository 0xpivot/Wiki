---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.11 Detecting CORS Misconfigurations (CORScanner, manual)"
---

# 12.11 — Detecting CORS Misconfigurations (CORScanner, Manual)

## Manual Detection Checklist

```bash
# STEP 1 — IDENTIFY ENDPOINTS WITH CORS HEADERS:
curl -v -H "Origin: https://evil.com" https://target.com/ 2>&1 | grep -i access-control

# STEP 2 — TEST ALL INTERESTING ENDPOINTS:
for path in "/" "/api" "/api/me" "/api/account" "/api/v1/user" "/admin" "/api/keys"; do
  echo "=== $path ==="
  curl -s -I \
    -H "Origin: https://evil.com" \
    -H "Cookie: session=YOUR_SESSION" \
    "https://target.com$path" | grep -i "access-control"
done

# STEP 3 — TEST DIFFERENT ORIGIN VALUES:
test_origins=(
  "https://evil.com"
  "null"
  "https://sub.target.com"
  "https://target.com.evil.com"
  "https://evil.target.com"
  "http://target.com"
)
for origin in "${test_origins[@]}"; do
  result=$(curl -s -I -H "Origin: $origin" \
    -H "Cookie: session=YOURS" \
    "https://target.com/api/me" | grep -i "access-control-allow-origin")
  echo "$origin → $result"
done
```

---

## What to Look For

```
CRITICAL (immediate exploit):
  Access-Control-Allow-Origin: https://evil.com    ← reflected!
  Access-Control-Allow-Credentials: true
  → ANY origin gets credentialed access!

CRITICAL:
  Access-Control-Allow-Origin: null
  Access-Control-Allow-Credentials: true
  → Sandboxed iframe attack!

HIGH:
  Access-Control-Allow-Origin: https://sub.target.com
  Access-Control-Allow-Credentials: true
  + sub.target.com has XSS or subdomain takeover!

MEDIUM:
  Access-Control-Allow-Origin: *
  (no credentials — public data exposed, no creds stolen)
  
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Credentials: true
  (browser blocks, but developer intent is broken, likely has reflected fallback)

LOW:
  Missing Vary: Origin header when ACAO is dynamic
  (cache poisoning risk)
```

---

## CORScanner Tool

```bash
# INSTALL:
git clone https://github.com/chenjj/CORScanner
cd CORScanner
pip3 install -r requirements.txt

# BASIC SCAN:
python3 cors_scan.py -u https://target.com

# SCAN WITH COOKIE (authenticated):
python3 cors_scan.py -u https://target.com \
  -H "Cookie: session=YOUR_SESSION"

# SCAN A LIST OF URLs:
python3 cors_scan.py -i urls.txt -H "Cookie: session=YOURS"

# OUTPUT:
# [!] Vulnerable:  https://target.com/api/me
#     Type:        reflect_origin
#     Details:     ACAO: https://evil.com, ACAC: true
```

---

## Corsy Tool

```bash
# INSTALL:
pip install corsy
# OR:
git clone https://github.com/s0md3v/Corsy
cd Corsy && pip3 install -r requirements.txt

# BASIC USAGE:
corsy -u https://target.com

# WITH COOKIE:
corsy -u https://target.com -H "Cookie: session=YOURS"

# OUTPUT FORMAT:
# Target: https://target.com
# ● Arbitrary Origin Trusting
#   Path: /api/account
#   Origin: https://evil.com
#   Response headers:
#     Access-Control-Allow-Origin: https://evil.com
#     Access-Control-Allow-Credentials: true
```

---

## Burp Suite Workflow

```
BURP MANUAL CORS TESTING:

1. SETUP:
   ✓ Enable Burp proxy
   ✓ Log in to target.com
   ✓ Browse all functionality

2. HTTP HISTORY ANALYSIS:
   ✓ Filter: Show only responses with "Access-Control" headers
   ✓ Find all endpoints with CORS headers
   
3. REPEATER TESTING:
   For each CORS endpoint:
   ✓ Add: Origin: https://evil.com
   ✓ Check response for ACAO: https://evil.com
   ✓ Check response for ACAC: true
   ✓ Add: Origin: null (test null origin)

4. BURP SCANNER:
   ✓ Active scan → "Cross-origin resource sharing" check
   ✓ Automatically tests origin reflection and null
   ✓ Reports findings with severity

5. BURP EXTENSION: "CORS * Scanner"
   Available in BApp Store
   Tests multiple origin bypass techniques automatically
```

---

## Automated Testing with ffuf

```bash
# USE FFUF TO FIND API ENDPOINTS AND TEST CORS:

# STEP 1: Find endpoints:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
  -H "Cookie: session=YOURS" \
  -mc 200,301,302,401,403

# STEP 2: Test CORS on found endpoints:
cat found_endpoints.txt | while read endpoint; do
  result=$(curl -s -I \
    -H "Origin: https://evil.com" \
    -H "Cookie: session=YOURS" \
    "https://target.com$endpoint" | grep -i "access-control")
  if [ -n "$result" ]; then
    echo "$endpoint: $result"
  fi
done
```

---

## Creating a One-Line Test

```bash
# QUICK CORS TEST FOR A SINGLE URL:
# Returns ACAO header or "none":
cors_test() {
  local url="$1"
  local cookie="${2:-}"
  local header_args=()
  [ -n "$cookie" ] && header_args+=(-H "Cookie: $cookie")
  
  curl -s -I \
    -H "Origin: https://evil.com" \
    "${header_args[@]}" \
    "$url" | grep -i "access-control" || echo "No CORS headers"
}

# USAGE:
cors_test "https://target.com/api/me" "session=abc123"
```

---

## Reporting Template

```
VULNERABILITY: CORS Misconfiguration — Origin Reflection

SEVERITY: Critical / High / Medium (choose based on impact)

AFFECTED URL: https://target.com/api/account

EVIDENCE:
  Request:
    GET /api/account HTTP/1.1
    Origin: https://evil.com
    Cookie: session=[victim_session]
  
  Response:
    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: https://evil.com  ← VULNERABLE
    Access-Control-Allow-Credentials: true          ← VULNERABLE
  
IMPACT:
  An attacker who can trick a victim into visiting a malicious website
  can read the victim's sensitive API responses, including [list what's exposed].
  This enables account takeover via [chain: CSRF token theft / direct email change].

REMEDIATION:
  Maintain an explicit whitelist of allowed origins.
  Never reflect the Origin header blindly.
  See: Defense note 12.12.
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — most common vuln
- [[05 - Null Origin Misconfiguration]] — null origin
- [[07 - Subdomain Trust]] — subdomain attacks
- [[09 - CORS to Credential Theft]] — exploitation
- [[12 - Defense Strict Origin Whitelisting]] — remediation
