---
tags: [vapt, open-redirect, ssrf, chaining, advanced]
difficulty: advanced
module: "24 - Open Redirect"
topic: "24.07 Open Redirect + SSRF (chained)"
---

# 24.07 — Open Redirect + SSRF (Chained)

## What is it?
Server-Side Request Forgery (SSRF) occurs when a backend server is tricked into making HTTP requests to internal networks. To prevent SSRF, developers often implement strict domain allowlists (e.g., "The server is only allowed to fetch URLs that belong to `https://api.trusted.com`").

If `https://api.trusted.com` has an Open Redirect vulnerability, an attacker can completely bypass the SSRF allowlist. 

The attacker tells the vulnerable SSRF service to fetch `https://api.trusted.com/redirect?url=http://169.254.169.254/latest/meta-data/`. The SSRF filter checks the domain, sees `api.trusted.com`, and allows the request. The backend server reaches out to the trusted API, which responds with an HTTP 302 Redirect pointing to the internal AWS metadata IP. Most HTTP libraries (like `curl`, Python's `requests`, or Java's `HttpURLConnection`) will **automatically follow redirects by default**, causing the backend server to fetch the internal IP, bypassing the filter entirely!

Think of it like a strict border checkpoint. The guard only lets vehicles belonging to the "Trusted Delivery Company" pass. An attacker sneaks a bomb into a Trusted Delivery Company truck. The guard checks the truck's logo, lets it through, and the bomb detonates inside the walls.

## ASCII Diagram
```text
[Attacker Payload] 
fetch_url = https://trusted.com/redirect?url=http://169.254.169.254/
       │
       ▼
[Target Application (SSRF Filter)]
       │
       ├─ Validates domain: Is it "trusted.com"? YES!
       ├─ Executes HTTP GET to trusted.com
       │
       ▼
[trusted.com (Open Redirect)]
       │
       ├─ Responds: HTTP 302 Found
       ├─ Location: http://169.254.169.254/
       │
       ▼
[Target Application (HTTP Library)]
       │
       ├─ Automatically follows the 302 Redirect
       ├─ Executes HTTP GET to http://169.254.169.254/
       ├─ Fetches AWS Cloud Metadata (IAM Credentials)
       │
[Response] ──> Returns internal cloud credentials to attacker!
```

## How to Find It
- **Manual steps:**
  1. Identify an SSRF vulnerability that is protected by an allowlist (e.g., an image fetching service that only allows URLs from `images.target.com` or `imgur.com`).
  2. Hunt for an Open Redirect on any of the allowed domains.
  3. Combine them: Pass the Open Redirect URL to the SSRF endpoint, pointing the redirect payload to a Burp Collaborator URL.
  4. If you get an HTTP ping on your Collaborator from the target server's backend IP, the SSRF library followed the redirect!

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Chain the vulnerabilities to bypass the filter.
  2. Point the final destination of the redirect to internal infrastructure.
  3. Common targets: `http://localhost:6379` (Redis), `http://localhost:8080` (Internal admin panels), or `http://169.254.169.254/` (Cloud metadata).
  4. Extract the response.

- **Actual payloads:**
  **AWS Metadata SSRF Bypass:**
  ```text
  POST /webhook
  url=https://api.allowed.com/logout?next=http://169.254.169.254/latest/meta-data/iam/security-credentials/
  ```

## Real-World Example
A Bug Bounty hunter was testing a web application that fetched RSS feeds. The application only allowed fetching feeds from `*.github.com`. The hunter knew they couldn't host an internal IP on GitHub, but they found an Open Redirect in a specific GitHub enterprise authentication flow. They supplied the GitHub Open Redirect URL to the RSS reader. The RSS reader checked the domain (`github.com` - passed!), made the request, received a 302 redirect to `http://127.0.0.1:8080/admin`, followed it, and returned the HTML of the internal administrator dashboard.

## How to Fix It
- **Developer remediation:**
  When making outbound HTTP requests from backend servers, **disable automatic redirect following** in your HTTP library. If you must follow redirects, you must intercept the 302 response and explicitly run the `Location:` header URL through your SSRF allowlist filter *before* allowing the library to fetch the new destination.

- **Code snippet:**
  **Python (Requests - Disabling Redirects):**
  ```python
  import requests

  def safe_fetch(url):
      # Validate initial URL
      if not url.startswith("https://trusted.com"):
          return "Invalid domain"

      # explicitly set allow_redirects=False to prevent SSRF chaining
      response = requests.get(url, allow_redirects=False)
      
      if response.status_code in (301, 302):
          return "Redirects are strictly forbidden."
          
      return response.text
  ```

## Chaining Opportunities
- This vuln + [[13.01 SSRF (Server-Side Request Forgery)]] → The perfect chain. An Open Redirect is the ultimate weapon against strict SSRF allowlists.

## Related Notes
- [[24.01 What is Open Redirect?]]
- [[13.01 SSRF (Server-Side Request Forgery)]]
