---
tags: [macos, persistence, privesc, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.13 macOS Auto-Start Locations and Persistence"
---

# macOS Auto-Start Locations and Persistence

## Introduction
Persistence on macOS means getting your code to run automatically at boot, login, or on some trigger — and, ideally, with elevated privileges. macOS offers many auto-start mechanisms; the most important is **launchd** (the init/service manager), but there are numerous others (login items, cron, at-jobs, profiles, dylib insertions, app-specific plugins). Some run as **root** (system daemons), others as the **user** (agents). A writable entry in a root-context location is simultaneously *persistence* and *privilege escalation*.

## launchd: Daemons vs Agents
`launchd` loads property-list (`.plist`) job definitions from well-known directories:

```text
+---------------------------------------------------------------+
|                  LAUNCHD AUTO-START TIERS                     |
+---------------------------------------------------------------+
| /Library/LaunchDaemons         | root  | at boot (no user)    |
| /Library/LaunchAgents          | user  | per GUI login (root- |
|                                |       |  installed, runs as  |
|                                |       |  the logged-in user) |
| ~/Library/LaunchAgents         | user  | per that user's login|
| /System/Library/Launch*        | Apple | SIP-protected        |
+---------------------------------------------------------------+
```
A minimal persistent agent:
```xml
<!-- ~/Library/LaunchAgents/com.example.persist.plist -->
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.persist</string>
  <key>ProgramArguments</key>
    <array><string>/bin/zsh</string><string>-c</string>
           <string>/tmp/payload.sh</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>          <!-- restart if killed -->
  <key>StartInterval</key><integer>300</integer> <!-- or every 5 min -->
</dict></plist>
```
```bash
launchctl load ~/Library/LaunchAgents/com.example.persist.plist   # legacy
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.persist.plist  # modern
```
**Escalation angle:** if `/Library/LaunchDaemons` or a referenced program is **writable** by your user, you can install/modify a job that runs as **root** at next boot — a clean privesc. Always check:
```bash
ls -la /Library/LaunchDaemons /Library/LaunchAgents
find /Library/LaunchDaemons -type f -writable 2>/dev/null
# also check the ProgramArguments targets are not user-writable
```

## Other Auto-Start / Persistence Locations
| Mechanism | Where | Context |
|---|---|---|
| **Login Items** | per-user (System Settings) / `SMLoginItemSetEnabled` | user, at login |
| **Login/Logout Hooks** | `com.apple.loginwindow` `LoginHook` | can be root |
| **cron** | `crontab -l`, `/usr/lib/cron/tabs/` | user/root |
| **at jobs** | `at`, `/var/at/` | scheduled |
| **Periodic** | `/etc/periodic/{daily,weekly,monthly}`, `/etc/periodic.conf` | root |
| **Configuration Profiles** | `.mobileconfig` (MDM) | managed, powerful |
| **emond** (legacy) | `/etc/emond.d/` | root (removed in newer macOS) |
| **Dock/Spotlight importers, QuickLook generators** | per type | user, on-demand |
| **Authorization plugins / SecurityAgent** | `/Library/Security/SecurityAgentPlugins` | at login window |
| **dylib insertion into an auto-started app** | bundle / rpath | inherits app context |

The HackTricks "auto-start locations" reference catalogs dozens; the high-value ones for an operator are LaunchDaemons (root persistence/privesc), LaunchAgents (user persistence), Login Items (least suspicious), and **dylib hijack of an already-autostarted signed app** (stealthiest — see [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]).

## App-Specific Persistence
Many apps auto-load plugins/extensions that double as persistence:
- **Electron** `app.asar` patching ([[12 - Electron Chromium and Interpreted App Injection]]) — runs every app launch.
- **Browser extensions** loaded on every browser start.
- **Office / scriptable app** startup scripts.
- **QuickLook generators**, **Spotlight importers**, **Automator/Preference panes/NSServices**, **plugins** for installed apps.

## Stealth & Privilege Trade-offs
```text
   Loud + simple ........... LaunchDaemon plist with obvious name
   Quieter ................. LaunchAgent with Apple-looking label
   Stealthy ................ dylib hijack of a signed auto-start app
                              (no new binary, runs as trusted app)
   Most powerful ........... configuration profile via MDM (fleet-wide)
```
On modern macOS, **`launchd` items are surfaced to the user** ("Background Items Added" notifications, Login Items list), so dylib hijacks of existing trusted apps and profile-based persistence are favored for stealth.

## Why It Matters
- A **writable root-context launch item** is privesc + persistence in one.
- Persistence selection is an exfil/stealth decision: match the mechanism's noise to the engagement's stealth requirements.

## Defensive Notes
- Audit `/Library/LaunchDaemons|LaunchAgents`, login items, and `/Library/Security/SecurityAgentPlugins` for unsigned/unknown entries and weak permissions; the program targets must not be user-writable.
- Watch macOS "Background Items" notifications; ship MDM rules baselining allowed launch items.
- Monitor creation/modification of plists and app `app.asar`/plugin directories; verify code signatures of auto-started binaries.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]
- [[12 - Electron Chromium and Interpreted App Injection]]
- [[17 - macOS MDM Abuse]]
- [[14 - Startup Applications Abuse]]
