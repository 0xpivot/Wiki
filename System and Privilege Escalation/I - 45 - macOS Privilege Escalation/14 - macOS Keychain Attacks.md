---
tags: [macos, credentials, keychain, privesc, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.14 macOS Keychain Attacks"
---

# macOS Keychain Attacks

## Introduction
The **Keychain** is macOS's central encrypted credential store: passwords, internet/Wi-Fi creds, app secrets, certificates, private keys, and tokens. Each user has a **login keychain** (`~/Library/Keychains/login.keychain-db`), there is a **System keychain** (`/Library/Keychains/System.keychain`, e.g. Wi-Fi/machine certs), and on Apple Silicon/T2 hardware-backed items live in the **Secure Enclave**-protected **Data Protection keychain**. Because the keychain concentrates so much value, it is a primary post-exploitation target — but it is defended by encryption keyed to the user's login password and by per-item **Access Control Lists (ACLs)**.

## How the Keychain Protects Items
```text
+---------------------------------------------------------------+
|                    KEYCHAIN PROTECTION                        |
+---------------------------------------------------------------+
| login.keychain-db encrypted with a key derived from the       |
| user's LOGIN PASSWORD; auto-unlocked at GUI login.            |
|                                                               |
| Each item has an ACL listing which apps may read it without   |
| prompting (e.g. Safari may read Safari's saved passwords).    |
| A different app reading it triggers the "allow access?" prompt|
| requiring the user's password.                                |
+---------------------------------------------------------------+
```
So merely being root is not enough to silently read every secret: you still face the password-derived encryption (if locked) and per-item ACL prompts.

## Attack Techniques
### 1. `security` CLI (when keychain is unlocked)
If you have the user's session and the login keychain is unlocked, the built-in tool dumps items — though cross-app reads still hit ACL prompts:
```bash
security list-keychains
security dump-keychain                 # metadata of items
security find-generic-password -ga "Wi-Fi name"   # specific secret (may prompt)
security unlock-keychain login.keychain-db        # if you know the password
```

### 2. Offline cracking of `login.keychain-db`
Exfiltrate the keychain file and crack the password-derived key offline:
```bash
cp ~/Library/Keychains/login.keychain-db /tmp/k.db   # exfil
# convert + crack with chainbreaker / hashcat (keychain mode) / john
python3 chainbreaker.py --dump-all --password <guess> /tmp/k.db
```
`chainbreaker` can extract all secrets given the password (or the master key). Hashcat has a keychain hash mode for password recovery.

### 3. Master-key extraction from memory
If you have root and the keychain is unlocked, the **decryption key resides in `securityd`/`SecurityAgent` memory**. Tools historically scraped the unlocked master key from process memory, decrypting everything without the password and **without ACL prompts**. Requires the ability to read another process's memory (task port / SIP considerations).

### 4. Riding an ACL-authorized app
Per-item ACLs grant specific apps prompt-free access. Injecting into an app already on an item's ACL (see [[12 - Electron Chromium and Interpreted App Injection]], [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]) lets you read that item silently — the same "inherit the privileged process's rights" pattern used for TCC.

### 5. Reusing the login password
The login keychain password equals the user's login password. Phishing it, capturing it via an Authorization prompt, or recovering it from another source unlocks the entire login keychain trivially.

```text
   Goal: read victim's stored secrets
   +-----------------------------------------------------------+
   | Have login password?  -> security unlock + dump           |
   | Keychain unlocked + root? -> scrape master key from memory|
   | Need one app's secret? -> inject into its ACL-listed app  |
   | Offline only?          -> exfil .keychain-db, crack       |
   +-----------------------------------------------------------+
```

## iCloud Keychain & Tokens
Beyond local items, look for **app session tokens**, **OAuth refresh tokens**, and **browser cookies** (often *not* in the keychain — see [[15 - macOS Sensitive Locations and Credential Theft]]). iCloud Keychain syncs Safari passwords; its items are also protected by the login keychain locally.

## Why It Matters
The keychain is where Wi-Fi keys, saved app/website passwords, certificates, SSH passphrases, and cloud tokens live. Cracking or scraping it converts a single-host compromise into broad credential access and lateral movement.

## Defensive Notes
- Use a **strong, unique login password** (it is the keychain's root secret) and enable FileVault so the file isn't readable from another OS.
- Keep SIP enabled so master-key memory scraping is constrained; prefer hardware-backed (Secure Enclave) items where possible.
- Don't broaden item ACLs; review apps granted keychain access.
- Monitor reads/copies of `*.keychain-db` and processes opening `securityd`'s memory.

## Related Notes
- [[15 - macOS Sensitive Locations and Credential Theft]]
- [[04 - TCC Transparency Consent and Control]]
- [[12 - Electron Chromium and Interpreted App Injection]]
- [[31 - Credential Dumping]]
- [[16 - Stored Credentials Windows Credential Manager]]
