---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.05 Dumping LSASS Memory"
---

# Dumping LSASS Memory: Mimikatz, Procdump, and Comsvcs.dll

## Introduction to LSASS
The Local Security Authority Subsystem Service (LSASS) is a core Windows process (`lsass.exe`) responsible for enforcing the security policy on the system. It handles user logins, password changes, and access token creation. Because it must seamlessly authenticate users to network resources (via Single Sign-On), LSASS caches various forms of credentials in its process memory.

Depending on the Windows version, configuration, and authentication protocols in use, LSASS memory may contain:
- Plaintext passwords (historically via WDigest or TSPKG, now mostly disabled by default).
- NTLM hashes.
- Kerberos Ticket Granting Tickets (TGTs) and session keys.
- DPAPI (Data Protection API) master keys.

For an attacker who has achieved Local Administrator or `SYSTEM` privileges, dumping the memory of the `lsass.exe` process is one of the most critical steps in lateral movement. It transforms local compromise into domain-wide compromise by harvesting credentials of other users (like Domain Admins) who have logged onto the compromised machine.

---

## Architectural ASCII Diagram: LSASS Credential Harvesting

```text
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   +-------------------+                                                                         |
|   | Domain Admin User | ---- Logs into target Server via RDP/SMB ---->                          |
|   +-------------------+                                            |                            |
|                                                                    |                            |
|                                                                    v                            |
|   +-----------------------------------------------------------------------------------------+   |
|   |                          Target Server (Compromised by Attacker)                        |   |
|   |                                                                                         |   |
|   |  +-----------------------------------------------------------------------------------+  |   |
|   |  |                                lsass.exe (PID: 648)                               |  |   |
|   |  |  [ WDigest: None ]  [ Kerberos: TGTs/Keys ]  [ MSV: NTLM Hashes ]  [ DPAPI Keys ] |  |   |
|   |  +-----------------------------------------------------------------------------------+  |   |
|   |            ^                              ^                              ^              |   |
|   |            |                              |                              |              |   |
|   |  +---------+---------+          +---------+---------+          +---------+---------+    |   |
|   |  |    Method 1:      |          |    Method 2:      |          |    Method 3:      |    |   |
|   |  |    Mimikatz       |          |    Procdump       |          |    Comsvcs.dll    |    |   |
|   |  | (sekurlsa module) |          |  (Sysinternals)   |          |  (Native LoLBin)  |    |   |
|   |  +---------+---------+          +---------+---------+          +---------+---------+    |   |
|   |            |                              |                              |              |   |
|   |            | Reads memory directly        | Writes memory to file        | Writes memory|   |
|   |            v                              v                              v              |   |
|   |  +-------------------+          +-------------------+          +-------------------+    |   |
|   |  | Outputs Hashes/   |          |     lsass.dmp     |          |     lsass.dmp     |    |   |
|   |  | Passwords to CLI  |          |  (Dump File on    |          |  (Dump File on    |    |   |
|   |  |                   |          |   Disk)           |          |   Disk)           |    |   |
|   |  +-------------------+          +-------------------+          +-------------------+    |   |
|   +-----------------------------------------------------------------------------------------+   |
|                                                                                                 |
|   +-----------------------------------------------------------------------------------------+   |
|   |  Attacker exfiltrates lsass.dmp and parses it offline (e.g., via pypykatz) to avoid     |   |
|   |  dropping malicious binaries like Mimikatz on the target server.                        |   |
|   +-----------------------------------------------------------------------------------------+   |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## Dumping Techniques and Tooling

### 1. Mimikatz (Direct Interaction)
Mimikatz, developed by Benjamin Delpy, is the premier tool for interacting with Windows security mechanisms. It can read LSASS memory directly and parse out credentials in real-time.

```text
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # sekurlsa::logonpasswords
```
**Pros**: Instant gratification, extracts almost everything (NTLM, Kerberos, WDigest).
**Cons**: Mimikatz is the most heavily signatured binary in the world. Dropping it on disk without heavy obfuscation or memory-loading (via Cobalt Strike) will result in immediate termination by AV/EDR.

### 2. Sysinternals Procdump (Disk-Based Dump)
To avoid dropping Mimikatz on the target, attackers often use legitimate Microsoft tools to create a memory dump file (`.dmp`) of the LSASS process. `procdump.exe` is a Sysinternals utility designed for crash analysis.

```cmd
C:\> procdump.exe -accepteula -ma lsass.exe C:\Temp\lsass.dmp
```
* `-ma`: Write a full memory dump.
Once `lsass.dmp` is created, the attacker exfiltrates the file to their Kali machine and parses it offline.

### 3. Comsvcs.dll (Native LoLBin)
Because EDRs often flag `procdump.exe` when targeted at LSASS, attackers shifted to using "Living off the Land" binaries (LoLBins). `comsvcs.dll` is a native Windows DLL that contains an exported function called `MiniDumpW`. This function can be invoked via `rundll32.exe` to dump process memory.

First, identify the PID of `lsass.exe`:
```cmd
C:\> tasklist /fi "imagename eq lsass.exe"
```

Next, invoke `comsvcs.dll` to dump the memory (Requires SYSTEM privileges, as it must bypass ACLs on the lsass process):
```cmd
C:\> rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump 648 C:\Temp\lsass.dmp full
```
**Pros**: Uses purely native Windows binaries.
**Cons**: Requires knowing the PID and executing from an elevated SYSTEM context. Modern EDRs heavily monitor `rundll32.exe` loading `comsvcs.dll`.

### 4. Task Manager (GUI Method)
If the attacker has GUI access (e.g., via RDP), they can simply open Task Manager as an Administrator, right-click `Local Security Authority Process` (lsass.exe), and select "Create dump file". This creates a dump in `%TEMP%`. While simple, this is highly effective if EDRs are focused solely on command-line detections.

---

## Offline Analysis of Dump Files
Once the `lsass.dmp` file is exfiltrated to the attacker's machine, it can be parsed safely without triggering the target's EDR.

**Using Mimikatz (on Windows):**
```text
mimikatz # sekurlsa::minidump lsass.dmp
mimikatz # sekurlsa::logonpasswords
```

**Using Pypykatz (on Linux/Kali):**
`pypykatz` is a Python implementation of Mimikatz tailored for parsing memory dumps cross-platform.
```bash
pypykatz lsa minidump lsass.dmp
```

---

## LSASS Protection and Evasion

### LSA Protection (RunAsPPL)
To mitigate LSASS dumping, Microsoft introduced LSA Protection, which utilizes the Protected Process Light (PPL) model. When enabled, non-PPL processes (even those running as SYSTEM) cannot request `PROCESS_VM_READ` access rights to `lsass.exe`. 

If an attacker tries to dump LSASS with PPL enabled, they will receive an `Access Denied` error.

**Bypassing PPL:**
To bypass PPL, attackers must typically drop a vulnerable or malicious signed driver to the system to disable the PPL flag on LSASS from kernel space. 
Mimikatz accomplishes this using `mimidrv.sys`:
```text
mimikatz # privilege::debug
mimikatz # !+
mimikatz # !processprotect /process:lsass.exe /remove
mimikatz # sekurlsa::logonpasswords
```

### Detection and OPSEC
Dumping LSASS is notoriously difficult to hide from mature EDRs. 

1. **Event ID 4656 / 4663 (Object Access)**: Windows can be configured to audit access to the `lsass.exe` process. Any process requesting `0x1410` or `0x1fffff` (PROCESS_VM_READ | PROCESS_VM_WRITE) access masks against LSASS will generate alerts.
2. **API Hooking**: EDRs heavily hook the `MiniDumpWriteDump` Windows API inside `dbghelp.dll` and `dbgcore.dll`. If a process calls this API targeting LSASS, the EDR blocks it. Attackers bypass this by implementing direct Syscalls or unhooking the DLLs in memory prior to dumping.
3. **File Creation**: Dumping LSASS creates a massive file (often 50MB - 150MB) on disk. EDRs look for large `.dmp` files containing LSASS memory signatures. Attackers counter this by dumping LSASS directly into memory and exfiltrating over C2 channels without writing to disk.

---


## Real-World Attack Scenario
During a compromise assessment for a telecommunications provider, an attacker had successfully phished an IT support technician, gaining local administrator privileges on their workstation. The attacker's primary goal was to obtain Domain Admin credentials to take over the Active Directory forest. Knowing that IT support staff frequently log into their machines with highly privileged accounts to perform administrative tasks, the attacker targeted the Local Security Authority Subsystem Service (`lsass.exe`) process memory, which caches credentials for active logon sessions.

The organization had deployed a robust Endpoint Detection and Response (EDR) solution that aggressively flagged and blocked known credential dumping tools like `mimikatz.exe`. To bypass this, the attacker decided to use a Living-off-the-Land (LotL) technique utilizing the built-in Windows `comsvcs.dll` library to dump the LSASS process memory to a file invisibly.

First, the attacker used a standard command prompt to identify the Process ID (PID) of `lsass.exe`.

```cmd
C:\> tasklist | findstr lsass
lsass.exe                      748 Services                   0     65,232 K
```

With the PID (748) identified, the attacker needed to execute the memory dump. Instead of running a suspicious executable, they used `rundll32.exe` to call the `MiniDump` export function of `comsvcs.dll`. To avoid alerting the EDR which monitors for command lines containing "lsass", they used PowerShell to craft the command dynamically.

```powershell
PS C:\> $pid_lsass = (Get-Process lsass).Id
PS C:\> rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump $pid_lsass C:\Temp\lsass.dmp full
```

The EDR failed to block the action because `rundll32.exe` and `comsvcs.dll` are legitimate, signed Microsoft binaries. The attacker successfully generated the `lsass.dmp` file in the `C:\Temp` directory. To further obfuscate their actions, they immediately compressed and password-protected the dump file using the built-in `Compress-Archive` cmdlet and downloaded it to their attack machine.

```bash
# On the attacker's Linux machine
pypykatz lsa minidump lsass.dmp
```

Back on their offline attack infrastructure, the attacker ran `pypykatz` (a Python implementation of Mimikatz) against the extracted dump file. The analysis revealed the plaintext password of a Domain Admin account (`DA_Admin1`) that the IT technician had used earlier that day to map a network drive. With these highly privileged credentials in hand, the attacker immediately pivoted to the primary Domain Controller, achieving total domain compromise within minutes of the initial LSASS dump.

## Chaining Opportunities
- **[[01 - Lateral Movement via RDP and Hijacking Sessions]]**: RDP provides the perfect GUI environment to use the Task Manager dumping method, completely bypassing command-line logging.
- **Pass-the-Hash**: Once NTLM hashes are extracted from the LSASS dump, they are immediately fed into tools like Impacket's `wmiexec.py` or `psexec.py` to move to the next system.
- **Silver / Golden Tickets**: Extracting the Kerberos `krbtgt` hash (if on a Domain Controller) or machine account hashes allows for the forging of Kerberos tickets.

## Related Notes
- [[02 - Lateral Movement via WinRM and PSRemoting]]
- [[03 - Lateral Movement via SMB PsExec SmbExec]]
- [[04 - Lateral Movement via WMI WMIExec]]
- [[Kerberoasting and AS-REP Roasting]]

---
*End of Document*
