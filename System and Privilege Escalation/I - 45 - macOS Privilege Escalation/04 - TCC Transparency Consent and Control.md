---
tags: [macos, privesc, tcc, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.04 TCC (Transparency, Consent & Control)"
---

# TCC (Transparency, Consent & Control)

## Introduction
**TCC (Transparency, Consent & Control)** is the macOS subsystem behind every "App X would like to access your Camera/Microphone/Documents/Desktop" prompt. It gates access to **user-private resources** — not by Unix permissions but by a per-user (and system-wide) consent database. Crucially, TCC restricts even **root**: a root shell still cannot read the user's `~/Documents`, address book, or photos unless the requesting process has been granted the relevant TCC permission. For an attacker, defeating TCC is the difference between "I am root" and "I can actually read the data that matters."

## How TCC Works
Consent decisions are stored in SQLite databases:

```text
+---------------------------------------------------------------+
|                         TCC DATABASES                         |
+---------------------------------------------------------------+
| User DB :  ~/Library/Application Support/com.apple.TCC/TCC.db |
|            per-user grants (most app permissions)             |
+---------------------------------------------------------------+
| System DB: /Library/Application Support/com.apple.TCC/TCC.db  |
|            high-power grants: Full Disk Access, Accessibility,|
|            Screen Recording, Input Monitoring                 |
+---------------------------------------------------------------+
| Both DBs are protected by SIP + Full Disk Access:             |
| you cannot simply edit TCC.db to grant yourself rights.       |
+---------------------------------------------------------------+
```

Each row maps a **client** (app, identified by bundle ID + code-signing requirement) to a **service** (`kTCCServiceCamera`, `kTCCServiceSystemPolicyAllFiles` = Full Disk Access, `kTCCServiceAccessibility`, etc.) and an **auth_value** (allowed/denied). The daemon `tccd` enforces decisions; the database is itself guarded so attackers cannot trivially insert their own "allow" row.

```bash
# User DB is readable by that user; system DB needs FDA/root and SIP considerations
sqlite3 "$HOME/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT service, client, auth_value FROM access;"
```

## High-Value TCC Services
| Service | Grants | Why attackers want it |
|---|---|---|
| `kTCCServiceSystemPolicyAllFiles` | **Full Disk Access** | Read *all* user data, other apps' sandboxes, Mail, Messages |
| `kTCCServiceAccessibility` | **Accessibility** | Control other apps (synthesize keystrokes/clicks) — keylogging, automation |
| `kTCCServiceScreenCapture` | **Screen Recording** | Capture screen, including other apps' secrets |
| `kTCCServiceListenEvent` | **Input Monitoring** | Global keyboard capture |
| `kTCCServiceSystemPolicyDesktopFolder` etc. | Desktop/Documents/Downloads | Targeted file theft without full FDA |
| `kTCCServiceAppleEvents` | Automate other apps | Pivot via a more-privileged app's permissions |

## TCC Bypass Techniques
TCC bypasses fall into recurring patterns; almost all are about **acting through a process that already holds the grant, or reaching the data path TCC didn't anticipate.**

### 1. Inheriting an entitled / already-granted app
If a permitted app (e.g. Terminal, an IDE, or an EDR agent) holds Full Disk Access, code running *as* that app inherits the grant. Injecting into such a process (see [[12 - Electron Chromium and Interpreted App Injection]]) or abusing its plugins/scripts gives you its TCC rights without a prompt.

### 2. AppleEvents / automation pivot
With `kTCCServiceAppleEvents` to a target app, you can drive that app (e.g. Finder, Mail) to read or exfiltrate data it can access. Classic chain: get Automation rights to Finder → use Finder to copy protected files.

### 3. Path-based gaps (the data lives somewhere TCC doesn't cover)
TCC protects *specific paths*. Backups, caches, or symlinked copies of protected data sometimes sit in unprotected locations. Historically, reading `~/Library/Application Support/com.apple.TCC/` via a backup, or accessing Messages data through a Time Machine snapshot, sidestepped the live protection.

### 4. Writable TCC.db (requires SIP off or FDA)
If SIP is disabled, or you already have Full Disk Access, you can directly insert an `allow` row:
```bash
sqlite3 "$HOME/Library/Application Support/com.apple.TCC/TCC.db" \
 "INSERT INTO access VALUES('kTCCServiceSystemPolicyAllFiles','com.evil.app',...);"
# Only works because the DB guard (SIP/FDA) is already defeated.
```

### 5. Mounting / `$HOME` redirection
Some TCC checks resolve the user DB relative to `$HOME`. By launching `tccd` (or a target) with a controlled `$HOME` pointing at an attacker-writable TCC.db, an attacker historically presented a fully-permissive consent DB (the basis of several CVEs). Apple has hardened this repeatedly.

### 6. Clicking-without-clicking (synthetic consent)
With Accessibility, an attacker can synthesize the click on a TCC consent dialog — turning one granted permission into many. This is why **Accessibility is among the most dangerous grants**.

```text
   Goal: read ~/Documents (TCC-protected)
   +-----------------------------------------------------------+
   | Option A  -> inject into app with Full Disk Access        |
   | Option B  -> AppleEvents to Finder, have it read the file |
   | Option C  -> data exists in an unprotected backup/cache   |
   | Option D  -> SIP off => edit TCC.db directly              |
   | Option E  -> Accessibility => auto-approve the prompt     |
   +-----------------------------------------------------------+
```

## Why It Matters
TCC is the gatekeeper for the data an engagement usually cares about (messages, mail, browser data, corporate documents). Even with root, you must address TCC to read it. Conversely, an app already holding **Full Disk Access** or **Accessibility** is a privileged pivot — enumerate the system TCC DB early.

## Defensive Notes
- Minimise apps with **Full Disk Access**, **Accessibility**, **Screen Recording**, and **Input Monitoring**; review them via MDM.
- Treat the granting of these as privileged events; alert on new rows in the system TCC DB.
- Keep SIP enabled — it is what protects TCC.db from direct editing.
- Watch for processes opening other apps' sandbox containers or `TCC.db`.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[03 - System Integrity Protection SIP]]
- [[12 - Electron Chromium and Interpreted App Injection]]
- [[09 - Dangerous Entitlements]]
- [[14 - macOS Keychain Attacks]]
