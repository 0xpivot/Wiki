---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 67"
---

# QnA - AD Module 67: Pass the Hash (PtH)

## Architecture Overview: Pass the Hash Mechanism

```text
+-------------------------------------------------------------+
|               Pass the Hash (PtH) Architecture              |
+-------------------------------------------------------------+
| [Attacker Machine]                                          |
|  1. Obtain NTLM Hash                                        |
|     (e.g., from LSASS dump, SAM registry, or NTDS.dit)      |
|                                                             |
|  2. Inject Hash into Local Session (Mimikatz / Rubeus)      |
|     sekurlsa::pth /user:Administrator /domain:CORP /ntlm:XX |
|                                                             |
|  3. Trigger NTLM Authentication                             |
+-------------------------------------------------------------+
               |
               | (SMB/WMI/WinRM Request)
               v
+-------------------------------------------------------------+
| [Target Server / Domain Controller]                         |
|  <-- 4. Server sends NTLM Challenge (Nonce)                 |
|                                                             |
|  [Attacker Machine]                                         |
|  --> 5. Attacker computes Response using INJECTED HASH      |
|         (Does NOT need the plaintext password!)             |
|                                                             |
|  [Target Server]                                            |
|  6. Server validates Response with its own Hash/DC          |
|  <-- 7. Access Granted (Token Generated)                    |
+-------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: Explain the exact cryptographic mechanics of Pass the Hash and why the plaintext password is not required.
**Answer:**
Pass the Hash (PtH) exploits the fact that the Windows NTLM authentication protocol does not transmit the plaintext password over the network. Instead, it uses a challenge-response mechanism based on the user's NTLM hash (MD4 of the UTF-16LE encoded password).
During NTLM authentication:
1. The client requests access to a server.
2. The server replies with a random 8-byte challenge (Nonce).
3. The client encrypts this challenge using the user's NTLM hash as the cryptographic key, producing the Authenticator Response, and sends it back.
Because the NTLM hash itself is the static key used to generate the response, an attacker who possesses the hash can natively compute the valid mathematical response to the server's challenge. The operating system handles the cryptography; the attacker simply injects the hash into LSASS memory so the OS uses it as if the user had just typed their password.

### Q2: What is the role of LSASS in a Pass the Hash attack, and how do tools like Mimikatz manipulate it?
**Answer:**
The Local Security Authority Subsystem Service (`lsass.exe`) manages local security, domain authentication, and Active Directory policies in Windows. When a user logs in, LSASS caches their credentials (including the NTLM hash and Kerberos tickets) in memory to facilitate single sign-on (SSO) across the network.
**Mimikatz Manipulation:**
When an attacker runs `sekurlsa::pth` in Mimikatz, the tool interacts directly with LSASS memory. It spawns a new process (e.g., `cmd.exe`) in a suspended state and creates a new logon session. Mimikatz then patches the LSASS memory structures associated with this newly created logon session, replacing the dummy or blank credentials with the target username, domain, and the stolen NTLM hash. Once patched, the process is resumed. Any network authentication originating from this process will now seamlessly utilize the injected NTLM hash.

### Q3: What is "Restricted Admin Mode" in RDP, and how does it relate to Pass the Hash?
**Answer:**
Restricted Admin Mode (`/RestrictedAdmin`) is an RDP security feature introduced to prevent credential exposure. Normally, when you RDP into a server, your plaintext credentials and hashes are cached in the target server's LSASS memory. In Restricted Admin Mode, the client performs a network-level authentication (using NTLM or Kerberos) and *does not* send reusable credentials to the remote server, thus protecting the admin from having their credentials dumped if the target server is already compromised.
**Relation to PtH:**
Ironically, because Restricted Admin Mode relies on network-level authentication rather than requiring an interactive plaintext password at the lock screen, it makes RDP vulnerable to Pass the Hash. If Restricted Admin Mode is enabled on a target server, an attacker with a compromised NTLM hash can perform PtH over RDP (using tools like `xfreerdp /pth:...`) to gain a graphical session, whereas traditionally, RDP requires the plaintext password.

---

## Scenario-Based Questions

### Scenario 1: You have compromised a local administrator account on a workstation and dumped the local SAM database. You extract the local 'Administrator' NTLM hash. You find that the local Administrator password is the same across the entire subnet, but PtH attempts using CrackMapExec fail with `STATUS_LOGON_FAILURE`. Why might this be happening, and how do you bypass it?
**Answer:**
This is typically caused by **LocalAccountTokenFilterPolicy** (UAC Remote Restrictions). On modern Windows systems (Vista and later), when a local user account (except the built-in Administrator account with RID 500, under certain conditions) attempts to access a machine over the network, Windows strips administrative privileges from the network token. The logon technically succeeds, but the token is medium-integrity, denying administrative access to resources like `ADMIN$` or WMI.
**Bypass/Resolution:**
1. **RID 500:** If the hash belongs to the built-in default Administrator account (RID 500), it normally bypasses this restriction unless explicitly disabled via Group Policy. Ensure you are using the exact built-in account.
2. **Registry Modification:** If you have remote registry access or another execution vector, you can set `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy` to `1`.
3. **Domain Accounts:** This restriction does *not* apply to Domain accounts. If you can compromise a Domain Admin or a domain user in the local Administrators group, PtH will work flawlessly.

### Scenario 2: You are attempting to perform a PtH attack against a highly monitored critical server. The SOC monitors Event ID 4624 heavily. How can you execute commands on the target server while minimizing suspicious Network Logon (Type 3) footprints?
**Answer:**
Standard PtH using SMB (`psexec`, `smbexec`) relies on Service Control Manager and dropping binaries/scripts to admin shares, which creates massive amounts of noise (Event IDs 4624, 4697, 7045, file creation events).
To minimize the footprint:
1. **WMI (Windows Management Instrumentation):** Use WMI for remote execution (e.g., `wmiexec.py`). WMI executes via the DCOM protocol (port 135) and spawns processes under `WmiPrvSE.exe` rather than `services.exe`. It does not create new services, avoiding Event ID 4697/7045.
2. **WinRM (Windows Remote Management):** Use PowerShell Remoting (`evil-winrm`). It communicates over HTTP/HTTPS (ports 5985/5986). It spawns under `wsmprovhost.exe`.
While both still generate a 4624 (Type 3) logon, they blend in much better with standard administrative traffic than SMB service creation, and they avoid disk I/O entirely if used for living-off-the-land fileless execution.

### Scenario 3: During a Purple Team exercise, you successfully dumped LSASS and used PtH to access a file server. However, the Blue Team detected your activity instantly. They claim they detected "Mimikatz PtH execution." You used heavily obfuscated Mimikatz. What specific artifact gave you away?
**Answer:**
The Blue Team likely detected the anomalous **Logon Type 9 (NewCredentials)**. 
When `sekurlsa::pth` is executed, Mimikatz uses the `LogonUser` API with the `LOGON32_LOGON_NEW_CREDENTIALS` flag. This spawns the dummy process and creates a local Event ID 4624 with Logon Type 9 on the *attacker's* machine (or the pivot machine where Mimikatz was run). 
Additionally, they might have noticed Event ID 4688 (Process Creation) showing `cmd.exe` or `powershell.exe` being spawned with suspicious command-line arguments, or Sysmon Event ID 10 (Process Access) showing an anomalous process requesting highly privileged access (e.g., `PROCESS_VM_READ | PROCESS_VM_WRITE`) to `lsass.exe`. Obfuscating Mimikatz only changes the binary signature, not the API telemetry or Event Logs it inherently generates.

---

## Deep-Dive Defensive Questions

### Q1: Detail the implementation and limitations of Windows Defender Credential Guard in preventing Pass the Hash attacks.
**Answer:**
**Implementation:**
Windows Defender Credential Guard uses Virtualization-Based Security (VBS) to isolate the LSASS process. It creates an isolated, virtualized container (Isolated LSA) that runs alongside the standard Windows OS kernel but is separated by the hypervisor. The standard LSASS process acts only as a proxy; the actual secrets (NTLM hashes, Kerberos TGTs) are stored in the Isolated LSA. Because the standard OS (and even the SYSTEM account or kernel-level drivers) cannot access the memory of the Isolated LSA, attackers cannot dump the hashes.
**Limitations:**
1. **Hardware Requirements:** Requires CPU virtualization extensions (Intel VT-x/AMD-V), TPM 2.0, and UEFI Secure Boot.
2. **Does not protect currently typed passwords:** If an attacker installs a keylogger, they can capture the password before it reaches the Isolated LSA.
3. **Does not prevent use of compromised hashes:** If an attacker compromises a hash from an unprotected machine or the NTDS.dit, they can still perform a PtH attack *against* a machine running Credential Guard. Credential Guard only protects secrets *stored* on the local machine; it does not disable the NTLM protocol.

### Q2: What event log telemetry uniquely identifies a Pass the Hash attack over the network, differentiating it from legitimate NTLM authentication?
**Answer:**
Detecting PtH purely over the network is notoriously difficult because PtH is fundamentally a valid implementation of the NTLM protocol. However, anomalies can be spotted:
1. **Event ID 4624 (Logon):** Look for Logon Type 3 (Network Logon) using the `NTLM` authentication package. 
2. **Workstation Name Anomaly:** In many PtH tools (like early versions of Impacket or Kali tools), the NTLM authentication exchange includes a static or blank Workstation Name in the NTLM negotiation flags (e.g., "KALI" or "WORKSTATION"). Cross-referencing the supplied Workstation Name with the source IP address can reveal mismatches.
3. **Account Profiling:** Legitimate administrators usually log in interactively (Kerberos/Logon Type 2/10). A sudden spike in NTLM Type 3 logons from an unexpected IP address using a Domain Admin account is highly suspicious.
4. **Sysmon Event ID 3 (Network Connection):** Correlating incoming SMB/RPC traffic with abnormal parent processes (like `python.exe` or `ruby.exe` if run from an attacker workstation inside the network).

### Q3: Organizations often attempt to mitigate PtH by disabling NTLM entirely. What are the operational challenges and dependencies that make disabling NTLM difficult?
**Answer:**
Disabling NTLM across an enterprise (setting `Network security: Restrict NTLM: NTLM authentication in this domain` to `Deny for all`) is the ultimate defense but fraught with operational risks:
1. **Legacy Applications:** Many older applications, third-party appliances, and non-Windows systems hardcode NTLM authentication and do not support Kerberos.
2. **IP-Based Access:** Kerberos requires Service Principal Names (SPNs) which are tied to hostnames. If users access resources via IP addresses (e.g., `\\192.168.1.50\share`), Kerberos will fail, and the system gracefully falls back to NTLM. Disabling NTLM breaks this access.
3. **External Trusts:** Authentication across forest trusts where Kerberos routing is not properly configured will fall back to NTLM.
4. **Workgroup Machines:** Machines not joined to the domain inherently cannot use Kerberos and rely solely on NTLM.
Organizations must first enable NTLM Auditing (Event ID 8004 in the NTLM Operational log) for months to map dependencies before enforcing a blocking policy.

---

## Real-World Attack Scenario
**The SMB Relay to PtH Pipeline:**
During an internal penetration test, an attacker was placed on a standard user VLAN with no credentials. The attacker deployed `Responder` to poison LLMNR/NBT-NS broadcasts. A server administrator mistyped a network share path (`\\fs-srv1`), and their machine broadcasted an LLMNR request.
Responder intercepted the request and captured the administrator's NetNTLMv2 hash. Since NetNTLMv2 hashes cannot be passed directly (they are challenged-based), the attacker cracked the hash offline using Hashcat, revealing a weak password.
With the plaintext password, the attacker generated the NTLM hash. They used CrackMapExec to spray the hash across the server subnet. They successfully found local administrator access on multiple critical servers. Because EDR blocked `psexec`, the attacker used `wmiexec.py` to seamlessly Pass the Hash, executing fileless PowerShell commands to establish a beacon. The attacker then dumped the local LSASS of those servers, obtaining a Domain Administrator's NTLM hash left in memory from a recent RDP session, leading to full domain compromise.

---

## Chaining Opportunities
- **Initial Access to Lateral Movement:** PtH is the primary engine for lateral movement after dumping credentials via [[AD QnA - Module 66 - Local Privilege Escalation Windows]] or discovering them in SYSVOL.
- **Overpass the Hash:** If the environment heavily restricts NTLM, attackers can use the NTLM hash to request a Kerberos TGT, upgrading the attack to [[AD QnA - Module 69 - Overpass the Hash]].
- **DCSync:** Once a highly privileged account's hash is obtained, PtH is used to execute remote replication APIs, leading directly to [[AD QnA - Module 70 - DCSync Attacks]].

---

## Related Notes
- [[NTLM Authentication Protocol Deep Dive]]
- [[LSASS Memory Protection and Bypasses]]
- [[Windows Defender Credential Guard]]
- [[Lateral Movement Techniques in Active Directory]]
- [[Kerberos vs NTLM - Protocol Comparisons]]
