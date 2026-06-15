---
tags: [macos, privesc, entitlements, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.09 Dangerous Entitlements"
---

# Dangerous Entitlements

## Introduction
Entitlements are signed capabilities (see [[06 - Code Signing and Entitlements]]). Most are benign, but a handful are **escalation primitives**: if a *privileged or TCC-blessed* binary holds one of them, it becomes a vehicle for injection, code-signing bypass, or unprompted data access. This note is a field guide to the entitlements worth hunting for and how each translates into an attack. The core idea: **you rarely break Apple's enforcement directly; you find the one app Apple's developers entitled too generously and ride it.**

## The High-Value Entitlements
```text
+-------------------------------------------+-----------------------------+
| Entitlement                               | What it unlocks for you     |
+-------------------------------------------+-----------------------------+
| cs.disable-library-validation             | load YOUR dylib into app    |
| cs.allow-dyld-environment-variables       | DYLD_INSERT_LIBRARIES works |
| cs.allow-unsigned-executable-memory       | run shellcode/JIT in-proc   |
| cs.disable-executable-page-protection     | rewrite code pages          |
| get-task-allow                            | grab task port -> inject    |
| com.apple.system-task-ports / task_for_pid| task port of OTHER procs    |
| private.tcc.allow[.*]                      | implicit TCC, no prompt     |
| rootless.install[.heritable]              | write SIP-protected paths   |
| automation.apple-events                   | drive other apps' privileges|
+-------------------------------------------+-----------------------------+
```

### Library-validation / DYLD entitlements
`com.apple.security.cs.disable-library-validation` tells AMFI "let this process load dylibs signed by anyone." Combined with a hijackable load path (see [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]), it means your unsigned dylib runs **inside that app's context** — inheriting its TCC permissions, keychain access, and entitlements. `com.apple.security.cs.allow-dyld-environment-variables` re-enables the `DYLD_*` env vars that are normally stripped, making env-based injection viable.

### `get-task-allow` and task-port entitlements
`get-task-allow` (normal on debug builds, dangerous on shipping privileged apps) lets another process obtain this app's **Mach task port** — full read/write of its memory, i.e. code injection. The `task_for_pid`-style entitlements are the inverse and worse: a binary that can get *other* processes' task ports can inject into more-privileged targets.

### Unsigned executable memory
`cs.allow-unsigned-executable-memory` / `cs.allow-jit` let a process map RWX/unsigned memory — i.e., run shellcode. Browsers and runtimes legitimately need JIT; if a *privileged* helper has it, it's a code-exec primitive once you reach it.

### `private.tcc.allow`
Apple grants some first-party (and rarely third-party) apps **implicit TCC permissions** via `com.apple.private.tcc.allow` with a list of services — these access protected data with **no prompt and no DB row**. Injecting into such an app (via the above primitives) yields its data access for free (chains into [[04 - TCC Transparency Consent and Control]]).

### `rootless.install` / `.heritable`
The SIP-bypass family: an installer daemon entitled to write protected paths, whose capability is **inherited by children** if not dropped, is the recurring SIP-bypass root cause (see [[03 - System Integrity Protection SIP]]).

### Automation / Apple Events
`com.apple.security.automation.apple-events` plus a granted Automation TCC entry lets the app script other apps — pivoting through *their* permissions (drive Finder/Mail to read protected files).

## Hunting Workflow
```bash
# Dump entitlements of every app binary and grep for the dangerous keys
find /Applications /System/Applications -type f -perm +111 2>/dev/null | while read b; do
  ent=$(codesign -d --entitlements - "$b" 2>/dev/null)
  echo "$ent" | grep -qiE 'disable-library-validation|get-task-allow|allow-dyld|unsigned-executable|task-ports|private.tcc|rootless.install' \
    && { echo "=== $b"; echo "$ent" | grep -iE 'library-validation|task|dyld|unsigned|tcc|rootless'; }
done
```
Then map each hit to a technique:

```text
   disable-library-validation  + writable dylib path -> dylib hijack
   get-task-allow              + you can run as user  -> task-port inject
   allow-dyld-environment-vars + writable launch      -> DYLD_INSERT
   private.tcc.allow.*         + injectable           -> free data access
   rootless.install.heritable  + influence its child  -> SIP bypass
```

## Why It Matters
On a modern, patched Mac you usually can't beat AMFI/SIP/TCC head-on. Dangerous entitlements are the **side door**: one over-entitled app converts "I'm a normal user" into injection, data theft, or SIP bypass. Entitlement enumeration is often the highest-yield single step in macOS local privesc.

## Defensive Notes
- Treat the entitlements above as a deny-list in app vetting / allow-listing; flag any third-party app requesting them.
- Never ship production binaries with `get-task-allow`, `disable-library-validation`, or `allow-dyld-environment-variables` unless strictly required, and then constrain them.
- Apple-private entitlements (`com.apple.private.*`) on a non-Apple binary are a red flag — investigate.

## Related Notes
- [[06 - Code Signing and Entitlements]]
- [[07 - AMFI and Launch Constraints]]
- [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]
- [[04 - TCC Transparency Consent and Control]]
- [[03 - System Integrity Protection SIP]]
