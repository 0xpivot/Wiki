---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.22 DNS Rebinding Deep Dive"
---

# DNS Rebinding Deep Dive

## Introduction
DNS Rebinding is a highly sophisticated attack technique used to bypass the Same-Origin Policy (SOP) by manipulating the Domain Name System (DNS) resolution process. It allows an attacker to force a victim's browser to execute JavaScript on a malicious domain, but then redirect subsequent HTTP requests to internal IP addresses or loopback interfaces, effectively turning the victim's browser into a proxy for attacking internal networks.

This attack is particularly devastating against IoT devices, internal administrative panels, and services binding to `localhost` without proper Host header validation or authentication.

## Technical Deep Dive

### The Same-Origin Policy (SOP)
SOP is a fundamental security mechanism in modern web browsers. It restricts how a document or script loaded from one origin can interact with a resource from another origin. An origin is defined by the scheme (protocol), host (domain), and port.

For example, `http://attacker.com` cannot read the response from `http://192.168.1.1` because the origins differ. DNS Rebinding tricks the browser into believing both requests are to the *same* origin.

### The Attack Mechanism
DNS Rebinding works by providing a DNS record with a very short Time-To-Live (TTL) and changing the resolved IP address between the initial load of the malicious page and subsequent XMLHttpRequests (XHR) or Fetch API calls.

1. **Victim visits `attacker.com`:** The browser makes a DNS request for `attacker.com`.
2. **First DNS Response:** The attacker's custom DNS server responds with the IP address of the attacker's web server (e.g., `203.0.113.5`) and a TTL of 0 or a very low value.
3. **Payload Delivery:** The victim's browser connects to `203.0.113.5` and downloads malicious JavaScript.
4. **Execution and Wait:** The malicious script starts executing. It might wait for a few seconds to ensure the DNS cache expires.
5. **Second Request:** The JavaScript makes an XHR or Fetch request to `http://attacker.com/api/admin`.
6. **Second DNS Response:** Because the TTL expired, the browser makes a new DNS request for `attacker.com`. The attacker's DNS server now responds with the target internal IP address (e.g., `127.0.0.1` or `192.168.1.1`).
7. **The Exploit:** The browser connects to `192.168.1.1`. Crucially, because the URL is still `http://attacker.com/api/admin`, the browser considers this request to be the **same origin** as the initial page load. SOP is bypassed. The attacker can now read the response from the internal service.

### ASCII Diagram: Attack Flow

```text
     Victim Browser                               Attacker DNS Server
           |                                              |
           |---(1) DNS Query: attacker.com -------------->|
           |                                              |
           |<--(2) DNS Response: 203.0.113.5 (TTL=0) -----|
           |                                              |
           |---(3) HTTP GET / (to 203.0.113.5) ---------->| Attacker Web Server
           |                                              |
           |<--(4) HTTP 200 OK (Malicious JS) ------------|
           |                                              |
           | [ JS waits for TTL to expire ]               |
           |                                              |
           |---(5) DNS Query: attacker.com -------------->|
           |                                              |
           |<--(6) DNS Response: 192.168.1.1 -------------|
           |                                              |
           |---(7) HTTP GET /admin (to 192.168.1.1) ----->| Internal Router/IoT
           |       Host: attacker.com                     |
           |                                              |
           |<--(8) HTTP 200 OK (Admin Data) --------------|
           |                                              |
           | [ JS exfiltrates data to attacker ]          |
           v                                              v
```

### Requirements for Success
For a DNS rebinding attack to be successful, several conditions must be met:
1. **Low TTL Enforcement:** The victim's OS and browser must respect the low TTL provided by the attacker's DNS server. Browsers often implement DNS pinning (caching records regardless of TTL to prevent rebinding), so attackers employ techniques to flush the cache or wait it out.
2. **Target Vulnerability:** The internal service being targeted must not require authentication (or rely on default credentials) and must not strictly validate the `Host` header.
3. **Port Alignment:** The attacker's web server and the target internal service must use the same port (e.g., both on port 80). If the internal service is on port 8080, the victim must visit `http://attacker.com:8080` initially.

### Bypassing DNS Pinning
Modern browsers implement DNS pinning to mitigate rebinding. However, attackers can bypass this by:
- **Multiple Subdomains:** Instead of relying on a single domain, the attacker uses wildcards. `a.attacker.com` resolves to the attacker, loads an iframe pointing to `b.attacker.com`. `b` resolves to the internal IP.
- **Connection Exhaustion:** The attacker forces the browser to open many connections, evicting the pinned DNS entry from the browser's cache.
- **WebRTC:** WebRTC can be used to leak internal IP addresses, making the targeting phase much faster and more accurate.

### Exploitation Tools
- **Singularity of Origin:** A powerful framework for performing DNS rebinding attacks. It includes a custom DNS server and a web front-end to manage payloads and target IP ranges.
- **rbndr:** A simple DNS rebinding service (e.g., `7f000001.c0a80001.rbndr.us` will alternate between resolving to `127.0.0.1` and `192.168.0.1`).
- **Tavis Ormandy's DNS Rebind Toolkit:** A collection of tools for demonstrating the attack.

### Defensive Measures

#### 1. Host Header Validation
The most robust defense against DNS rebinding is strict `Host` header validation on the server side. If a service is meant to be accessed via `localhost` or an internal IP, it should reject any HTTP request where the `Host` header does not match exactly `localhost` or the specific IP address.

```python
# Vulnerable Flask
@app.route('/')
def admin():
    return "Sensitive Admin Data"

# Secure Flask
@app.route('/')
def admin():
    if request.headers['Host'] not in ['localhost:8080', '127.0.0.1:8080']:
        abort(403)
    return "Sensitive Admin Data"
```

#### 2. Authentication
Enforcing strong authentication on all internal services, including local APIs and IoT management panels, prevents the attacker from performing unauthorized actions even if they bypass SOP.

#### 3. HTTPS and TLS Certificates
If the internal service requires HTTPS, a DNS rebinding attack will fail because the attacker's domain (`attacker.com`) will not match the TLS certificate presented by the internal service (which might be a self-signed cert or one for a different internal domain). The browser will throw a certificate error and halt the request.

#### 4. DNS Filtering
Network administrators can configure local DNS servers to filter out public DNS responses that contain internal or loopback IP addresses (RFC 1918 addresses). This is known as "DNS rebinding protection" and is a feature in pfSense, OpenWRT, and Pi-hole.

### Real-World Scenarios
- **Attacking Developer Environments:** Developers often run local services (e.g., Redis, Elasticsearch, debuggers) on `localhost` without authentication. A DNS rebinding attack can execute arbitrary commands on the developer's machine by interacting with these local services.
- **Smart Home Hacking:** Many IoT devices (smart TVs, routers, cameras) have web servers running on internal IP addresses. A victim browsing the web can inadvertently allow an attacker to reconfigure their router or access camera feeds.
- **Cloud Metadata Exfiltration:** Similar to SSRF, DNS rebinding can be used to attack cloud metadata services (e.g., `169.254.169.254`) if a developer accesses a malicious site from within a cloud instance.

## Chaining Opportunities
- **SSRF (Server-Side Request Forgery):** DNS Rebinding is often considered a "Client-Side SSRF". If traditional SSRF fails due to blacklisting, DNS Rebinding can achieve similar results by using the victim's browser as the pivot.
- **RCE (Remote Code Execution):** By rebinding to a local service like Redis, Memcached, or a vulnerable debug port, the attacker can chain the SOP bypass into full RCE on the victim's machine.

## Related Notes
- [[15 - Server-Side Request Forgery (SSRF)]]
- [[25 - Abuse of Browser APIs]]
- [[40 - IoT Web Interface Vulnerabilities]]
