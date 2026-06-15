---
tags: [mobile, android, reversing, pentesting]
difficulty: intermediate
module: "50 - Mobile Application Security"
topic: "50.06 APK Decompilation and Smali Patching"
---

# APK Decompilation and Smali Patching

## Introduction
Because the Android app ships its compiled code to the device, **static reverse engineering** is central to mobile testing. You can decompile DEX bytecode back to readable Java, inspect resources and the manifest, and — powerfully — **modify the app's bytecode (smali), repackage, re-sign, and run your patched version**. Smali patching lets you defeat client-side controls (root/pinning checks), flip flags (`debuggable`), inject logging, or change behaviour — without touching the live process. This note covers the decompile→read→patch→rebuild→re-sign loop.

## Decompiling and Reading
```text
+---------------------------------------------------------------+
|                  ANDROID REVERSING TOOLS                     |
+---------------------------------------------------------------+
| jadx / jadx-gui   DEX -> readable Java (best for reading)     |
| apktool           APK -> smali + decoded manifest/resources   |
|                   (best for MODIFYING + rebuilding)           |
| dex2jar + JD-GUI  alt path to Java                            |
| bytecode-viewer   multi-decompiler GUI                        |
+---------------------------------------------------------------+
```
```bash
jadx-gui app.apk                 # browse decompiled Java, search strings
apktool d app.apk -o app_src     # decode to smali + resources for editing
# hunt for secrets / endpoints / logic
grep -rEi 'api[_-]?key|secret|password|http://|https://|BEGIN ' app_src
```
Start by reading the **manifest** (exports, flags — see [[02 - Android Fundamentals and Attack Surface]]), then `assets/`, `res/raw/`, string resources, and the decompiled code for secrets, endpoints, and the controls you'll need to bypass.

## Smali — Editing the Bytecode
`apktool` produces **smali** (human-readable Dalvik assembly). Common patches:
```smali
# Force a boolean method (e.g. isRooted/isPinningOk) to return true/false:
.method public isDeviceRooted()Z
    .locals 1
    const/4 v0, 0x0        # 0 = false  (was returning true)
    return v0
.end method
```
Typical targets: root/jailbreak detection routines, SSL-pinning verification methods, license/premium checks, and integrity checks — flip the return value so the check passes. You can also add `Log` calls to trace values, or change strings/URLs.

## Rebuild and Re-sign (mandatory)
Android refuses unsigned/badly-signed APKs, so after editing you must rebuild and **sign** (any key works for testing; the signature just must be valid and consistent):
```bash
apktool b app_src -o patched.apk
# zipalign (recommended)
zipalign -p 4 patched.apk patched-aligned.apk
# create a debug keystore if needed, then sign
apksigner sign --ks debug.keystore --ks-pass pass:android patched-aligned.apk
apksigner verify patched-aligned.apk
adb install -r patched-aligned.apk
```
Note: changing the signing key changes the app's signature — apps doing **signature self-verification** (or server-side signature attestation, Play Integrity) will detect the resign; combine with those bypasses ([[16 - Anti-Instrumentation and Attestation Bypass]]) when needed.

## Patching the Network Security Config (trust your CA)
A common patch to enable interception without root: edit/add `res/xml/network_security_config.xml` to trust user CAs, reference it in the manifest, rebuild + re-sign:
```xml
<network-security-config>
  <base-config><trust-anchors>
    <certificates src="user"/><certificates src="system"/>
  </trust-anchors></base-config>
</network-security-config>
```

## Deobfuscation Note
Many apps use **R8/ProGuard** (renamed identifiers) or commercial obfuscators (DexGuard) plus string encryption and native packing. Approaches: rely on dynamic analysis (Frida) where static is opaque, use mapping files if available, and manually deobfuscate hot paths. Native logic may be pushed into `.so` libraries — see [[07 - Reversing Android Native Libraries]].

## Why It Matters
Smali patching is the universal "modify the client" primitive: it defeats any control implemented purely on the device (root/pinning/license checks), enables interception, and reveals hardcoded secrets and logic. It also demonstrates the central mobile lesson — client-side controls are bypassable, so security must live server-side.

## Defensive Notes
- Implement **tamper/signature self-checks** and server-side attestation (Play Integrity) — speed bumps that catch resigned/patched APKs ([[16 ...]]).
- Apply robust obfuscation + string encryption + native packing to raise reversing cost (not a substitute for server-side enforcement).
- Never embed real secrets in the APK; assume everything client-side is readable and modifiable.

## Related Notes
- [[02 - Android Fundamentals and Attack Surface]]
- [[07 - Reversing Android Native Libraries]]
- [[12 - Network Interception and SSL Pinning Bypass]]
- [[16 - Anti-Instrumentation and Attestation Bypass]]
