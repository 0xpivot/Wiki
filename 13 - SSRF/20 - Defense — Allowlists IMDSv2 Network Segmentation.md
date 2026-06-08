---
tags: [vapt, ssrf, defense, beginner]
difficulty: beginner
module: "13 - SSRF"
topic: "13.20 Defense — Allowlists, IMDSv2, Network Segmentation"
---

# 13.20 — Defense: Allowlists, IMDSv2, Network Segmentation

## Defense Layer 1 — Input Validation (Allowlist, Not Blocklist)

```
WRONG APPROACH (blocklist):
  Block: 127.0.0.1, localhost, 169.254.169.254, 10.x, 192.168.x
  → Bypassable with hex, decimal, IPv6, DNS rebinding!

RIGHT APPROACH (allowlist):
  Only allow specific pre-approved domains/IPs that the feature needs.
  If feature only needs to fetch from api.example.com → ONLY allow that!

ALLOWLIST IMPLEMENTATION (Python):
  from urllib.parse import urlparse
  import ipaddress
  import socket
  
  ALLOWED_DOMAINS = {'api.example.com', 'cdn.example.com'}
  
  def validate_ssrf_url(url):
      parsed = urlparse(url)
      
      # Only allow HTTPS
      if parsed.scheme not in ('https',):
          raise ValueError("Only HTTPS allowed")
      
      hostname = parsed.hostname
      
      # Allowlist check
      if hostname not in ALLOWED_DOMAINS:
          raise ValueError(f"Domain {hostname} not in allowlist")
      
      # Resolve and check IP (prevent DNS rebinding!)
      try:
          ip = socket.gethostbyname(hostname)
          addr = ipaddress.ip_address(ip)
          if addr.is_private or addr.is_loopback or addr.is_link_local:
              raise ValueError("Resolved to private/loopback IP!")
      except socket.gaierror:
          raise ValueError("DNS resolution failed")
      
      return url
```

---

## Defense Layer 2 — Resolve and Pin IP (Prevent DNS Rebinding)

```python
# RESOLVE HOSTNAME ONCE, USE IP FOR CONNECTION:
# This prevents DNS rebinding attacks!

import socket
import ipaddress
import requests
from urllib.parse import urlparse

def safe_request(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    # Resolve IP
    ip = socket.gethostbyname(hostname)
    addr = ipaddress.ip_address(ip)
    
    # Block private/loopback/link-local
    if any([
        addr.is_private,
        addr.is_loopback,
        addr.is_link_local,
        addr.is_multicast,
        str(addr) == '0.0.0.0'
    ]):
        raise ValueError(f"Blocked IP: {ip}")
    
    # Make request using resolved IP (not hostname)
    # This prevents DNS rebinding — we already know the IP!
    safe_url = url.replace(hostname, ip, 1)
    
    response = requests.get(
        safe_url,
        headers={'Host': hostname},  # Keep Host header for virtual hosting
        verify=True,
        timeout=5,
        allow_redirects=False  # Don't follow redirects!
    )
    return response
```

---

## Defense Layer 3 — Disable Redirects

```python
# DON'T FOLLOW REDIRECTS IN SSRF-PRONE REQUESTS!

# BAD (follows redirects → allows redirect to 169.254.169.254):
requests.get(url, allow_redirects=True)  # default!

# GOOD:
response = requests.get(url, allow_redirects=False)
if response.status_code in (301, 302, 303, 307, 308):
    raise ValueError("Redirects not allowed!")

# WHY: Open redirect chain bypass is very common!
# If you follow redirects, an attacker can chain:
# trusted-domain.com/redirect?url=http://169.254.169.254/
```

---

## Defense Layer 4 — Enforce IMDSv2 on AWS

```bash
# ON EXISTING EC2 INSTANCES:
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234567890abcdef0 \
  --http-tokens required \
  --http-endpoint enabled \
  --http-put-response-hop-limit 1

# WITH TERRAFORM:
resource "aws_instance" "example" {
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"    # IMDSv2 only!
    http_put_response_hop_limit = 1
  }
}

# WITH AWS LAUNCH TEMPLATE:
aws ec2 create-launch-template-version \
  --launch-template-id lt-xxx \
  --launch-template-data '{"MetadataOptions":{"HttpTokens":"required","HttpPutResponseHopLimit":1}}'

# ORGANIZATION-WIDE ENFORCEMENT (Service Control Policy):
# Use AWS SCP to require IMDSv2 on all EC2 instances in the account:
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Resource": "arn:aws:ec2:*:*:instance/*",
  "Condition": {
    "StringNotEquals": {
      "ec2:MetadataHttpTokens": "required"
    }
  }
}
```

---

## Defense Layer 5 — Network Segmentation

```
ISOLATE INTERNAL SERVICES FROM APPLICATION SERVERS:

ARCHITECTURE:
  Internet → WAF/CDN → App Server → VPC (private subnet)
  
  App servers should NOT be able to reach:
  ✗ Other internal databases directly (use VPC private DNS, not IP)
  ✗ Admin panels of other services
  ✗ Metadata of other cloud instances
  ✗ Docker/Kubernetes management APIs
  ✗ Cloud metadata beyond what's needed

FIREWALL RULES (iptables):
  # Block app server from reaching cloud metadata:
  iptables -A OUTPUT -d 169.254.169.254 -j DROP
  
  # Allow only specific internal services:
  iptables -A OUTPUT -d 10.0.1.50 -p tcp --dport 5432 -j ACCEPT  # specific DB
  iptables -A OUTPUT -d 10.0.0.0/8 -j DROP                        # block all other internal

AWS VPC SECURITY GROUPS:
  Outbound rules on app server security group:
  Allow: tcp 443 to api.external.com/32
  Allow: tcp 5432 to db-security-group
  Deny: all other traffic
```

---

## Defense Layer 6 — Protocol Restrictions

```python
# ONLY ALLOW SPECIFIC PROTOCOLS:

from urllib.parse import urlparse

def validate_url_scheme(url):
    parsed = urlparse(url)
    if parsed.scheme not in ('https',):  # only HTTPS, not HTTP, file, gopher, etc.
        raise ValueError(f"Protocol {parsed.scheme} not allowed")
    return url

# IN NGINX (block outbound to internal ranges at proxy level):
# If using nginx as a forward proxy:
location / {
    proxy_pass $request_uri;
    
    # Deny internal IP ranges:
    deny 10.0.0.0/8;
    deny 172.16.0.0/12;
    deny 192.168.0.0/16;
    deny 127.0.0.0/8;
    deny 169.254.0.0/16;
}
```

---

## Defense Checklist

```
SSRF DEFENSE CHECKLIST:
  [ ] Input validated against allowlist (not blocklist)
  [ ] Resolved IPs checked against private/loopback/link-local ranges
  [ ] DNS resolved once and pinned (no re-resolution for connection)
  [ ] Redirects disabled in HTTP client
  [ ] Only HTTPS allowed (no http, gopher, file, dict, ftp)
  [ ] Only port 443 allowed (or specific required ports)
  [ ] IMDSv2 enforced on all EC2 instances (HttpTokens: required)
  [ ] IMDSv2 hop limit set to 1
  [ ] Network egress rules restrict app server outbound
  [ ] Internal services have authentication (no anonymous Redis/Elasticsearch)
  [ ] Docker API not exposed without TLS
  [ ] Kubernetes API has RBAC enabled
  [ ] Monitoring/alerting for requests to unusual IPs (169.254.x, 10.x, etc.)
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[09 - SSRF Cloud Metadata]] — what the defense protects against
- [[10 - SSRF AWS IMDSv1 vs IMDSv2]] — IMDSv2 details
- [[14 - SSRF Localhost Bypass]] — bypass techniques to defend against
- [[15 - SSRF DNS Rebinding]] — rebinding defense (pin IP after resolution)
