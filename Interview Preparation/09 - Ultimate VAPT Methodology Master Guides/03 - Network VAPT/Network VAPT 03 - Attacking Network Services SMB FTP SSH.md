---
tags: [vapt, methodology, network-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - Network"
topic: "Master Guide - Network VAPT 03"
---

# Master Guide: Attacking Network Services - SMB, FTP, SSH

## 1. Interview Strategy: How to Explain Service Exploitation
When discussing the exploitation of core network services (SMB, FTP, SSH) in an interview, candidates often default to "I would brute force it." This is a novice answer. An expert candidate focuses on **misconfigurations, protocol weaknesses, and CVEs** before falling back to brute force.
Structure your methodology logically:
1.  **Enumeration First:** Explain how you extract version numbers, banners, and anonymous access rights.
2.  **Configuration Flaws:** Discuss missing patches, anonymous logins, null sessions, or weak cryptographic protocols.
3.  **Known Vulnerabilities (CVEs):** Mention specific critical CVEs (e.g., MS17-010, ProFTPD mod_copy) and how they work fundamentally.
4.  **Credential Attacks as a Last Resort:** If brute forcing is necessary, explain how you target specific user lists and avoid account lockouts (password spraying).
5.  **Post-Exploitation:** What do you do *after* you get access? (e.g., SSH tunneling, SMB relaying).

*Key Interview Phrase:* "I approach service exploitation by looking for architectural or configuration flaws first—such as SMB Null Sessions or anonymous FTP access. Brute forcing is noisy and risks lockouts, so I prioritize mapping the attack surface for known CVEs or relying on captured hashes and relay attacks to authenticate seamlessly."

---

## 2. Attacking SMB (Server Message Block - Port 445/139)

SMB is the backbone of Windows networks (file sharing, IPC, printing). It is notoriously vulnerable and usually the fastest path to Domain compromise.

### Phase 1: Enumeration and Null Sessions
**The Flaw:** Historically, Windows allowed "Null Sessions" (unauthenticated logins) to query the IPC$ share, revealing domains, users, and groups.
- *Tools:* `enum4linux-ng`, `smbclient`, `CrackMapExec` (or `NetExec`), `rpcclient`.
- *Null Session Check:* `smbclient -N -L //10.10.10.5`
- *Deep Enumeration:* `enum4linux-ng -A 10.10.10.5`
- *RPC Enumeration:* `rpcclient -U "" -N 10.10.10.5` -> `enumdomusers`

### Phase 2: Exploiting Known CVEs
If the SMB version is outdated, exploit it directly.
- **MS17-010 (EternalBlue):** Exploits a buffer overflow in SMBv1. Gives `NT AUTHORITY\SYSTEM`.
  - *Scan:* `nmap -p 445 --script smb-vuln-ms17-010 10.10.10.0/24`
  - *Exploit:* Metasploit `exploit/windows/smb/ms17_010_eternalblue` or custom AutoBlue Python scripts.
- **CVE-2020-0796 (SMBGhost):** A compression vulnerability in SMBv3.1.1 (Windows 10). Allows RCE.

### Phase 3: Credential Abuse & Relaying
If SMB is patched but you have credentials (or hashes), abuse them.
- **Pass-the-Hash (PtH):** You don't need the plaintext password; the NTLM hash is sufficient to authenticate over SMB.
  - *Command:* `crackmapexec smb 10.10.10.5 -u Administrator -H <NTLM_HASH> -x "whoami"`
- **SMB Relay:** Capture NTLM hashes via MitM (Responder) and relay them to an SMB server where SMB Signing is disabled.
  - *Check Signing:* `crackmapexec smb 10.10.10.0/24 --gen-relay-list relay.txt`
  - *Relay:* `ntlmrelayx.py -tf relay.txt -socks`

---

## 3. Attacking FTP (File Transfer Protocol - Port 21)

FTP is an aging, plaintext protocol. It is targeted for data exfiltration, credential sniffing, and occasional RCE.

### Phase 1: Anonymous Access & Misconfigurations
**The Flaw:** Administrators often enable anonymous access for public file drops but misconfigure the read/write permissions.
- *Login:* `ftp 10.10.10.5` -> User: `anonymous`, Password: `anonymous`
- *Exploitation:* If you have write access to a web root via FTP, upload a web shell (e.g., `cmd.php`) and access it via port 80/443.

### Phase 2: Known Vulnerabilities
- **VSFTPD v2.3.4 Backdoor:** A malicious backdoor was inserted into the source code. Sending a `:)` in the username opens a shell on port 6200.
  - *Exploit:* `ncat 10.10.10.5 21` -> `USER user:)` -> `PASS pass` -> `ncat 10.10.10.5 6200`
- **ProFTPD 1.3.5 (mod_copy):** Allows unauthenticated users to use `SITE CPFR` and `SITE CPTO` commands to copy files anywhere on the file system.
  - *Exploit:* Copy the `/etc/shadow` file to the web root and download it.

### Phase 3: FTP Bounce Attacks
**The Flaw:** The `PORT` command in FTP allows an attacker to tell the FTP server to connect to a *different* machine.
- *The Attack:* The attacker uses the FTP server as a proxy to port-scan an internal, segmented network that the attacker cannot reach directly.
- *Command:* `nmap -P0 -n -b username:password@ftp-server.com target-internal-ip`

---

## 4. Attacking SSH (Secure Shell - Port 22)

SSH is highly secure by design. Attacks usually focus on weak passwords, stolen keys, or post-exploitation abuse.

### Phase 1: Authentication Attacks
- **Password Spraying:** Instead of brute-forcing one user with many passwords, test many users with one common password (e.g., `Company2023!`) to avoid lockouts.
  - *Tool:* `hydra -L users.txt -p 'Spring2023!' ssh://10.10.10.5`
- **Key Compromise:** Look for improperly secured private keys (`id_rsa`) on GitHub, exposed SMB shares, or local user directories.
  - *Crack Key Passphrases:* Extract the hash with `ssh2john` and crack with Hashcat.

### Phase 2: SSH Server Vulnerabilities
- **Debian OpenSSL Predictable PRNG (CVE-2008-0166):** Old but legendary. A flawed RNG generated only 32,767 possible SSH keys. Attackers can iterate through all possible keys instantly.
- **Username Enumeration (CVE-2018-15473):** OpenSSH up to v7.7 allowed attackers to verify if a username existed based on authentication failure responses.

### Phase 3: Post-Exploitation (Tunneling & Hijacking)
Once access is gained, SSH is the ultimate pivoting tool.
- **Local Port Forwarding:** Access an internal port from the attacker machine.
  `ssh -L 8080:internal-server:80 user@edge-server`
- **Dynamic Port Forwarding:** Create a SOCKS proxy into the network.
  `ssh -D 9050 user@edge-server` (Use with Proxychains).
- **SSH Agent Hijacking:** If a root user compromises a server, they can hijack an active SSH agent socket (`SSH_AUTH_SOCK`) to pivot to other servers using the victim's loaded keys, without knowing the passphrase.

---

## ASCII Diagram: Multi-Protocol Attack Chain

```text
 [ Attacker Machine ]
         |
         | (1. SMB Relay Attack - Port 445)
         v
 [ Windows File Server ]  --> (SMB Signing Disabled, Code Execution Gained)
   IP: 10.10.10.20        --> (Dumps SAM database, extracts Administrator Hash)
         |
         | (2. Pass-the-Hash via CrackMapExec over SMB)
         v
 [ Windows Workstation ]
   IP: 10.10.10.50        --> (Finds developer's id_rsa key in C:\Users\Dev\.ssh)
         |
         | (3. SSH Login using stolen key - Port 22)
         v
 [ Linux Database Server ]
   IP: 10.20.20.100       --> (Creates SSH Dynamic SOCKS proxy)
         |
         | (4. Pivot into restricted DB subnet)
         v
 [ Mainframe / Backend ]
```

---

## 5. Real-World Attack Scenario

**Scenario: The FTP to SMB Ghost Chain**
1. **Recon:** During a pentest, the attacker finds an exposed FTP server on the DMZ.
2. **Exploitation (FTP):** The FTP server allows anonymous login. The attacker enumerates directories and finds a backup folder containing `backup_script.bat`.
3. **Information Disclosure:** Reading the `.bat` script reveals hardcoded domain credentials used to map an SMB share: `net use Z: \\10.10.1.10\Backups /user:CORP\SVC_Backup SuperSecret123`.
4. **Validation:** The attacker uses `crackmapexec smb 10.10.0.0/24 -u SVC_Backup -p SuperSecret123` to spray the network. The credentials are valid across the environment.
5. **Privilege Escalation:** The `SVC_Backup` account is not a Domain Admin, but `CrackMapExec` shows it has local administrator rights on a server vulnerable to `ZeroLogon (CVE-2020-1472)`.
6. **Domain Compromise:** The attacker pivots through the server, executes the ZeroLogon exploit against the Domain Controller, and resets the machine account password, dumping the entire `NTDS.dit`.

---

## 6. Chaining Opportunities

- **FTP -> Web:** Upload an ASP/PHP web shell via FTP to gain code execution on the underlying IIS/Apache server.
- **SMB -> RDP:** Use SMB Pass-the-Hash to enable the RDP service remotely and add a user to the Remote Desktop Users group, converting command-line access into a full graphical session.
- **SSH -> Internal Recon:** Bind an SSH Dynamic Port Forward (SOCKS proxy) to run `nmap` and `BloodHound` stealthily against the internal segregated network.

---

## 7. Related Notes

- [[Network VAPT 04 - Bypassing Firewalls NAC and Network Segregation]] - Learn how to reach these services if they are blocked by network boundary defenses.
- [[Network VAPT 05 - Pivoting and Lateral Movement Methodologies]] - Master the SSH tunneling and proxychain techniques mentioned in this guide.
- [[Windows Privilege Escalation Guide]] - What to do once your SMB/FTP payload gives you a low-privileged shell.

---
**Disclaimer:** The exploitation of network services and the use of relay/pass-the-hash attacks should only be conducted during authorized penetration testing. Unauthorized access to computer systems is illegal.

---

## 8. Deep Dive: Kerberos Integration with SMB
While NTLM and Pass-the-Hash are powerful, modern environments enforce Kerberos. You must understand how to attack SMB using Kerberos tickets.
- **The SPN (Service Principal Name):** Kerberos uses SPNs to identify services. An SMB server's SPN looks like `cifs/server.domain.local`.
- **Pass-the-Ticket (PtT) over SMB:** If you dump a Kerberos TGS (Ticket Granting Service) ticket for `cifs/server` from a compromised machine using Mimikatz, you can inject it into your Linux session using `export KRB5CCNAME=/path/to/ticket.ccache`.
- **Execution:** Once the ticket is loaded, tools like `smbclient` or `CrackMapExec` can be run with the `-k` flag to authenticate purely via Kerberos, completely bypassing NTLM restrictions and EDRs looking for NTLM anomalous logins.
- **Silver Tickets:** If you compromise the computer account hash of the file server, you can forge your own Kerberos tickets (Silver Tickets) specifically for the `cifs` service, granting yourself persistent, undetectable Domain Admin-level access to that specific server.

## 9. Comprehensive Tool Reference Matrix
| Tool | Target Service | Primary Use Case | Protocol Layer |
|------|----------------|------------------|----------------|
| CrackMapExec / NetExec | SMB, WinRM, SSH | Mass credential spraying, Pass-the-Hash, and active directory enumeration. | Application (L7) |
| enum4linux-ng | SMB / RPC | Deep enumeration of SID, users, groups, and password policies via null sessions. | Application (L7) |
| Hydra | FTP, SSH, SMB | High-speed, multi-threaded dictionary attacks and brute-forcing. | Application (L7) |
| ntlmrelayx.py | SMB / HTTP | Relaying intercepted NTLM authentication to execute code on target servers. | Application (L7) |
| smbclient | SMB | Manual interaction with SMB shares, downloading/uploading files. | Application (L7) |
| ssh2john | SSH | Extracting the hash from an encrypted `id_rsa` private key for Hashcat cracking. | Application (L7) |
| Responder | SMB / LLMNR | Coercing authentication to capture NTLMv2 hashes. | Application/Network |

## 10. Blue Team: Detection Engineering
Understanding how defenders monitor these services makes your offensive answers much stronger.
- **SMB Detection (Event ID 4624):** A network logon over SMB generates a Type 3 Logon event. Defenders look for Pass-the-Hash signatures, such as a Logon Type 3 where the authentication package is NTLM, but the source IP belongs to an IT admin's laptop (indicating the admin's hash was stolen).
- **SSH Brute-Force Detection:** Fail2Ban or SIEMs monitor `/var/log/auth.log` for multiple `Failed password` entries. An expert attacker bypasses this by rotating proxies or limiting sprays to one attempt per hour.
- **FTP Anomaly Detection:** Monitoring for the `USER anonymous` string in cleartext traffic, or alerting on large data transfers (potential exfiltration) over port 21.

## 11. Common Interview Pitfalls and How to Avoid Them
1.  **Defaulting to "Brute-Force"**: If an interviewer asks how you attack SSH, saying "I run Hydra" is a failing answer. Instead, discuss looking for exposed keys, misconfigurations, or password spraying across the entire AD domain rather than brute-forcing a single account.
2.  **Misunderstanding SMB Relay**: Many candidates confuse Pass-the-Hash with SMB Relay.
    - *Pass-the-Hash:* You ALREADY HAVE the hash, and you actively use it to log in.
    - *SMB Relay:* You DO NOT have the hash. You sit in the middle, wait for a user to authenticate to you, and you forward their authentication to a third server.
3.  **Forgetting SMB Signing**: If you suggest an SMB Relay attack, the interviewer will ask, "What stops that?" You must immediately answer: "SMB Signing. If SMB Signing is enforced on the target server, the relay will fail because I cannot cryptographic sign the relayed packets."
4.  **Ignoring Anonymous FTP Uploads**: Don't just say you would read files from anonymous FTP. Always mention the RCE vector: "If write permissions are enabled, I would upload a reverse shell to the web directory."
