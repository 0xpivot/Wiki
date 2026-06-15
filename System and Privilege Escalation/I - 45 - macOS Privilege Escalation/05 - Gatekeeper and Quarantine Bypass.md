---
tags: [macos, privesc, gatekeeper, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.05 Gatekeeper and Quarantine Bypass"
---

# Gatekeeper and Quarantine Bypass

## Introduction
**Gatekeeper** is the macOS mechanism that decides whether a downloaded application is allowed to run. It enforces that apps are **code-signed** by a known developer and, since macOS 10.15, **notarized** by Apple (scanned and stamped). Gatekeeper works hand-in-hand with the **quarantine** extended attribute (`com.apple.quarantine`), which the OS and "quarantine-aware" apps (browsers, mail clients, messengers) attach to files arriving from the internet. The first time a quarantined app launches, Gatekeeper assesses it and, if unsigned/un-notarized, blocks it with the familiar "cannot be opened because the developer cannot be verified" dialog.

For an attacker delivering a payload, Gatekeeper is the barrier between "user downloaded my app" and "my code ran." Bypasses therefore center on **preventing the quarantine flag from being set, stripping it, or evading the assessment**.

## How Quarantine + Gatekeeper Interact
```text
+---------------------------------------------------------------+
|              DOWNLOAD -> FIRST-LAUNCH FLOW                    |
+---------------------------------------------------------------+
|  Browser downloads file                                       |
|        | sets xattr com.apple.quarantine on the file          |
|        v                                                       |
|  User double-clicks app                                       |
|        | LaunchServices sees quarantine flag                  |
|        v                                                       |
|  Gatekeeper assessment (Syspolicyd):                          |
|     - valid Developer ID signature?                           |
|     - notarized (stapled ticket or online check)?             |
|        |                  |                                    |
|     yes|               no |                                    |
|        v                  v                                    |
|     RUNS            BLOCKED dialog                             |
+---------------------------------------------------------------+
```
Check and inspect:
```bash
xattr -l file.dmg                     # is com.apple.quarantine present?
spctl --status                        # Gatekeeper on?
spctl -a -vv /path/App.app            # would it be allowed? shows reason
codesign -dvvv /path/App.app          # signature / notarization details
stapler validate /path/App.app        # notarization ticket stapled?
```

## Bypass / Evasion Techniques
The historical bug classes all reduce to **the quarantine flag never being set, or Gatekeeper assessing the wrong thing.**

### 1. Archive/container formats that don't propagate quarantine
The OS only quarantines what the *downloading app* writes. If a payload is delivered inside a container whose extraction tool does **not** propagate the quarantine xattr to the extracted files, the inner app launches without assessment. Many CVEs exploited this: certain ZIP layouts, symlinks inside archives, nested archives, ISO/DMG mounting quirks, and unusual bundle structures where LaunchServices failed to find/honor the flag.

### 2. File types not treated as quarantine-aware
Quarantine relies on the writing app cooperating. Payloads delivered via channels that don't set the flag (some scripting paths, certain rsync/scp transfers, AFP/SMB mounts, or apps that simply forget to call the API) arrive *un-quarantined* and run freely.

### 3. Stripping the attribute (post-access)
With local code execution you can remove the flag:
```bash
xattr -d -r com.apple.quarantine /path/App.app
# or prevent it system-wide for a process by clearing the inherited xattr
```

### 4. Bundle-structure confusion
Gatekeeper assessed the top-level bundle, but the *executed* component lived elsewhere (e.g. a symlinked binary, an app whose `Info.plist` pointed the main executable outside the assessed path). The assessment passed on a benign component while a different, unsigned component actually ran — the core of several "Gatekeeper bypass" CVEs.

### 5. Living off already-trusted apps
Instead of shipping a new app, abuse an installed, notarized app's scripting/plugin surface (Office macros, Electron app resources, interpreter app injection — see [[12 - Electron Chromium and Interpreted App Injection]]). The trusted app already passed Gatekeeper; your code rides inside it.

## Gatekeeper vs. the Rest of the Stack
Gatekeeper is a **first-launch trust check**, not a runtime sandbox. Passing Gatekeeper does **not** grant TCC permissions or escape the sandbox — those are separate layers. Conversely, bypassing Gatekeeper only gets your code *running*; you still face [[04 - TCC Transparency Consent and Control]] for data and [[08 - App Sandbox Escapes]] if you start sandboxed.

## Why It Matters
- **Initial execution / phishing payloads:** the practical question in a social-engineering test is whether your delivered app runs without the scary dialog.
- **Reporting:** out-of-date macOS vulnerable to a known quarantine-propagation CVE is a deliverable finding.

## Defensive Notes
- Keep macOS patched — Gatekeeper bypasses are a steady CVE stream tied to archive/bundle parsing.
- Do not advise users to `xattr -d com.apple.quarantine` arbitrary downloads.
- Use MDM to enforce Gatekeeper (`spctl` enabled) and block unsigned apps.
- Endpoint tooling should alert on quarantine-flag removal and on apps launching from unusual paths.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[06 - Code Signing and Entitlements]]
- [[08 - App Sandbox Escapes]]
- [[16 - macOS Installers and Package Abuse]]
