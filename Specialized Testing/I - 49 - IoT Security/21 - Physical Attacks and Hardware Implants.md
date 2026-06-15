---
tags: [iot, pentesting, hardware, physical, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.21 Physical Attacks and Hardware Implants"
---

# Physical Attacks and Hardware Implants

## Introduction
When an attacker has **physical access** to a device — a laptop, server, kiosk, IoT/embedded device, or ATM — a class of attacks opens that no software control fully prevents. Physical attacks target the hardware directly: reading memory and disks, abusing high-speed ports, tampering with boot, and implanting malicious hardware. This matters for IoT/embedded devices (often deployed in hostile physical locations), for endpoint threat models ("evil maid," stolen laptops), and for red-team physical engagements. This note surveys the major physical attack classes; the hardware debug interfaces themselves are covered in [[07 - UART JTAG Hardware Debugging Interfaces]] and [[09 - SPI Flash Dumping]].

## Attack Classes
```text
+---------------------------------------------------------------+
|                   PHYSICAL ATTACK CLASSES                    |
+---------------------------------------------------------------+
| Memory remanence  COLD BOOT: RAM retains data for seconds     |
|                   after power-off (longer if chilled) ->       |
|                   reboot to a tiny OS / transplant DIMM ->     |
|                   dump RAM -> recover disk-encryption keys     |
| DMA attacks       PCIe/Thunderbolt/FireWire/ExpressCard have  |
|                   direct memory access -> a malicious device  |
|                   reads/writes RAM (keys, unlock) bypassing OS |
| Evil maid         brief access to tamper boot/firmware ->      |
|                   implant keylogger/bootkit -> capture creds   |
| Disk/chip removal pull the disk/flash, read offline; desolder  |
|                   eMMC/SPI to dump ([[09]])                    |
| Side channel      power analysis (SPA/DPA), EM, timing ->      |
|                   extract crypto keys from the chip            |
| Fault injection   voltage/clock GLITCHING, EM/laser fault ->   |
|                   skip security checks (e.g. bypass secure     |
|                   boot / PIN compare)                          |
| Hardware implants interposers, malicious USB (BadUSB/Rubber    |
|                   Ducky), keyloggers, modified cables/chips    |
+---------------------------------------------------------------+
```

## Key Techniques in Detail
### Cold boot
DRAM contents fade slowly; cooling the chips extends retention to minutes. An attacker power-cycles into a minimal memory-dumping image (or moves the DIMM to another machine) and scans RAM for **disk-encryption keys** (BitLocker/FileVault/LUKS), unlocking an otherwise-encrypted disk. Defeated by RAM scrubbing on boot, soldered RAM, and TPM+PIN.

### DMA attacks
Ports with **direct memory access** (Thunderbolt, PCIe, FireWire, ExpressCard) let a connected device read/write system RAM without CPU mediation — bypassing the OS and lock screen to extract keys or inject code. Mitigated by **IOMMU/VT-d**, Kernel DMA Protection, and disabling unused DMA ports / pre-boot DMA.

### Fault injection / glitching
Briefly disturbing **voltage or clock**, or using EM/laser pulses, can cause the CPU to skip an instruction — e.g. skip a signature check, a PIN comparison, or a secure-boot gate. A core technique for defeating embedded **secure boot** ([[23 - Secure Boot and Bootloader Testing]]) and reading locked microcontrollers.

### Side-channel
Measuring **power consumption** (SPA/DPA), electromagnetic emission, or timing during crypto operations leaks key material — extracting keys from smartcards, HSMs, and embedded crypto without breaking the algorithm.

## Why It Matters
Physical access changes the threat model entirely: "encrypted disk" and "secure boot" assume the attacker can't read RAM, glitch the CPU, or probe the chip. For IoT/embedded devices deployed in the field (meters, kiosks, cameras, automotive, medical), physical attacks are realistic and often the *intended* research path; for endpoints, cold-boot/DMA/evil-maid define the "lost or unattended device" risk.

## Defensive Notes
- **Disk encryption with TPM + PIN/pre-boot auth**; scrub RAM on boot; soldered RAM where feasible (mitigates cold boot).
- Enable **IOMMU/VT-d / Kernel DMA Protection**; disable unused DMA-capable ports (Thunderbolt/FireWire) and pre-boot DMA.
- **Tamper-evidence/response** (seals, mesh, tamper switches that zeroize keys); secure boot + measured boot; epoxy/shielding and constant-time crypto against side channels; glitch detection.
- Port lockdown, USB device control (block BadUSB), and physical security for field-deployed devices.

## Related Notes
- [[07 - UART JTAG Hardware Debugging Interfaces]]
- [[09 - SPI Flash Dumping]]
- [[22 - Escaping Kiosk and Locked-Down GUI Applications]]
- [[23 - Secure Boot and Bootloader Testing]]
