---
tags: [mobile, ios, pentesting, attack-surface]
difficulty: beginner
module: "50 - Mobile Application Security"
topic: "50.04 iOS Fundamentals and Attack Surface"
---

# iOS Fundamentals and Attack Surface

## Introduction
iOS apps run in a tightly controlled environment: distributed as **IPA** packages, compiled to **Mach-O** binaries (Objective-C/Swift), confined by a per-app **sandbox** governed by **entitlements**, with code-signing and **AMFI** enforcement (the same machinery covered in the macOS module, since iOS and macOS share heritage). The platform's strictness means iOS testing leans heavily on the **app sandbox container** (where data lives), **inter-app communication** (URL schemes, Universal Links, App Extensions, the pasteboard), and runtime instrumentation. This note maps the iOS-specific attack surface that the rest of the module builds on.

## IPA Structure
An IPA is a ZIP:
```text
app.ipa
└── Payload/
    └── App.app/
        ├── App                 (Mach-O executable — the binary)
        ├── Info.plist          (bundle id, URL schemes, ATS, perms)
        ├── embedded.mobileprovision  (provisioning profile)
        ├── _CodeSignature/     (signing)
        ├── *.nib / Assets.car  (UI)
        └── Frameworks/         (embedded dylibs/frameworks)
```
App Store binaries are additionally **FairPlay-encrypted**; to statically analyze them you must **decrypt** (dump from memory on a jailbroken device with `frida-ios-dump`/`Clutch`) before tools like Hopper/Ghidra/`class-dump` are useful.

## Sandbox, Entitlements, and Data Protection
```text
+---------------------------------------------------------------+
|                    iOS APP CONFINEMENT                       |
+---------------------------------------------------------------+
|  Each app -> private container:                               |
|     .../Containers/Data/Application/<UUID>/                   |
|        Documents/  Library/  tmp/                             |
|  Entitlements (signed) grant capabilities (keychain groups,   |
|     app groups, push, associated-domains for Universal Links) |
|  Data Protection: files encrypted with classes tied to        |
|     device-lock state (NSFileProtection...)                   |
|  Keychain: OS-managed secret store (per-app/app-group ACLs)   |
+---------------------------------------------------------------+
```
Extract entitlements to understand capabilities (`codesign -d --entitlements - App` or from the binary). Weak Data Protection classes (e.g. `NSFileProtectionNone`) mean data is readable even when the device is locked — a finding.

## Inter-App / Platform Attack Surface
iOS IPC is narrower than Android but rich:
```text
+---------------------------+------------------------------------+
| Mechanism                 | Abuse                              |
+---------------------------+------------------------------------+
| Custom URL schemes        | other apps invoke yours w/ params  |
|  (myapp://)               | -> deeplink injection ([[10 ...]]) |
| Universal Links           | https-backed deep links; assoc.    |
|                           | domain validation matters          |
| App Extensions            | share/today/keyboard extensions —  |
|                           | data flow + entitlement boundaries |
| UIPasteboard              | general pasteboard leaks data      |
|                           | across apps ([[17 ...]])           |
| UIActivity / share sheet  | data exfil via sharing             |
| Pasteboard/handoff        | cross-device leakage               |
| WKWebView / JS bridges    | web-to-native exposure ([[11 ...]])|
+---------------------------+------------------------------------+
```

## Reading Info.plist (where the surface is declared)
```xml
CFBundleURLTypes            <!-- custom URL schemes the app handles -->
NSAppTransportSecurity      <!-- ATS exceptions = allowed insecure TLS -->
  NSAllowsArbitraryLoads    <!-- disables ATS -> HTTP allowed -->
com.apple.developer.associated-domains  <!-- Universal Links -->
UIFileSharingEnabled        <!-- iTunes file sharing exposes Documents -->
NS*UsageDescription         <!-- requested sensitive permissions -->
```
ATS exceptions and custom URL schemes are immediate things to note.

## Jailbreak vs No-Jailbreak Testing
- **Jailbroken**: full filesystem access, Frida/objection, Cydia tooling, binary decryption — the richest environment ([[05 - iOS Testing Environment and Jailbreak]]).
- **No-jailbreak**: repackage the IPA with a Frida gadget / use sideloading + objection against the patched app — viable when no JB exists for the iOS version.

## Why It Matters
iOS's strict sandbox pushes the interesting bugs toward **local data protection** (keychain/Data Protection misuse), **inter-app entry points** (URL schemes, Universal Links, extensions, pasteboard), and **WebView bridges** — plus the same TLS/pinning and backend issues as any app. Mapping Info.plist + entitlements + container contents pinpoints these quickly.

## Defensive Notes
- Use strong **Data Protection** classes; store secrets in the **Keychain** with appropriate accessibility (not `Always`); never in `NSUserDefaults`/plist.
- Validate all input from URL schemes; prefer **Universal Links** (with strict associated-domain validation) over custom schemes.
- Keep ATS enabled (no `NSAllowsArbitraryLoads`); disable file sharing unless required; minimize entitlements.

## Related Notes
- [[01 - Mobile Pentest Methodology Overview]]
- [[05 - iOS Testing Environment and Jailbreak]]
- [[10 - iOS URL Schemes Deeplinks and Universal Links]]
- [[08 - Insecure Data Storage]]
- [[06 - Code Signing and Entitlements]]
