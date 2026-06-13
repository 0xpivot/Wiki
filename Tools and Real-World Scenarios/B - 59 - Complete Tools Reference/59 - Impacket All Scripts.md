---
tags: [tools, ad, pivoting, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.59 Impacket All Scripts"
---

# Impacket: Complete Script Reference and Usage

Impacket is a collection of Python classes for working with network protocols. In the context of offensive security, it provides an unparalleled suite of tools for interacting with Windows environments, Active Directory, SMB, and MSRPC without requiring native Windows APIs.

Because Impacket is written in Python, it allows attackers to execute complex Active Directory attacks natively from Linux (Kali/Parrot), making it essential for external exploitation and lateral movement.

## Architecture and Core Libraries

Impacket implements raw network protocols from the ground up:
- Ethernet, IP, TCP, UDP
- NBT, MSRPC, SMB1/SMB2/SMB3
- NTLM, Kerberos (encryption and authentication)
- DCOM, WMI

### ASCII Architecture Diagram

```text
+-----------------------+                    +-----------------------+
| Attacker (Kali Linux) |                    | Target Windows Domain |
|                       |                    |                       |
|  [Impacket Script]    |                    |                       |
|   (e.g., wmiexec.py)  |                    |                       |
|          |            |                    |                       |
|  +-------v-------+    |                    |   +---------------+   |
|  |  WMI / DCOM   |    |----(TCP 135)------>|   | RPC Endpoint  |   |
|  +---------------+    |                    |   | Mapper        |   |
|  | SMB/MSRPC Libs|    |----(TCP 445)------>|   +---------------+   |
|  +---------------+    |                    |   | SMB Server    |   |
|  | Auth (NTLM/Krb|    |                    |   +---------------+   |
|  +-------+-------+    |                    |                       |
+-----------------------+                    +-----------------------+
```

## Authentication Mechanisms

Almost all Impacket scripts support identical authentication flags:

-   **Password Auth:** `-target-ip IP 'domain/user:password'`
-   **Pass-the-Hash (PtH):** `-hashes LMHASH:NTHASH 'domain/user@target'`
    - *If LM hash is unknown, use 32 zeros: `-hashes 00000000000000000000000000000000:NTHASH`*
-   **Kerberos Auth (Ticket):** `-k -no-pass 'domain/user@target.fqdn'`
    - *Requires `KRB5CCNAME` environment variable to be set to a valid `.ccache` file.*
-   **Kerberos Auth (Password/Hash):** Request a TGT on the fly using a password or hash, then authenticate. Use `-k`.
-   **AES Keys:** `-aesKey [hex key]` (Alternative to password/hash for Kerberos).
-   **DC-IP Binding:** `-dc-ip [DC_IP]` forces resolution and authentication to a specific Domain Controller.

## Tool Categories and Scripts

### 1. Remote Execution (Lateral Movement)

These tools provide interactive or semi-interactive shells on remote Windows systems.

#### psexec.py
The classic standard. It uploads a random executable to the `ADMIN$` share, creates a remote Windows service via RPC, starts it, and connects via named pipes.
- **Pros:** Highly reliable, runs as `NT AUTHORITY\SYSTEM`.
- **Cons:** Extremely noisy. Drops files to disk. Highly signatured by AV/EDR (Event ID 7045 - Service Creation).
- **Usage:** `psexec.py domain/admin:password@10.10.10.10`

#### smbexec.py
A stealthier alternative to `psexec.py`. It does not upload an executable. Instead, it creates a temporary service whose `binPath` executes `cmd.exe /c` commands sequentially, redirecting output to a temporary file on the SMB share.
- **Pros:** No binary uploaded. Runs as `SYSTEM`.
- **Cons:** Commands are executed asynchronously (blindly), and output is retrieved later. No interactive prompt (e.g., running `powershell` will hang). Leaves Event ID 7045 traces.
- **Usage:** `smbexec.py -hashes :<NTHash> domain/admin@10.10.10.10`

#### wmiexec.py
The preferred modern execution method. Utilizes Windows Management Instrumentation (WMI) and DCOM to execute commands. Output is retrieved by writing to a hidden file on the `ADMIN$` share and reading it via SMB.
- **Pros:** Extremely stealthy. No services created. Blends with administrative traffic.
- **Cons:** Runs in the context of the authenticating user (usually Local Admin), not `SYSTEM`. Can be blocked by DCOM hardening.
- **Usage:** `wmiexec.py domain/admin:password@10.10.10.10`

#### atexec.py
Executes commands remotely using the Task Scheduler service (ATSvc).
- **Usage:** `atexec.py domain/admin:password@10.10.10.10 command`

#### dcomexec.py
Similar to wmiexec but leverages different DCOM endpoints (MMC20.Application, ShellWindows, etc.). Useful for bypassing specific EDR hooks on WMI.

### 2. Credential Dumping and Enumeration

#### secretsdump.py
The crown jewel of Impacket. Performs credential extraction from Windows systems and Domain Controllers.
- **Local Dumping:** Extracts SAM, SECURITY, and SYSTEM registry hives to dump local NTLM hashes, LSA secrets, and cached credentials.
- **DCSync:** If the user has `GetChangesAll` rights, it queries the Domain Controller via Directory Replication Service (DRS) RPC protocol to pull AD hashes (NTLM, AES keys, Kerberos keys) without code execution on the DC.
- **NTDS.dit parsing:** Can parse offline NTDS.dit files.
- **Usage (Local Admin):** `secretsdump.py domain/admin:password@10.10.10.10`
- **Usage (DCSync):** `secretsdump.py -just-dc domain/dcsync_user:password@dc01.domain.local`
- **Usage (Offline):** `secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL`

#### GetNPUsers.py (AS-REP Roasting)
Queries the Domain Controller for users with "Do not require Kerberos preauthentication" set and retrieves their AS-REP ticket, which contains a crackable encrypted TGT.
- **Usage:** `GetNPUsers.py domain.local/ -usersfile users.txt -format hashcat -outputfile hashes.txt -dc-ip 10.10.10.5`

#### GetUserSPNs.py (Kerberoasting)
Queries the Domain Controller for users possessing a Service Principal Name (SPN) and retrieves the TGS-REP ticket, which is encrypted with the service account's NTLM hash.
- **Usage:** `GetUserSPNs.py domain.local/user:password -request -dc-ip 10.10.10.5`

#### samrdump.py
Communicates with the Security Account Manager Remote (SAMR) interface to enumerate users, groups, and aliases.
- **Usage:** `samrdump.py domain/user:password@10.10.10.10`

### 3. Attack and Relay Tools

#### ntlmrelayx.py
The core tool for NTLM relay attacks. It receives incoming NTLM authentication (usually from Responder, coerce, or poisoned protocols), relays it to a target system, and executes a payload if the authentication is successful and possesses sufficient rights.
- **Features:** Relays to SMB, HTTP, LDAP, IMAP. Can execute commands, dump hashes, or initiate DCSync.
- **SMB Relay (Execute Command):** `ntlmrelayx.py -tf targets.txt -smb2support -c "ipconfig"`
- **LDAP Relay (Create computer object / escalate privileges):** `ntlmrelayx.py -t ldap://dc01.domain.local -smb2support`
- **SOCKS Proxy:** `-socks` allows pivoting interactive tools through the relayed session.

#### ticketer.py
Creates forged Kerberos tickets (Golden and Silver Tickets) offline using the domain's `krbtgt` hash or a service's hash.
- **Golden Ticket:** `ticketer.py -nthash <krbtgt_hash> -domain-sid <SID> -domain <domain> <user>`

#### rpcdump.py
Dumps all registered RPC endpoints on a target. Useful for identifying hidden services (like custom DCOM objects or Exchange endpoints).

### 4. Coercion Tools

While not primarily coercion focused, Impacket libraries are the backbone of tools that force Windows machines to authenticate to an attacker.
- **PetitPotam.py:** Abuses MS-EFSRPC.
- **printerbug.py:** Abuses MS-RPRN (Spooler service).

## Evasion and Limitations

-   **Signatureing:** Impacket is highly signatured by network IDS and EDRs. Default configurations (like `psexec` binaries or `wmiexec` output files) are instantly flagged.
-   **OPSEC Modifications:** Advanced adversaries often modify Impacket's source code to alter hardcoded service names, binary signatures, or pipe names to evade basic detections.
-   **Alternative Tools:** When Impacket fails due to EDR, consider C#-based equivalents (SharpWMI, SharpKatz) or BOFs executed via C2 frameworks.

## Chaining Opportunities
- Chain `secretsdump.py` with Pass-the-Hash using [[60 - CrackMapExec NetExec Full Command Reference]] to spray credentials across a domain.
- Use `ntlmrelayx.py` in conjunction with Responder (from [[04 - Network Pivoting and Tunneling]] concepts) for relay attacks.
- Tunnel all Impacket tools through [[56 - proxychains SOCKS Proxy Chaining]] when operating outside the internal network.

## Related Notes
- [[22 - Kerberoasting and AS-REP Roasting]]
- [[26 - NTLM Relaying and Coercion]]
- [[27 - Credential Dumping and AD Persistence]]
