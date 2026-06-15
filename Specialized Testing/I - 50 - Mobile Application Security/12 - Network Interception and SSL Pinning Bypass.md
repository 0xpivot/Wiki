---
tags: [mobile, android, ios, network, tls, pinning, pentesting]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.12 Network Interception and SSL Pinning Bypass"
---

# Network Interception and SSL Pinning Bypass

## Introduction
Most of a mobile app's interesting behaviour — authentication, data sync, the backend API — happens over the network, so **intercepting the app's traffic** is essential to testing. Apps that only validate the system CA chain are interceptable once your proxy's CA is trusted ([[03 - Android Testing Environment Setup]], [[05 - iOS Testing Environment and Jailbreak]]). Apps that implement **certificate/public-key pinning** reject your proxy CA, so you must **bypass pinning** at runtime (usually with Frida/objection). This note covers achieving interception and defeating pinning on both platforms — and why pinning is a speed bump, not a security control against a determined tester.

## Getting Interception Working
```text
   1. Trust your proxy CA (system store on Android 7+, full-trust
      profile on iOS) -> see env-setup notes
   2. Route app traffic to the proxy (WiFi proxy / adb reverse /
      transparent redirect for apps ignoring system proxy)
   3. If traffic still fails -> the app is PINNING -> bypass below
   4. If app ignores proxy entirely -> force proxy via Frida or use
      a VPN-based interceptor
```
Symptoms of pinning: handshake errors, "network error" only when the proxy is on, traffic visible in proxy as TLS-alert/connection-reset.

## How Pinning Works (and where to break it)
Pinning hardcodes the expected server cert or public key and rejects anything else (even a "valid" CA chain that includes your proxy). It can be implemented at several layers — each a bypass target:
```text
+---------------------------------------------------------------+
|                  PINNING IMPLEMENTATION LAYERS               |
+---------------------------------------------------------------+
| Android: Network Security Config <pin-set>                    |
|          OkHttp CertificatePinner                            |
|          TrustManager / X509TrustManager custom checks       |
|          native (.so) pinning ([[07 ...]])                    |
| iOS:     URLSession delegate (didReceiveChallenge)            |
|          TrustKit / AFNetworking pinning                     |
|          native pinning                                      |
+---------------------------------------------------------------+
```

## Bypass Techniques
### 1. objection / Frida one-liner (fastest)
```bash
objection -g com.target.app explore        # then:
android sslpinning disable
# iOS:
ios sslpinning disable
# or a generic Frida script (e.g. the well-known "universal" pinning bypass)
frida -U -f com.target.app -l frida-multiple-unpinning.js --no-pause
```
These hook the common pinning APIs (OkHttp `CertificatePinner`, `TrustManager`, `SSLContext`, iOS `SecTrustEvaluate`/`URLSession` delegates) and force them to accept the proxy cert.

### 2. Patch the config / bytecode (no Frida)
- **Android Network Security Config**: repackage the APK trusting user CAs and removing `<pin-set>` ([[06 - APK Decompilation and Smali Patching]]).
- **Smali patch**: neuter the pinning method to return success.

### 3. Native pinning
If pinning is in a `.so`, hook the native function (e.g. the cert-compare or `SSL_CTX_set_verify`) with Frida ([[07 - Reversing Android Native Libraries]]) — static config/bytecode patches won't touch it.

### 4. Hook the verification result
Generic approach: hook whatever function returns the pinning verdict and force "valid," regardless of implementation.

## After Interception
Once you can read/modify traffic, the assessment expands to the **backend API** — the highest-value target. Test auth, IDOR/BOLA, injection, rate limits, and business logic against the live API (feeds the API Security module). The mobile client is often just the doorway.

## Why It Matters
Without interception you're blind to the app's real behaviour; pinning is the wall between you and that visibility, and bypassing it is routine. The deeper point: pinning protects users against *network* MITM (rogue WiFi, corporate proxies) but does **not** protect the app from its own user/owner running Frida — so the API must enforce security independently.

## Defensive Notes
- **Do pin** (it genuinely stops network MITM and casual interception) — prefer public-key pinning with backup pins and a rotation plan; layer with native implementation + anti-Frida ([[16 - Anti-Instrumentation and Attestation Bypass]]).
- Treat pinning/root-detection as **resilience speed bumps**; enforce real authn/authz/rate-limiting **server-side** — assume a determined attacker sees and replays all client traffic.
- Use **App Attest / Play Integrity** for stronger (still not absolute) device/app integrity signals server-side.

## Related Notes
- [[03 - Android Testing Environment Setup]]
- [[05 - iOS Testing Environment and Jailbreak]]
- [[06 - APK Decompilation and Smali Patching]]
- [[07 - Reversing Android Native Libraries]]
- [[16 - Anti-Instrumentation and Attestation Bypass]]
