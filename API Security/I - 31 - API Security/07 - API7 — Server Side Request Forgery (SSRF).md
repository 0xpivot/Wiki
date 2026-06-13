---
tags: [API, VAPT, API7, SSRF, Cloud, Webhooks, AWS]
difficulty: intermediate
module: "31 - API Security"
topic: "31.07 API7 - Server Side Request Forgery (SSRF)"
---

# API7:2023 — Server Side Request Forgery (SSRF)

## 1. Executive Summary

Server-Side Request Forgery (SSRF) is a critical vulnerability that occurs when an API fetches a remote resource based on a user-controlled URI without validating the destination. In modern cloud-native architectures, APIs frequently interact with external services, webhooks, microservices, and file servers. If an attacker can manipulate the destination URL, they can force the backend API server to make HTTP/TCP requests on their behalf.

SSRF effectively turns the vulnerable API server into a proxy for the attacker. Because the request originates from the server itself, it bypasses external firewalls and network segmentation, gaining access to internal resources, cloud metadata endpoints, loopback services, and internal databases that are strictly isolated from the public internet.

## 2. Deep Dive: Mechanics of API SSRF

Modern applications are highly interconnected. Features that commonly introduce SSRF vulnerabilities in APIs include:
*   **Webhooks & Callbacks:** APIs that push notifications to a user-supplied URL.
*   **File Uploads via URL:** APIs that allow users to import profile pictures, documents, or data by providing a URL (e.g., `POST /api/v1/profile/picture?url=https://...`).
*   **PDF Generators / HTML Renderers:** APIs that take a URL, render the page, and return a PDF or screenshot.
*   **Link Previews:** Chat or social APIs that generate rich previews for user-submitted links.
*   **Service Integrations:** APIs connecting to external custom endpoints defined by the user (e.g., custom SSO providers, third-party SIEM logging).

### Visualizing the SSRF Architecture

```ascii
                                            +--------------------------------------+
                                            |           INTERNAL NETWORK           |
                                            |                                      |
  [ Attacker ]                              |   +------------------------------+   |
       |                                    |   | AWS / GCP Metadata Service   |   |
       | (1) POST /api/v1/fetch             |   | http://169.254.169.254       |   |
       |     {"url": "http://169.254..."}   |   +------------------------------+   |
       |                                    |                  ^                   |
       v                                    |                  |                   |
 +-----------+     (2) Proxies request      |                  | (3) Request sent  |
 | Internet  | ------------------------>  +-------------+      | from Server       |
 | Firewall  |                            | TARGET API  |------+                   |
 +-----------+                            |   SERVER    |      |                   |
                                          +-------------+      | (4) Request sent  |
       ^                                    |                  v from Server       |
       | (6) Server returns                 |   +------------------------------+   |
       |     internal metadata              |   | Internal Admin Dashboard     |   |
       +------------------------------------+   | http://localhost:8080/admin  |   |
                                            |   +------------------------------+   |
                                            +--------------------------------------+
```

## 3. Types of SSRF

SSRF vulnerabilities generally fall into one of three categories based on the API's response behavior:

1.  **Basic (In-Band) SSRF:** The attacker provides a URL, the server fetches it, and the API directly returns the fetched data in the HTTP response. This is the most dangerous as it allows direct data exfiltration (e.g., reading cloud credentials).
2.  **Blind SSRF:** The server makes the requested outbound call but does *not* return the response body to the attacker. The attacker must rely on out-of-band (OOB) techniques, such as monitoring DNS lookups or incoming HTTP logs on an attacker-controlled server, to confirm the vulnerability. Blind SSRF is often used to trigger internal remote code execution (RCE) chains or internal state changes.
3.  **Semi-Blind (Time-Based/Error-Based) SSRF:** The response body isn't returned, but the attacker can infer information based on error messages (e.g., "Connection Refused" vs. "Timeout") or response times. This allows for internal port scanning.

## 4. Real-World Exploitation Scenarios

### Scenario A: Cloud Metadata Extraction
Modern cloud environments (AWS, GCP, Azure, Oracle) expose instance metadata services at a non-routable link-local IP address: `169.254.169.254`.

**The Request:**
```http
POST /api/v1/import_data HTTP/1.1
Host: api.target.com
Content-Type: application/json

{
  "source_url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-production-role"
}
```

**The Consequence:** The API server fetches the URL and returns the temporary AWS `AccessKeyId`, `SecretAccessKey`, and `Token`. The attacker configures their local AWS CLI with these credentials and assumes the IAM role of the production server, potentially taking over the entire AWS account.

*(Note: AWS introduced IMDSv2 to mitigate this by requiring a custom `X-aws-ec2-metadata-token` header, but many organizations still support IMDSv1 for legacy compatibility).*

### Scenario B: Internal Network Port Scanning & Service Fingerprinting
An attacker uses Semi-Blind SSRF to map the internal network infrastructure.

**The Request:**
```http
POST /api/v1/webhooks/register HTTP/1.1
Host: api.target.com
Content-Type: application/json

{
  "webhook_url": "http://10.0.0.5:6379"
}
```

**The Consequence:** If the API returns a 500 error instantly, the port might be closed. If it hangs and returns a timeout error, the IP exists but is firewalled. If it returns an unexpected data parsing error, an internal Redis server is open on 10.0.0.5:6379. The attacker can then craft an SSRF payload to send Redis commands (like `SLAVEOF` or writing SSH keys to disk) using the `dict://` or `gopher://` schemas.

### Scenario C: Local File Inclusion via Alternative Schemas
SSRF isn't just about `http://` or `https://`. Many underlying HTTP libraries support other URI schemas.

**The Request:**
```http
POST /api/v1/documents/convert HTTP/1.1
Host: api.target.com
Content-Type: application/json

{
  "doc_url": "file:///etc/passwd"
}
```

**The Consequence:** The API's underlying fetch library (e.g., cURL, urllib, Java's URLConnection) interprets the `file://` schema and reads the local system file, returning the contents of `/etc/passwd` to the attacker.

## 5. Advanced Evasion and Bypass Techniques

When developers attempt to implement blacklists (e.g., blocking `169.254.169.254` or `localhost`), attackers use sophisticated techniques to bypass these filters:

1.  **IP Encoding / Obfuscation:**
    *   Decimal: `http://2852039166` (resolves to 169.254.169.254)
    *   Octal: `http://0251.0376.0251.0376`
    *   Hexadecimal: `http://0xA9FEA9FE`
    *   Short-hand IPv4: `http://127.1` (resolves to 127.0.0.1)
2.  **DNS Rebinding:**
    *   The attacker sets up a malicious DNS server.
    *   The API validates the domain (e.g., `attacker.com`), and the DNS server resolves it to a safe, public IP (e.g., `8.8.8.8`).
    *   The validation passes. Just milliseconds later, the API actually makes the HTTP request. The DNS server replies with a short TTL, causing a second DNS lookup. This time, the DNS server resolves the domain to `169.254.169.254`.
3.  **Open Redirects:**
    *   If the target API correctly validates the initial URL but blindly follows HTTP 301/302 redirects, the attacker can point the API to `http://attacker.com/redirect`.
    *   The attacker's server responds with: `Location: http://169.254.169.254/latest/meta-data/`
4.  **Enclosed / IPv6 Localhost:**
    *   `http://[::]:80/`
    *   `http://0000::1:80/`
    *   `http://localtest.me` (Public DNS record that resolves to 127.0.0.1)

## 6. Detection and Identification

### Testing for SSRF
*   Identify all endpoints accepting URLs, IP addresses, or file imports.
*   Submit payloads pointing to external interaction servers (e.g., Burp Collaborator, ProjectDiscovery's interactsh). If a pingback is received, Blind SSRF is present.
*   Test alternative URI schemas: `file://`, `dict://`, `gopher://`, `ftp://`.
*   Test edge-case encodings of loopback addresses to bypass basic regex filters.

### Log Analysis
*   Look for outbound network traffic originating from the API servers to unexpected external IPs or internal subnets.
*   Monitor cloud metadata endpoints for access logs originating from unauthorized application containers rather than cloud management agents.

## 7. Defense in Depth and Mitigation

Relying on a single mitigation for SSRF is doomed to fail due to bypass techniques like DNS Rebinding. A defense-in-depth strategy is mandatory.

### Application Level Mitigations
1.  **Strict Allow-listing (The Best Approach):** If the API only needs to fetch images from specific partners, maintain a strict list of allowed hostnames or domains. Reject all others.
2.  **Disable Unused URL Schemas:** Ensure the HTTP client library used by the backend explicitly disables `file://`, `ftp://`, `gopher://`, and `dict://` protocols. Force `https://` only.
3.  **Disable HTTP Redirections:** Configure the API's HTTP client to *not* follow redirects automatically. If redirects must be followed, validate the `Location` header URL against the allow-list *before* proceeding.
4.  **Dedicated Safe Resolvers:** Implement a custom DNS resolver for the HTTP client that refuses to resolve any domains to internal IPs, loopback, or private CIDR ranges (RFC 1918).

### Network Level Mitigations
1.  **Network Segmentation:** API servers that need to make outbound requests should be deployed in a segregated network zone (e.g., a specific DMZ or VPC subnet).
2.  **Egress Filtering:** Implement strict egress firewalls. The API server should only be allowed to connect to the internet on ports 80/443, and ideally only to specifically approved IP addresses. Block internal routing from the API server to sensitive internal enclaves.
3.  **Cloud Hardening:** Always enforce IMDSv2 on AWS, which requires a custom HTTP header for metadata access. Similar metadata protections should be enabled on GCP/Azure.

### Example Remediation (Python Requests)
```python
import requests
import socket
from urllib.parse import urlparse

ALLOWED_DOMAINS = ["api.partner.com", "cdn.trusted.com"]

def safe_fetch(url):
    parsed = urlparse(url)
    
    # 1. Enforce Schema
    if parsed.scheme != "https":
        raise Exception("Only HTTPS is allowed.")
        
    # 2. Strict Domain Allow-list
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise Exception("Domain not in allow-list.")
        
    # 3. Prevent DNS Rebinding (Resolve once, connect by IP)
    try:
        ip = socket.gethostbyname(parsed.hostname)
    except Exception:
        raise Exception("DNS resolution failed.")
        
    # 4. Check against private IP ranges (simplified check)
    if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("127.") or ip.startswith("169.254."):
        raise Exception("Forbidden IP space.")
        
    # 5. Fetch without following redirects
    # Note: We connect to the IP but pass the original Host header
    headers = {"Host": parsed.hostname}
    safe_url = f"https://{ip}{parsed.path}?{parsed.query}"
    
    response = requests.get(safe_url, headers=headers, allow_redirects=False, timeout=5)
    return response.text
```

## 8. Chaining Opportunities

SSRF is often the gateway vulnerability to critical system compromise:
*   **[[08 - API8 — Security Misconfiguration]]:** Overly permissive internal network rules allow the SSRF to reach sensitive services.
*   **[[Remote Code Execution (RCE)]]:** Using SSRF to send crafted payloads to internal, unauthenticated services like Redis, Memcached, or Jenkins.
*   **[[10 - API10 — Unsafe Consumption of APIs]]:** Exploiting an SSRF within a third-party API provider to attack *their* internal network, poisoning data sent back to the primary API.

## 9. Related Notes
- [[Cloud Metadata Attack Surface]]
- [[DNS Rebinding Techniques]]
- [[Securing Webhooks and Callbacks]]

---
*End of Note*
