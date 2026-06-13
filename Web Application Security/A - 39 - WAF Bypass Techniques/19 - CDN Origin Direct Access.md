---
tags: [waf, evasion, bypass, vapt]
difficulty: advanced
module: "39 - WAF Bypass Techniques"
topic: "39.19 CDN Origin Direct Access"
---

# CDN Origin Direct Access (Origin IP Leakage)

Content Delivery Networks (CDNs) like Cloudflare, Akamai, Fastly, and AWS CloudFront act as reverse proxies positioned at the edge of the internet. They absorb massive DDoS attacks, cache static content globally, and, crucially, run Web Application Firewalls (WAFs) to inspect incoming traffic before it reaches the target network.

When a regular user visits `target.com`, their DNS resolves to the CDN's anycast IP address. The CDN terminates the TLS connection, inspects the HTTP traffic against its WAF rules, and then forwards legitimate requests to the hidden "Origin IP"—the actual backend server hosting the web application.

**CDN Origin Direct Access** (or Origin Bypass) is the technique of discovering that hidden Origin IP and sending HTTP/HTTPS requests directly to it, completely circumventing the CDN and rendering its multimillion-dollar WAF entirely useless.

## The Architecture of a CDN Bypass

If an attacker discovers the Origin IP, they can modify their local OS `hosts` file or use tools like `curl` and Burp Suite to send traffic directly to the backend server. If the backend server's firewall (e.g., AWS Security Groups, iptables) is not strictly configured to *only* accept traffic from the CDN's published IP ranges, the attack succeeds, and the WAF is bypassed.

### ASCII Architecture of Origin Bypass

```text
Normal Traffic Flow (Blocked by Edge WAF):
[ Attacker ] ---> [ DNS: target.com ] ---> [ CDN Edge / WAF (IP: 104.16.x.x) ] ---X (Blocked Payload)

Bypass Traffic Flow (Direct Origin Access):
[ Attacker ] ---> [ Discovered Origin IP: 203.0.113.88 ] ---> [ Backend Server ] ---> (Payload Executed!)
```

## Comprehensive Techniques for Discovering the Origin IP

Discovering the Origin IP requires a blend of OSINT, historical data analysis, active scanning, and exploiting application features.

### 1. Historical DNS Records Analysis

Organizations frequently spin up a new server, point their DNS `A` records directly to that server (leaking the IP to global DNS logs), and only later place the domain behind Cloudflare or Akamai. Services like SecurityTrails, ViewDNS.info, DNSDumpster, and passive DNS databases maintain historical archives of DNS records. By reviewing the `A` records for `target.com` from a year ago, an attacker will likely find the true, unchanged Origin IP.

### 2. Subdomain Enumeration and Scope Leaks

Administrators often secure the main production domain (`www.target.com`) behind a strict CDN but forget to protect ancillary subdomains used for internal purposes (e.g., `dev.target.com`, `staging.target.com`, `ftp.target.com`, `mail.target.com`, `cpanel.target.com`). 

Often, these subdomains are hosted on the exact same physical server, the same AWS VPC, or the same subnet as the main application. If `dev.target.com` resolves directly to `203.0.113.88`, there is an extremely high probability that the main application is also hosted on that IP or the adjacent `.89`.

### 3. Internet Scanning Engines (Shodan / Censys / Zoomeye)

Scanning engines continuously index the entire IPv4 space, storing responses, headers, and certificates. Attackers use these platforms to search for the target's unique digital fingerprints.

- **SSL/TLS Certificates:** An attacker can search Censys or Shodan for the target's SSL certificate hash or Common Name (CN). If the origin server is directly exposed to the internet and is configured with the target's SSL certificate, the scanning engine will have indexed the IP address.
  - *Query Example (Censys):* `services.tls.certificates.leaf_data.names: "target.com" and not autonomous_system.name: "Cloudflare"`
- **HTML Body/Title Matches:** Searching for unique strings, Google Analytics IDs, copyright notices, or specific HTML DOM structures found on the target website. If an unknown IP address serves the exact same HTML content as `target.com`, it is almost certainly the origin server.
  - *Query Example (Shodan):* `http.html:"Unique Copyright String 2024 TargetCorp"`

### 4. Out-of-Band (OOB) Interactions and SSRF

If the target web application has functionality that causes it to make outbound HTTP requests, the attacker can trap these requests to reveal the origin IP.
- **SSRF (Server-Side Request Forgery):** Forcing the server to fetch a URL controlled by the attacker (`http://attacker.com/log_ip`). The source IP of the incoming request hitting the attacker's server will be the origin server.
- **Email Headers:** Triggering password resets or registration emails. Examining the `Received:` headers in the raw email source often reveals the true IP of the internal SMTP server or web server that dispatched the email.
- **Webhooks and Integrations:** Exploiting integrations where the server pushes data to external endpoints (e.g., Slack webhooks, custom API integrations).

### 5. Cloud Storage and Bucket Metadata

Sometimes, static assets are loaded from AWS S3, Azure Blobs, or GCP buckets. Misconfigured bucket policies or metadata files might accidentally reveal internal network configurations, routing tables, or the origin IPs.

## Executing the Direct Access Attack

Once the suspected Origin IP is found, the attacker must craft a specific HTTP request to verify it.

Simply navigating to `http://203.0.113.88` in a browser often fails because the backend web server (e.g., Nginx, Apache) uses **Virtual Hosts (VHosts)**. It relies on the HTTP `Host` header to know which specific website to serve from that IP.

The attacker uses `curl` or configures Burp Suite to override the Host header:

```bash
# Force curl to connect to the Origin IP but request the target domain
curl -H "Host: target.com" https://203.0.113.88/ -k -v
```

If the server responds with the target website's content, the Origin IP is verified. The attacker can now launch full SQLi, XSS, or directory traversal attacks directly against `203.0.113.88`, entirely ignoring the CDN's WAF rules.

## Advanced Origin Routing (Host Header & SNI Manipulation)

Sometimes, the origin server sits behind an internal cloud load balancer (like AWS ALB) or an ingress controller. The attacker might need to manipulate the Host header and the SNI (Server Name Indication) independently during the TLS handshake to reach the correct backend instance.

```bash
# curl syntax for specific IP resolution with SNI spoofing
curl --resolve target.com:443:203.0.113.88 https://target.com/ -k
```
This command tells `curl` to connect to `203.0.113.88`, perform the TLS handshake presenting `target.com` as the SNI, and send `Host: target.com` in the HTTP request.

## Detection and Mitigation Strategies

Securing the origin requires a defense-in-depth approach, assuming the Origin IP will eventually be discovered by attackers.

1. **Firewall IP Whitelisting (The Golden Rule):** The most critical defense. The origin server's firewall (iptables, AWS Security Groups, Azure NSG) MUST be configured to drop all incoming traffic on ports 80/443 *except* traffic originating from the CDN's published IP ranges.
2. **Authenticated Origin Pulls (mTLS):** Implement mutually authenticated TLS (mTLS) between the CDN and the Origin server. The origin server will demand a specific cryptographic client certificate from the CDN before accepting the TCP connection. Even if an attacker knows the IP, they lack the CDN's private key and cannot establish a connection.
3. **Secret Headers:** Configure the CDN to inject a secret, complex custom header (e.g., `X-Shared-Secret: SecureRandomString-9f8a7b6c`) into every request forwarded to the origin. The origin server checks for this header and returns a 403 Forbidden for requests lacking it.
4. **Regular IP Rotation:** Periodically change the Origin IP address to invalidate historical DNS records and Shodan indexing.

## Summary

CDN Origin Bypass represents a critical architectural failure rather than a flaw in the WAF logic itself. A WAF is only effective if it acts as a mandatory, unavoidable chokepoint. Discovering the origin IP turns millions of dollars of enterprise CDN protection into a useless facade, leaving the underlying application completely exposed.

### Chaining Opportunities
- If direct access is achieved, attackers immediately transition to exploiting payload-based vulnerabilities like [[09 - SQL Injection WAF Bypass]] or [[13 - Insecure Deserialization]] since no filtering is present.
- Information gathering tools discussed in [[01 - Reconnaissance for WAF Evasion]] are heavily utilized to discover the origin.

### Related Notes
- [[24 - Cloud Architecture Vulnerabilities]]
- [[15 - Server-Side Request Forgery (SSRF) Evasion]]
- [[06 - Host Header Injection]]
- [[29 - Bypassing Cloudflare Protections]]
