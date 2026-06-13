---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.19 DPAPI"
---

# 19 - DPAPI (Data Protection API)

## Overview

The Windows Data Protection API (DPAPI) is a built-in cryptographic service designed to allow applications to securely store sensitive data. Introduced in Windows 2000, DPAPI provides a simple API (`CryptProtectData` and `CryptUnprotectData`) for developers to encrypt data without needing to manage complex key generation and storage.

For a penetration tester or red teamer, DPAPI is a massive target. It is the underlying mechanism protecting Chrome/Edge saved passwords and cookies, Wi-Fi passwords, saved RDP connection credentials, Outlook profiles, and Task Scheduler credentials. If an attacker can obtain the necessary master keys, they can decrypt all this data, leading to massive lateral movement potential and access to highly sensitive web sessions (Session Hijacking).

## The Architecture of DPAPI

DPAPI operates transparently using the user's login credentials or system secrets to generate a Master Key.

```text
+--------------------------------------------------------------------------+
|                           DPAPI Key Hierarchy                            |
|                                                                          |
|  +-------------------+        +-------------------+                      |
|  | User's Password / |        | System Key (LSA) /|                      |
|  | Domain Backup Key |        | Machine Credentials|                      |
|  +---------+---------+        +---------+---------+                      |
|            |                            |                                |
|            v                            v                                |
|  +---------+---------+        +---------+---------+                      |
|  |  User Master Key  |        | System Master Key |                      |
|  | (Stored in AppData|        | (Stored in System)|                      |
|  +---------+---------+        +---------+---------+                      |
|            |                            |                                |
|            +-------------+--------------+                                |
|                          |                                               |
|                          v                                               |
|               +----------+----------+                                    |
|               | DPAPI Cryptographic |                                    |
|               |     Functions       |                                    |
|               +----------+----------+                                    |
|                          |                                               |
|         +----------------+----------------+                              |
|         |                |                |                              |
|         v                v                v                              |
|  +------------+   +------------+   +------------+                        |
|  | Chrome /   |   | Saved RDP  |   |   Wi-Fi    |                        |
|  | Edge Vault |   | Credentials|   | Passwords  |                        |
|  +------------+   +------------+   +------------+                        |
+--------------------------------------------------------------------------+
```

## Deep Dive: How DPAPI Works

DPAPI encrypts data into structures known as **DPAPI Blobs**. To decrypt a DPAPI Blob, you need the **Master Key** that was used to encrypt it. 

### Master Key Locations
- **User Master Keys**: Stored in `%APPDATA%\Microsoft\Protect\%SID%`
- **System Master Keys**: Stored in `%WINDIR%\System32\Microsoft\Protect\S-1-5-18`

### Unlocking the Master Key
A Master Key itself is encrypted. It can be decrypted using:
1. The user's plaintext password.
2. The user's NTLM hash.
3. The Domain Backup Key (for domain-joined machines, allowing Domain Admins to recover data if a user forgets their password).

If an attacker gains local administrator or SYSTEM access, they can dump the Master Keys directly from the LSASS memory, bypassing the need to know the plaintext password or crack the NTLM hash.

## Exploitation Scenarios

### 1. Extracting DPAPI Blobs and Keys using Mimikatz

Mimikatz is the premier tool for interacting with DPAPI. If you have administrative privileges, you can extract DPAPI keys directly from LSASS memory.

```mimikatz
privilege::debug
token::elevate
dpapi::cache
```
This command retrieves all Master Keys currently cached in memory (since users are logged in).

Once you have the Master Keys, you can start decrypting files. For example, if you find a stored Chrome password database (Login Data), you can decrypt it.

### 2. Decrypting Chrome/Edge Cookies and Passwords

Web browsers like Google Chrome and Microsoft Edge use DPAPI to protect the SQLite databases containing saved passwords and session cookies.

**Location of Chrome Passwords:**
`C:\Users\<User>\AppData\Local\Google\Chrome\User Data\Default\Login Data`

**Location of Chrome State Key (Used to decrypt the DB, protected by DPAPI):**
`C:\Users\<User>\AppData\Local\Google\Chrome\User Data\Local State`

Using tools like **SharpDPAPI** (a C# port of Mimikatz's DPAPI functionality), you can automate the entire process of finding master keys, decrypting the local state key, and extracting plaintext Chrome passwords.

```cmd
:: Using SharpDPAPI to dump browser data
SharpDPAPI.exe triage
SharpDPAPI.exe cookies
```

If you are attacking offline (e.g., you downloaded the files to your machine):
1. Extract the Master Key using the user's NTLM hash.
   ```mimikatz
   dpapi::masterkey /in:"C:\Path\To\MasterKey" /hash:<NTLM_HASH>
   ```
2. Decrypt the `Local State` key using the decrypted Master Key.
3. Decrypt the SQLite database entries.

### 3. Extracting Saved RDP Credentials

When a user checks the "Remember me" box in the Remote Desktop Connection client, the credentials are saved using DPAPI.

The credential files are stored here:
`C:\Users\<User>\AppData\Local\Microsoft\Credentials`

Using Mimikatz:
```mimikatz
dpapi::cred /in:"C:\Users\<User>\AppData\Local\Microsoft\Credentials\<CredID>" /masterkey:<Decrypted_MasterKey_Hex>
```
This will yield the plaintext password for the saved RDP session, allowing for trivial lateral movement to other servers.

### 4. Domain Backup Key Extraction

In Active Directory environments, domain controllers store a **DPAPI Backup Key**. This key is designed to allow enterprise administrators to recover user data. If a Red Teamer compromises a Domain Controller, they can export this Backup Key.

```mimikatz
lsadump::backupkeys /system:DC01.domain.local /export
```
With this `.pvk` (Private Key) file, the attacker can decrypt *any* DPAPI blob for *any* user in the entire domain without needing their passwords or hashes. This is the ultimate "game over" for DPAPI protection.

## Defensive Strategies & Mitigation

DPAPI is a fundamental component of Windows, so it cannot simply be "turned off." However, the blast radius of DPAPI abuse can be minimized.

1. **Protect LSASS**: Use Credential Guard and LSA Protection (RunAsPPL) to prevent attackers from easily dumping cached Master Keys from memory using Mimikatz.
2. **Limit Local Admins**: Since local administrators can dump LSASS and access the DPAPI keys of any logged-in user, strictly limit who has local administrator rights.
3. **Browser Policies**: Implement enterprise policies to prevent users from saving passwords in web browsers. Use dedicated, secure password managers (e.g., 1Password, Bitwarden) that do not rely solely on DPAPI.
4. **Protect Domain Backup Keys**: The Domain Backup Key is only accessible to Domain Admins. Ensure strict tiering (Tier 0 protection) for Domain Controllers.

## Detection and Logging

- **Event ID 4690 (DPAPI Activity)**: Auditing DPAPI activity can be extremely noisy because the OS uses it constantly. It is rarely useful for real-time alerting.
- **Process Access (Event ID 4656)**: Detect tools like Mimikatz or SharpDPAPI acquiring a handle to `lsass.exe` with `PROCESS_VM_READ` rights.
- **File Access Monitoring**: Monitor for unusual processes accessing the `MasterKey` files in `%APPDATA%\Microsoft\Protect\` or the Chrome `Login Data` database.

## Chaining Opportunities

- **[[17 - Stored Credentials Files]]**: If you find a plaintext password in an unattended install file, you can use it to derive the Master Key for that user and decrypt their DPAPI data.
- **[[23 - Abusing SeDebugPrivilege]]**: You need SeDebugPrivilege to inject into LSASS or dump its memory to extract cached DPAPI Master Keys.
- **[[20 - Pass the Hash on Local Admin]]**: Passing the hash can get you code execution, but you can also use that same NTLM hash offline to decrypt DPAPI master keys.

## Related Notes
- [[18 - PowerShell History File]]
- [[28 - Token Impersonation]]
- [[22 - LAPS]]
