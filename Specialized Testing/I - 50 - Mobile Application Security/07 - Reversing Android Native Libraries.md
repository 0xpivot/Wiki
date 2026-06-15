---
tags: [mobile, android, reversing, native, jni, pentesting]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.07 Reversing Android Native Libraries"
---

# Reversing Android Native Libraries

## Introduction
Security-sensitive logic in Android apps is increasingly pushed out of (easily decompiled) Java/Kotlin into **native libraries** (`.so` files written in C/C++), reached via the **JNI (Java Native Interface)**. Developers do this to hide secrets, implement crypto/DRM, run anti-tamper/root checks, and pack obfuscated code — precisely the things a tester wants to inspect. Native libraries resist `jadx`/smali analysis (they're compiled machine code), so reversing them requires disassemblers (Ghidra/IDA), JNI knowledge, and Frida for the dynamic side. This note covers locating native code, understanding the JNI bridge, and analyzing `.so` files.

## Where Native Code Lives
```text
app.apk
└── lib/
    ├── arm64-v8a/libfoo.so     (64-bit ARM — most devices)
    ├── armeabi-v7a/libfoo.so   (32-bit ARM)
    └── x86_64/libfoo.so        (emulator)
```
Pick the ABI matching your test device (usually `arm64-v8a`). Some apps also load `.so` files dynamically from assets/downloads.

## The JNI Bridge
Java declares `native` methods; the `.so` implements them. Two binding styles determine how you find the implementation:
```text
+---------------------------------------------------------------+
|                     JNI METHOD BINDING                       |
+---------------------------------------------------------------+
| 1. STATIC naming:  Java_<pkg>_<Class>_<method>                |
|      e.g. Java_com_app_Crypto_sign  -> grep exports for it    |
| 2. DYNAMIC: RegisterNatives() in JNI_OnLoad maps Java names   |
|      to arbitrary C functions -> analyze JNI_OnLoad to find   |
|      the function-pointer table (hides the real names)        |
+---------------------------------------------------------------+
```
The first JNI arg is always `JNIEnv*` (the gateway to call back into Java/JVM); the second is the `jobject`/`jclass`. Recognizing `JNIEnv` usage in the disassembly orients you in the function.

## Static Analysis Workflow
```bash
# pull the .so
unzip -j app.apk 'lib/arm64-v8a/libfoo.so' -d .
file libfoo.so; readelf -d libfoo.so          # arch, deps
nm -D libfoo.so | grep Java_                   # statically-bound JNI exports
strings -a libfoo.so | grep -Ei 'key|http|password'
```
Then load into **Ghidra** (free) or **IDA**:
- Find exported `Java_...` functions or analyze **`JNI_OnLoad`** for `RegisterNatives` (dynamic binding) to map functions.
- Trace the logic of interest (crypto keys, signing, root checks). Look for `AES`, `HMAC`, hardcoded byte arrays (keys/IVs), and calls to libc/crypto APIs.

## Dynamic Analysis with Frida
Static is slow; Frida lets you hook native functions at runtime to read arguments/return values or change behaviour:
```javascript
// hook an exported native function and dump args / patch return
const addr = Module.findExportByName("libfoo.so", "Java_com_app_Crypto_sign");
Interceptor.attach(addr, {
  onEnter(args) { console.log("arg1", args[2]); },     // [0]=JNIEnv [1]=this
  onLeave(ret)  { console.log("ret", ret); ret.replace(0x1); } // force success
});
// or hook libc/crypto: Module.findExportByName("libc.so","strcmp") etc.
```
This is the fast path to extract keys (hook the crypto call and read the key/plaintext), defeat native root/integrity checks (force the return), and understand behaviour without fully reversing the binary.

## Common Targets in Native Libs
```text
   - Hardcoded crypto keys / API secrets (hidden from jadx)
   - Root/emulator/Frida detection implemented in C
   - SSL pinning logic (cert hashes in the .so)
   - DRM / license / signing routines
   - Custom packers/obfuscators (unpack at runtime -> dump from memory)
```

## Why It Matters
Moving logic to native code is the most common way apps try to hide secrets and harden controls from Java-level analysis. Knowing JNI + using Ghidra/Frida defeats this: you recover the "hidden" keys, bypass native-implemented protections, and reach the logic developers assumed was safe. It's often where the real secrets are.

## Defensive Notes
- Native code raises the bar but **does not hide secrets** from a determined analyst — assume embedded keys are recoverable; fetch secrets server-side with short-lived tokens instead.
- Use dynamic JNI registration + control-flow obfuscation + native packing to increase cost; add anti-Frida checks in native code ([[16 - Anti-Instrumentation and Attestation Bypass]]).
- Enforce all security decisions server-side; treat native checks as defense-in-depth only.

## Related Notes
- [[06 - APK Decompilation and Smali Patching]]
- [[03 - Android Testing Environment Setup]]
- [[16 - Anti-Instrumentation and Attestation Bypass]]
- [[12 - Network Interception and SSL Pinning Bypass]]
