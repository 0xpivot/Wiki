---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.53 Server — Version Disclosure, Remove It"
---

# 03.53 — Server

## What is it?

The `Server` response header identifies the web server software and often its version. Like `X-Powered-By`, it's purely informational for clients but gives attackers a direct map to known vulnerabilities for the specific version disclosed.

---

## Common Server Header Values

```
Server: Apache/2.4.41 (Ubuntu)            → Apache version + Linux distro!
Server: nginx/1.18.0                       → Nginx version
Server: Microsoft-IIS/10.0                 → IIS version
Server: Apache-Coyote/1.1                  → Tomcat
Server: Jetty/9.4.31.v20200723             → Jetty + exact build!
Server: LiteSpeed                          → LiteSpeed (no version)
Server: cloudflare                         → Cloudflare (expected)
Server: openresty/1.19.3.1                 → OpenResty (Nginx-based)
```

---

## Attack: Version-Targeted Exploitation

```
EXAMPLE: Server: Apache/2.4.49

CVE-2021-41773 (Apache 2.4.49):
  Path traversal + RCE!
  GET /cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh HTTP/1.1
  
  JUST FROM THE SERVER HEADER → immediate critical exploit!

LOOKUP FLOW:
  1. curl -sI https://target.com | grep "^Server:"
  2. → Server: Apache/2.4.49
  3. searchsploit "apache 2.4.49"
     OR: exploit-db.com search
     OR: packetstormsecurity.com
  4. Found: CVE-2021-41773 → test immediately!
```

---

## OS Fingerprinting from Server Header

```
Server: Apache/2.4.41 (Ubuntu)     → Ubuntu Linux
Server: Apache/2.4.6 (CentOS)      → CentOS Linux
Server: Apache/2.4.38 (Debian)     → Debian Linux
Server: Apache/2.2.34 (Debian)     → Old Debian → probably EOL!
Server: Microsoft-IIS/8.5          → Windows Server 2012

WHY IT MATTERS:
  OS version → specific kernel exploits!
  "Ubuntu with Apache 2.4.41" → Ubuntu 20.04 LTS → specific packages/versions!
```

---

## Full Stack Fingerprinting

```bash
# Get all disclosure headers:
curl -sI https://target.com | grep -iE "^server:|^x-powered-by:|^x-aspnet|^x-runtime|^x-drupal|^via:"

# Use WhatWeb for comprehensive fingerprinting:
whatweb -v https://target.com

# Shodan for passive fingerprinting:
shodan host <ip>
shodan search "Server: Apache/2.4.49"  → find all vulnerable servers!

# Censys:
censys search 'services.http.response.headers.server="Apache/2.4.49"'
```

---

## Detecting Through Error Pages

```
Default error pages often reveal server version even if header is hidden:
  404: "Apache/2.4.41 Server at target.com Port 443"
  403: "nginx/1.18.0"
  
ATTACK:
  GET /nonexistent-path-12345 HTTP/1.1
  → Trigger 404 → check error page for version disclosure!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Apache version in Server | `ServerTokens Prod` in Apache config → just "Apache" |
| Nginx version in Server | `server_tokens off` in Nginx config |
| IIS version in Server | Disable via IIS Manager → HTTP Response Headers |
| Default error pages with version | Configure custom error pages |

**Apache:**
```apache
ServerTokens Prod
ServerSignature Off
```

**Nginx:**
```nginx
server_tokens off;
```

---

## Related Notes
- [[52 - X-Powered-By]] — framework fingerprinting
- [[54 - X-AspNet-Version]] — ASP.NET version
- [[Module 17 - Recon]] — recon and fingerprinting
