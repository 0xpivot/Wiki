---
tags: [iot, pentesting, hardware, firmware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.24 Firmware Integrity and Update Verification"
---

# Firmware Integrity and Update Verification

## Introduction
A device's security depends on it running **authentic, unmodified firmware** — at boot ([[23 - Secure Boot and Bootloader Testing]]) and across **updates**. Firmware integrity covers how a device verifies firmware images (signatures, hashes, encryption) and how its **update mechanism** delivers and validates new firmware. Weaknesses here let an attacker flash malicious firmware, downgrade to vulnerable versions, or intercept/forge updates — persistent, below-the-OS compromise. This note focuses on assessing firmware-image integrity and the update pipeline, complementing the insecure-update note ([[06 - Insecure Update Mechanisms]]) with the cryptographic/integrity angle.

## Firmware Integrity Mechanisms
```text
+---------------------------------------------------------------+
|              FIRMWARE INTEGRITY CONTROLS                     |
+---------------------------------------------------------------+
| Signature        firmware signed by vendor key; device        |
|                  verifies before boot/flash (root in OTP)     |
| Hash/checksum    integrity check (CRC/SHA) — integrity only,  |
|                  NOT authenticity (forgeable if unsigned)     |
| Encryption       firmware image encrypted (confidentiality);  |
|                  key on device -> may be extractable          |
| Anti-rollback    monotonic version counter blocks downgrade    |
| Measured boot    hashes extended into TPM/SE for attestation  |
+---------------------------------------------------------------+
```
A frequent flaw: a device checks a **CRC/hash** (integrity) but not a **signature** (authenticity) — so an attacker recomputes the checksum after modifying the image and the device accepts it.

## Common Weaknesses
```text
   - UNSIGNED firmware: accepts any image with a valid checksum ->
     flash a backdoored image directly
   - WEAK/leaked signing keys; test keys accepted in production
   - signature covers only PART of the image (header signed, body not)
   - update over HTTP / no TLS / no cert pinning -> MITM the update,
     serve malicious firmware ([[06]])
   - no ANTI-ROLLBACK -> downgrade to an old signed but vulnerable
     version, then exploit it
   - encrypted firmware whose KEY is on the device/extractable
     (defeats confidentiality and aids forging)
   - update auth bypass: predictable URLs, no auth on update endpoint,
     client-controlled "current version"
```

## Testing Workflow
```text
1. OBTAIN firmware: vendor download, OTA capture, or dump from flash
   ([[02 - IoT Device Firmware Extraction]], [[09 - SPI Flash Dumping]]).
2. ANALYZE the image (binwalk/extract -> [[03]]): is it encrypted?
   signed? where are the signature/hash and where do keys live?
3. TEST integrity enforcement: modify the firmware, fix the checksum,
   attempt to flash/boot it. Does the device accept an UNSIGNED change?
4. TEST the update channel: is it TLS + pinned + authenticated? Can you
   MITM and serve a forged image? ([[06]])  Replay/downgrade possible
   (anti-rollback)?
5. KEYS: hunt signing/decryption keys in the firmware/flash; assess
   whether you can forge a valid image.
6. Combine with secure-boot testing ([[23]]) for the full boot+update
   trust picture.
```

## Why It Matters
The update mechanism is a powerful — and frequently weak — path to **persistent firmware compromise** affecting potentially the entire fleet of a device model. Unsigned/CRC-only firmware, MITM-able update channels, and missing anti-rollback are extremely common in IoT/embedded products, and a malicious firmware flash sits below the OS, surviving resets and evading host defenses. It's a top finding in IoT assessments.

## Defensive Notes
- **Sign firmware** with a key rooted in OTP and verify the **full** image's signature (authenticity, not just a CRC) before flashing and at boot; reject unsigned/modified images.
- **Secure the update channel**: HTTPS + certificate pinning + authenticated update server; verify the signature on-device regardless of transport.
- **Anti-rollback** (monotonic versioning) to block downgrade attacks; protect/rotate signing keys; don't ship decryption keys recoverable from the device.
- Tie into secure/measured boot ([[23]]) and attestation so tampered firmware is detected; provide a secure recovery path.

## Related Notes
- [[06 - Insecure Update Mechanisms]]
- [[23 - Secure Boot and Bootloader Testing]]
- [[02 - IoT Device Firmware Extraction]]
- [[03 - Firmware Analysis and Reverse Engineering]]
