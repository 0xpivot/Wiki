---
tags: [mobile, android, ios, ui-redress, pentesting]
difficulty: intermediate
module: "50 - Mobile Application Security"
topic: "50.17 UI Redress, Tapjacking, Overlays and Pasteboard Leakage"
---

# UI Redress, Tapjacking, Overlays and Pasteboard Leakage

## Introduction
Not all mobile attacks target data or code — some target the **user's perception of the UI**. A malicious app can draw over, around, or in place of a legitimate app to trick the user into approving actions or entering credentials (the mobile equivalents of clickjacking), and shared OS facilities like the **clipboard/pasteboard** silently leak sensitive data between apps. This note groups the UI-redress and cross-app-leakage techniques: **tapjacking/overlays**, **task hijacking**, **accessibility-service abuse**, and **clipboard/UIPasteboard leakage**.

## Tapjacking / Overlay Attacks (Android)
A malicious app draws a transparent or decoy overlay on top of a target app so the user's taps land on the **target** while they think they're interacting with the overlay (or vice-versa):
```text
+---------------------------------------------------------------+
|                      TAPJACKING                              |
+---------------------------------------------------------------+
|  Malicious overlay (SYSTEM_ALERT_WINDOW / "draw over apps")    |
|        |  transparent layer or fake UI on top of target       |
|        v                                                       |
|  User taps what looks benign -> tap passes through to the     |
|  TARGET app's sensitive button (grant permission, confirm pay)|
+---------------------------------------------------------------+
```
Used to trick users into granting permissions, confirming transactions, or enabling accessibility for the malicious app itself. Requires the overlay permission (increasingly restricted) and is mitigated by `filterTouchesWhenObscured`.

## Task Hijacking (StrandHogg)
By manipulating `taskAffinity`/`allowTaskReparenting`/launch modes, a malicious app inserts its Activity into the **target app's task**, so when the user opens the legitimate app, the attacker's look-alike screen appears instead — harvesting credentials or approvals. (See also [[09 - Android IPC and Intent Attacks]].)

## Accessibility Service Abuse (Android)
Android **Accessibility Services** can read screen content and **perform actions on behalf of the user** (clicks, text input) across apps — designed for assistive tech, abused by malware to:
- Read on-screen data (including other apps' sensitive fields).
- **Auto-click** consent/permission dialogs (escalating its own privileges — conceptually like the macOS Accessibility/TCC abuse).
- Perform on-device fraud (auto-fill transfers). Tricking the user into enabling the malicious app's accessibility service (often via tapjacking) is the typical entry, after which it has broad control. Newer techniques like **InputMethodService (IME) abuse** and **AccessibilityService**-based input injection extend this.

## iOS UI / Input Concerns
iOS restricts overlays heavily, but related issues exist: **app-extension/keyboard** abuse (a malicious custom keyboard capturing input), **UIActivity share-sheet** data exposure, and **screenshot/snapshot** capture on backgrounding ([[08 - Insecure Data Storage]]).

## Clipboard / UIPasteboard Leakage
The clipboard is **shared across all apps** (and, with Universal Clipboard/Handoff, across devices):
```text
   App copies a password/OTP/token to the clipboard
        |  any other app can read the general pasteboard
        v  background app silently exfiltrates it
   iOS: UIPasteboard.general is global; iOS 14+ warns on reads
   Android: ClipboardManager; background read restricted on newer OS
```
- Apps that **copy secrets** (password managers, OTP autofill, "copy token") expose them to any app reading the clipboard.
- **Persistent** clipboard content survives app switches; OTP/2FA codes are common leaks.
- Test by copying sensitive values in the target and reading `UIPasteboard.general` / `ClipboardManager` from another app or via objection (`ios pasteboard monitor`).

## Why It Matters
UI-redress and accessibility abuse turn the user into the exploit — bypassing technical controls by manipulating what the user sees and taps, enabling credential theft, unwanted permission grants, and on-device fraud. Clipboard leakage silently exposes exactly the high-value secrets (passwords, OTPs, tokens) apps copy for "convenience." Both are easy to overlook and map to real-world mobile malware behaviour.

## Defensive Notes
- **Tapjacking**: set `filterTouchesWhenObscured="true"` / `setFilterTouchesWhenObscured(true)` on sensitive controls; detect overlay presence for critical actions.
- **Task hijacking**: set `taskAffinity=""`, use `singleInstance`/`FLAG_ACTIVITY_NEW_TASK` appropriately; target modern SDKs with built-in mitigations.
- **Accessibility/IME**: educate users; detect/limit; never rely on a11y for security; iOS — avoid third-party keyboards for sensitive input (`isSecureTextEntry`).
- **Clipboard**: don't copy secrets; if you must, use Android `ClipDescription` sensitive flag / auto-clear timers; avoid putting OTPs/passwords on the general pasteboard.

## Related Notes
- [[09 - Android IPC and Intent Attacks]]
- [[08 - Insecure Data Storage]]
- [[13 - Hardcoded Secrets and Sensitive Data Leakage]]
- [[03 - ClickFix and Fake Verification Lures]]
