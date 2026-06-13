---
tags: [tools, privesc, enumeration, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.75 Snaffler Finding Secrets in AD"
---

# Snaffler: Finding Secrets in Active Directory

## 1. Introduction to Snaffler

`Snaffler` is an incredibly powerful, purpose-built C# tool designed for one specific task: rapidly scouring an Active Directory (AD) environment for sensitive information, credentials, and secrets hidden within file shares. During an assessment, after gaining an initial foothold as a low-privileged domain user, attackers frequently discover massive repositories of organizational data across hundreds of network shares (SMB). Manually reviewing these shares is impossible.

Snaffler automates this process at scale. It queries AD for computers, enumerates file shares on those computers, recursively lists directories, and then analyzes the contents of files against an extensive set of predefined rules (regex and string matching) to identify high-value targets like passwords, private keys, database connection strings, and configuration files.

## 2. ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                              Snaffler Execution Flow                              |
|                                                                                   |
|  +-----------------+                                                              |
|  |                 |                                                              |
|  |  Attacker Host  | 1. LDAP Query (Get all Computer Objects)                     |
|  | (Domain Joined) |--------------------------------------------+                 |
|  |                 |                                            |                 |
|  +-----------------+                                            v                 |
|          |                                            +--------------------+      |
|          | 2. Connect to Port 445 (SMB)               |  Domain Controller |      |
|          +--------------------------+                 +--------------------+      |
|          |                          |                                             |
|          v                          v                                             |
|  +---------------+          +---------------+                                     |
|  |  File Server A|          |  Workstation B|     ... (Parallel Execution)        |
|  |  (10.0.1.50)  |          |  (10.0.2.15)  |                                     |
|  +---------------+          +---------------+                                     |
|          |                          |                                             |
|          | 3. Share Enum            | 3. Share Enum                               |
|          | (SYSVOL, IT_Scripts,     | (C$, ADMIN$ - access denied)                |
|          |  Backups)                |                                             |
|          v                          v                                             |
|  +-----------------------------------------------------------------------------+  |
|  |                          Snaffler Analysis Engine                           |  |
|  |                                                                             |  |
|  | - Filters out massive, irrelevant files (.iso, .vmdk, .mp4)                 |  |
|  | - Parses file extensions (.ps1, .xml, .config, .kdbx)                       |  |
|  | - Inspects file contents using Regex / YARA-style rules                     |  |
|  |   (e.g., matches `password\s*=\s*['"][^'"]+['"]`)                           |  |
|  +-----------------------------------------------------------------------------+  |
|                                     |                                             |
|                                     v                                             |
|  +-----------------------------------------------------------------------------+  |
|  |                          Triage Output & Reporting                          |  |
|  | [Black]   Irrelevant files                                                  |  |
|  | [Green]   Informational (e.g., interesting file name, low confidence)       |  |
|  | [Yellow]  Medium Confidence (e.g., generic configuration file)              |  |
|  | [Red]     High Confidence (e.g., id_rsa private key, Unattend.xml)          |  |
|  | [Snaff]   Critical Secret Found IN FILE (Extracts snippet of text)          |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 3. Operational Mechanics and Rule Engine

Snaffler's effectiveness is entirely dependent on its internal ruleset. Instead of blindly grepping, it uses a tiered approach to save time and network bandwidth.

1.  **Share Triage:** It identifies if a share is readable. It skips default administrative shares (`C$`, `ADMIN$`) unless the context dictates otherwise. It targets shares like `SYSVOL`, `NETLOGON`, or custom departmental shares.
2.  **File/Extension Triage:** Before downloading a file, Snaffler checks its name, extension, and size. It immediately flags files like `.kdbx` (KeePass database), `id_rsa` (SSH key), or `web.config` as high-priority based purely on metadata. It ignores massive binary files to prevent overwhelming the network.
3.  **Content Inspection:** If a file passes triage, Snaffler downloads a small chunk of it and runs regex rules against the contents. This is where it extracts hardcoded credentials from `.ps1` scripts, `.bat` files, or `.txt` notes left by IT staff.

### 3.1 The "Snaff" Output
When Snaffler finds a secret *inside* a file, it generates a `[Snaff]` level alert. This is the highest severity finding. Snaffler will actually extract the surrounding context (the specific line containing the password) and display it in the console, saving the attacker the effort of manually opening the file.

## 4. Deployment and Execution

### 4.1 Prerequisites
Snaffler must be run from a machine that is authenticated to the domain. This is typically achieved in one of two ways:
1.  **Domain-Joined System:** Running the tool directly on a compromised workstation.
2.  **Proxying/SOCKS:** Running Snaffler through a SOCKS proxy (e.g., via Chisel or Cobalt Strike) using tools like `proxychains` or Windows native features, provided the attacker has valid domain user credentials.
3.  **Runas /netonly:** If running from a non-domain Windows machine, the attacker can use `runas /netonly /user:DOMAIN\username "snaffler.exe"` to execute it in the context of the domain user for network operations.

### 4.2 Basic Syntax
Executing Snaffler against the entire domain:
```cmd
snaffler.exe -s -d target.domain.local -o snaffler_output.txt
```
- `-s`: Print output to stdout.
- `-d`: Specify the target domain. Snaffler will automatically query LDAP for all computers in this domain.
- `-o`: Log output to a file (highly recommended).

### 4.3 Advanced Targeting
Scanning an entire massive enterprise domain can take hours and generate significant network noise. Operators often narrow the scope.

**Targeting Specific Computers or Shares:**
```cmd
:: Target a specific file server IP
snaffler.exe -i 10.10.50.22 -s -o file_server_hunt.txt

:: Target a specific share directory
snaffler.exe -i \\10.10.50.22\IT_Share$ -s
```

**Targeting Specific Users (The "Hunt" Mode):**
If an attacker is looking for passwords belonging to a specific high-value user (e.g., `svc_sql_admin`), they can use Snaffler to search for strings related to that user across all shares.

## 5. Noise, OPSEC, and Detection

Snaffler is inherently noisy.
1.  **Network Traffic:** It generates massive amounts of SMB traffic (Port 445) as it recursively traverses directory trees across the network. This spike in SMB activity is easily detectable by network monitoring tools (NDR).
2.  **Authentication Logs:** It generates authentication events to every computer it attempts to access.
3.  **Honeypots:** Defenders frequently deploy Canary Tokens or honey-files (e.g., a fake `passwords.xlsx` on a public share). When Snaffler touches this file to inspect it, an alert is triggered immediately in the SOC.

**Mitigation Strategies for Attackers:**
- Restrict scope: Target only specific organizational units (OUs) or known file servers rather than the whole domain.
- Throttle execution (though Snaffler does not have built-in rate limiting, scope reduction serves this purpose).
- Run it during business hours to blend in with legitimate network traffic, rather than at 3 AM.

## 6. Real-World Findings and Impact

What does Snaffler actually find in a typical engagement?
- **IT Scripts:** System administrators often write PowerShell scripts to automate user creation or software deployment. These scripts frequently contain hardcoded Domain Admin credentials used to execute the tasks.
- **Unattend.xml / Sysprep:** Files used for automated Windows image deployment often contain local administrator passwords (sometimes base64 encoded) that are reused across the entire domain.
- **Group Policy Preferences (GPP):** Older AD environments might still have `groups.xml` files in SYSVOL containing AES-encrypted passwords (cpassword) that can be instantly decrypted due to a published static key (MS14-025).
- **KeePass Databases:** Password manager databases stored on shared drives. If the master password is weak, it can be cracked offline.

## 7. Chaining Opportunities
- **[[Lateral Movement via SMB]]:** Credentials found by Snaffler (e.g., local admin passwords) are immediately used for lateral movement using tools like CrackMapExec or PsExec.
- **[[Cracking KeePass Databases]]:** If Snaffler finds `.kdbx` files, the next step is extracting the hash and using Hashcat.
- **[[BloodHound AD Enumeration]]:** Snaffler provides the credentials; BloodHound provides the map. Together, they dictate the path to Domain Admin.
- **[[GPP cpassword Decryption]]:** A specific technique often triggered by Snaffler finding XML files in SYSVOL.

## 8. Related Notes
- [[Active Directory Enumeration]]: Broad overview of AD data gathering techniques.
- [[SMB Share Enumeration]]: Manual techniques for enumerating shares before utilizing automated tools like Snaffler.
- [[Post-Exploitation Pillaging]]: The conceptual phase of an attack where Snaffler is utilized.
