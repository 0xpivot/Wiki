---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.09 Enumerating SMB Null Sessions Enum4linux"
---

# Enumerating SMB: Null Sessions and Enum4linux

## Introduction to SMB/CIFS
Server Message Block (SMB), and its dialect Common Internet File System (CIFS), is a network protocol primarily used by Microsoft Windows (though implemented in Linux via Samba) for providing shared access to files, printers, and serial ports between nodes on a network. It also provides an authenticated inter-process communication (IPC) mechanism.

SMB historically operates on:
- **Port 139 (TCP):** SMB over NetBIOS (Network Basic Input/Output System). This is the legacy implementation.
- **Port 445 (TCP):** Direct-hosted SMB over TCP/IP. This is the modern implementation (Windows 2000 and later) and bypasses the need for NetBIOS entirely.

In an enterprise environment (particularly Active Directory), SMB is ubiquitous. Because it is deeply integrated into the Windows operating system and handles authentication (NTLM, Kerberos) and access control, misconfigurations in SMB are a primary vector for both reconnaissance and exploitation. For a penetration tester, enumerating SMB is often the most lucrative step in mapping an internal network, extracting domain structures, and identifying privilege escalation or lateral movement paths.

### SMB Dialects and Versions
Understanding the version is crucial for exploiting SMB.
- **SMBv1:** Legacy protocol. Highly vulnerable to devastating remote code execution exploits like MS08-067 and MS17-010 (EternalBlue). It should be completely disabled on modern networks.
- **SMBv2:** Introduced in Windows Vista/Server 2008. Vastly improved performance and reduced chatty nature.
- **SMBv3:** Introduced in Windows 8/Server 2012. Added end-to-end encryption and secure dialect negotiation.

## The Vulnerability: SMB Null Sessions
A "Null Session" (Anonymous Logon) occurs when an attacker connects to a Windows system's IPC$ (Inter-Process Communication) share without providing a valid username or password (i.e., supplying a null username `""` and a null password `""`).

### The IPC$ Share and Named Pipes
The IPC$ share is a hidden administrative share. It does not map to a physical directory on the hard drive like a typical file share. Instead, it is used to facilitate communication between processes on different computers using Named Pipes. It allows systems to exchange data and query information about each other prior to full authentication. Named pipes act like a conduit for RPC (Remote Procedure Call) commands.

Historically (in Windows NT and Windows 2000), Windows allowed Null Sessions by default. The intent was to allow legitimate network devices to query the system to see what services were available.

### Impact of Null Sessions
If a system allows Null Session connections, an unauthenticated attacker can query the system over the IPC$ share via RPC to extract a staggering amount of highly sensitive information, including:
- **Operating System and Version Details.**
- **List of Users:** Exact usernames, full names, descriptions, and last login times. (Critical for building brute-force lists).
- **List of Groups:** Local groups and domain groups.
- **List of Network Shares:** Both standard shares (`C$`, `ADMIN$`) and custom user shares.
- **Password Policies:** Minimum password length, complexity requirements, account lockout thresholds. (Critical for tailoring password attacks without causing account lockouts).
- **Security Identifiers (SIDs):** The unique identifiers for users and groups.

While modern Windows operating systems (Windows Server 2003+ and Windows 10/11) restrict Null Sessions by default, they are frequently re-enabled by administrators to support legacy applications, or they exist on older, unpatched systems (e.g., Windows XP, Server 2008) still lingering in enterprise networks. Furthermore, Linux Samba servers are often misconfigured to allow anonymous access by default.

## Tool 1: Enum4linux
`enum4linux` is a Perl script wrapper around several standard Samba tools (`smbclient`, `rpcclient`, `net`, and `nmblookup`). It is the definitive tool for automating the extraction of information from Windows and Samba systems over SMB.

### Basic Usage
The most common and comprehensive way to run enum4linux is using the `-a` (all) flag.
`enum4linux -a 192.168.1.100`

This performs the following enumeration steps automatically:
1. **OS Information:** Attempts to determine the Windows version or Samba version.
2. **Share Enumeration:** Lists all accessible SMB shares.
3. **Password Policy Extraction:** Pulls the domain or local password policy.
4. **User Enumeration:** Uses various techniques (RID cycling) to dump the user list.
5. **Group Enumeration:** Dumps local and domain groups.
6. **Printer Information:** Lists connected network printers.

### Advanced Options and Targeted Enumeration
Sometimes, running the full `-a` scan is too noisy or gets blocked by intrusion detection systems. You can target specific data:
- `-U`: Extract the userlist.
- `-S`: Enumerate shares.
- `-P`: Extract password policy information.
- `-G`: Extract group and member list.
- `-u <user> -p <pass>`: If you have valid credentials, you can pass them to enum4linux. Authenticated enumeration provides significantly more data than a Null Session, especially on modern systems.

### Understanding RID Cycling
Every user and group in Windows has a Security Identifier (SID). The SID consists of a domain identifier and a Relative Identifier (RID). The Administrator account always has a RID of 500. Guest is 501. Standard users typically start at 1000.
Enum4linux performs "RID Cycling" or "RID Brute-forcing". It establishes a Null Session and then sequentially asks the server via RPC, "Who is the user with RID 1000? Who is 1001? Who is 1002?" If the server answers, enum4linux dumps the entire user database one by one without needing administrative privileges.

## Tool 2: Smbclient
`smbclient` is an FTP-like client that allows you to interact with SMB shares directly from the Linux command line.

### Connecting via Null Session
To list shares available via a Null Session using a blank username and no password:
`smbclient -L //192.168.1.100 -U "" -N`
- `-L`: List shares.
- `-U ""`: Specifies a blank username.
- `-N`: No password prompt.

### Interacting with a Share
If a share is found to be accessible (either anonymously or with compromised credentials), you can connect to it:
`smbclient //192.168.1.100/PublicData -U "anonymous" -N`
Once connected, you are presented with an `smb: \>` prompt. Commands are similar to FTP:
- `ls` / `dir`: List files and directories.
- `cd`: Change directory.
- `get filename.txt`: Download a file to your local machine.
- `put payload.exe`: Upload a file to the server.
- `recurse ON` and `prompt OFF` followed by `mget *`: Download all files recursively.

## Tool 3: Rpcclient
`rpcclient` allows you to execute Remote Procedure Call (RPC) functions over an SMB session directly interacting with Named Pipes. It provides raw access to the functions that tools like enum4linux wrap.

Connecting with a Null Session:
`rpcclient -U "" -N 192.168.1.100`

Once in the `rpcclient $>` prompt, you can manually execute commands:
- `srvinfo`: Get server OS info.
- `enumdomusers`: Enumerate all users.
- `enumdomgroups`: Enumerate all groups.
- `queryuser <username>`: Get detailed info on a specific user.
- `getdompwinfo`: Get password policy.
- `lsaenumsid`: Enumerate SIDs.

---

## ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                     SMB Null Session Enumeration Flow                       |
+-----------------------------------------------------------------------------+

      [ Attacker Machine ]                            [ Target Windows Server ]
      (Running enum4linux)                                  (IP: 10.0.0.50)
               |                                                   |
               |                                                   |
               | (1) TCP SYN (Port 445)                            |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     TCP SYN/ACK                                   |
               |                                                   |
               | (2) SMB Negotiate Protocol Request                |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     SMB Negotiate Protocol Response               |
               |     (Selected Dialect, e.g., SMBv2)               |
               |                                                   |
               | (3) SMB Session Setup Request                     |
               |     (User: "", Password: "")                      |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     SMB Session Setup Response                    |
               |     Status: STATUS_SUCCESS (Null Session Allowed) |
               |                                                   |
               | (4) SMB Tree Connect Request (IPC$)               |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     SMB Tree Connect Response (Success)           |
               |                                                   |
               | (5) RPC Bind Request (SAMR - SAM Remote Protocol) |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     RPC Bind ACK                                  |
               |                                                   |
               | (6) RPC Request: EnumDomainUsers (RID Cycling)    |
               |-------------------------------------------------->|
               |<--------------------------------------------------|
               |     RPC Response: (Admin, JSmith, BWayne...)      |
               |                                                   |
               | (7) Attacker parses results into wordlists        |
               v
```

## Defensive Perspective and Mitigation
- **Disable Null Sessions:** The primary defense is ensuring Null Sessions are disabled entirely.
  In Windows Registry: `HKLM\System\CurrentControlSet\Control\Lsa\RestrictAnonymous` should be set to `1` or `2`.
  In Active Directory Group Policy: `Network access: Restrict anonymous access to Named Pipes and Shares` should be enabled.
- **SMB Signing:** Require SMB Signing to prevent SMB Relay attacks, though this does not stop enumeration if a Null Session is allowed or if valid credentials are compromised.
- **Patch Management:** Ensure systems are updated to prevent exploitation of severe SMB vulnerabilities like MS17-010 (EternalBlue) or SMBGhost.
- **Network Segmentation:** Block ports 139 and 445 at the perimeter firewall. SMB should never be exposed to the public internet under any circumstance.
- **Audit Logging:** Enable auditing on sensitive shares to monitor who is accessing and modifying files.

## Chaining Opportunities
- **Enumeration to Brute-Forcing:** The usernames extracted via enum4linux are directly fed into tools like `Hydra` or `CrackMapExec` to brute-force SMB, SSH, or RDP logins. See [[06 - Network Service Brute Forcing Protocol Attacks]].
- **Password Spraying:** Knowing the exact password policy (extracted via Null Session) allows attackers to craft password spraying attacks that stay precisely below the account lockout threshold (e.g., trying 1 password against 100 users, rather than 100 passwords against 1 user). See [[12 - Password Spraying Techniques]].
- **SMB Relay Attacks:** If SMB signing is disabled on internal servers, captured NTLM hashes (via Responder) can be relayed to the enumerated SMB service to gain immediate administrative access. See [[08 - NTLM Relay Attacks Responder]].
- **Exploitation:** Discovering vulnerable OS versions during SMB enumeration leads directly to exploiting vulnerabilities like MS08-067 or MS17-010 to gain a SYSTEM shell. See [[07 - Exploiting SMB Vulnerabilities EternalBlue]].

## Related Notes
- [[04 - Nmap Advanced Port Scanning]]
- [[23 - Active Directory Enumeration Basics]]
- [[13 - Understanding Windows Authentication NTLM Kerberos]]
- [[31 - Exploiting Misconfigured Network Shares]]
