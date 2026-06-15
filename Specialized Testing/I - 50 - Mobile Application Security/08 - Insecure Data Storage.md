---
tags: [mobile, android, ios, storage, pentesting]
difficulty: intermediate
module: "50 - Mobile Application Security"
topic: "50.08 Insecure Data Storage"
---

# Insecure Data Storage

## Introduction
**Insecure data storage** is consistently the most common mobile finding (top of the OWASP Mobile Top 10). Apps cache credentials, tokens, PII, payment data, and session info on the device — and frequently store it in plaintext, in world-readable locations, in logs, or in backups. Because devices are lost, stolen, shared, rooted/jailbroken, and forensically imaged, anything sensitive at rest must be protected. This note covers where data lives on both platforms, the common mistakes, and how to test for them.

## Where Apps Store Data
```text
+---------------------------------------------------------------+
|  ANDROID  /data/data/<pkg>/         |  iOS  app container       |
+---------------------------------------------------------------+
|  shared_prefs/*.xml (key-value)     |  NSUserDefaults (plist)  |
|  databases/*.db (SQLite)            |  Core Data / SQLite      |
|  files/  (arbitrary)                |  Documents/ Library/ tmp/|
|  cache/                             |  Caches/                 |
|  external storage (/sdcard) = WORLD |  Keychain (OS secret     |
|    readable historically — risky    |   store, correct place)  |
|  EncryptedSharedPreferences (good)  |  Data Protection classes |
+---------------------------------------------------------------+
```
On Android, **external storage** (`/sdcard`) is shared and must never hold secrets. On iOS, **NSUserDefaults** is an unencrypted plist — wrong for secrets; the **Keychain** is the correct store.

## Common Mistakes
- **Plaintext credentials/tokens** in shared_prefs / NSUserDefaults / SQLite.
- **Sensitive data in logs** (`logcat`, NSLog) — tokens printed during debugging.
- **Secrets on external storage** (Android `/sdcard`) readable by other apps/users.
- **Backups** — Android `allowBackup=true` (adb backup extracts data); iOS unencrypted iTunes/iCloud backups including app data.
- **Caches & screenshots** — the OS snapshots the app on backgrounding (iOS app-switcher screenshot can capture sensitive screens); WebView/HTTP caches retain responses.
- **Weak Data Protection class** (iOS `NSFileProtectionNone`) — file readable while device locked.
- **Keychain misuse** — `kSecAttrAccessibleAlways` keeps secrets available even when locked.
- **Hardcoded keys used to "encrypt"** local data (the key is in the app — see [[13 - Hardcoded Secrets and Sensitive Data Leakage]]).

## Testing Workflow
```bash
# ANDROID — exercise the app, then inspect its private dir (root or run-as)
adb shell run-as <pkg> ls -R /data/data/<pkg>/        # debuggable apps
adb shell "su -c 'find /data/data/<pkg> -type f'"      # rooted
adb shell run-as <pkg> cat shared_prefs/*.xml
adb shell run-as <pkg> sqlite3 databases/app.db .dump
adb backup -f b.ab <pkg> && abe unpack b.ab b.tar       # if allowBackup
adb logcat | grep -i <pkg>                              # leaked logs
ls -la /sdcard/Android/data/<pkg>/                      # external storage
```
```bash
# iOS — on jailbroken device, browse the container; check the right stores
find /var/mobile/Containers/Data/Application/<UUID> -type f
objection -g <app> run ios nsuserdefaults get           # plist secrets
objection -g <app> run ios keychain dump                # keychain contents
```
**Method:** drive the app through login and sensitive flows, *then* inspect every storage location for credentials/tokens/PII; background the app and check the snapshot; trigger a backup and inspect it.

## Why It Matters
Local data theft turns a lost/stolen/forensically-imaged or rooted device into a full account compromise (stored session tokens), a PII breach, or payment-data exposure — often with no network attack at all. It is the highest-frequency, easily-demonstrable mobile finding and maps directly to privacy/compliance impact.

## Defensive Notes
- Store secrets in the **platform keystore**: Android **Keystore** / `EncryptedSharedPreferences`; iOS **Keychain** with `WhenUnlocked`/`...ThisDeviceOnly` accessibility.
- Don't log sensitive data; strip debug logging from release builds.
- Set Android `allowBackup=false`; mark iOS files with strong **Data Protection**; mask the app-switcher snapshot for sensitive screens.
- Never put secrets on external storage; minimize what's stored at all (prefer short-lived server-issued tokens).

## Related Notes
- [[02 - Android Fundamentals and Attack Surface]]
- [[04 - iOS Fundamentals and Attack Surface]]
- [[13 - Hardcoded Secrets and Sensitive Data Leakage]]
- [[17 - UI Redress Tapjacking Overlays and Pasteboard Leakage]]
