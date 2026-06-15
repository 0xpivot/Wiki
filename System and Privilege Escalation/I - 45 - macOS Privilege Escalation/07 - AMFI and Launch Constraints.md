---
tags: [macos, privesc, amfi, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.07 AMFI and Launch Constraints"
---

# AMFI and Launch Constraints

## Introduction
**AMFI (AppleMobileFileIntegrity)** is the kernel-and-daemon subsystem that *enforces* code signing and entitlements at runtime. Where [[06 - Code Signing and Entitlements]] describes the data, AMFI is the cop that reads it: it decides whether a binary is allowed to execute, whether its claimed entitlements are legitimate, and whether unsigned/foreign libraries may load. **Launch Environment Constraints** (introduced in macOS 13 Ventura) are a newer layer that pins *where* a binary may be launched from and *who* may launch it, closing a class of "copy an Apple binary somewhere writable and abuse it" attacks.

Together these are the runtime backbone of macOS code trust — and major obstacles to process injection and persistence.

## AMFI: What It Enforces
AMFI runs partly in the kernel (the `AppleMobileFileIntegrity` kext / policy module) and partly as the user-space daemon `amfid`, which validates signatures the kernel hands off.

```text
+---------------------------------------------------------------+
|                  AMFI ENFORCEMENT PATH                        |
+---------------------------------------------------------------+
|  execve(binary)                                               |
|     | kernel hashes code pages, checks Code Directory          |
|     v                                                          |
|  Is signature valid?                                          |
|     | for non-platform binaries kernel asks amfid             |
|     v                                                          |
|  amfid verifies cert chain + entitlements                     |
|     | OK?  -> allow; entitlements honored                      |
|     | bad? -> kill (SIGKILL "Code Signature Invalid")          |
+---------------------------------------------------------------+
|  At runtime also enforces:                                    |
|   - library validation (only same-Team/Apple dylibs)          |
|   - no unsigned executable memory unless entitled             |
|   - DYLD_* ignored unless entitled                            |
+---------------------------------------------------------------+
```

The classic *research* (not remote) attack surface was **`amfid`** itself: because the kernel trusts `amfid`'s verdict, gaining the ability to inject into or MITM `amfid` (e.g. via a debugger entitlement or a task-port primitive) let researchers make it approve arbitrary signatures — a jailbreak-grade primitive. On a patched, SIP-enabled Mac this is not reachable remotely; it illustrates *why* `amfid` and the entitlements that touch it are so sensitive.

`amfi_get_out_of_my_way=1` is a **boot-arg** that disables AMFI entirely — settable only with SIP off and boot control. Finding it set (`nvram boot-args`) means code-signing enforcement is gone:
```bash
nvram boot-args     # look for amfi_get_out_of_my_way / cs_enforcement_disable
```

## Launch Environment Constraints (Ventura+)
Modern Apple binaries ship with **launch constraints** baked into a trust cache, declaring rules such as: *"this binary may only be launched from `/System/...`, only by launchd, and only as a specific identity."* This kills techniques that depended on:
- Copying a privileged Apple binary to a writable path and launching it with a tampered environment.
- Launching a system daemon manually to abuse its entitlements.
- "Process spoofing" where a different binary impersonated a constrained one.

```text
   Pre-Ventura:  cp /usr/sbin/<entitled-bin> /tmp/x; DYLD_... /tmp/x   -> abuse
   Ventura+:     launch constraint says "only from original path, only
                 launched by launchd as identity Y" -> the /tmp copy is
                 refused before it runs.
```
Constraint categories include **self constraints** (where/how the binary may run), **parent constraints** (who may spawn it), and **responsible-process constraints**.

## Attacker Takeaways
- AMFI means you generally **cannot run unsigned code inside a hardened/entitled process**, and **cannot load foreign dylibs** unless the target disabled library validation or holds the relevant entitlement — which is exactly why [[06 - Code Signing and Entitlements]] enumeration is step one.
- The viable injection paths are apps that **opted out**: `disable-library-validation`, `allow-dyld-environment-variables`, `get-task-allow`, or interpreted/Electron apps (see [[12 - Electron Chromium and Interpreted App Injection]]).
- Boot-args disabling AMFI, or SIP off, collapse this entire layer — always check.

## Why It Matters
AMFI + launch constraints are *why* macOS injection is hard. They scope which targets are even attackable and explain why the field has shifted toward abusing entitled/interpreted apps rather than classic shellcode injection.

## Defensive Notes
- Keep SIP enabled and never set `amfi_get_out_of_my_way`; audit `boot-args` fleet-wide.
- Prefer hardened-runtime, library-validated, notarized apps so AMFI can do its job.
- On modern macOS, launch constraints come "for free" on Apple binaries — keep the OS current to benefit.

## Related Notes
- [[06 - Code Signing and Entitlements]]
- [[03 - System Integrity Protection SIP]]
- [[09 - Dangerous Entitlements]]
- [[10 - Dyld Hijacking and DYLD_INSERT_LIBRARIES]]
