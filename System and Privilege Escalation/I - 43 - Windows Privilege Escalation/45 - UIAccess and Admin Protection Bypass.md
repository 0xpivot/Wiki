---
tags: [windows, privesc, uac, uiaccess, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.45 UIAccess and Admin Protection Bypass"
---

# UIAccess and Admin Protection Bypass

## Introduction
`UIAccess` is a special integrity/accessibility capability that lets a program **drive the user interface of higher-integrity windows** — it exists so assistive tools (screen readers, on-screen keyboards) can interact with elevated and secure UI. Because it crosses the normal UI isolation boundary (UIPI, User Interface Privilege Isolation), `UIAccess` applications are a recurring **UAC-bypass and integrity-escalation** vector. Separately, Windows 11's newer **Administrator Protection** (an evolution of UAC that runs admins as a separate, isolated admin context) introduces fresh bypass research. This note covers both, complementing the UAC techniques in [[12 - UAC Bypass Techniques]].

## UIPI and Why UIAccess Is Special
Normally **UIPI** blocks a lower-integrity process from sending window messages to a higher-integrity process (so a Medium-integrity app can't inject keystrokes into a High-integrity window). A process flagged `uiAccess="true"` in its manifest is **exempt from UIPI** and may interact with higher-integrity windows.

```text
+---------------------------------------------------------------+
|                    UIACCESS PRIVILEGE                        |
+---------------------------------------------------------------+
|  Normal Medium-IL app  --X-->  High-IL window  (UIPI blocks)  |
|                                                               |
|  UIAccess app (Medium-IL but uiAccess=true)                   |
|        ---- allowed ---->  drive High-IL / elevated UI        |
|        - can send input, read window content, automate dialogs|
+---------------------------------------------------------------+
| Requirements to GET UIAccess:                                 |
|   1. manifest uiAccess="true"                                 |
|   2. binary is Authenticode-signed                            |
|   3. binary runs from a "secure location" (Program Files /    |
|      System32) — these are normally non-writable by users     |
+---------------------------------------------------------------+
```

## Bypass Patterns
### 1. UIAccess UAC bypass (auto-elevation assist)
A UIAccess app can **automate the UAC consent dialog or an auto-elevating admin app's UI** — effectively clicking "Yes" or driving an elevated tool's controls to perform privileged actions on the attacker's behalf. Combined with an auto-elevating Windows binary, a UIAccess helper can escalate from Medium to High integrity without user interaction. This is conceptually similar to the macOS "Accessibility synthesizes the consent click" idea.

### 2. Defeating the "secure location" requirement
The protections above assume users cannot write to `Program Files`/`System32`. If an attacker has a **write primitive** to such a location (e.g. via [[41 - Abusing SeManageVolumePrivilege]] or a writable installer dir), they can place a UIAccess-manifested, signed binary in a secure path and obtain UIAccess legitimately. Some bypasses also abuse the relaxed checks for IL/secure-path under specific conditions.

### 3. Hijacking an existing UIAccess application
Rather than ship your own, hijack a DLL or input flow of an installed UIAccess accessibility tool ([[06 - DLL Hijacking]]); your code then inherits its UIPI exemption to drive elevated UI.

### 4. Administrator Protection bypass (Windows 11)
Administrator Protection runs an admin's elevated work in a **separate, more isolated admin user context** (a stronger split-token model) and changes how elevation/consent works. As it rolls out, research targets gaps in the new consent/isolation flow — e.g. tricking the elevation broker, abusing auto-elevated paths that haven't been re-hardened, or token/handle confusion across the isolated contexts ([[43 - Leaked Handle Exploitation]]). Treat it as "UAC bypass research, new generation": the same categories (auto-elevation, mock trusted directories, COM elevation moniker) re-examined against the new model.

## Enumeration
```cmd
:: Find UIAccess binaries (manifest uiAccess=true), signed, in secure paths
:: (inspect manifests / use tooling like sigcheck + manifest dump)
whoami /groups        :: current integrity level (Medium vs High)
```

## Why It Matters in an Engagement
UIAccess is an under-appreciated bridge across the UI isolation boundary that underpins UAC's UI-side defenses. Where direct UAC bypasses are patched, driving elevated UI via a UIAccess app (or one you can hijack) remains effective. On Windows 11 with Administrator Protection, the bypass surface is actively shifting — worth checking the target build.

## Detection and Mitigation
- Set UAC to **"Always notify"** and enable **secure desktop** for consent prompts (UIAccess apps cannot interact with the secure desktop unless explicitly allowed); review the `EnableUIADesktopToggle` / secure-desktop policy.
- Keep `Program Files`/`System32` non-writable; remediate any write primitive ([[41 - Abusing SeManageVolumePrivilege]]).
- Allow-list which signed UIAccess apps may run; monitor for new uiAccess binaries in secure locations.
- Apply the latest builds — Administrator Protection bypasses are patched as found.

## Chaining Opportunities
- A System32 write primitive ([[41 - Abusing SeManageVolumePrivilege]]) → plant a UIAccess binary → bypass.
- Pairs with [[12 - UAC Bypass Techniques]] and auto-elevation abuse.

## Related Notes
- [[12 - UAC Bypass Techniques]]
- [[41 - Abusing SeManageVolumePrivilege]]
- [[06 - DLL Hijacking]]
- [[43 - Leaked Handle Exploitation]]
