---
tags: [macos, privesc, code-signing, entitlements, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.06 Code Signing and Entitlements"
---

# Code Signing and Entitlements

## Introduction
Almost every macOS security decision ultimately resolves to one question: **"What code-signing identity and entitlements does this binary have?"** Code signing proves *who* produced a binary and that it hasn't been tampered with; **entitlements** are signed key/value capabilities that grant a binary specific privileges (debug other processes, bypass SIP for installs, access the keychain, run unsigned JIT code, and so on). TCC client identity, Gatekeeper trust, AMFI enforcement, and the sandbox profile all read from this signing data. Understanding it is foundational to every other macOS technique.

## Code Signing Essentials
A Mach-O binary's signature is embedded in a `LC_CODE_SIGNATURE` load command and contains a **Code Directory** (hashes of every page), the signing certificate chain, and the embedded entitlements blob.

```bash
codesign -dvvv /path/bin            # identity, TeamID, CDHash, flags
codesign -d --entitlements - /path/bin   # entitlements (XML)
codesign --verify --deep -vvvv /path/App.app  # integrity check
otool -l /path/bin | grep -A4 LC_CODE_SIGNATURE
```

Key signing **flags** to recognize:
- **`hardened runtime`** — opts the process into extra protections (no unsigned dylibs, no `DYLD_*` injection, no debugger unless `get-task-allow`). Required for notarization.
- **`get-task-allow`** — the process *can be debugged / its task port obtained*. Dev builds set this; if a **shipping** privileged binary has it, that's an injection door (see [[09 - Dangerous Entitlements]]).
- **`library validation`** — only libraries signed by the same Team ID (or Apple) may load, blocking dylib hijacks.
- **`restricted` / platform binary** — Apple system binaries; SIP-protected at runtime.

## Signature Requirements (the "designated requirement")
TCC and XPC peers identify clients not just by path but by a **code-signing requirement** ("must be signed by Team ID XYZ with bundle id com.foo"). This is why simply copying a trusted app's bundle ID isn't enough — the signature must also match. Inspect with:
```bash
codesign -d -r- /path/App.app    # prints the designated requirement string
```

## Entitlements: the Real Privilege Currency
Entitlements are what actually make a binary powerful. Examples that matter for escalation:

| Entitlement | Capability | Abuse |
|---|---|---|
| `com.apple.security.cs.disable-library-validation` | load any dylib | dylib injection into this app |
| `com.apple.security.get-task-allow` | be debugged / task port | inject code, steal its TCC/keychain |
| `com.apple.security.cs.allow-dyld-environment-variables` | honor `DYLD_*` | env-based injection |
| `com.apple.security.cs.allow-unsigned-executable-memory` | JIT / unsigned exec mem | run shellcode in-process |
| `com.apple.private.tcc.allow` | implicit TCC grants | access protected data with no prompt |
| `com.apple.rootless.install[.heritable]` | write SIP-protected paths | SIP bypass (see [[03 ...]]) |
| `com.apple.system-task-ports` / `task_for_pid-allow` | get any process's task port | inject into other processes |

```text
+---------------------------------------------------------------+
|     "POWERFUL TARGET" = signed binary + dangerous entitlement |
+---------------------------------------------------------------+
|  Find apps with:                                              |
|    disable-library-validation  -> dylib hijack candidate      |
|    get-task-allow              -> inject + inherit its rights  |
|    allow-dyld-environment-vars -> DYLD_INSERT_LIBRARIES works  |
|    private.tcc.allow.*         -> free access to user data     |
+---------------------------------------------------------------+
```

## Attacker Workflow
1. **Inventory entitlements** of privileged/Apple/3rd-party apps:
   ```bash
   for b in /Applications/*/Contents/MacOS/*; do
     echo "== $b"; codesign -d --entitlements - "$b" 2>/dev/null
   done
   ```
2. **Match weaknesses to techniques:** library-validation disabled → dylib hijack ([[10 ...]]); `get-task-allow` on a TCC-blessed app → inject and inherit Full Disk Access.
3. **Forge / ad-hoc sign** your own payloads when only *presence* of a signature matters:
   ```bash
   codesign -s - --force --deep ./payload.app      # ad-hoc (no identity)
   codesign -s - --entitlements ent.xml --force ./payload  # claim entitlements
   ```
   Ad-hoc signing satisfies AMFI's "is it signed at all" on some paths, but **not** entitlements that require Apple's private signing — those cannot be self-granted on a SIP/AMFI-enforced system.

## Why It Matters
Code signing/entitlement state determines whether dylib hijacking, DYLD injection, debugger attach, sandbox profile strength, and TCC identity all work. Reading entitlements is the fastest way to find the **one privileged app** that becomes your escalation pivot.

## Defensive Notes
- Ship production apps with the **hardened runtime**, **library validation on**, and **without** `get-task-allow` / `allow-dyld-environment-variables`.
- Request the *minimum* entitlements; never ship `disable-library-validation` unless a plugin model truly requires it (and then sign plugins).
- Audit third-party apps for dangerous entitlements as part of allow-listing.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[07 - AMFI and Launch Constraints]]
- [[09 - Dangerous Entitlements]]
- [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]
- [[05 - Gatekeeper and Quarantine Bypass]]
