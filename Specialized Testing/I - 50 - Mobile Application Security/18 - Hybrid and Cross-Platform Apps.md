---
tags: [mobile, android, ios, hybrid, flutter, react-native, pentesting]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.18 Hybrid and Cross-Platform Apps"
---

# Hybrid and Cross-Platform Apps

## Introduction
A large share of mobile apps are not pure native — they're built with **cross-platform frameworks** (Flutter, React Native, Cordova/Ionic/PhoneGap, Xamarin/.NET MAUI). Each framework changes *where the app's logic lives and how to reverse/instrument it*, so the standard native techniques (jadx on DEX, Frida hooking Java/Obj-C) often don't apply directly. The vulnerability classes are the same (insecure storage, weak transport, exposed IPC, secrets), but the **analysis approach differs per framework**. This note maps how to test each.

## Why Framework Matters
```text
+---------------------------------------------------------------+
|  Framework     | Logic lives in...     | Analysis approach     |
+---------------------------------------------------------------+
| Cordova/Ionic  | HTML/JS/CSS in assets | read www/ assets;     |
|                | (WebView app)         | WebView attacks       |
| React Native   | JS bundle (Hermes or  | extract/decompile     |
|                | plain) in assets      | index.android.bundle  |
| Flutter        | compiled Dart in      | reverse libapp.so;    |
|                | libapp.so (AOT)       | hard to hook (no JNI) |
| Xamarin/MAUI   | .NET assemblies (DLL) | decompile IL (dnSpy)  |
+---------------------------------------------------------------+
```

## Cordova / Ionic / PhoneGap
These are essentially a **WebView wrapping a web app**; the entire UI/logic is HTML/JS/CSS shipped in `assets/www/`:
```bash
# unzip APK -> assets/www/  (or iOS App.app/www)
ls app_src/assets/www        # index.html, js/, plugins config
grep -rEi 'api|key|http|token' app_src/assets/www
cat app_src/res/xml/config.xml   # whitelist / allowed navigation / plugins
```
- **All WebView attacks apply** ([[11 - WebView Attacks]]) — JS bridge = Cordova plugins exposing native functions to JS.
- Secrets are in plain JS; the **whitelist/allow-navigation** config controls what the WebView may load (misconfig → load attacker content → call plugins).

## React Native
JS logic is bundled into `index.android.bundle` (Android `assets/`) / `main.jsbundle` (iOS):
```bash
unzip -j app.apk 'assets/index.android.bundle' -d .
# plain JS bundle -> beautify/read directly
js-beautify index.android.bundle | grep -Ei 'key|token|http'
# Hermes bytecode bundle -> use hermes-dec / hbctool to decompile
file index.android.bundle      # "Hermes" magic? -> hermes decompiler
```
- If **not** Hermes: the bundle is readable JS — secrets and logic are exposed.
- If **Hermes**: decompile the bytecode (`hbctool`, `hermes-dec`).
- Native modules bridge JS↔native; storage often via `AsyncStorage` (check it's not holding secrets — [[08 - Insecure Data Storage]]).

## Flutter (the hard one)
Flutter compiles **Dart to native AOT machine code** in `libapp.so` (release) and doesn't use the standard JNI/Obj-C runtime — so:
- **Reversing** means analyzing `libapp.so` in Ghidra/IDA with Dart-aware tooling (e.g. **reFlutter**, Dart snapshot parsers) — much harder than reading JS.
- **Frida hooking is difficult**: no Java/Obj-C symbols to hook; Flutter also has its **own TLS stack (BoringSSL)** that ignores the system proxy/CA — so SSL interception needs a Flutter-specific approach: patch `libapp.so`/`libflutter.so` with **reFlutter** to disable pinning and force a proxy, or hook BoringSSL's `ssl_verify` in the native lib ([[12 - Network Interception and SSL Pinning Bypass]], [[07 - Reversing Android Native Libraries]]).
- This is why Flutter apps often *appear* to "not use the proxy" — they bypass it by design.

## Xamarin / .NET MAUI
Logic compiles to **.NET IL** in DLLs bundled in the APK/IPA (sometimes AOT/bundled):
```bash
unzip app.apk 'assemblies/*' -d asm   # .dll assemblies (may be compressed/AOT)
# decompile IL with dnSpy / ILSpy / dotPeek -> near-source C#
```
Secrets and logic are recoverable from IL; storage/transport classes follow .NET APIs.

## Why It Matters
Recognizing the framework early saves hours: you won't find logic in `classes.dex` for a Flutter app, and you won't intercept a Flutter app's traffic with a normal CA install. Each framework also has characteristic weak spots — readable JS bundles (Cordova/RN) leak secrets trivially; Flutter's separate TLS stack defeats naive interception until patched. The underlying vuln classes are unchanged; only the access path differs.

## Defensive Notes
- Don't embed secrets regardless of framework — JS bundles and IL are easily read; Dart is harder but not secret-safe.
- Cordova/RN: lock the WebView whitelist, minimize exposed native plugins/modules, keep `AsyncStorage`/local data non-sensitive.
- Flutter: still implement pinning (in the Dart/BoringSSL layer) knowing it's patchable; enforce security server-side.
- Apply the same storage/transport/IPC hardening as native; obfuscate, but treat client code as readable.

## Related Notes
- [[11 - WebView Attacks]]
- [[12 - Network Interception and SSL Pinning Bypass]]
- [[07 - Reversing Android Native Libraries]]
- [[13 - Hardcoded Secrets and Sensitive Data Leakage]]
- [[01 - Mobile Pentest Methodology Overview]]
