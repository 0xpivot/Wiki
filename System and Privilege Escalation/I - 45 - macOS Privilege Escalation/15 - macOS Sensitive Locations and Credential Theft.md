---
tags: [macos, credentials, looting, privesc, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.15 macOS Sensitive Locations and Credential Theft"
---

# macOS Sensitive Locations and Credential Theft

## Introduction
Beyond the Keychain ([[14 - macOS Keychain Attacks]]), a macOS host scatters credentials, tokens, and sensitive data across well-known filesystem locations. Post-exploitation looting is largely about knowing **where** to look. Note the interplay with [[04 - TCC Transparency Consent and Control]]: many of the richest targets (Messages, Mail, Safari, photos) sit under TCC-protected paths, so reading them may require Full Disk Access or an injection into a permitted app — but plenty of high-value secrets (SSH keys, cloud CLI tokens, dotfiles) are **not** TCC-protected and are readable as the user immediately.

## High-Value Locations
```text
+---------------------------------------------------------------+
|         NON-TCC (read as the user, no prompt)                 |
+---------------------------------------------------------------+
| ~/.ssh/                 private keys, known_hosts, config     |
| ~/.aws/credentials      AWS access keys                       |
| ~/.config/gcloud/       GCP tokens                            |
| ~/.azure/               Azure tokens                          |
| ~/.kube/config          Kubernetes creds                      |
| ~/.docker/config.json   registry auth                         |
| ~/.netrc ~/.git-credentials   plaintext creds                 |
| ~/.zsh_history ~/.bash_history   commands w/ secrets          |
| ~/Library/Application Support/<app>/   tokens, session blobs  |
| environment / launchctl setenv   secrets in env               |
+---------------------------------------------------------------+
|         TCC-PROTECTED (need FDA / permitted app)              |
+---------------------------------------------------------------+
| ~/Library/Messages/chat.db        iMessage history            |
| ~/Library/Mail/                   Mail store                  |
| ~/Library/Safari/                 history, downloads          |
| ~/Library/Application Support/AddressBook/   contacts         |
| ~/Pictures/Photos Library.photoslibrary/     photos           |
| ~/Library/Application Support/com.apple.TCC/  the TCC DB       |
+---------------------------------------------------------------+
```

## Browser Credentials & Cookies
Browser secrets are usually **not** in the Keychain wholesale and are prime targets:
```bash
# Chrome/Edge/Brave: Login Data (SQLite) + cookies, encrypted with a key
~/Library/Application\ Support/Google/Chrome/Default/Login\ Data
~/Library/Application\ Support/Google/Chrome/Default/Cookies
# The encryption key ("Chrome Safe Storage") is stored in the Keychain ->
# read it (ACL-permitted to Chrome) then AES-decrypt the cookie/password blobs
security find-generic-password -wa "Chrome Safe Storage"
```
Stealing live **cookies/session tokens** sidesteps passwords and MFA entirely — often the highest-value loot for cloud/SaaS access.

## Notes, Memory, and Dumps
- **Notes/Stickies** caches, **Spotlight** metadata, **`~/Library/Caches/`** can hold sensitive fragments.
- **Memory dumping** (`macos-memory-dumping`): with sufficient privilege, dumping process memory can recover plaintext secrets, the keychain master key, or tokens.
- **Crash logs** (`~/Library/Logs/DiagnosticReports/`) sometimes leak arguments/env containing secrets.

## Configuration Files & Provisioning
- **Configuration profiles** (`/Library/Managed Preferences/`, installed `.mobileconfig`) may contain Wi-Fi/VPN/802.1X creds and certs.
- **Wi-Fi**: `security find-generic-password -wa "<SSID>"` (System keychain) or via `networksetup`.
- **`sudo` / admin hints**: `~/.zsh_history` frequently contains passwords typed after `echo`/`--password`.

## Looting Workflow
```text
   1. Grab non-TCC creds first (ssh, cloud CLIs, dotfiles, history) - instant
   2. Pull browser cookies/tokens (decrypt via Chrome Safe Storage key)
   3. If FDA/permitted-app: dump Messages/Mail/Safari/Contacts
   4. Keychain extraction (see note 14)
   5. Memory dump for in-RAM secrets / master keys
   6. Profiles & Wi-Fi for network pivot creds
```

## Why It Matters
A single Mac often holds the keys to a user's entire cloud and SaaS footprint (AWS/GCP/Azure CLI tokens, kube configs, Git creds, live session cookies). These convert a host foothold into **organization-wide** access and lateral movement, frequently without ever needing root.

## Defensive Notes
- Store cloud creds in short-lived/SSO form (e.g. `aws sso`, not long-lived `~/.aws/credentials`); rotate aggressively.
- Enable FileVault; restrict Full Disk Access grants (gateway to Messages/Mail/Safari).
- Use hardware-bound session tokens where supported; monitor reads of `Login Data`, `Cookies`, `~/.aws`, `~/.ssh`.
- Discourage secrets in shell history (`HISTIGNORE`, space-prefix); scan endpoints for plaintext credential files.

## Related Notes
- [[14 - macOS Keychain Attacks]]
- [[04 - TCC Transparency Consent and Control]]
- [[02 - macOS Enumeration and Useful Commands]]
- [[17 - Stored Credentials Files]]
- [[16 - Password in Config Files History Env Vars]]
