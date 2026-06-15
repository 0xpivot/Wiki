---
tags: [mobile, android, ios, resilience, pentesting, frida]
difficulty: intermediate
module: "50 - Mobile Application Security"
topic: "50.14 Root and Jailbreak Detection Bypass"
---

# Root and Jailbreak Detection Bypass

## Introduction
Many apps (banking, payment, DRM, enterprise) try to **refuse to run on rooted/jailbroken devices**, reasoning that such devices can't be trusted. Since testing usually *requires* a rooted/jailbroken device or Frida ([[03 - Android Testing Environment Setup]], [[05 - iOS Testing Environment and Jailbreak]]), you must bypass these checks to proceed. Root/JB detection is a **client-side control**, and like all client-side controls it is bypassable — the app and the attacker run on the same device the attacker controls. This note covers how detection works and how to defeat it.

## How Detection Works
```text
+---------------------------------------------------------------+
|              ROOT / JAILBREAK DETECTION SIGNALS              |
+---------------------------------------------------------------+
|  ANDROID (root):                                              |
|    - su binary present (/system/bin/su, which su)             |
|    - root-management apps (Magisk, Superuser packages)        |
|    - test-keys build tag / ro.debuggable / ro.secure          |
|    - writable /system; busybox; dangerous props               |
|    - SafetyNet/Play Integrity attestation ([[16 ...]])        |
|  iOS (jailbreak):                                             |
|    - /Applications/Cydia.app, Sileo; /bin/bash, /etc/apt      |
|    - can fork()/system() (sandbox should forbid)              |
|    - write outside sandbox; suspicious dylibs (Substrate)     |
|    - URL scheme cydia:// openable                             |
+---------------------------------------------------------------+
```
Detection is typically a method returning a boolean (`isRooted()`/`isJailbroken()`); some apps run many checks and combine them, and stronger apps push checks into native code or back them with server-side attestation.

## Bypass Techniques
### 1. objection / Frida (fastest)
```bash
objection -g com.target.app explore
android root disable          # or:  ios jailbreak disable
# generic Frida scripts hook the common checks (file-exists, which, fork,
# package-manager queries, SecTrust) and force "not rooted/jailbroken"
```

### 2. Hook the detection method
Force the boolean to return false:
```javascript
Java.perform(() => {
  const C = Java.use('com.app.security.RootCheck');
  C.isDeviceRooted.implementation = function(){ return false; };
});
```
Find the method via static analysis ([[06 - APK Decompilation and Smali Patching]]) or by tracing `File.exists`, `Runtime.exec("which su")`, `PackageManager.getPackageInfo`, etc.

### 3. Smali patch (no Frida)
Patch the detection method's smali to `return false`, repackage, re-sign ([[06 ...]]).

### 4. Hide root from the app (Magisk DenyList / Zygisk)
On Android, **Magisk DenyList + Zygisk (e.g. Shamiko)** hides root from specific apps so detection never fires — useful when you want the app to behave normally without hooking. On iOS, jailbreak-hiding tweaks (e.g. for rootless JBs) serve the same role.

### 5. Native-implemented checks
If detection is in a `.so`, hook the native function with Frida ([[07 - Reversing Android Native Libraries]]); Java-level hooks/smali patches won't reach it.

## The Cat-and-Mouse Reality
Apps add more/stealthier checks (native, obfuscated, server-attested); testers add more hooks. There's no single permanent bypass — combine objection, custom Frida hooks for app-specific checks, Magisk hiding, and (for attestation) the techniques in [[16 - Anti-Instrumentation and Attestation Bypass]].

## Why It Matters
Root/JB detection blocks the entire dynamic assessment if not bypassed. Demonstrating the bypass is also a finding in itself: it proves the control is not a security boundary, reinforcing that sensitive logic and authorization must be enforced **server-side** rather than gated on "is the device trusted."

## Defensive Notes
- Treat root/JB detection as **defense-in-depth / anti-fraud signal**, never a security control — assume it's bypassed and enforce security server-side.
- Implement checks in **native code**, vary and obfuscate them, and combine with **hardware-backed attestation** (Play Integrity / App Attest) reported to and verified by the server ([[16 ...]]) — this raises cost and gives a server-side signal that's harder to forge than a client boolean.
- Respond server-side (step-up auth, limits) rather than just refusing to launch (which only teaches attackers where the check is).

## Related Notes
- [[05 - iOS Testing Environment and Jailbreak]]
- [[06 - APK Decompilation and Smali Patching]]
- [[12 - Network Interception and SSL Pinning Bypass]]
- [[16 - Anti-Instrumentation and Attestation Bypass]]
