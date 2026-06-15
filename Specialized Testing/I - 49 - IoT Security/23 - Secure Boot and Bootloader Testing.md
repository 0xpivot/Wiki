---
tags: [iot, pentesting, hardware, secure-boot, firmware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.23 Secure Boot and Bootloader Testing"
---

# Secure Boot and Bootloader Testing

## Introduction
**Secure boot** is the chain of trust that ensures a device only runs authenticated firmware/OS, starting from an immutable **root of trust** (boot ROM) and verifying each subsequent stage's signature before executing it. On embedded/IoT/mobile devices this is the barrier between "load my own firmware/get root" and "locked device" — so testing it is central to embedded security research. The **bootloader** (U-Boot on Linux embedded, ABL/LK on Android, etc.) is both the enforcer of this chain and a rich attack surface in its own right. This note covers the secure-boot chain, bootloader attack surface, and how the chain is broken in practice.

## The Chain of Trust
```text
+---------------------------------------------------------------+
|                  SECURE BOOT CHAIN                           |
+---------------------------------------------------------------+
|  Boot ROM (immutable, root of trust; keys fused in OTP)       |
|     | verifies signature of ->                                |
|  Bootloader stage 1 (e.g. SPL / preloader)                    |
|     | verifies ->                                             |
|  Bootloader stage 2 (U-Boot / ABL / LK)                       |
|     | verifies ->                                             |
|  Kernel / OS image                                            |
|     | (measured boot also EXTENDS hashes into a TPM/secure    |
|     |  element for attestation)                               |
+---------------------------------------------------------------+
|  Break ANY link (skip/forge a verification) -> run your code  |
+---------------------------------------------------------------+
```
Signatures are checked against keys rooted in **one-time-programmable (OTP/eFuse)** memory, so the root key can't be changed in software.

## Bootloader Attack Surface
```text
   - U-Boot console: if accessible (over UART -> [[07]]), the env
     and commands allow loading/booting arbitrary images, reading/
     writing memory & flash, dumping the kernel/keys
   - U-Boot environment variables: modify bootargs (add init=/bin/sh,
     disable verification flags) if env is writable
   - "fastboot"/download modes (Android): flashing, unlock states,
     OEM commands — often less hardened than runtime
   - command injection / parsing bugs in the bootloader's image,
     DTB, or command handling
   - leftover debug/test commands, hidden key combos to enter modes
```
A bootloader console (frequently reachable by interrupting boot over **UART** — see [[07 - UART JTAG Hardware Debugging Interfaces]]) is often the fastest path to dumping firmware ([[02 - IoT Device Firmware Extraction]]) and to booting unsigned code if verification can be disabled.

## How Secure Boot Gets Broken
```text
+---------------------------------------------------------------+
|              SECURE-BOOT BYPASS TECHNIQUES                   |
+---------------------------------------------------------------+
| Verification    a stage that fails to actually check the next |
| flaw            stage's signature (logic bug), or checks the   |
|                 wrong/partial region                          |
| Unsigned region a portion loaded/executed before verification |
|                 (e.g. a header/DTB/loadable parsed pre-check)  |
| Fault injection voltage/clock GLITCHING to skip the signature  |
|                 check instruction ([[21]]) — common on MCUs    |
| Downgrade       boot an older, signed-but-vulnerable image     |
|                 (no anti-rollback)                            |
| Key/keystore    leaked/weak signing keys; test keys left       |
| issues          enabled; modifiable key storage               |
| BootROM exploit memory-corruption in the immutable ROM (e.g.  |
|                 checkm8) -> unpatchable root compromise        |
+---------------------------------------------------------------+
```
Real examples span all of these: MediaTek "download agent" hash-bypass and Android `bl2_ext` secure-boot bypass-to-EL3 are bootloader/secure-boot verification flaws; checkm8 is a BootROM bug; glitching routinely defeats MCU secure boot.

## Testing Workflow
```text
1. Get a console: UART -> interrupt autoboot -> U-Boot/bootloader prompt
   ([[07]]); enumerate commands, env, versions.
2. Try to boot unsigned: can you load your own image / modify bootargs
   (init=/bin/sh) / disable verification? Is the env writable?
3. Map the chain: which stage verifies which? any pre-verification
   parsing (headers/DTB)? downgrade/anti-rollback present?
4. Dump firmware for offline analysis ([[02]],[[03]]); extract keys.
5. Advanced: fault-injection/glitching to skip checks ([[21]]); look
   for known BootROM/loader CVEs for the SoC.
```

## Why It Matters
Secure boot is what stops attackers from persisting malicious firmware and from trivially rooting a device for analysis. Breaking it enables loading custom firmware, dumping protected secrets/keys, defeating anti-tamper, and persistent implants below the OS. It's the linchpin of embedded device security — and SoC/bootloader verification flaws (plus glitching) break it regularly.

## Defensive Notes
- Verify **every** stage's full signature against a key rooted in OTP **before** execution; verify *before* parsing untrusted structures (no pre-verification code paths).
- **Anti-rollback** (monotonic version counters) to block downgrade; disable test keys, debug/fastboot OEM commands, and bootloader consoles in production; lock the env.
- Glitch-hardening (redundant checks, randomization, voltage/clock monitors); protect/rotate signing keys; keep boot ROM/loader patched for known SoC CVEs.
- Combine with measured boot + attestation so a broken chain is detectable server-side.

## Related Notes
- [[07 - UART JTAG Hardware Debugging Interfaces]]
- [[02 - IoT Device Firmware Extraction]]
- [[21 - Physical Attacks and Hardware Implants]]
- [[24 - Firmware Integrity and Update Verification]]
