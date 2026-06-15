---
tags: [mobile, ios, ipc, deeplinks, pentesting]
difficulty: intermediate
module: "50 - Mobile Application Security"
topic: "50.10 iOS URL Schemes, Deeplinks and Universal Links"
---

# iOS URL Schemes, Deeplinks and Universal Links

## Introduction
iOS apps expose entry points to other apps and to the web through **custom URL schemes** (`myapp://...`), **Universal Links** (`https://...` that open the app), and related mechanisms (App Extensions, protocol handlers). These are iOS's analogue of Android's exported components + deep links ([[09 - Android IPC and Intent Attacks]]) and carry the same risk: if the app **trusts the parameters in an incoming URL** to perform sensitive actions, any other app — or a web page — can invoke that behaviour. This note covers the mechanisms and their abuse.

## Custom URL Schemes
An app registers schemes in `Info.plist` (`CFBundleURLTypes`); any app/web page can then invoke it:
```text
   myapp://transfer?to=attacker&amount=1000
   myapp://open?url=https://evil
   myapp://resetpassword?token=...
```
**The core flaw:** schemes are **not unique or authenticated** — multiple apps can claim the same scheme (hijacking), and the receiving app cannot reliably know *who* sent the URL. If the handler acts on parameters without validation/authorization, it's exploitable.
```bash
# trigger a scheme on a test device
# (Safari address bar, or)
objection -g <app> run ios url <scheme>   # or via a crafted webpage / another app
```
Abuse patterns:
- **Sensitive action via parameters** — initiate transfers, change settings, auto-login with an injected token.
- **Open-redirect / WebView injection** — `myapp://open?url=` loading attacker content into an in-app WebView ([[11 - WebView Attacks]]).
- **Scheme hijacking** — a malicious app registers the same scheme to intercept data or phish.
- **Parameter/secret leakage** — tokens passed in URLs land in logs/history.

## Universal Links
Universal Links are **HTTPS URLs** that open the app instead of Safari, validated by an **`apple-app-site-association` (AASA)** file hosted on the domain and the app's `associated-domains` entitlement:
```text
+---------------------------------------------------------------+
|                   UNIVERSAL LINK TRUST                       |
+---------------------------------------------------------------+
|  https://example.com/path  -> opens App if:                   |
|    1. App has associated-domains: applinks:example.com        |
|    2. https://example.com/.well-known/apple-app-site-assoc..  |
|       lists the app's appID + matching path patterns          |
|  => domain ownership is the trust anchor (better than schemes)|
+---------------------------------------------------------------+
```
More secure than custom schemes (domain-validated, not hijackable by another app), but flaws appear in:
- **Over-broad AASA path patterns** (`"*"`) routing unexpected URLs into the app.
- The app still **trusting URL content** for sensitive actions (same parameter-trust bug).
- **AASA / associated-domain misconfig** weakening the validation.

## App Extensions, Protocol Handlers, Activity Sharing
- **App Extensions** (share/today/keyboard/file-provider) run code with their own entitlements and exchange data with the host — a boundary worth auditing for data exposure.
- **Custom protocol handlers** and **`UIActivity`/share-sheet** flows can leak data to other apps.
- **`itms-`/`mailto:`-style** and other system schemes can be abused for redirection.

## Testing Workflow
```text
1. Enumerate schemes: read CFBundleURLTypes in Info.plist;
   enumerate associated-domains entitlement (Universal Links).
2. Map handlers: in the (decrypted) binary find application:openURL:
   / continueUserActivity: and trace how parameters are used.
3. Fuzz/abuse: invoke each scheme/link with crafted params; look for
   sensitive actions, WebView loads, auth/token handling.
4. Test hijacking: register a competing scheme from a test app.
```

## Why It Matters
Deep-link entry points are routinely trusted as if only the app's own UI could reach them, but a web page or sibling app can invoke them directly — enabling auth bypass, unauthorized actions, WebView injection, and token leakage. They're a high-value, often-overlooked iOS attack surface and the direct counterpart to Android intent attacks.

## Defensive Notes
- Prefer **Universal Links** (domain-validated) over custom schemes; keep AASA path patterns tight.
- **Never trust URL parameters** for authorization or sensitive actions — re-authenticate/authorize server-side; validate and sanitize all input.
- Don't pass secrets/tokens in URLs; validate the source where possible; treat in-app WebView loads from URLs as untrusted.

## Related Notes
- [[09 - Android IPC and Intent Attacks]]
- [[11 - WebView Attacks]]
- [[04 - iOS Fundamentals and Attack Surface]]
- [[08 - Insecure Data Storage]]
