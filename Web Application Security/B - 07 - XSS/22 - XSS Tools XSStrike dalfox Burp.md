---
tags: [vapt, xss, tools, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.22 XSS Tools — XSStrike, dalfox, Burp Scanner"
---

# 07.22 — XSS Tools (XSStrike, dalfox, Burp Scanner)

## Tool Overview

```
TOOL         BEST FOR                         SPEED      ACCURACY
XSStrike     Context-aware payload generation  Medium     High
dalfox       CI/CD pipelines, fast automation  Fast       High
Burp Scanner Full web app scanning             Slow       Very High
OWASP ZAP    Free alternative to Burp          Medium     High
```

---

## XSStrike

XSStrike is an intelligent XSS detection tool that analyzes reflection context and generates context-specific payloads. Unlike dumb fuzzers, it understands HTML/JS parsing.

### Installation

```bash
git clone https://github.com/s0md3v/XSStrike
cd XSStrike
pip3 install -r requirements.txt
python3 xsstrike.py
```

### Basic Usage

```bash
# SCAN A SINGLE URL (GET parameter):
python3 xsstrike.py -u "https://target.com/search?q=test"

# SCAN POST REQUEST:
python3 xsstrike.py -u "https://target.com/search" --data "q=test&category=books"

# FUZZING MODE (test all parameters):
python3 xsstrike.py -u "https://target.com/search?q=test" --fuzzer

# BLIND XSS MODE (for out-of-band detection):
python3 xsstrike.py -u "https://target.com/feedback" --data "msg=test" --blind

# CRAWL AND SCAN ALL LINKS:
python3 xsstrike.py -u "https://target.com" --crawl --level 3

# SKIP DOM SCANNING (faster):
python3 xsstrike.py -u "https://target.com/search?q=test" --skip-dom

# FILTER EVASION:
python3 xsstrike.py -u "https://target.com/search?q=test" --encode
```

### XSStrike with Headers

```bash
# WITH CUSTOM HEADERS (authentication):
python3 xsstrike.py -u "https://target.com/profile?name=test" \
  --headers "Cookie: session=abc123\nAuthorization: Bearer TOKEN"

# WITH PROXY (through Burp):
python3 xsstrike.py -u "https://target.com/search?q=test" \
  --proxy "http://127.0.0.1:8080"

# WITH TIMEOUT:
python3 xsstrike.py -u "https://target.com/search?q=test" --timeout 10
```

---

## dalfox

dalfox (formerly xssor) is a fast, Go-based XSS scanner with excellent CI/CD integration and pipe mode.

### Installation

```bash
# GO INSTALL:
go install github.com/hahwul/dalfox/v2@latest

# OR VIA HOMEBREW:
brew install dalfox

# OR DOCKER:
docker run -it hahwul/dalfox:latest
```

### Basic Usage

```bash
# SINGLE URL:
dalfox url "https://target.com/search?q=test"

# WITH AUTHENTICATION (cookie):
dalfox url "https://target.com/search?q=test" --cookie "session=abc123"

# SCAN POST REQUEST (from Burp file):
dalfox file request.txt

# PIPE MODE (accepts URLs from stdin):
cat urls.txt | dalfox pipe

# WITH CUSTOM HEADERS:
dalfox url "https://target.com/page?id=1" \
  --header "Authorization: Bearer TOKEN123"

# BLIND XSS MODE (specify callback server):
dalfox url "https://target.com/search?q=test" \
  --blind "https://your-blind-xss-server.com/callback"

# OUTPUT ONLY VULNERABILITIES:
dalfox url "https://target.com/search?q=test" --only-poc

# WITH WORKER THREADS (faster):
dalfox url "https://target.com/" --worker 40

# SKIP BAD STATUS CODES:
dalfox url "https://target.com/search?q=test" --skip-bav

# FORMAT OUTPUT AS JSON:
dalfox url "https://target.com/search?q=test" --format json -o results.json
```

### dalfox in CI/CD Pipeline

```bash
# SCAN ALL ENDPOINTS FROM A FILE:
cat endpoints.txt | dalfox pipe --cookie "session=test_session" --format json -o xss_results.json

# ENDPOINTS.TXT FORMAT:
# https://target.com/search?q=FUZZ
# https://target.com/profile?name=FUZZ
# https://target.com/comment?id=1&text=FUZZ

# CHECK EXIT CODE IN CI:
dalfox url "https://target.com/search?q=test" && echo "No XSS" || echo "XSS FOUND!"
```

---

## Burp Suite Scanner

Burp's Active Scanner is the gold standard for comprehensive XSS detection.

### Setting Up Burp Scan

```
STEP 1: PROXY SETUP
  Browser → Proxy → 127.0.0.1:8080
  Install Burp CA certificate in browser

STEP 2: BROWSE TARGET
  Navigate through all app functionality with Burp proxy on
  All requests appear in HTTP History

STEP 3: ACTIVE SCAN
  Right-click on a request in HTTP History
  → "Scan" → "Active Scan"
  OR:
  Target → Site map → right-click URL → "Scan"

STEP 4: AUTOMATED CRAWL + SCAN
  New Scan → Crawl and Audit
  → Set scope: include target.com
  → Configure: Audit → Insertion points
  → Check: XSS, Stored XSS, DOM XSS
```

### Burp Manual XSS Testing

```
REPEATER:
  1. Send request to Repeater (Ctrl+R)
  2. Modify parameter values with XSS payloads
  3. Check response for unencoded reflection

INTRUDER (for automated parameter fuzzing):
  1. Send request to Intruder (Ctrl+I)
  2. Mark injection point: §PAYLOAD§
  3. Load XSS wordlist from SecLists or custom list
  4. Attack type: Sniper
  5. Check for unencoded reflection in results

USEFUL BURP EXTENSIONS:
  - XSS Validator: confirms XSS by actually executing payloads
  - Active Scan++ : extends scan logic
  - Param Miner: discovers hidden parameters
  - DOM Invader (in Burp browser): DOM XSS finding
```

### Burp DOM Invader

```
DOM INVADER (built into Burp browser):
  1. Open Burp's embedded Chromium browser
  2. Enable DOM Invader in DevTools → "Augmented reality" tab
  3. Browse to target
  4. DOM Invader automatically:
     → Identifies DOM XSS sources (location.hash, etc.)
     → Tests sinks (innerHTML, eval, etc.)
     → Reports exploitable DOM XSS
     → Can generate full PoC payloads

MANUAL DOM INVADER:
  In Burp browser DevTools console:
  domInvader.enablePostMessage()  // enable postMessage testing
```

---

## OWASP ZAP (Free Alternative)

```bash
# DOCKER:
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://target.com

# FULL ACTIVE SCAN:
docker run -t owasp/zap2docker-stable zap-full-scan.py -t https://target.com -r report.html

# API SCAN (for REST APIs):
docker run -t owasp/zap2docker-stable zap-api-scan.py -t https://target.com/api/openapi.json -f openapi

# WITH AUTHENTICATION:
# ZAP supports form-based auth, scripted auth, JSON auth
# Configure via GUI: Tools → Options → Authentication
```

---

## Workflow: Combining Tools for Maximum Coverage

```bash
# PHASE 1: DISCOVER ENDPOINTS:
gau target.com | grep "?" > urls.txt
waybackurls target.com | grep "?" >> urls.txt
# Remove duplicates:
sort -u urls.txt > unique_urls.txt

# PHASE 2: FAST DALFOX SCAN:
cat unique_urls.txt | dalfox pipe \
  --cookie "session=YOUR_SESSION" \
  --worker 10 \
  --format json \
  -o phase2_results.json

# PHASE 3: XSSTRIKE ON INTERESTING ENDPOINTS:
# Take endpoints that look promising from phase 2
python3 xsstrike.py -u "https://target.com/search?q=test" \
  --headers "Cookie: session=YOUR_SESSION" \
  --crawl --level 2

# PHASE 4: MANUAL VERIFICATION:
# Confirm findings in browser → take screenshot/video for report

# PHASE 5: BURP ACTIVE SCAN:
# Run on any authenticated areas dalfox/XSStrike can't reach
```

---

## Reading Tool Output

```
DALFOX OUTPUT:
  [I] Injected PoC: "><script>alert(1)</script>
  [V] Reflected parameter: q
  [POC] GET https://target.com/search?q="><script>alert(1)</script>
         ↑ CONFIRMED XSS — copy this URL as PoC!

XSSTRIKE OUTPUT:
  [+] Vulnerability Found
  Payload: <svg onload=confirm(1)>
  Efficiency: 100
  Confidence: 10
  Parameter: q
         ↑ High confidence = very likely real XSS

BURP SCANNER OUTPUT:
  Issue: Cross-site scripting (reflected)
  Severity: High
  Confidence: Certain
  URL: https://target.com/search?q=test
  Request: GET /search?q=<script>alert(1)</script>
  Response: <script>alert(1)</script> reflected
         ↑ "Certain" = Burp confirmed execution!
```

---

## Tool Comparison for Different Scenarios

```
SCENARIO                       RECOMMENDED TOOL
------                         ---------------
Quick parameter scan            dalfox (fastest)
Deep single-endpoint analysis   XSStrike (context-aware)
Full app audit (auth required)  Burp Scanner
DOM XSS hunting                 Burp DOM Invader + manual
Blind XSS detection             XSS Hunter + dalfox --blind
CI/CD pipeline integration      dalfox pipe
Behind login forms              Burp (session handling)
Bug bounty scope scan           dalfox + gau/waybackurls combo
```

---

## Related Notes
- [[02 - Reflected XSS]] — what these tools detect
- [[03 - Stored XSS]] — stored XSS found differently
- [[04 - DOM-Based XSS]] — DOM Invader for DOM XSS
- [[05 - Blind XSS]] — blind XSS detection
- [[14 - XSS Filter Bypass Techniques]] — manual bypass after tool finds reflection
- [[21 - XSS Payloads Comprehensive List]] — payload reference
