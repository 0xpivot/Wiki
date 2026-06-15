---
tags: [iot, pentesting, kiosk, physical, vapt]
difficulty: intermediate
module: "49 - IoT Security"
topic: "49.22 Escaping Kiosk and Locked-Down GUI Applications"
---

# Escaping Kiosk and Locked-Down GUI Applications

## Introduction
**Kiosks** — interactive terminals running a single locked-down GUI application full-screen (ATMs, ticket machines, check-in terminals, museum displays, digital signage, point-of-sale, info booths) — are designed to expose only one app and hide the underlying OS. **Kiosk escape** is breaking out of that restricted GUI to reach the operating system underneath, where normal post-exploitation applies. Because kiosks are physically accessible to the public and often run privileged software on a full OS, escaping them is a high-value physical/embedded attack — the GUI analogue of restricted-shell escape ([[41 - Restricted Shell Escape]]).

## How Kiosks Try to Lock Down
```text
+---------------------------------------------------------------+
|                   KIOSK LOCKDOWN MEASURES                    |
+---------------------------------------------------------------+
|  - single full-screen app, no taskbar/desktop                 |
|  - disabled keyboard shortcuts / hotkeys                      |
|  - hidden or disabled file dialogs, address bars, menus       |
|  - restricted browser (for web kiosks)                        |
|  - no visible terminal/explorer                               |
+---------------------------------------------------------------+
|  Escape principle: find ANY feature that reaches the OS —      |
|  a dialog, a link, a helper, a shortcut — and pivot through it|
+---------------------------------------------------------------+
```

## Escape Techniques
The recurring idea: **reach a standard OS dialog or external handler from inside the app**, then navigate to a shell/file manager.
```text
+---------------------------------------------------------------+
|                   KIOSK ESCAPE VECTORS                       |
+---------------------------------------------------------------+
| File dialogs    any Open/Save/Print/Upload/Browse dialog ->   |
|                 type a path (cmd.exe, explorer.exe, /bin/sh), |
|                 right-click -> "Open"/"Run", browse the FS    |
| Hyperlinks      links opening file:// , a new window, or an   |
|                 external app -> escape the sandboxed view     |
| Keyboard combos try ALL shortcuts: Ctrl+O/P/N/S/T, Win/Super, |
|                 Alt+Tab/F4, Ctrl+Alt+Del, Ctrl+Esc, F1 (help  |
|                 windows often spawn a browser/explorer)       |
| Help / about    Help -> opens browser/PDF viewer -> pivot     |
| Right-click     context menus -> "open with", "view source",  |
|                 "save as" -> file dialog                      |
| Protocol/URI    web kiosk: file://, smb://, jar:, custom URI  |
|                 handlers -> external apps                     |
| Crash/error     crash the app to drop to desktop/error dialog |
|                 with OS access                                |
| Accessibility   on-screen keyboard / magnifier / narrator ->  |
|                 some launch with extra privileges             |
| Print dialog    "Print to file"/printer properties -> browse  |
|                 FS / spawn helper                             |
+---------------------------------------------------------------+
```
For **web-based kiosks**, also try the URL bar (if any), `view-source:`, downloading then opening a file, JavaScript prompts, and the browser's built-in pages (`chrome://`, `about:`) to reach settings/file access.

## Post-Escape
Once you reach a file dialog or browser, navigate to and launch a **command interpreter** (`cmd.exe`, `powershell`, `explorer.exe`, `/bin/bash`, a file manager). From there it's standard local enumeration and privilege escalation — kiosk software frequently runs as **admin/SYSTEM or an over-privileged user**, so escape may directly yield high privileges. Then apply the OS privesc modules (I-43/I-44).

## Why It Matters
Kiosks sit in public, run a full OS, and often hold network access to internal systems plus privileged local software — yet their only security is "the user can only see one app." A single reachable dialog, link, or hotkey breaks that, exposing the OS to a physically-present attacker. ATMs, POS, and check-in terminals are real, high-impact targets, and kiosk escape is a staple of physical red-team work.

## Defensive Notes
- Use a **purpose-built kiosk mode/lockdown** (Windows Assigned Access/Shell Launcher, kiosk browser with no file access, Linux kiosk session) — not just a maximized app.
- Disable file dialogs, printing-to-file, external protocol handlers, right-click, developer tools, and **all** unneeded keyboard shortcuts; block `file://`/custom URIs; strip help/about links that open browsers.
- Run the kiosk app as a **least-privilege** user (never admin/SYSTEM); apply application allow-listing so even on escape no shell/explorer runs; segment the network so a kiosk can't reach internal systems.
- Watchdog to restart the app and detect/escape attempts; physically secure ports ([[21 - Physical Attacks and Hardware Implants]]).

## Related Notes
- [[21 - Physical Attacks and Hardware Implants]]
- [[41 - Restricted Shell Escape]]
- [[10 - Command Injection in IoT Web Interfaces]]
- [[01 - Windows PrivEsc Methodology Overview]]
