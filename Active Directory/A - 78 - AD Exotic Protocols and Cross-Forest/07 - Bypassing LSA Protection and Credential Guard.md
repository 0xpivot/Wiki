---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.07 Bypassing LSA Protection and Credential Guard"
---

# Bypassing LSA Protection and Credential Guard

## 1. Introduction to LSA Defenses

In modern Windows environments, Microsoft has introduced several robust mechanisms to protect the Local Security Authority Subsystem Service (`lsass.exe`). LSASS is responsible for enforcing the security policy on the system, verifying user logging on to a Windows computer or server, handling password changes, and creating access tokens. Because LSASS stores plaintext passwords, NTLM hashes, and Kerberos tickets in its memory space, it has historically been the primary target for credential dumping tools like Mimikatz.

To combat this, two distinct but related protective technologies are commonly deployed in hardened Active Directory environments: LSA Protection (RunAsPPL) and Windows Defender Credential Guard. Understanding how these protections work and, more importantly, how to bypass them, is a critical skill for advanced red team operations.

### 1.1 LSA Protection (RunAsPPL)
LSA Protection leverages the Protected Process Light (PPL) mechanism introduced in Windows 8.1 / Server 2012 R2. When enabled, `lsass.exe` runs as a protected process (`PsProtectedSignerLsa-Light`). This prevents non-protected processes—even those running with `NT AUTHORITY\SYSTEM` privileges—from interacting with LSASS memory. Specifically, it prevents a non-PPL process from obtaining a handle with `PROCESS_VM_READ` or `PROCESS_ALL_ACCESS` rights to `lsass.exe`.

### 1.2 Windows Defender Credential Guard
Credential Guard uses Virtualization-Based Security (VBS) to isolate the most sensitive secrets (like NTLM password hashes and Kerberos Ticket Granting Tickets - TGTs). Instead of residing in the normal memory space of `lsass.exe`, these secrets are stored in an isolated environment called the `LSAIso` (Local Security Authority Isolated) process, which runs within a secure micro-hypervisor container (Trustlet). Even if an attacker gains kernel-level execution (`Ring 0`) in the standard operating system, they cannot read the memory of the `LSAIso` trustlet.

---

## 2. Bypassing LSA Protection (RunAsPPL)

LSA Protection is primarily a user-mode and specific-level kernel boundary defense. Since it relies on the Windows kernel to enforce the PPL access checks, an attacker who can execute code in kernel mode (Ring 0) can bypass or disable these protections entirely.

### 2.1 The "Bring Your Own Vulnerable Driver" (BYOVD) Attack

The most common method to bypass PPL is the BYOVD technique. The attacker drops a legitimately signed, but vulnerable, kernel-mode driver onto the system. Because the driver is signed by a trusted certificate authority (e.g., Microsoft hardware compatibility program), the OS allows it to load. Once loaded, the attacker exploits the vulnerability within the driver to execute arbitrary code in kernel mode.

From kernel mode, the attacker can:
1.  **Strip the PPL flag:** Locate the `EPROCESS` structure for the `lsass.exe` process in kernel memory and clear the `Protection` bit, effectively converting it back into a standard, unprotected process.
2.  **Elevate the attacker's process:** Locate the `EPROCESS` structure for the attacker's dumping tool (e.g., Mimikatz) and set its `Protection` bit to match or exceed the PPL level of LSASS, allowing the tool to request a valid handle.

#### Example: Using `mimidrv.sys`
Mimikatz provides a signed driver (`mimidrv.sys`) that can be used to interact with kernel memory.

```text
mimikatz # !+               ; Load the mimidrv driver
mimikatz # !processprotect /process:lsass.exe /remove ; Strip PPL from LSASS
mimikatz # sekurlsa::logonpasswords ; Dump credentials normally
```
*Note: Loading custom drivers often requires the `SeLoadDriverPrivilege` and may be blocked by HVCI/Driver Blocklists.*

#### Example: Using PPLdump / PPLkiller / PPLMedic
Tools like `PPLdump` utilize known vulnerable drivers (e.g., the RTCore64.sys driver from MSI Afterburner or vulnerable gigabyte drivers) to achieve arbitrary kernel memory read/write. They surgically alter the `EPROCESS` block of the target process to bypass the PPL check, dump the memory, and then restore the structure to avoid system instability.

### 2.2 Exploiting the LSA Plugin Architecture

Another bypass technique involves abusing how LSASS loads authentication packages (LSA plugins). If an attacker can drop a malicious DLL and modify the registry to load it as an LSA authentication package (e.g., via the `Security Packages` value in `HKLM\SYSTEM\CurrentControlSet\Control\Lsa`), the DLL will be loaded directly into the `lsass.exe` process space upon the next reboot. 

Because the malicious code is now executing *inside* the protected LSASS process, it inherently bypasses the PPL boundary and can hook functions like `SpAcceptCredentials` to capture plaintext passwords as users log in.

---

## 3. Bypassing Windows Defender Credential Guard

Bypassing Credential Guard is significantly more difficult than bypassing PPL. Because Credential Guard uses a hypervisor to isolate memory, purely kernel-based read/write exploits (like BYOVD) are insufficient to extract the protected NTLM hashes or TGTs. The secrets are physically inaccessible to the standard OS.

However, Credential Guard only protects *stored* secrets. It does not protect credentials as they are actively being typed, nor does it prevent the system from requesting new Kerberos tickets.

### 3.1 Custom Security Support Providers (SSP) and Keystroke Logging

Since Credential Guard cannot protect the plaintext password before it is hashed and sent to LSASS, attackers can intercept the password during the logon process.

1.  **Malicious SSP:** An attacker can inject a malicious Security Support Provider (SSP) into LSASS. While Credential Guard protects the hashes, an SSP loaded into the normal LSASS process can still intercept plaintext credentials as they are passed down from Winlogon.
2.  **Keylogging:** Implementing a low-level keylogger to capture the user's keystrokes at the `winlogon.exe` or `logonui.exe` level before the data ever reaches the LSA architecture.

### 3.2 WDigest Downgrade

Windows historically supported the WDigest authentication protocol, which required keeping plaintext passwords in LSASS memory. While disabled by default in modern Windows versions, an attacker with local administrator privileges can re-enable WDigest via the registry.

```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f
```
Once re-enabled, the attacker must wait for the user to log off and log back on, or forcefully lock the screen to coerce a re-authentication. When the user logs in, the plaintext password will be stored in the standard LSASS memory, outside the Credential Guard trustlet, where it can be extracted using standard techniques (assuming PPL has been bypassed).

### 3.3 Extracting Kerberos Service Tickets (TGS)

Credential Guard specifically protects the Kerberos Ticket Granting Ticket (TGT) and the user's NTLM hash. It **does not** protect Kerberos Service Tickets (TGS). 

An attacker who compromises a machine running Credential Guard can still extract the TGS tickets from memory (e.g., using Rubeus). Furthermore, the attacker can leverage the compromised machine's context to request new TGS tickets for other services in the domain. 

For example, using `Rubeus`, an attacker can extract a TGS for the CIFS service of a file server, and use that ticket to move laterally, bypassing the need to extract the TGT.

```powershell
Rubeus.exe dump /service:cifs/filesrv01.corp.local
```

### 3.4 Delegation Abuse via RPC / COM

If an attacker has an interactive session or high-privileged remote execution on a Credential Guard protected machine, they can coerce the machine to authenticate to another machine controlled by the attacker using specific protocols (like DCOM or RPC) that leverage Kerberos delegation. If the target machine is allowed to delegate credentials, the attacker can intercept the forwarded TGT, which is transmitted outside the VBS boundary.

---

## 4. Visualizing the Protections and Bypasses

The following diagram illustrates the isolation boundaries of PPL and Credential Guard, and the vectors attackers use to penetrate or circumvent them.

```text
+-------------------------------------------------------------------------+
|                        Windows Operating System                         |
|                                                                         |
|  +---------------------+                                                |
|  | User-Mode Process   |  (e.g., Attacker C2 / Mimikatz)                |
|  | Level: Unprotected  |                                                |
|  +---------+-----------+                                                |
|            | 1. Attempt PROCESS_VM_READ (BLOCKED by PPL)                |
|            x                                                            |
|  +---------+-----------+  +------------------------------------------+  |
|  | lsass.exe (PPL)     |  | 2. BYOVD Attack (Vulnerable Driver)      |  |
|  | Level: PPL-Light    |  |    Modifies EPROCESS struct in Kernel    |  |
|  |                     |  |    Strips PPL from lsass.exe             |  |
|  | Stores:             |<----+ +--------------------------------+    |  |
|  | - TGS Tickets       |  |    | kernel32.sys / ntoskrnl.exe    |    |  |
|  | - WDigest Plaintext |  |    +--------------------------------+    |  |
|  +---------+-----------+  +------------------------------------------+  |
|            |                                                            |
+------------|------------------------------------------------------------+
             | 3. RPC/ALPC Communication
=============|=============================================================
             v  VBS BOUNDARY (Hypervisor Enforced)
+------------+------------------------------------------------------------+
|  +---------+-----------+                                                |
|  | LSAIso.exe (Trustlet|  4. Credential Guard Boundary                  |
|  | Level: Isolated     |     - Inaccessible from normal OS Ring 0       |
|  |                     |     - Attacker must wait for user to re-auth   |
|  | Stores:             |       (Keylog/WDigest) or abuse TGS/Delegation |
|  | - NTLM Hashes       |                                                |
|  | - Kerberos TGTs     |                                                |
|  +---------------------+                                                |
|                        Virtualization-Based Security (VBS)              |
+-------------------------------------------------------------------------+
```

---

## 5. Defensive Considerations and Mitigation

Defending against PPL and Credential Guard bypasses requires strict control over the execution environment.

### 5.1 Block Vulnerable Drivers
Implement Microsoft's recommended Driver Block Rules using Windows Defender Application Control (WDAC). Ensure that Hypervisor-Protected Code Integrity (HVCI) is enabled, which strictly prevents the execution of unsigned or blocklisted drivers in kernel mode, neutralizing most BYOVD attacks.

### 5.2 Restrict Local Admin Access
Bypassing these protections invariably requires local Administrator or SYSTEM privileges. Implement Just-In-Time (JIT) administration and strict Tiering to prevent attackers from gaining the prerequisite privileges to execute bypass tools.

### 5.3 Disable WDigest
Ensure WDigest is explicitly disabled across the domain via Group Policy, and monitor the registry key `UseLogonCredential` for unauthorized modifications.

### 5.4 Monitor for Suspicious Process Handles
Use EDR solutions to monitor for processes requesting unusual handles to `lsass.exe`, even if they fail due to PPL. The attempt itself is highly indicative of malicious activity. Hunt for Event ID 4656 (A handle to an object was requested) targeting LSASS.

### 5.5 Alert on Service Creation
The loading of custom drivers or malicious SSPs requires creating new system services or modifying critical registry keys. Alerting on unexpected service creation (Event ID 7045) or modifications to `HKLM\SYSTEM\CurrentControlSet\Control\Lsa` is critical.

---

## 6. Chaining Opportunities

- **[[06 - Exploiting Microsoft Identity Manager MIM]]**: If a MIM server is heavily defended with PPL and Credential Guard, bypassing these mechanisms is necessary to dump the memory of `miiserver.exe` or extract the DPAPI keys needed for further lateral movement.
- **[[04 - Extracting and Reversing DPAPI Secrets]]**: DPAPI master keys are often cached in LSASS. Bypassing PPL is often the first step required before executing DPAPI extraction tools to decrypt user master keys.
- **[[08 - Advanced NTLM Relaying to MSSQL]]**: If Credential Guard prevents hash extraction, an attacker might instead opt to coerce authentication from the target machine and relay the NTLM authentication to a secondary target, entirely bypassing the need to extract the hash.

## 7. Related Notes

- [[02 - Local Privilege Escalation Techniques in Windows]]
- [[05 - Windows Defender Application Control WDAC Evasion]]
- [[01 - Introduction to Active Directory Trusts]]
- [[09 - PrinterBug and PetitPotam Alternatives]]
