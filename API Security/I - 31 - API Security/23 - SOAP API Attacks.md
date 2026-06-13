---
tags: [API, Security, SOAP, XML, XXE, Injection, Legacy]
difficulty: advanced
module: "31 - API Security"
topic: "31.23 SOAP API Attacks"
---

# SOAP API Attacks

## Introduction
SOAP (Simple Object Access Protocol) is a messaging protocol specification for exchanging structured information in the implementation of web services. Unlike REST, which relies heavily on HTTP verbs and standard URIs, SOAP relies almost exclusively on XML for its message format and typically uses POST requests for all operations. 

While modern applications largely favor REST or GraphQL, SOAP remains deeply entrenched in enterprise environments, financial systems, telecommunications, and legacy B2B integrations. The complexity of the SOAP specification, combined with its heavy reliance on XML parsing, introduces a massive attack surface. Attacking SOAP APIs requires a solid understanding of XML vulnerabilities, WSDL (Web Services Description Language) parsing, and complex encapsulation schemes like WS-Security.

## The Anatomy of a SOAP Message
A SOAP message is an XML document containing the following elements:
- **Envelope:** The root element that identifies the XML document as a SOAP message.
- **Header (Optional):** Contains application-specific information (like authentication, routing, or transaction IDs).
- **Body:** Contains the actual call and response information.
- **Fault (Optional):** Contained within the Body, provides information about errors.

```xml
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:m="http://www.example.org/stock">
  <soap:Header>
     <!-- WS-Security or custom headers go here -->
  </soap:Header>
  <soap:Body>
    <m:GetStockPrice>
      <m:StockName>IBM</m:StockName>
    </m:GetStockPrice>
  </soap:Body>
</soap:Envelope>
```

## Architecture and Attack Flow

```text
+----------------+       1. Malicious XML / XXE Payload       +----------------+
|                |------------------------------------------->|                |
|    Attacker    |                                            |    XML Parser  |
|                |<-------------------------------------------|    (Backend)   |
+----------------+       2. Local File / SSRF Data returned   +----------------+
        |                                                             |
        | 3. WSDL Manipulation                                        | 4. Backend Processing
        v                                                             v
+----------------+                                            +----------------+
|                |       5. Forged SOAP Envelope              |                |
| SOAP UI / Burp |------------------------------------------->|  SOAP Service  |
|                |                                            |  (Logic Layer) |
+----------------+                                            +----------------+
```

## Key Attack Vectors

### 1. WSDL Reconnaissance and Enumeration
The WSDL file is the blueprint of a SOAP API. It defines all available operations, expected parameters, and data types.
- **Discovery:** Look for endpoints ending in `?wsdl` or `.wsdl` (e.g., `https://api.target.com/service?wsdl`).
- **Exploitation:** Load the WSDL into tools like SoapUI or Burp Suite's Wsdler extension. This automatically generates valid requests for every single method the API supports.
- Attackers will often find administrative or internal methods (e.g., `DeleteUser`, `ResetPassword`, `GetSystemConfig`) defined in the WSDL that are not properly protected by authentication.

### 2. XML External Entity (XXE) Injection
Because SOAP relies entirely on XML, the underlying XML parser is the first target. If the parser is configured to resolve external entities, the application is vulnerable to XXE.
- **Attack:** The attacker injects an external entity definition in the XML preamble and references it within the SOAP Body.
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [  
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetUserDetails>
      <Username>&xxe;</Username>
    </GetUserDetails>
  </soap:Body>
</soap:Envelope>
```
- **Impact:** Local file disclosure, Server-Side Request Forgery (SSRF), and potentially Remote Code Execution (if expecting PHP wrappers, etc.).

### 3. XML Signature Wrapping (XSW)
Many SOAP APIs use WS-Security to sign parts of the message (usually the Body) to ensure integrity and non-repudiation.
- **Vulnerability:** The XML parser verifies the signature of a specific element (e.g., identified by an ID). However, the application logic processes a *different* element with the same name.
- **Attack:** The attacker takes a legitimately signed SOAP message, moves the original signed `Body` to a harmless location (like the `Header`), and inserts a malicious `Body` payload. The signature validator sees the original signed element and approves it, but the business logic processes the malicious `Body`.
- **Impact:** Authentication bypass, privilege escalation, and execution of unauthorized actions.

### 4. SOAP Action Spoofing
HTTP requests carrying SOAP messages often include a `SOAPAction` HTTP header. This header tells the server which operation is being called without requiring the server to parse the entire XML body first (for performance routing).
- **Vulnerability:** The routing mechanism relies on the `SOAPAction` header, but the backend execution logic relies on the XML Body.
- **Attack:** An attacker changes the `SOAPAction` header to a low-privileged operation (e.g., `SOAPAction: "GetPublicProfile"`), bypassing WAF or gateway security checks. However, the XML Body contains a high-privileged operation (e.g., `<AdminUserDelete>`).
- **Impact:** Authorization bypass and execution of administrative functions.

### 5. XML Bomb (Billion Laughs Attack)
A form of Denial of Service (DoS) specific to XML parsers.
- **Attack:** The attacker creates a nested XML entity structure where one entity refers to multiple other entities, expanding exponentially.
```xml
<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!-- ... repeats up to lol9 ... -->
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<soap:Envelope...>
 <soap:Body><test>&lol9;</test></soap:Body>
</soap:Envelope>
```
- **Impact:** CPU and memory exhaustion, crashing the SOAP service.

## Security Testing Methodology for SOAP

1. **WSDL Discovery:** Use `gobuster` or manual browsing to find `?wsdl` endpoints.
2. **Parsing and Generation:** Import the WSDL into SoapUI. Generate all requests.
3. **Authentication Testing:** Try calling sensitive methods without WS-Security headers. Try modifying the `UsernameToken` in WS-Security.
4. **Injection Testing:** Fuzz all input parameters with standard SQLi, XSS, and Command Injection payloads. (Backend systems processing SOAP data are often legacy mainframes or old SQL databases highly vulnerable to injection).
5. **XXE Testing:** Inject DTDs into the XML declaration. Use Out-of-Band (OOB) techniques if the parser is blind.
6. **Header Manipulation:** Alter `SOAPAction` and `Content-Type` headers to look for inconsistencies between gateway routing and backend processing.

## Remediation and Secure Design

### 1. Disable DTD Processing
The absolute most critical defense against XXE and XML Bombs. Configure the XML parser to explicitly disable Document Type Definitions (DTDs) and external entity resolution.
- Java (JAXP): `factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);`

### 2. Strict Schema Validation
Validate all incoming SOAP messages against a strict XML Schema (XSD). Reject any message that contains unexpected elements, attributes, or incorrect data types before the application logic processes it.

### 3. Secure WS-Security Implementation
- If using XML Signatures, ensure the validator and the application logic are referencing the *exact same* element in the DOM tree (mitigates XSW). Use strict XPath targeting.
- Enforce message timestamps to prevent replay attacks.

### 4. Consistent Operation Resolution
Ensure that the `SOAPAction` HTTP header (if used) strictly matches the operation defined in the SOAP Envelope Body. Reject requests where these do not align.

### 5. Migrate to Modern Alternatives (If Possible)
Where feasible, deprecate public-facing SOAP endpoints in favor of REST or GraphQL with JSON, which eliminates the XML parsing attack surface entirely.

## Chaining Opportunities
- **[[Injection Vulnerabilities]]**: Data extracted from SOAP XML is frequently fed directly into backend SQL databases or LDAP directories without sanitization.
- **[[Server-Side Request Forgery (SSRF)]]**: XXE in a SOAP parser can easily be leveraged into an SSRF to scan internal network infrastructure.

## Related Notes
- [[XML External Entity (XXE) Deep Dive]]
- [[API Gateway Security Patterns]]
- [[Legacy System Penetration Testing]]
