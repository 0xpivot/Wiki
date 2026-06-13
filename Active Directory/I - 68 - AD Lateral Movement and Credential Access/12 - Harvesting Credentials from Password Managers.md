---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.12 Harvesting Credentials from Password Managers"
---
# 12 - Harvesting Credentials from Password Managers

## 1. Introduction and Context

As security awareness grows, organizations increasingly adopt password managers (e.g., KeePass, 1Password, LastPass, Bitwarden, Dashlane) to store and manage complex passwords. While this improves overall password hygiene and mitigates password reuse across different infrastructure nodes, it introduces a massive single point of failure: the password manager vault itself.

During post-exploitation, identifying and extracting credentials from password managers on a compromised host provides an attacker with a treasure trove of information. A compromised password vault often yields high-privilege domain accounts, SSH keys, VPN credentials, and sensitive web application access—often containing multi-factor authentication (MFA) backup codes or TOTP seeds as well.

Harvesting from password managers typically falls into three categories:
1. **Extracting the Vault File:** Stealing the encrypted database file for offline brute-forcing or cracking.
2. **Extracting the Master Password:** Capturing the master password via keylogging or memory extraction, allowing direct access to the exfiltrated vault.
3. **Memory Scraping:** Extracting the decrypted vault or individual passwords directly from the memory space of the running password manager application when it is in an "unlocked" state.

## 2. Targeting Specific Password Managers

### 2.1 KeePass

KeePass is widely used in enterprise environments because it operates entirely offline, storing passwords in local `.kdbx` files. This makes it a prime target for attackers, as no cloud synchronization is required to access the data.

#### Identifying KeePass Files

KeePass databases usually have the `.kdb` (KeePass 1.x) or `.kdbx` (KeePass 2.x) extension.

**Search Command:**
```cmd
dir /s /b C:\*.kdbx
```

Attackers also look for the KeePass configuration file (`KeePass.config.xml` or `KeePass.ini`) to identify the last used database, the path to any key files `.key` used for dual-factor decryption, and whether specific memory protection features are enabled.

#### Extraction Techniques

1. **Offline Brute-forcing:**
   Once the `.kdbx` file (and optionally the `.key` file) is exfiltrated, attackers use `hashcat` or `john` to crack the master password offline without generating network traffic on the victim's domain.
   First, extract the hash using `keepass2john`:
   ```bash
   keepass2john database.kdbx > keepass.hash
   ```
   Then crack with Hashcat (Mode 13400 for KeePass 1.x/2.x):
   ```bash
   hashcat -m 13400 keepass.hash rockyou.txt -r rules/best64.rule
   ```

2. **Memory Extraction (KeeThief / KeePassCVEs):**
   Historically, KeePass left the master password or decrypted entries in plaintext within its process memory (`KeePass.exe`). Tools like `KeeThief` allow an attacker to dump the master password from memory if the database is currently unlocked or was recently unlocked.
   Additionally, **CVE-2023-32784** allowed attackers to extract the master password from KeePass memory dumps because of how the managed .NET string class handled text box inputs, leaving a trail of characters in memory.

### 2.2 Browser-Based Password Managers (Chrome, Firefox, Edge)

Modern web browsers have built-in password managers that encrypt saved passwords using the host OS's native data protection APIs (DPAPI on Windows). Many users rely on these for both corporate and personal credentials.

#### Extracting Chrome/Edge Passwords

Chromium-based browsers encrypt credentials using an AES key, which is itself encrypted using DPAPI and stored in a `Local State` file. The encrypted passwords are kept in a SQLite database called `Login Data`.

**Locations:**
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data`
- Local State: `%LOCALAPPDATA%\Google\Chrome\User Data\Local State`

**Extraction Process Pipeline:**
1. Read the encrypted AES key from the `Local State` file (stored as a base64 encoded JSON value).
2. Decrypt the AES key using DPAPI (requires the user's context, or SYSTEM privileges with DPAPI backup keys).
3. Connect to the `Login Data` SQLite database and extract the encrypted `password_value` blobs from the `logins` table.
4. Decrypt the individual blobs using the decrypted AES key.

Tools like `Seatbelt`, `SharpChrome`, and `Mimikatz` (`dpapi::chrome`) automate this entire process seamlessly.

### 2.3 Cloud-Synced Password Managers (1Password, LastPass)

These managers often store cached, encrypted vaults locally to allow offline access. Extracting data usually involves accessing local SQLite databases and dumping the memory of the application or browser extension to find the master key or session tokens. If the vault is unlocked, tools can scrape the memory for the master vault key, allowing full decryption of the local cache.

## 3. Visualizing the Password Manager Attack Flow

```text
+------------------------------------------------------------------+
|                Password Manager Harvesting Workflow                |
+------------------------------------------------------------------+

[Compromised System (User Context)]
         |
         +--> 1. Enumerate Installed Managers (Registry, AppData)
         |
         +--> 2. Locate Vaults & Configs (*.kdbx, Login Data)
         |
         +--> 3. Is the vault currently locked or unlocked?
                 |
        [Locked] |                               [Unlocked]
         v                                         v
+-----------------------+              +---------------------------+
| Offline Attack Path   |              | Memory Extraction Path    |
+-----------------------+              +---------------------------+
| A. Exfiltrate vault   |              | A. Dump process memory    |
| B. Exfiltrate keyfile |              |    (e.g., procdump)       |
| C. Run keepass2john   |              | B. Parse memory for keys  |
| D. Hashcat cracking   |              |    or plaintext passwords |
+-----------------------+              +---------------------------+
         |                                         |
         +-------------------+---------------------+
                             |
                             v
                  +---------------------+
                  |   Extracted Clear   |
                  |     Credentials     |
                  +---------------------+
                             |
                             v
                  +---------------------+
                  | Lateral Movement &  |
                  | Privilege Escalation|
                  +---------------------+
```

## 4. Advanced Memory Scraping Concepts

When a password manager is unlocked, the decrypted master key must reside in RAM to facilitate decrypting individual entries on-the-fly. Attackers leverage Windows APIs like `ReadProcessMemory` or use tools like `procdump` to create a full minidump of the password manager process. 

### Generating a Minidump via Sysinternals

```cmd
procdump.exe -accepteula -ma KeePass.exe keepass_dump.dmp
```
Once the `.dmp` file is exfiltrated, the attacker can use string analysis, YARA rules, or custom parsers (like `pypykatz` or specific KeePass dump analyzers) to find the key structures. 

In the case of DPAPI (Browser passwords), the attacker leverages the `CryptUnprotectData` API by injecting code into a process running under the user's context, forcing the OS to decrypt the secrets on the attacker's behalf using the user's master key cached by the LSA.

## 5. Defensive Evasion Considerations

Dumping memory of processes like `KeePass.exe` or `chrome.exe` is highly scrutinized by modern EDR solutions. Cross-process memory access (e.g., using `MiniDumpWriteDump` API) will frequently trigger alerts.

**Attacker Evasion Tactics:**
- **BYOVD (Bring Your Own Vulnerable Driver):** Attackers load a signed but vulnerable driver to read memory from the kernel layer, completely bypassing user-mode EDR hooks.
- **Handle Duplication:** Duplicating existing handles to the target process instead of opening new ones (`DuplicateHandle`) to fly under the radar of `OpenProcess` telemetry.
- **Offline DPAPI Decryption:** Exfiltrating the raw encrypted files and stealing the DPAPI master keys via domain controller compromise (DPAPI backup keys) to decrypt the files entirely offline without touching the user's running processes or triggering DPAPI access alerts.

## 6. Mitigation and Detection Strategies

### 6.1 Defenses
- **Enforce Complex Master Passwords:** Mitigates the threat of offline brute-forcing of `.kdbx` files. A >20 character passphrase renders offline cracking practically impossible.
- **Implement 2FA on Vaults:** Require a hardware token (YubiKey) to unlock the password manager, neutralizing the theft of the `.kdbx` file alone.
- **Restrict Local Admin Rights:** Prevent attackers from using `procdump` or DPAPI system-level extraction techniques by denying them the `SeDebugPrivilege`.
- **Disable Browser Password Managers:** Use Active Directory Group Policy to explicitly forbid users from saving passwords in Chrome/Edge, forcing them to use an approved, hardened enterprise password manager.
- **Enable Memory Protection:** In KeePass, enforce settings that protect memory (e.g., using Windows DPAPI to encrypt memory blocks when the UI is minimized).

### 6.2 Detections
- **Process Access Events:** Event ID 10 (Sysmon) monitoring for anomalous processes requesting `PROCESS_VM_READ` against `KeePass.exe`, `chrome.exe`, or `1Password.exe`.
- **File Access Analytics:** Alerting on processes other than the password manager itself accessing `.kdbx` files or the Chrome `Login Data` file.
- **Command Line Signatures:** Look for instances of `procdump`, `taskmgr.exe` (creating dumps), or PowerShell scripts attempting to read memory.

## 7. Splunk / SIEM Search Query Example

To detect `procdump` targeting sensitive processes:

```spl
index=windows sourcetype="WinEventLog:Sysmon" EventCode=1 
| search CommandLine="*procdump*" AND (CommandLine="*keepass*" OR CommandLine="*chrome*" OR CommandLine="*lsass*")
| table _time, host, user, process_name, CommandLine, parent_process_name
```

## Real-World Attack Scenario

During a red team engagement at a financial institution, the team compromised an endpoint belonging to a senior IT support engineer via a spear-phishing payload. After establishing a C2 beacon running in the context of the user, the team observed that the endpoint was heavily monitored by an EDR, precluding the use of standard credential dumping tools like Mimikatz or dropping custom binaries to disk.

However, during basic host enumeration, the team discovered that the user actively used KeePass to manage administrative credentials for multiple jump servers. Using native Windows commands, the attacker confirmed the location of the KeePass database:
```cmd
dir /s /b C:\Users\support_admin\Documents\*.kdbx
```
This returned `C:\Users\support_admin\Documents\IT_Jump_Hosts_Vault.kdbx`. Checking the process list with `tasklist`, the attacker noticed that `KeePass.exe` was currently running. This meant the vault was likely unlocked and the decrypted master key was residing in the process memory.

To extract the key without alerting the EDR with cross-process memory reads from the C2 beacon, the attacker leveraged `procdump`, a legitimate Sysinternals tool that is often whitelisted by default, to create a minidump of the KeePass process:
```cmd
procdump.exe -accepteula -ma KeePass.exe C:\Users\support_admin\AppData\Local\Temp\keepass_dump.dmp
```
The command successfully wrote the full memory dump to disk. The attacker then compressed both the `.kdbx` file and the `.dmp` file and exfiltrated them via the C2 channel. 

Back on the attacker's offline infrastructure, they used a specialized KeePass memory extraction tool (such as `pypykatz` or `keepass-password-dumper`) against the memory dump:
```bash
python3 keepass_dumper.py keepass_dump.dmp
```
The tool successfully carved the master password from memory: `Super$ecure1TAdminVault2024!`. Using this password, the attacker opened the exfiltrated `IT_Jump_Hosts_Vault.kdbx` locally. The vault contained the highly privileged credentials for a Domain Admin service account used for patching. The attacker then used these credentials to establish a WinRM session to a Domain Controller, effectively taking full control of the Active Directory environment.

## 8. Chaining Opportunities

- **[[11 - Extracting Credentials from Configuration Files]]:** Attackers might find the password manager's master password stored in a configuration script or unattended file.
- **[[15 - Token Impersonation and Stealing Incognito]]:** Attackers may need to impersonate the specific user who owns the password vault to successfully interact with the DPAPI subsystem.
- **[[06 - Keylogging and Clipboard Sniffing]]:** If the vault is locked and cannot be cracked offline, attackers may deploy a keylogger or clipboard sniffer to capture the master password the next time the user types it.
- **[[07 - DPAPI Extraction and Abuse]]:** Deep-dive into extracting DPAPI backup keys from the Domain Controller to decrypt browser vaults offline.

## 9. Related Notes

- [[02 - Local Privilege Escalation Essentials]]
- [[10 - Memory Dumping Techniques]]
- [[05 - Windows Post-Exploitation Enumeration]]
