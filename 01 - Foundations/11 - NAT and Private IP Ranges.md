---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.11 NAT and Private IP Ranges"
---

# 01.11 — NAT and Private IP Ranges

## What is it?

**NAT (Network Address Translation)** allows multiple devices on a private network to share a single public IP address when accessing the internet. Your home has one public IP but 10+ devices — NAT makes this work.

**Private IP ranges** are blocks of IP addresses reserved for use inside private networks. They are not routable on the public internet.

---

## Private IP Ranges (RFC 1918)

```
RANGE                      CIDR       ADDRESSES      USE
─────────────────────────────────────────────────────────────
10.0.0.0–10.255.255.255    10.0.0.0/8     16M    Large corps, clouds
172.16.0.0–172.31.255.255  172.16.0.0/12  1M     Medium networks
192.168.0.0–192.168.255.255 192.168.0.0/16 65K   Home/small office

ALSO SPECIAL:
127.0.0.0/8        Loopback (127.0.0.1 = localhost)
169.254.0.0/16     APIPA (link-local, no DHCP)
169.254.169.254    Cloud metadata server (AWS, GCP, Azure)
```

**If you see these IPs in requests/headers → you're looking at internal traffic!**

---

## How NAT Works

```
HOME NETWORK                            INTERNET
                                           │
192.168.1.100 (PC)    ┐                   │
192.168.1.101 (Phone) ├─→ [Router/NAT] ──→ Public IP: 203.0.113.42
192.168.1.102 (TV)    ┘

When your PC (192.168.1.100) visits google.com:

OUTGOING:
  PC sends:    Src=192.168.1.100:54231  Dst=142.250.182.46:443
  Router NATSrc=203.0.113.42:54231   Dst=142.250.182.46:443
  ← NAT table: 203.0.113.42:54231 → 192.168.1.100:54231

INCOMING:
  Google sends: Src=142.250.182.46:443  Dst=203.0.113.42:54231
  Router NATs:  Src=142.250.182.46:443  Dst=192.168.1.100:54231
  ← Delivers to correct internal device using NAT table
```

---

## Types of NAT

```
1. SNAT (Source NAT) — most common (home internet)
   Translates private source IP → public IP

2. DNAT (Destination NAT) — port forwarding
   Translates public destination IP:port → internal server
   Example: 203.0.113.42:80 → 192.168.1.50:80 (web server)

3. PAT (Port Address Translation) / Masquerading
   Many-to-one: many private IPs share one public IP
   Distinguished by port numbers in NAT table
   This is what your home router does

4. Full NAT (One-to-One NAT)
   One private IP ↔ One public IP
   Used in data centers
```

---

## Security Context — NAT and Private IPs in VAPT

### 1. SSRF — Reaching Internal Private IPs

When a server fetches URLs on your behalf (SSRF), it can access private IPs that you normally can't reach.

```
External request:
  You → http://target.com/fetch?url=http://192.168.1.1/
  Blocked: 192.168.1.1 is not routable from internet

SSRF — server makes the request internally:
  You → http://target.com/fetch?url=http://192.168.1.1/
  Server → http://192.168.1.1/   ← server IS on the internal network!
  Server returns response to you ← you get internal data!

What to try:
  http://192.168.0.1/       ← common router admin pages
  http://10.0.0.1/          ← common internal web apps
  http://172.16.0.1/        ← common internal services
  http://169.254.169.254/   ← cloud metadata (most critical!)
```

### 2. Internal IP Disclosure

Private IPs appearing where they shouldn't reveals network topology.

```
Check these locations for internal IP leakage:

1. HTTP Response Headers:
   X-Forwarded-For: 192.168.1.100    ← internal IP of upstream server
   X-Real-IP: 10.0.0.5               ← backend server IP
   Via: 1.1 internal-proxy.corp (squid) ← proxy hostname

2. Error Messages:
   "Connection to 172.16.0.50:3306 failed"  ← DB server internal IP

3. HTML Source / JavaScript:
   var api_url = "http://10.0.1.20/api/"   ← internal API server

4. DNS PTR records:
   dig -x 203.0.113.42 → dc01.corp.internal  ← reveals internal hostname

5. SSL Certificate SANs:
   openssl s_client -connect target.com:443
   Subject Alternative Names: internal.corp.local, 10.0.0.5
```

### 3. X-Forwarded-For Spoofing — Bypass IP-Based Controls

Many apps use `X-Forwarded-For` to get the "real" client IP. If they trust it without validation:

```http
GET /admin HTTP/1.1
Host: target.com
X-Forwarded-For: 127.0.0.1

→ App thinks request comes from localhost → grants admin access!

Other headers to try:
X-Forwarded-For: 10.0.0.1
X-Real-IP: 127.0.0.1
X-Original-IP: 10.0.0.1
X-Client-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
```

### 4. Cloud Metadata via NAT (169.254.169.254)

The cloud metadata server at `169.254.169.254` is a link-local address — only accessible from within the cloud instance via NAT.

```bash
# From a cloud instance or via SSRF on a cloud app:
curl http://169.254.169.254/latest/meta-data/
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/[role-name]

# Returns AWS credentials:
# {
#   "AccessKeyId": "ASIAXXX",
#   "SecretAccessKey": "abc123...",
#   "Token": "IQoJb...",
#   "Expiration": "2024-01-01T12:00:00Z"
# }
# → Full AWS account access!
```

---

## Hands-On: NAT Commands

```bash
# See NAT rules on Linux (iptables)
iptables -t nat -L -n -v

# Add port forwarding (DNAT): external port 8080 → internal 192.168.1.50:80
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to 192.168.1.50:80
iptables -t nat -A POSTROUTING -j MASQUERADE

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# See your public IP
curl ifconfig.me
curl ipinfo.io/ip

# See internal IPs
ip addr show
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| SSRF to internal IPs | Block RFC1918 ranges and 169.254.169.254 in URL fetchers |
| Internal IP leakage in headers | Remove or sanitize internal IPs from response headers |
| X-Forwarded-For bypass | Validate X-Forwarded-For only from trusted proxies |
| Cloud metadata accessible | Use IMDSv2 (requires token), restrict metadata access |

---

## Related Notes
- [[02 - IP Addresses]] — IP addressing and ranges
- [[04 - Subnets and CIDR]] — network segmentation
- [[Module 13 - SSRF]] — abusing SSRF to reach private IPs
- [[Module 37 - Cloud Infrastructure]] — cloud metadata exploitation
