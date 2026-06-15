---
tags: [mobile, android, ios, authentication, biometrics, pentesting, frida]
difficulty: advanced
module: "50 - Mobile Application Security"
topic: "50.15 Biometric Authentication Bypass"
---

# Biometric Authentication Bypass

## Introduction
Apps use fingerprint/face biometrics to gate access (app unlock, payment confirmation, viewing secrets). The security of this gate depends entirely on **how** the biometric result is used. Done correctly, a successful biometric **unlocks a hardware-backed cryptographic key** that's required to decrypt data or sign a transaction — so a bypass is infeasible. Done incorrectly (the common case), biometric auth is just an **"event": a callback that says "success,"** which the app trusts to flip a boolean or proceed — and that callback can be forced with Frida. This note covers the secure vs insecure patterns and how to bypass the insecure ones.

## Secure vs Insecure Patterns
```text
+---------------------------------------------------------------+
|        INSECURE (event-based)  |   SECURE (crypto-bound)       |
+---------------------------------------------------------------+
| onAuthenticationSucceeded() -> |  biometric unlocks a Keystore/|
|   app sets isAuthed=true, or   |  Keychain key (setUserAuth-   |
|   just calls the next screen   |  enticationRequired); that key|
|                                |  decrypts data / signs a      |
| Trust is in the CALLBACK       |  server challenge             |
| -> hook callback => bypass     |  Trust is in the KEY -> forcing|
|                                |  the callback yields nothing  |
|                                |  (no key = no plaintext)      |
+---------------------------------------------------------------+
```
- **Android**: `BiometricPrompt` used **without** a `CryptoObject` (no Keystore key bound) = insecure event. Secure use passes a `CryptoObject` wrapping a Keystore key created with `setUserAuthenticationRequired(true)`.
- **iOS**: `LAContext.evaluatePolicy(...)` result trusted directly = insecure. Secure use stores the secret in the **Keychain** with `SecAccessControl` (`.biometryCurrentSet`/`.userPresence`) so the item is only released after biometric auth — the OS, not the app, enforces it.

## Bypassing the Insecure (Event-Based) Pattern
If the app merely trusts the success callback, force it with Frida:
```javascript
// Android — directly invoke the success callback / force the boolean
Java.perform(() => {
  // e.g. hook the app's onAuthenticationSucceeded handler to always run,
  // or hook its isAuthenticated()/checkBiometric() to return true
  const A = Java.use('com.app.auth.BioManager');
  A.isAuthenticated.implementation = () => true;
});
```
```bash
objection -g com.app explore
ios ui biometrics_bypass        # iOS: hooks LAContext.evaluatePolicy -> success
```
objection's `ios ui biometrics_bypass` hooks `evaluatePolicy` to return success — instantly defeating any app that trusts the LAContext result. On Android, hook the success callback or the app's own "is authenticated" gate.

## Why the Secure Pattern Resists This
When the biometric is **crypto-bound**, forcing the callback gains nothing: the protected data is encrypted under a Keystore/Keychain key that is **only released by the OS after a genuine biometric match in secure hardware (TEE/Secure Enclave)**. No key → no plaintext → no bypass via hooking. This is why the recommendation is always "bind biometrics to a key, don't trust the event."

## Testing Workflow
```text
1. Static: find biometric API usage. Is a CryptoObject / SecAccessControl
   used, or is the success callback / a boolean trusted directly?
2. If event-based -> hook callback/gate with objection/Frida -> bypass.
3. If crypto-bound -> attack elsewhere (the data is protected); check
   whether the SAME data is reachable WITHOUT biometrics (fallback path,
   stored copy, server endpoint) -> often the real weakness.
4. Check fallbacks: device-PIN fallback, "skip", or a plaintext copy.
```

## Why It Matters
Biometric gates protect high-value actions (payments, secret reveal, app unlock). The event-based mistake is widespread and makes the gate trivially bypassable with one Frida hook — turning "biometric-protected" into "not protected" for anyone with the device. Demonstrating it (or confirming the secure pattern) is a core auth finding.

## Defensive Notes
- **Bind biometrics to a hardware-backed key**: Android `BiometricPrompt` + `CryptoObject` with a Keystore key (`setUserAuthenticationRequired`, ideally `StrongBox`); iOS Keychain item with `SecAccessControl` biometric policy. Never trust the bare success callback/`evaluatePolicy` result.
- Protect against fallbacks that bypass biometrics; re-verify server-side for sensitive transactions (sign a server challenge with the biometric-gated key).
- Combine with anti-instrumentation ([[16 - Anti-Instrumentation and Attestation Bypass]]) as defense-in-depth.

## Related Notes
- [[05 - iOS Testing Environment and Jailbreak]]
- [[08 - Insecure Data Storage]]
- [[14 - Root and Jailbreak Detection Bypass]]
- [[16 - Anti-Instrumentation and Attestation Bypass]]
