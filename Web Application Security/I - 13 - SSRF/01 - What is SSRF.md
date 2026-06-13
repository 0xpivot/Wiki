---
tags: [vapt, ssrf, beginner]
difficulty: beginner
module: "13 - SSRF"
topic: "13.01 What is SSRF?"
portswigger_labs: ["Basic SSRF against the local server", "Basic SSRF against another back-end system"]
---

# 13.01 — What is SSRF?

## Core Concept

```
SSRF = Server-Side Request Forgery

The ATTACKER tricks the SERVER into making HTTP requests on the attacker's behalf.

NORMAL WEB REQUEST:
  Browser → internet → target server → response

SSRF ATTACK:
  Browser → target server → [attacker-controlled URL] → target server fetches it!
  
  The server becomes a proxy for the attacker.
  The server can reach places the attacker cannot directly access!
```

---

## Why SSRF Is Dangerous

```
WHAT THE SERVER CAN REACH THAT YOU CAN'T:
  ✓ Internal services: 192.168.x.x, 10.x.x.x (internal network!)
  ✓ Localhost services: 127.0.0.1:6379 (Redis, Memcached, etc.)
  ✓ Cloud metadata APIs: 169.254.169.254 (AWS/GCP/Azure credentials!)
  ✓ Other servers in the same VPC/datacenter
  ✓ Internal admin panels (not exposed to internet)
  ✓ Internal databases (Elasticsearch on 9200, MongoDB on 27017)
  ✓ Docker/Kubernetes APIs (172.17.0.1)

WORST CASE:
  SSRF to AWS metadata endpoint → steal cloud credentials →
  Access ALL cloud resources → full cloud account takeover!
```

---

## Simple SSRF Example

```
VULNERABLE APPLICATION FEATURE:
  "Preview URL" functionality:
  POST /preview
  Body: url=https://example.com
  
  App fetches: https://example.com → shows preview to user

ATTACK:
  POST /preview
  Body: url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
  
  App fetches: AWS metadata endpoint!
  Response contains: AWS access keys, secret keys, session tokens!
  Attacker reads the response → has AWS credentials!
```

---

## Types of SSRF

```
IN-BAND (BASIC) SSRF:
  ✓ Server fetches URL and returns response to attacker
  ✓ Most exploitable — attacker sees everything
  ✓ Can interact with internal services
  ✓ Example: "fetch URL" feature that shows response

BLIND SSRF:
  ✗ Server fetches URL but does NOT return response to attacker
  ✓ Attacker uses out-of-band techniques (Burp Collaborator, interactsh)
  ✓ Can confirm server made request (DNS ping, HTTP hit)
  ✓ Harder to exploit for data exfiltration
  ✓ Example: "webhook notification" URL that sends notifications

SEMI-BLIND SSRF (Error-Based):
  ✓ Server doesn't return content but shows different errors
  ✓ Error: "Connection refused" vs "Connection timed out" vs "200 OK"
  ✓ Can map internal network topology via errors
  ✓ Example: Observing response time differences
```

---

## Where SSRF Appears

```
COMMON FEATURES THAT LEAD TO SSRF:

URL PARAMETERS:
  ?url=https://...
  ?redirect=https://...
  ?image=https://...
  ?feed=https://...
  ?webhook=https://...
  
FORM INPUTS:
  Import from URL (document/spreadsheet importers)
  Webhook configuration
  "Fetch avatar from URL"
  "Preview link"
  
HTTP HEADERS:
  X-Forwarded-Host: (if app fetches from host in header)
  Referer: (if app fetches page to show link preview)
  Host: (virtual hosting misconfig)

DOCUMENT/FILE PROCESSING:
  PDF generation (wkhtmltopdf fetches resources)
  DOCX/XLSX with remote image URLs
  XML with external entity loading (XXE → SSRF)
  SVG files with external resources
  
API INTEGRATIONS:
  "Connect your account" (OAuth redirect URIs)
  Webhook delivery systems
  Proxy services
```

---

## ASCII Diagram: SSRF Flow

```
ATTACKER                APP SERVER              INTERNAL/CLOUD
   │                        │                       │
   │  POST /preview         │                       │
   │  url=http://           │                       │
   │  169.254.169.254/...   │                       │
   │───────────────────────→│                       │
   │                        │  GET /latest/...      │
   │                        │───────────────────────→
   │                        │                       │
   │                        │  200 OK               │
   │                        │  {"AccessKeyId": ...} │
   │                        │←──────────────────────
   │  Response with         │                       │
   │  AWS credentials!      │                       │
   │←───────────────────────│                       │
   │                        │                       │
ATTACKER READS AWS CREDENTIALS → FULL CLOUD TAKEOVER!
```

---

## Basic Impact Scale

```
LOW IMPACT:
  SSRF to public internet → limited (attacker can do this themselves)
  SSRF to internal IPs that return nothing interesting

MEDIUM IMPACT:
  SSRF mapping internal network topology
  SSRF reaching internal services that don't require auth

HIGH IMPACT:
  SSRF to admin panel → gaining admin access
  SSRF to internal APIs → data exfiltration
  SSRF to Redis/Memcached → code execution potential

CRITICAL IMPACT:
  SSRF to cloud metadata → cloud credential theft
  SSRF + RCE on internal service → shell access
  SSRF to Kubernetes API → container escape
  SSRF leading to full infrastructure compromise
```

---

## Related Notes
- [[02 - Basic SSRF Fetching Internal URLs]] — hands-on testing
- [[03 - SSRF via URL Parameters]] — finding SSRF via URL params
- [[07 - Blind SSRF]] — when you can't see the response
- [[09 - SSRF Cloud Metadata AWS]] — highest impact scenario
- [[Module 10 - Injection Attacks — PDF Injection]] — PDF SSRF
