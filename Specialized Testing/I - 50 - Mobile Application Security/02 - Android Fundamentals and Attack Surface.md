---
tags: [mobile, android, pentesting, attack-surface]
difficulty: beginner
module: "50 - Mobile Application Security"
topic: "50.02 Android Fundamentals and Attack Surface"
---

# Android Fundamentals and Attack Surface

## Introduction
To test an Android app you must understand how it is packaged, how its code runs, and how it exposes functionality. Android apps ship as **APK** files (or split **AAB**-derived APKs), run each app under a **dedicated Linux UID** confined by **SELinux**, and expose functionality through four **component** types reachable via **Intents**. Knowing this model tells you exactly where the attack surface is: the manifest declares what's exposed, the components are the entry points, and local storage holds the data. This note is the foundation for the IPC, storage, and reversing notes that follow.

## APK Structure
An APK is a ZIP archive:
```text
app.apk
├── AndroidManifest.xml   (binary XML — components, permissions, flags)
├── classes.dex           (Dalvik bytecode — the app's compiled Java/Kotlin)
├── resources.arsc        (compiled resources)
├── res/                  (layouts, drawables)
├── assets/               (raw files — often hide secrets/config)
├── lib/                  (native .so libraries per ABI)
└── META-INF/             (signing certs, manifest)
```
`assets/` and `res/raw/` frequently contain API keys, config, or embedded JS — always inspect them ([[06 - APK Decompilation and Smali Patching]]).

## The Sandbox Model
```text
+---------------------------------------------------------------+
|                   ANDROID APP SANDBOX                        |
+---------------------------------------------------------------+
|  Each app = unique Linux UID (e.g. u0_a123)                   |
|  Private dir /data/data/<package>/  owned by that UID         |
|  SELinux (since 4.3) + seccomp confine further                |
|  Apps interact ONLY through declared permissions + IPC        |
|  (sharedUserId legacy feature can merge UIDs — risky)         |
+---------------------------------------------------------------+
```
The sandbox is why "insecure data storage" matters: data in the app's private dir is protected from *other apps*, but not from a user with **root**, **adb backup**, or physical/forensic access.

## The Four Components (the IPC attack surface)
```text
+----------------+----------------------------------------------+
| Component      | Purpose / abuse                              |
+----------------+----------------------------------------------+
| Activity       | UI screens; exported ones launchable by any  |
|                | app -> auth bypass, intent injection         |
| Service        | background work; exported -> command abuse   |
| BroadcastRecv  | event handlers; exported -> spoofed intents  |
| ContentProvider| data interface; exported/SQL -> data leak,   |
|                | SQLi, path traversal                         |
+----------------+----------------------------------------------+
```
A component is reachable by other apps when **`android:exported="true"`** (explicit, or implicit if it has an intent-filter on older targets). Exported components are the #1 Android IPC attack surface — see [[09 - Android IPC and Intent Attacks]].

## Reading the Manifest (where the surface is declared)
Key things to hunt in `AndroidManifest.xml`:
```xml
android:debuggable="true"          <!-- attach debugger / run as app uid -->
android:allowBackup="true"         <!-- adb backup extracts app data -->
android:exported="true"            <!-- component reachable by other apps -->
android:usesCleartextTraffic="true"<!-- allows HTTP -->
<uses-permission .../>             <!-- over-privilege; dangerous perms -->
android:networkSecurityConfig      <!-- custom CA / pinning config -->
<grant-uri-permission .../>        <!-- provider sharing -->
```
`debuggable` and `allowBackup` are immediate findings: the former lets you run code as the app and debug it ([[06 ...]]); the latter lets `adb backup` pull private data.

## Permission Model
Apps declare permissions; **dangerous** permissions (location, contacts, camera, SMS) require runtime grants. Over-privileged apps and **custom permissions** with weak `protectionLevel` (e.g. `normal` instead of `signature`) let other apps invoke protected functionality — a recurring IPC weakness.

## Attack-Surface Summary
```text
   APK contents      -> secrets in assets/res, native libs
   Manifest flags    -> debuggable, allowBackup, cleartext, exports
   Components        -> exported activities/services/receivers/providers
   Local storage     -> /data/data/<pkg> (shared prefs, DBs, files)
   Network           -> API calls (intercept), pinning
   WebViews          -> JS bridges, file access
   Native libs       -> JNI, memory bugs
   Platform features -> deep links, intents, accessibility, overlays
```

## Why It Matters
Almost every Android finding traces back to one of these primitives: a flag in the manifest, an over-exposed component, data in the private dir, or a permission misconfiguration. Mapping the surface from the manifest + APK contents is the fastest route to the real bugs.

## Defensive Notes
- Ship release builds with `debuggable=false`, `allowBackup=false`, `usesCleartextTraffic=false`.
- Set `exported="false"` unless a component must be public; protect public components with `signature`-level permissions and validate all incoming Intents.
- Keep secrets off the device; obfuscate (R8/ProGuard) but never rely on it for secrecy.

## Related Notes
- [[01 - Mobile Pentest Methodology Overview]]
- [[06 - APK Decompilation and Smali Patching]]
- [[09 - Android IPC and Intent Attacks]]
- [[08 - Insecure Data Storage]]
- [[03 - Android Testing Environment Setup]]
