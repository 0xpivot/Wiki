---
tags: [macos, privesc, enumeration, pentesting, red-team]
difficulty: beginner
module: "45 - macOS Privilege Escalation"
topic: "45.02 macOS Enumeration and Useful Commands"
---

# macOS Enumeration and Useful Commands

## Introduction
Effective macOS privilege escalation starts with thorough enumeration. macOS shares many tools with Linux (`ps`, `find`, `ls`, `lsof`) but adds a family of Apple-specific utilities — `dscl`, `launchctl`, `system_profiler`, `csrutil`, `spctl`, `codesign`, `sqlite3` (for TCC) — that surface the information you actually need to plan an escalation. This note is a working command reference; deeper exploitation of each finding lives in the dedicated notes.

## Directory Services (`dscl`) — Users, Groups, Admins
macOS does **not** use `/etc/passwd` as the source of truth; it uses **OpenDirectory**, queried via `dscl` (Directory Service Command Line).

```bash
dscl . list /Users | grep -v '^_'          # real users (underscore = service accts)
dscl . -read /Users/<user>                  # full record for a user
dscl . -read /Users/<user> NFSHomeDirectory # home dir
dscl . -read /Groups/admin GroupMembership  # local admins  <-- key target
dscl . list /Groups | grep -v '^_'
dseditgroup -o checkmember -m <user> admin  # is user an admin?
```

Local **admin** group membership (not UID 0) is what grants `sudo`/Authorization rights to install software and manage the system — frequently the real objective.

## System & Security Posture
```bash
sw_vers                          # macOS version + build (map to known CVEs)
uname -a
csrutil status                   # SIP: enabled? (often the deciding factor)
spctl --status                   # Gatekeeper assessments enabled?
fdesetup status                  # FileVault disk encryption
nvram -p                         # NVRAM vars (boot-args may reveal SIP tweaks)
profiles status -type enrollment # MDM enrollment status
pmset -g                         # power/sleep (useful for persistence timing)
```

## Processes, Services & Launch Items
```bash
ps aux
launchctl list                   # loaded jobs for current context
launchctl print system           # detailed system domain (newer syntax)

# The four persistence/auto-start tiers:
ls -la /Library/LaunchDaemons       # root, run at boot
ls -la /Library/LaunchAgents        # root context, per-login
ls -la ~/Library/LaunchAgents       # user context, per-login
ls -la /System/Library/Launch*      # Apple-owned (SIP-protected)
```
Writable plists in any of the first three tiers are an immediate persistence/escalation win — see [[13 - macOS Auto-Start Locations and Persistence]].

## File Hunting
```bash
# SUID/SGID
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null

# World-writable dirs outside user homes (planting ground)
find / -type d -perm -0002 2>/dev/null | grep -v '/Users/'

# Extended attributes (quarantine flag, provenance)
xattr -l <file>
xattr -d com.apple.quarantine <file>   # strip quarantine (Gatekeeper bypass aid)

# Sensitive files
ls -la ~/Library/Keychains/
find / -name '*.plist' -path '*PrivilegedHelperTools*' 2>/dev/null
```

## Code Signing Inspection
```bash
codesign -dvvv /path/to/App.app        # signing identity, team ID, flags
codesign -d --entitlements - /path/to/binary   # entitlements
spctl -a -vv /path/to/App.app          # would Gatekeeper allow it?
otool -L /path/to/binary               # linked dylibs (hijack candidates)
otool -l /path/to/binary | grep -A5 LC_RPATH   # @rpath search paths
```

## ASCII: Enumeration-to-Technique Map
```text
+------------------------+-----------------------------------------------+
| Enumeration finding    | Points you to                                 |
+------------------------+-----------------------------------------------+
| csrutil disabled       | kernel/system persistence (SIP gone)          |
| writable LaunchDaemon  | root persistence -> [[13 ...]]                |
| app w/ Full Disk Access| TCC data theft -> [[04 ...]]                  |
| dangerous entitlement  | injection / TCC -> [[09 ...]]                 |
| weak XPC helper perms  | local root -> [[11 ...]]                      |
| writable dylib in rpath| dylib hijack -> [[10 ...]]                    |
| Electron/Java app      | code injection -> [[12 ...]]                  |
+------------------------+-----------------------------------------------+
```

## Useful One-Liners
```bash
# Dump current user's TCC permissions
sqlite3 "$HOME/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT service,client,auth_value FROM access;" 2>/dev/null

# List apps with Accessibility / Full Disk Access (system TCC, needs root)
sudo sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT service,client,auth_value FROM access;" 2>/dev/null

# Find sudo rights
sudo -l

# Recently used / sensitive doc locations
ls -la ~/Library/Application\ Support/ ~/Library/Preferences/
```

## Defensive Notes
- Treat broad **admin group** membership as privileged; review it like Domain Admins on Windows.
- Monitor reads of `TCC.db` and `*.keychain-db` — legitimate processes rarely open them directly.
- Alert on new/modified plists in the LaunchDaemons/LaunchAgents tiers.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[13 - macOS Auto-Start Locations and Persistence]]
- [[04 - TCC Transparency Consent and Control]]
- [[06 - Code Signing and Entitlements]]
