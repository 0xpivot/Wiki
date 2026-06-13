---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.16 Password in Files"
---

# 44.16 Passwords in Config Files, History, and Env Vars

## 1. Introduction

One of the most common oversights by system administrators and developers is the hardcoding or logging of sensitive credentials in plain text. Passwords, API keys, and database connection strings frequently end up in configuration files, shell history, environment variables, or backup files. 

During a penetration test or red team engagement, discovering these plaintext credentials provides an immediate and often effortless pathway to privilege escalation or lateral movement. If a compromised low-privileged user can read a configuration file containing the database root password, and the system administrator reused that password for their local root account, the entire system is instantly compromised.

## 2. Core Concepts and Underlying Mechanisms

Credentials leak into the filesystem through several distinct mechanisms:

### 2.1 Shell History Files
When a user types a command into their shell (e.g., bash, zsh), the shell typically logs the command to a history file (`~/.bash_history`, `~/.zsh_history`). If an administrator passes a password as a command-line argument, it gets recorded permanently unless manually cleared.
Example: `mysql -u root -pPassword123`

### 2.2 Configuration Files
Web applications, databases, and background services require credentials to communicate with one another. These are often stored in configuration files (e.g., `wp-config.php`, `config.yml`, `.env`). If these files are world-readable, any local user can harvest the credentials.

### 2.3 Environment Variables
Modern application architectures (especially containerized and cloud-native applications) heavily rely on environment variables to pass secrets to applications at runtime. If a low-privileged user can inspect the environment of a privileged process (e.g., via `/proc/<pid>/environ`), they can extract these secrets.

## 3. Technical Breakdown and Architecture

The following ASCII diagram maps the paths through which credentials leak and how an attacker harvests them for escalation.

```text
+-------------------------------------------------------------------------+
|                  CREDENTIAL LEAKAGE ARCHITECTURE                        |
|                                                                         |
|  [ Admin Actions ]          [ Application Deployment ]                  |
|         |                               |                               |
|         v                               v                               |
|  Types password on CLI      Stores DB creds in .env                     |
|  export DB_PASS="secret"    Docker passes ENV to app                    |
|         |                               |                               |
|         v                               v                               |
|  +----------------+         +-----------------------+                   |
|  | ~/.bash_history|         | /var/www/html/.env    |                   |
|  | /var/log/auth  |         | /proc/<PID>/environ   |                   |
|  +----------------+         +-----------------------+                   |
|         |                               |                               |
|         +---------------+---------------+                               |
|                         |                                               |
|                         v                                               |
|               [ Unprivileged Attacker ]                                 |
|               Runs grep, find, cat enum                                 |
|                         |                                               |
|                         v                                               |
|                Recovers 'root' password                                 |
|                         |                                               |
|                         v                                               |
|                     $ su root                                           |
|                     # id -> uid=0(root)                                 |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Effective enumeration involves recursively searching the filesystem for keywords, examining dotfiles, and analyzing running processes.

### 4.1 Shell History Enumeration
Always check the home directory of the current user, and if possible, other users.
```bash
cat ~/.bash_history
cat ~/.zsh_history
cat ~/.mysql_history
cat ~/.psql_history
cat ~/.nano_history
cat ~/.viminfo
```
Look for patterns like `pass`, `password`, `mysql`, `ssh`, `wget`, `curl`.

### 4.2 Configuration File Search
Web directories and `/etc` are prime targets. Use `grep` to recursively search for credential keywords.
```bash
grep -rnw '/var/www/html' -e "DB_PASSWORD" -e "pwd" -e "password"
grep -rnw '/etc' -e "password" 2>/dev/null
```
Look for common configuration extensions:
```bash
find / -type f \( -name "*.conf" -o -name "*.config" -o -name "*.yml" -o -name "*.env" -o -name "*.ini" \) 2>/dev/null
```

### 4.3 Environment Variable Extraction
Check the environment variables of the current session:
```bash
env
printenv
set
```
If you can read `/proc`, check the environment variables of other processes. While `/proc/<pid>/environ` is usually restricted to the process owner or root, you can always read the environment of your own processes, and occasionally misconfigurations allow reading others.
```bash
cat /proc/self/environ | tr '\0' '\n'
```
You can automate process environment extraction for all accessible processes:
```bash
for i in $(ls /proc | grep -E '^[0-9]+$'); do cat /proc/$i/environ 2>/dev/null | tr '\0' '\n'; done
```

### 4.4 Automated Tools
LinPEAS is exceptional at highlighting credentials in common locations. It has a dedicated module that parses history files and searches for password keywords in log files and web roots.

## 5. Exploitation Methodology

The exploitation phase here is simply the application of the discovered credentials.

### 5.1 Credential Reuse (Password Spraying locally)
If you find a database password (e.g., `SuperSecretDB123!`), the very first step should be attempting to `su` to root or other users using that exact password. Humans are creatures of habit and frequently reuse passwords across different services on the same machine.
```bash
su root
# Enter 'SuperSecretDB123!'
```

### 5.2 SSH Lateral Movement
If you find a password, check `/etc/passwd` for other valid users and attempt to SSH into the local machine or remote machines using the discovered credentials.
```bash
ssh admin@127.0.0.1
```

### 5.3 Database to System Execution
If you recover database credentials, log into the database. If it's running as root, you may be able to execute system commands.
- **MySQL**: Check for `FILE` privileges. Can you load a shared library and create a User-Defined Function (UDF) for command execution? Can you write to `/etc/passwd` using `SELECT ... INTO OUTFILE`?
- **PostgreSQL**: Can you use `COPY` to write an arbitrary file, or `CREATE OR REPLACE FUNCTION` to execute shell commands?

## 6. Edge Cases and Obfuscation

Sometimes credentials are base64 encoded or stored in a hashed format within the configuration.
If you find `cGFzc3dvcmQxMjM=`, decode it:
```bash
echo "cGFzc3dvcmQxMjM=" | base64 -d
```
If you find an MD5 or SHA1 hash in a backup database dump, you will need to crack it offline using Hashcat or John the Ripper before attempting reuse.

Another edge case is finding a password in an old, unlinked file that is only visible by recovering deleted data or analyzing a full memory dump.

## 7. Post-Exploitation & Persistence

After leveraging a leaked credential to gain root access:
- Change the root password to lock out competitors (in a King of the Hill scenario) or secure your access.
- Deploy alternative persistence mechanisms (SSH keys, cron jobs) in case the legitimate administrator changes the compromised password.
- Document exactly where the credential was found to provide accurate remediation advice in the final report.

## 8. Defense & Remediation

Preventing credential leakage requires disciplined administrative practices and secure architecture.

### 8.1 Secure Handling of History
Administrators should configure their shell to ignore commands that start with a space (`HISTCONTROL=ignorespace`) and prefix any command containing a password with a space. Better yet, passwords should never be passed as CLI arguments.
```bash
# Bad:
mysql -u root -pPassword123
# Good (prompts for password):
mysql -u root -p
```
Clear history files after sensitive operations: `history -c`.

### 8.2 Securing Configurations
- Never store plaintext passwords in source control or accessible configuration files.
- Use secrets management solutions like HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets.
- Ensure strict file permissions on any `.env` or `config.php` files (e.g., `chmod 600` or `chmod 640` with proper group ownership).

### 8.3 Environment Variable Hygiene
Avoid passing highly sensitive secrets via environment variables if possible, or ensure the environment is strictly isolated. Never expose a `/info` or `/env` debugging endpoint on a web server that dumps environment variables.

## 9. Chaining Opportunities

Finding plaintext passwords is a powerful primitive that links perfectly with other vectors:
- **SSRF to Env Vars**: If a web application is vulnerable to Server-Side Request Forgery or Local File Inclusion (LFI), an attacker can read `/proc/self/environ` to dump the environment variables containing AWS keys or database passwords.
- **Backup File Abstraction**: Finding an old, world-readable `.bak` or `.tar.gz` archive in `/var/backups` often yields old configuration files containing valid, reused passwords.
- **Database to SUID**: Using found DB credentials to write a SUID wrapper binary into `/tmp` and executing it via a vulnerable cron job.

## 10. Related Notes
- [[15 - Weak File Permissions on Sensitive Files]]
- [[17 - SSH Private Key Reuse]]
- [[24 - Sudo Tokens and Caching]]
- [[08 - Abusing Internal Network Services]]
