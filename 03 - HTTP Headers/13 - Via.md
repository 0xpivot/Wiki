---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.13 Via — Proxy Chain Disclosure"
---

# 03.13 — Via

## What is it?

The `Via` header is added by proxies to indicate that the request was forwarded through them. Each proxy in the chain appends its information. It's part of the HTTP/1.1 spec (RFC 7230). It can reveal internal infrastructure: proxy versions, internal hostnames, and network topology.

---

## Format

```
Via: [protocol-version] [host] [comment]

Examples:
  Via: 1.1 proxy1.internal.corp
  Via: 1.1 varnish                ← Varnish cache server
  Via: 1.1 squid-proxy:3128
  Via: 2 cloudflare               ← HTTP/2 via Cloudflare
  Via: 1.1 proxy1, 1.1 proxy2    ← chain of two proxies
```

---

## Information Disclosed

```
EXAMPLE RESPONSE:
  Via: 1.1 proxy.internal.corp:8080

REVEALS:
  - Internal hostname: proxy.internal.corp
  - Internal port: 8080
  - Proxy software (sometimes version)
  - Number of hops in chain
  - Internal network structure

ATTACK VALUE:
  - Internal hostnames → SSRF targets
  - Internal port numbers → service enumeration
  - Software version → CVE lookup
  - Network topology → better understanding of target infrastructure
```

---

## SSRF via Discovered Internal Hosts

```
1. Enumerate target's headers:
   curl -sI https://target.com/ | grep -i via
   Via: 1.1 internal-cache.corp.local

2. Use discovered hostname in SSRF:
   GET /ssrf?url=http://internal-cache.corp.local:8080/
   → May reach internal service!

3. Check if internal proxy is accessible:
   curl http://internal-cache.corp.local:8080/
   (from compromised host or through SSRF)
```

---

## Detection / Enumeration

```bash
# Check Via header on responses
curl -sI https://target.com/ | grep -i via
curl -sI https://target.com/ | grep -i "via\|x-cache\|x-served-by\|x-varnish"

# All proxy-related headers at once
curl -sI https://target.com/ | grep -iE "via|x-cache|x-proxy|x-forwarded|age|server"

# The "Age" header (how long since cached) also confirms caching proxy:
# Age: 300 → Response cached 5 minutes ago
```

---

## Via in Requests (Proxy Chaining)

```
When you send a request through a proxy (like Burp Suite):
  Via: 1.1 burp-proxy    ← reveals you're using a proxy!

WAF might flag known proxy signatures in Via.
In stealth testing, set Via to empty or a legitimate value.
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Via reveals internal hostnames | Strip/rewrite Via header at external-facing proxy |
| Version information in Via | Use generic identifier instead of product/version |

---

## Related Notes
- [[12 - Forwarded]] — RFC 7239 standard proxy header
- [[02 - X-Forwarded-For]] — IP disclosure
- [[52 - X-Powered-By]] — other tech fingerprinting header
- [[53 - Server]] — server version disclosure
