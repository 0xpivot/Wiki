---
tags: [mobile, android, ios, secrets, pentesting]
difficulty: beginner
module: "50 - Mobile Application Security"
topic: "50.13 Hardcoded Secrets and Sensitive Data Leakage"
---

# Hardcoded Secrets and Sensitive Data Leakage

## Introduction
Because the app binary is fully in the attacker's hands, **any secret embedded in it is recoverable** — API keys, cloud credentials, signing keys, encryption keys, third-party tokens, and backend URLs. Developers repeatedly hardcode these (in code, resources, configs, or native libs) assuming compilation/obfuscation hides them; it doesn't. Separately, apps **leak** sensitive data at runtime through logs, error messages, analytics, and clipboard. This note covers finding embedded secrets and runtime leakage — among the quickest wins in any mobile assessment.

## Where Secrets Hide
```text
+---------------------------------------------------------------+
|                  HARDCODED-SECRET LOCATIONS                  |
+---------------------------------------------------------------+
|  Android: strings.xml / res/raw / assets/ / BuildConfig /     |
|           gradle-injected fields / classes.dex / .so libs     |
|  iOS:     Info.plist / embedded plists / strings in Mach-O /  |
|           embedded frameworks                                 |
|  Both:    config/JSON in assets, .env-style files, firebase   |
|           config, OAuth client secrets, signing keys          |
+---------------------------------------------------------------+
```

## Hunting Secrets (static)
```bash
# decompile first ([[06 ...]]), then grep broadly
grep -rEi 'api[_-]?key|secret|token|password|passwd|aws_|AKIA[0-9A-Z]{16}|bearer|private[_-]?key|BEGIN (RSA|EC|PRIVATE)' app_src/
# resources & assets specifically
find app_src/res app_src/assets -type f | xargs grep -rEi 'key|secret|http' 2>/dev/null
# native libraries
strings -a lib/arm64-v8a/*.so | grep -Ei 'key|secret|http|AKIA'
# iOS
strings -a Payload/App.app/App | grep -Ei 'key|secret|AKIA|https?://'
plutil -p Payload/App.app/Info.plist
# automated scanners
# - mobsf (static analysis), apkleaks, trufflehog on the extracted files
```
High-value finds: **cloud keys** (AWS/GCP/Azure → pivot to cloud, see Cloud module), **third-party API keys** (maps/payments/SMS — abuse/quota theft), **Firebase config** (test for open databases/buckets), **OAuth client secrets**, and **backend base URLs** (expand the attack surface).

## Firebase / Backend Misconfig from Config
A common chain: the app embeds a **Firebase** config → test the database/storage for open rules:
```bash
# from google-services.json / Info.plist firebase config -> project URL
curl https://<project>.firebaseio.com/.json        # open Realtime DB?
# also test default open Firebase Storage buckets / Firestore rules
```

## Runtime Leakage
```text
   Logs:      adb logcat / NSLog -> tokens, PII printed in debug builds
   Errors:    verbose stack traces / debug screens exposing internals
   Analytics: PII/tokens sent to 3rd-party SDKs (intercept to confirm)
   Clipboard: copying secrets to the shared clipboard ([[17 ...]])
   Caches:    HTTP/WebView caches, app-switcher screenshots ([[08 ...]])
   Backups:   secrets included in device backups ([[08 ...]])
```
Exercise the app while watching `logcat`/console and the intercepting proxy to catch tokens/PII in logs, analytics calls, and crash reports.

## Why It Matters
A recovered cloud key or third-party token can pivot far beyond the app — into cloud infrastructure, paid-API quota theft, or other users' data — and embedded secrets are trivially found with a grep. Runtime leakage exposes session tokens and PII to anyone with the device or local logs. These are low-effort, high-impact, and consistently present.

## Defensive Notes
- **Don't embed secrets**; fetch short-lived, scoped credentials from the backend at runtime; keep client secrets server-side. Restrict/scope any unavoidable client API keys (referrer/bundle restrictions, minimal scope).
- Rotate keys that must ship; assume any shipped secret is public.
- Strip debug logging from release builds; lock down Firebase rules and cloud bucket/DB permissions; vet third-party SDK data flows.
- Scan builds in CI for secrets (truffleHog/MobSF) before release.

## Related Notes
- [[06 - APK Decompilation and Smali Patching]]
- [[07 - Reversing Android Native Libraries]]
- [[08 - Insecure Data Storage]]
- [[17 - UI Redress Tapjacking Overlays and Pasteboard Leakage]]
