---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.28 Virtual Host (vHost) Enumeration"
---

# 05.28 — Virtual Host (vHost) Enumeration

## What is Virtual Hosting?

A single IP address can serve multiple websites using the HTTP `Host` header. The server reads the Host header and routes the request to the correct website. This means `192.168.1.1` might serve `target.com`, `admin.target.com`, `staging.target.com`, and a completely different site — all from the same IP.

```
HTTP REQUEST:
  GET / HTTP/1.1
  Host: target.com        ← Server reads this to decide which site to show

VIRTUAL HOSTING:
  IP 203.0.113.1 serves:
    Host: target.com       → public website
    Host: admin.target.com → admin panel (maybe not in DNS!)
    Host: staging.target.com → staging site with debug mode on
    Host: internal.corp    → internal app (not in public DNS at all!)

WHY IT MATTERS:
  → Hidden vhosts may not be in DNS → subdomain enumeration won't find them
  → Admin/staging vhosts often have less security
  → vhosts on same IP share the server → pivot between sites
  → Internal vhosts accessible if you know the Host header value!
```

---

## How vHost Enumeration Works

```
PROCESS:
  1. Find target's IP address: 203.0.113.1
  2. Try different Host header values against that IP
  3. Compare responses:
     - Same default response → vhost doesn't exist on this server
     - Different/interesting response → vhost found!

  TOOL SENDS:
  GET / HTTP/1.1
  Host: admin.target.com      ← trying this
  
  vs DEFAULT:
  GET / HTTP/1.1
  Host: 203.0.113.1           ← baseline response
  
  IF THEY DIFFER → admin.target.com exists on this server!
```

---

## ffuf for vHost Enumeration

```bash
# INSTALL:
go install -v github.com/ffuf/ffuf/v2@latest

# BASIC VHOST FUZZING:
ffuf -u https://target.com/ \
  -H "Host: FUZZ.target.com" \
  -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# FILTER BY SIZE (remove default responses):
# First run to find default response size:
ffuf -u https://target.com/ -H "Host: FUZZ.target.com" \
  -w wordlist.txt -mc all 2>/dev/null | head -10
# Note the size of "nonexistent" responses

# Then filter out that size:
ffuf -u https://target.com/ \
  -H "Host: FUZZ.target.com" \
  -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -fs 1234        # filter responses with this size

# FILTER BY STATUS CODE:
ffuf -u https://target.com/ \
  -H "Host: FUZZ.target.com" \
  -w wordlist.txt \
  -mc 200,301,302,401,403  # only show these status codes

# SCAN AGAINST IP DIRECTLY (find vhosts not in DNS):
ffuf -u http://203.0.113.1/ \
  -H "Host: FUZZ.target.com" \
  -w wordlist.txt \
  -fs 1234

# HTTPS WITH SELF-SIGNED CERT:
ffuf -u https://203.0.113.1/ \
  -H "Host: FUZZ.target.com" \
  -w wordlist.txt \
  -k          # skip TLS verification
  -fs 1234

# WITH RATE LIMITING:
ffuf -u https://target.com/ -H "Host: FUZZ.target.com" \
  -w wordlist.txt -rate 100 -fs 1234
```

---

## gobuster vhost Mode

```bash
# GOBUSTER VHOST:
gobuster vhost \
  -u https://target.com \
  -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  --append-domain

# FILTER RESPONSES:
gobuster vhost \
  -u https://target.com \
  -w wordlist.txt \
  --append-domain \
  --exclude-length 1234

# SPECIFIC DOMAIN PATTERN:
gobuster vhost \
  -u https://target.com \
  -w wordlist.txt \
  -t 50 \
  --append-domain

# WITH HTTPS AND NO TLS VERIFY:
gobuster vhost \
  -u https://203.0.113.1 \
  -w wordlist.txt \
  --append-domain \
  -k
```

---

## wfuzz for vHost Enumeration

```bash
# WFUZZ:
wfuzz -c -w /usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt \
  -u http://target.com \
  -H "Host: FUZZ.target.com" \
  --hc 404 --hh 1234

# AGAINST IP WITH HOST HEADER:
wfuzz -c -w wordlist.txt \
  -u http://203.0.113.1 \
  -H "Host: FUZZ.target.com" \
  --hc 404,400
```

---

## Manual vHost Testing

```bash
# TEST SPECIFIC HOST VALUES MANUALLY:
curl -H "Host: admin.target.com" http://target.com/
curl -H "Host: staging.target.com" http://target.com/
curl -H "Host: dev.target.com" http://target.com/
curl -H "Host: internal.target.com" http://target.com/

# COMPARE RESPONSES:
# Run baseline:
curl -s http://target.com/ | wc -c        # default response size

# Run candidate:
curl -s -H "Host: admin.target.com" http://target.com/ | wc -c
# Different size → different content → vhost found!

# AGAINST DISCOVERED IP (bypass DNS):
curl -H "Host: target.com" http://203.0.113.1/
curl -H "Host: admin.target.com" http://203.0.113.1/  # Check admin vhost at same IP!
```

---

## Wordlists for vHost Fuzzing

```bash
# SECLISTS (most complete):
ls /usr/share/wordlists/seclists/Discovery/DNS/
# subdomains-top1million-5000.txt       → small, fast
# subdomains-top1million-20000.txt      → medium
# subdomains-top1million-110000.txt     → large
# bitquark-subdomains-top100000.txt     → alternative
# dns-Jhaddix.txt                       → Jhaddix's list

# CUSTOM WORDLIST (target-specific):
# Add: admin, internal, staging, dev, test, uat, qa, beta
# Add: api, api2, v1, v2, graphql
# Add: mail, smtp, ftp, rdp, vpn, ssh
# Add: management, monitoring, analytics, dashboard
# Add: legacy, old, backup, archive

# TARGET-SPECIFIC PERMUTATIONS:
echo "target.com" | alterx -enrich -pp word=common-words.txt
```

---

## Internal vHost Discovery (Inside a Network)

When you're inside a network (post-exploitation or VPN) or testing an internal target:

```bash
# ENUMERATE INTERNAL HOSTS FROM SAME SERVER:
# Look for virtual host configs in web server:

# APACHE:
cat /etc/apache2/sites-enabled/*.conf | grep "ServerName\|ServerAlias"

# NGINX:
cat /etc/nginx/sites-enabled/* | grep "server_name"

# IIS:
# Check IIS Manager → Sites → Bindings

# HOSTS FILE:
cat /etc/hosts | grep -v "^#\|^127\|^::1"

# /etc/hosts ON TARGET SERVER (if you have shell access!):
# Shows all manually configured internal hostnames!
```

---

## Identifying Hidden Admin Panels

```bash
# COMMON HIDDEN VHOSTS TO TRY:
VHOSTS=(
  admin admin.target.com
  management management.target.com
  portal portal.target.com
  internal internal.target.com
  intranet intranet.target.com
  dashboard dashboard.target.com
  monitoring monitoring.target.com
  jenkins jenkins.target.com
  gitlab gitlab.target.com
  jira jira.target.com
  confluence confluence.target.com
  kibana kibana.target.com
  grafana grafana.target.com
  phpmyadmin phpmyadmin.target.com
  cpanel cpanel.target.com
  webmail webmail.target.com
)

for vhost in "${VHOSTS[@]}"; do
  resp=$(curl -s -o /dev/null -w "%{http_code} %{size_download}" \
    -H "Host: $vhost" "http://target.com/")
  echo "$resp $vhost"
done | grep -v "^404\|^400"
```

---

## Related Notes
- [[08 - Subdomain Enumeration]] — DNS-based subdomain discovery
- [[29 - Directory and File Bruteforcing]] — path-level enumeration
- [[03 - Google Dorking]] — finding vhosts via search engines
- [[07 - DNS Enumeration]] — DNS lookups for host discovery
