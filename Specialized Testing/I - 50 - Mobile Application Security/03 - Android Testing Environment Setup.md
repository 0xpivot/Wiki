---
tags: [mobile, android, pentesting, tooling, frida]
difficulty: beginner
module: "50 - Mobile Application Security"
topic: "50.03 Android Testing Environment Setup"
---

# Android Testing Environment Setup

## Introduction
Dynamic Android testing requires a controlled device (physical or emulated), a way to **route traffic through an intercepting proxy**, and an **instrumentation framework** (Frida/objection) to hook the app at runtime. Setting this up correctly is the difference between productive testing and fighting the platform. This note covers `adb`, emulator vs rooted device, installing the Burp CA so HTTPS is interceptable, and getting Frida running.

## adb — Your Primary Interface
The Android Debug Bridge controls the device/emulator:
```bash
adb devices                      # list connected devices
adb shell                        # shell on device
adb install app.apk              # install
adb pull /data/local/tmp/x .     # exfil files
adb push frida-server /data/local/tmp/
adb logcat                       # live logs (watch for leaked data)
adb backup -f b.ab <pkg>         # if allowBackup=true -> extract app data
adb shell pm list packages       # installed packages
adb shell run-as <pkg>           # run as the app's uid (if debuggable)
```

## Device Choice: Emulator vs Rooted Physical
```text
+---------------------------------------------------------------+
|  AVD Emulator                |  Rooted physical device         |
+---------------------------------------------------------------+
|  easy, snapshot, x86 fast    |  real hardware, sensors, NFC    |
|  root via -writable-system   |  Magisk root; SafetyNet harder  |
|  some apps detect emulator   |  matches production behaviour   |
+---------------------------------------------------------------+
```
- **AVD** (`avdmanager`/Android Studio): pick a **Google APIs** image (not Play Store) so you get root-capable `adb root`/`-writable-system`.
- **Physical**: root with **Magisk** (supports DenyList/Zygisk to hide root from detection — useful against [[14 - Root and Jailbreak Detection Bypass]]).

## Installing the Burp CA (intercept HTTPS)
By default apps trust only **system** CAs (since Android 7 / API 24, user CAs aren't trusted for app traffic). Steps:
```bash
# 1. export Burp cert, convert to PEM, name by subject hash
openssl x509 -inform DER -in cacert.der -out cacert.pem
hash=$(openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1)
mv cacert.pem $hash.0
# 2. push into the SYSTEM trust store (needs root / writable-system)
adb root; adb remount
adb push $hash.0 /system/etc/security/cacerts/
adb shell chmod 644 /system/etc/security/cacerts/$hash.0
adb reboot
```
Alternatively, repackage the APK with a **network security config** trusting user CAs (`make-apk-accept-ca-certificate`) when you can't modify the system store — modify `res/xml/network_security_config.xml` to trust user certs, then re-sign ([[06 - APK Decompilation and Smali Patching]]).

## Frida — Runtime Instrumentation
Frida injects a JS engine into the app to hook methods (defeat pinning/root detection, dump data, call functions):
```bash
# device side: matching frida-server for the device ABI
adb push frida-server /data/local/tmp/ && adb shell "/data/local/tmp/frida-server &"
# host side
frida-ps -Ua                          # list running apps
frida -U -f com.target.app -l hook.js --no-pause
objection -g com.target.app explore   # objection = Frida-powered toolkit
```
**objection** wraps Frida with ready commands: `android sslpinning disable`, `android root disable`, dump keystore, list activities, etc. — the fastest path for common tasks.

## Proxy Routing
```text
   Device WiFi proxy -> Burp (host:8080)   [manual proxy]
   or  adb reverse tcp:8080 tcp:8080        [route device->host]
   For apps ignoring system proxy: use a transparent proxy /
   ProxyDroid / iptables redirect, or Frida to force the proxy.
```

## Why It Matters
Most dynamic findings (token leakage, weak TLS, insecure storage, broken auth) require seeing and manipulating live traffic and runtime state. A correctly trusted CA + working Frida is the prerequisite for everything in the dynamic phase; the Android-7 system-store requirement trips up many testers and silently breaks interception.

## Defensive Notes
- Apps should **pin certificates** and refuse user/added CAs (raises the bar — though bypassable via Frida, see [[12 - Network Interception and SSL Pinning Bypass]]).
- Detect rooted/emulated/instrumented environments as defense-in-depth ([[14 - Root and Jailbreak Detection Bypass]], [[16 - Anti-Instrumentation and Attestation Bypass]]) — but enforce real security server-side.
- Disable `debuggable`/`allowBackup` so `run-as`/`adb backup` can't trivially extract data.

## Related Notes
- [[02 - Android Fundamentals and Attack Surface]]
- [[06 - APK Decompilation and Smali Patching]]
- [[12 - Network Interception and SSL Pinning Bypass]]
- [[14 - Root and Jailbreak Detection Bypass]]
