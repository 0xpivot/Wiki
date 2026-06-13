---
tags: [vapt, command-injection, defense, beginner]
difficulty: beginner
module: "08 - Command Injection"
topic: "08.12 Defense — Input Sanitization and Allowlists"
---

# 08.12 — Defense: Input Sanitization and Allowlists

## Primary Defense: Avoid Shell Commands

The best defense against command injection is not calling OS commands with user input at all. Use built-in language libraries instead.

```
INSTEAD OF:                          USE:
system("ping " + ip)                 → socket library / ICMP library
exec("nslookup " + domain)           → DNS resolver library
shell_exec("convert " + filename)    → ImageMagick PHP extension
passthru("sendmail " + email)        → SMTP library (PHPMailer, etc.)
os.system("ls " + directory)         → os.listdir() in Python
```

---

## Defense Layer 1: Allowlists

Only allow known-good values. Reject everything else.

```python
# PYTHON ALLOWLIST — IP ADDRESS:
import re, ipaddress

def validate_ip(user_input):
    try:
        ipaddress.ip_address(user_input)  # Validates IPv4/IPv6
        return user_input
    except ValueError:
        raise ValueError("Invalid IP address")

# PYTHON ALLOWLIST — DOMAIN NAME:
def validate_domain(domain):
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]{0,253}[a-zA-Z0-9]$'
    if re.match(pattern, domain):
        return domain
    raise ValueError("Invalid domain")

# PYTHON ALLOWLIST — FILENAME:
import os
def safe_filename(filename):
    # Only alphanumeric, hyphens, underscores, dots
    safe = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Remove path components
    safe = os.path.basename(safe)
    return safe[:255]  # Max length

# PHP ALLOWLIST:
function validate_ip($input) {
    if (filter_var($input, FILTER_VALIDATE_IP)) {
        return $input;
    }
    throw new InvalidArgumentException("Invalid IP");
}
```

---

## Defense Layer 2: Subprocess Without Shell (Python)

```python
# WRONG — SHELL=TRUE IS DANGEROUS!:
import subprocess
host = request.args.get('host')
subprocess.run("ping -c 1 " + host, shell=True)  # VULNERABLE!

# CORRECT — ARRAY FORM, NO SHELL:
import subprocess
host = request.args.get('host')
# Validate first:
validated_host = validate_ip(host)  # From allowlist function above
# Then run WITHOUT shell:
result = subprocess.run(
    ['ping', '-c', '1', validated_host],  # List form — no shell!
    capture_output=True,
    text=True,
    timeout=5
)
print(result.stdout)

# WHY ARRAY FORM IS SAFE:
# subprocess.run(['ping', validated_host]) → OS directly executes ping
# No shell involved → shell metacharacters (;|&) have no meaning!
# Even if validated_host = "8.8.8.8;id" → ping gets literal "8.8.8.8;id" as hostname
```

---

## Defense Layer 3: Escaping (Last Resort)

```python
# USE ONLY WHEN YOU MUST CALL A SHELL:
import shlex

# PYTHON:
host = request.args.get('host')
safe_host = shlex.quote(host)  # Wraps in single quotes, escapes any ' inside
cmd = "ping -c 1 " + safe_host
# Result: ping -c 1 '8.8.8.8;id'  ← treated as literal hostname!

# PHP:
$host = $_GET['host'];
$safe_host = escapeshellarg($host);   // wraps in single quotes
$cmd = "ping -c 1 " . $safe_host;    // 'ping -c 1 '8.8.8.8;id''
system($cmd);

# ALSO PHP:
$safe_arg = escapeshellcmd($host);   // escapes metacharacters
// Less safe than escapeshellarg! Use escapeshellarg instead.

# NOTE: ESCAPING IS NOT PERFECT!
// Edge cases can still bypass escaping
// Prefer allowlists + array form over escaping
```

---

## Defense Layer 4: Principle of Least Privilege

```
IF THE SERVER IS COMPROMISED — MINIMIZE DAMAGE:

1. Run web server as low-privilege user (www-data, nobody):
   → Even if injected: commands run as www-data, not root
   → Can't read /etc/shadow, can't install software, can't modify system

2. No sudo for web server user:
   → sudo -l shows nothing for www-data

3. Read-only filesystem where possible:
   → Mount web root as read-only
   → Can't write webshells!

4. Disable shell for web user:
   usermod -s /sbin/nologin www-data
   → Even if shell obtained → can't use interactive shell features

5. Network restrictions:
   → App server has no direct internet access
   → Reverse shells to internet blocked by egress firewall!
   → OOB command injection fails!
```

---

## Defense Layer 5: Web Application Firewall (WAF)

```
WAF RULES FOR COMMAND INJECTION:
  Block:
  - ; | & && ||
  - Backticks `
  - Dollar-paren $(
  - Common commands: cat, id, whoami, ls, wget, curl, nc
  - Paths: /etc/, /bin/, /usr/bin/
  - Whitespace followed by system commands

LIMITATIONS:
  - WAFs are NOT a complete defense (can be bypassed!)
  - Use WAF as additional layer, not primary defense
  - Known bypass: encoding, whitespace tricks, alternatives

CLOUDFLARE WAF:
  - Has built-in rules for command injection
  - Rate limiting helps against brute-force bypass attempts

MOD_SECURITY:
  - Open-source WAF for Apache/Nginx
  - OWASP Core Rule Set includes command injection rules
```

---

## Defense Layer 6: Secure Coding by Language

### PHP

```php
// NEVER USE:
system(), exec(), shell_exec(), passthru(), popen(), proc_open()
// And especially: `backtick operator`

// IF YOU MUST: validate + escapeshellarg:
$host = filter_var($_GET['host'], FILTER_VALIDATE_IP);  // validate
if (!$host) { die("Invalid IP"); }
$output = shell_exec("ping -c 1 " . escapeshellarg($host));  // escape

// BETTER: Use PHP functions:
// Instead of running nslookup: use dns_get_record()
// Instead of running openssl: use PHP OpenSSL extension
// Instead of running curl: use PHP cURL library
```

### Python

```python
# NEVER USE:
os.system("cmd " + user_input)
subprocess.run("cmd " + user_input, shell=True)
subprocess.call("cmd " + user_input, shell=True)
exec(user_input)
eval(user_input)

# ALWAYS USE:
subprocess.run(['cmd', safe_validated_input])  # list form, no shell!
# Or use built-in libraries (socket, dns.resolver, etc.)
```

### Node.js

```javascript
// NEVER USE:
const { exec } = require('child_process');
exec('cmd ' + userInput, callback);  // DANGEROUS — uses shell!

// USE:
const { execFile } = require('child_process');
execFile('cmd', [validatedInput], callback);  // list form, no shell!

// OR SPAWN (also safe):
const { spawn } = require('child_process');
const proc = spawn('ping', ['-c', '1', validatedInput]);  // safe!
```

---

## Vulnerability Review Checklist

```
CODE REVIEW CHECKLIST — COMMAND INJECTION:
  □ Any use of system(), exec(), shell_exec(), passthru()?
  □ Any subprocess.run/call with shell=True?
  □ Any child_process.exec() in Node.js?
  □ Any os.popen() in Python?
  □ Any Runtime.exec() with shell in Java?
  □ Any user input flows into these functions?
  □ Is the input validated against an allowlist?
  □ Is escaping applied (escapeshellarg, shlex.quote)?
  □ Is the web user low-privilege?
  □ Is outbound internet access restricted?
```

---

## Related Notes
- [[01 - What is Command Injection]] — what we're defending against
- [[02 - OS Command Injection Linux]] — attack perspective
- [[09 - WAF Bypass for Command Injection]] — why WAF alone isn't enough
- [[Module 22 - Reporting]] — how to report and recommend fixes
