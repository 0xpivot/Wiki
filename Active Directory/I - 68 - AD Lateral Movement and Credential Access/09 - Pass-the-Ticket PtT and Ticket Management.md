---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.09 Pass-the-Ticket PtT"
---

# 68.09 Pass-the-Ticket (PtT) and Ticket Management

## Introduction to Pass-the-Ticket (PtT)

Pass-the-Ticket (PtT) is an advanced lateral movement technique that operates entirely within the Kerberos authentication protocol framework. Unlike Pass-the-Hash, which requires an attacker to steal a user's password hash to prove their identity, Pass-the-Ticket involves stealing pre-generated, valid Kerberos tickets and injecting them directly into a session.

By stealing either a Ticket Granting Ticket (TGT) or a Service Ticket (TGS), an attacker can impersonate the victim user and access network resources without ever needing to touch a password, a hash, or interact with the Domain Controller's Authentication Service. This technique bypasses many credential-theft defenses because the attacker is simply using the exact same logical access token that the legitimate user's session is using.

## Deep Dive: Ticket Extraction and Injection

To understand PtT, you must understand where Windows stores Kerberos tickets and how an attacker can manipulate that storage.

When a user logs in, the Local Security Authority Subsystem Service (LSASS) negotiates with the Domain Controller to acquire a TGT. This TGT, along with any subsequent TGSs requested for specific services (like CIFS, HTTP, WSMAN), are cached in the LSASS memory space associated with that specific user's Logon Session.

### The Attack Flow

1. **Extraction:** The attacker gains administrative access or SYSTEM level access on a compromised machine. They access LSASS memory to extract the cached `.kirbi` files (the raw Kerberos ticket format) for logged-on users.
2. **Transfer (Optional):** The attacker can move these `.kirbi` files to a different machine (e.g., from a jump box to their personal attack machine).
3. **Injection:** The attacker injects the stolen `.kirbi` file into their current logon session memory.
4. **Execution:** The attacker requests access to a network resource. The Windows Kerberos client checks the local cache, sees the injected valid ticket, and presents it to the target service.

## ASCII Diagram: The Pass-the-Ticket Architecture

```text
       [Compromised Host A]                               [Attacker Host B]
       (Victim is logged in)
                                                          
  +-----------------------------+                  +-----------------------------+
  | LSASS Process Memory        |                  | Attacker's Logon Session    |
  |                             |                  |                             |
  | [Logon Session: Victim]     |                  | [Logon Session: Attacker]   |
  | - TGT (krbtgt/DOMAIN)       | =======(1)======>|                             |
  | - TGS (cifs/SERVER01)       |   Extraction     |                             |
  +-----------------------------+                  +-----------------------------+
                                                                 |
                                                                (2) Injection
                                                                 |
                                                                 v
                                                   +-----------------------------+
                                                   | Attacker's Logon Session    |
                                                   |                             |
                                                   | [Logon Session: Attacker]   |
                                                   | - TGT (krbtgt/DOMAIN)       | <--- Injected!
                                                   +-----------------------------+
                                                                 |
                                                                (3) Usage
                                                                 |
                                                                 v
                                                     [Target Domain Controller]
                                                     [Target Server (SERVER01)]
```

## Methodology: Tools and Execution

Ticket management and PtT are almost exclusively handled by tools that interact heavily with the Windows API, specifically `LsaCallAuthenticationPackage`. `Rubeus` and `Mimikatz` are the undisputed champions of this on Windows.

### 1. Extracting Tickets

To extract tickets from other users, you need high privileges (`SYSTEM` or Local Admin with `SeDebugPrivilege`).

**Using Rubeus (Preferred):**
Rubeus can dump tickets in base64 format, making them easy to copy-paste.
```powershell
# Triage the currently cached tickets
Rubeus.exe triage

# Dump all tickets from all sessions (requires elevation)
Rubeus.exe dump

# Dump tickets for a specific service (e.g., krbtgt)
Rubeus.exe dump /service:krbtgt /nowrap
```

**Using Mimikatz:**
Mimikatz traditionally exports tickets to disk as `.kirbi` files.
```text
mimikatz # privilege::debug
mimikatz # sekurlsa::tickets /export
```
This will flood the current directory with `.kirbi` files for every ticket in memory.

### 2. Injecting Tickets (Pass-the-Ticket)

Once you have a ticket (either as a `.kirbi` file or a base64 string), you can inject it into your current session. You do *not* need administrative privileges to inject a ticket into your *own* current session.

**Using Rubeus:**
Injecting a base64 encoded ticket:
```powershell
Rubeus.exe ptt /ticket:doIE8jCCBO6gAwIBBaEDAgEWooIE...[truncated]...
```
Injecting a `.kirbi` file:
```powershell
Rubeus.exe ptt /ticket:C:\temp\Administrator_krbtgt.kirbi
```

**Using Mimikatz:**
```text
mimikatz # kerberos::ptt C:\temp\Administrator_krbtgt.kirbi
```

### 3. Ticket Management and Purging

When executing PtT, you are polluting your own Kerberos cache. If you inject a TGT for `UserA`, but then want to inject a TGT for `UserB`, the Windows Kerberos client can get confused. It is critical to purge your cache between attacks.

**Purging via Native Windows Utility:**
```cmd
klist purge
```

**Purging via Rubeus:**
```powershell
Rubeus.exe purge
```

### 4. Linux and Impacket (.ccache files)

If you extract a `.kirbi` file from a Windows machine, you can convert it to a Linux `.ccache` format to use with Impacket tools.

```bash
# Convert kirbi to ccache using impacket's ticketConverter.py
ticketConverter.py administrator.kirbi administrator.ccache

# Set the environment variable
export KRB5CCNAME=/path/to/administrator.ccache

# Execute tools
impacket-smbclient -k -no-pass DC01.corp.local
```

## Defensive Considerations and Constraints

**Ticket Lifetimes:**
Kerberos tickets are ephemeral. By default, a TGT is valid for 10 hours. If you steal a TGT that is 9 hours old, you only have 1 hour to use it before it expires. If a user logs out, their tickets are typically purged from LSASS.

**Defenses:**
1. **Credential Guard:** Windows Defender Credential Guard protects tickets within a virtualization-based isolated process (LSAIso). When enabled, tools like Mimikatz and Rubeus cannot extract the actual cryptographic key material of the ticket, rendering ticket extraction impossible.
2. **Kerberos Armoring (FAST):** Protects Kerberos traffic and can tie tickets to a specific machine, making tickets stolen from Host A useless if injected into Host B.
3. **Restricting Tiering:** Implementing the Tiered Administration Model ensures that high-privilege accounts (Tier 0) never log onto low-privilege workstations (Tier 2). If a Domain Admin never logs onto a developer's workstation, their TGT will never be in that workstation's LSASS memory to be stolen.


## Real-World Attack Scenario
During an adversary simulation for a cloud hosting provider, the attackers had established a foothold on a shared terminal server used by Level 1 support technicians. The objective was to escalate privileges to the Tier 0 infrastructure. Standard credential dumping techniques like Mimikatz or LSASS manipulation were heavily monitored and blocked by an aggressive EDR agent. 

Instead of targeting passwords or hashes, the attackers focused on Kerberos tickets residing in memory. When a user authenticates to a service, Kerberos Service Tickets (TGS) and Ticket Granting Tickets (TGT) are cached to facilitate Single Sign-On (SSO). The attacker realized that if they could extract a valid TGT belonging to a highly privileged user, they could inject it into their own session—a technique known as Pass-the-Ticket (PtT)—without needing to crack hashes or bypass NTLM restrictions.

The attacker utilized `Rubeus`, a C# tool set designed for Kerberos abuse, executing it purely in memory via an obfuscated PowerShell cradle to evade the EDR. They ran the `triage` command to list all cached tickets on the server.

```powershell
PS C:\> [Reflection.Assembly]::Load([Convert]::FromBase64String($RubeusBin)); [Rubeus.Program]::Main("triage".Split())
```

The output revealed a goldmine: a Domain Admin (`DA_admin1`) had recently logged onto the terminal server, and their TGT was still cached in memory and valid for another 8 hours. The attacker immediately used Rubeus to dump the specific ticket encoded in Base64 format.

```powershell
PS C:\> [Rubeus.Program]::Main("dump /luid:0x4f8a21 /service:krbtgt".Split())
```

With the Base64-encoded TGT extracted, the attacker copied the string and moved to a separate, entirely untrusted rogue laptop they had connected to the corporate guest network. The guest network had network line-of-sight to the Domain Controllers but was isolated from internal management zones.

On the rogue laptop, the attacker injected the stolen TGT into their local, unprivileged logon session using Rubeus.

```cmd
C:\> Rubeus.exe ptt /ticket:doIE1jCCBNKgAwIBBaEDAgEWooID+TCCA/VhggPxMIID7aADAgEFoQ...[truncated]
```

Instantly, the unprivileged session was granted the identity of `DA_admin1`. The attacker opened a standard command prompt and executed `dir \\Primary-DC.corp.local\C$`. Because the Kerberos ticket was perfectly valid and cryptographically signed by the Domain Controller, the authentication succeeded transparently. The attacker had achieved complete domain dominance without ever touching a password, extracting a hash, or triggering credential dumping alerts on the heavily monitored tier-0 servers.

## Chaining Opportunities

- **[[08 - Over-Pass-the-Hash Pass-the-Key]]**: Over-Pass-the-Hash generates a ticket. PtT is the immediate next step where you inject that generated ticket.
- **[[17 - Silver Ticket Attacks]]**: Forging a Silver Ticket creates a `.kirbi` file. You must use PtT to inject that forged ticket into your session to utilize it.
- **[[18 - Golden Ticket Attacks]]**: Similar to Silver Tickets, forging a Golden TGT requires PtT to load it into memory.

## Related Notes

- [[01 - Active Directory Lateral Movement Overview]]
- [[11 - LSASS Memory Dumping Techniques]]
- [[16 - Kerberos Delegation Abuse]]
