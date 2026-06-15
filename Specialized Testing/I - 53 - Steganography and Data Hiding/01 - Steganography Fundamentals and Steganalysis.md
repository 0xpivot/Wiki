---
tags: [stego, forensics, ctf, pentesting]
difficulty: beginner
module: "53 - Steganography and Data Hiding"
topic: "53.01 Steganography Fundamentals and Steganalysis"
---

# Steganography Fundamentals and Steganalysis

## Introduction
**Steganography** is hiding data *within* other data so that the very existence of the hidden message is concealed — distinct from cryptography, which hides the *meaning* but not the existence. A stego payload rides inside an innocent-looking carrier (image, audio, document, network traffic) so a casual observer sees only the cover. In security work it appears in two places: **offensive/defensive operations** (malware hiding C2 or exfiltration in images/traffic; data exfiltration channels — see [[04 - Data Exfiltration Techniques]]) and **CTF/forensics** (extracting flags or evidence). **Steganalysis** is the detection side. This note frames the concepts and the analysis workflow the rest of the module applies per carrier type.

## Stego vs Crypto vs Obfuscation
```text
+---------------------------------------------------------------+
|  Cryptography  hides MEANING (ciphertext is visibly secret)   |
|  Steganography hides EXISTENCE (looks like an ordinary file)  |
|  Often combined: encrypt THEN hide -> even if found, unreadable|
+---------------------------------------------------------------+
```

## Core Concepts
- **Carrier / cover** — the innocent file (e.g. a JPEG).
- **Payload** — the hidden data.
- **Embedding domain** — *where* data is hidden: spatial/LSB (raw pixel/sample bits), transform domain (DCT coefficients in JPEG), metadata, structural slack (unused/append space), or linguistic (word/whitespace choices).
- **Capacity vs detectability** — more hidden data = more statistical distortion = easier to detect.
- **Passphrase** — many tools encrypt+embed under a password (e.g. `steghide`).

## The Analysis Workflow (carrier-agnostic)
```text
+---------------------------------------------------------------+
|                  STEGANALYSIS WORKFLOW                       |
+---------------------------------------------------------------+
|  1. IDENTIFY    what is the file really?  file, exiftool,     |
|                 binwalk (don't trust the extension)           |
|  2. SURFACE     strings, metadata (exiftool), comments         |
|  3. STRUCTURE   appended data after EOF, embedded files        |
|                 (binwalk, foremost) -> "carve" them out        |
|  4. DOMAIN      carrier-specific tools (LSB/DCT/audio spectrum |
|                 /whitespace) -> [[02]]-[[05]]                  |
|  5. CRACK       password-protected stego -> stegcracker/       |
|                 stegseek + wordlist                           |
|  6. DECODE      payload may be encoded/encrypted -> base64,    |
|                 xor, decrypt                                  |
+---------------------------------------------------------------+
```
```bash
file suspect.jpg                 # real type?
exiftool suspect.jpg             # metadata, comments, GPS
binwalk -e suspect.jpg           # embedded/appended files -> extract
strings -n 8 suspect.jpg | less  # readable strings / base64 blobs
```

## General-Purpose Tools
```text
   binwalk / foremost   carve embedded/appended files (any carrier)
   exiftool             read/write metadata across formats
   strings / xxd        quick surface + hex inspection
   stegseek / stegcracker  brute-force steghide passphrases (fast)
   zsteg (PNG/BMP), steghide (JPG/BMP/WAV/AU), stegsolve (image) -> [[02]]
   Sonic Visualiser / Audacity (audio spectrogram) -> [[03]]
   aperisolve / StegOnline  online all-in-one image stego
```

## Detection (Steganalysis) Signals
```text
   - file size / dimensions unusually large for content
   - statistical anomalies in LSBs (chi-square, RS analysis)
   - JPEG: double-compression / DCT histogram artifacts
   - audio: hidden tones/images visible in a SPECTROGRAM
   - structural: data after the format's EOF marker
   - known-tool signatures (steghide/OpenStego headers)
```

## Why It Matters
Offensively/defensively, stego is a covert channel for **exfiltration and malware C2** that evades content inspection (an image leaving the network looks benign — [[04 - Data Exfiltration Techniques]], [[05 - Stego in Malware and Network Channels]]). In CTF/forensics it's a staple challenge category. Knowing the workflow lets you both *find* hidden data during an investigation and *recognize* stego as an exfil vector to defend against.

## Defensive Notes
- **Content disarm & reconstruction (CDR)** / re-encoding of files at the boundary destroys most embedded payloads (re-save images, strip metadata).
- Monitor for anomalous outbound media uploads and DNS/traffic patterns ([[05]]); apply DLP on volume + entropy, not just keywords.
- Strip metadata from files; flag files whose true type ≠ extension.

## Related Notes
- [[02 - Image Steganography]]
- [[03 - Audio and Video Steganography]]
- [[04 - Text and Document Steganography]]
- [[05 - Stego in Malware and Network Channels]]
- [[04 - Data Exfiltration Techniques]]
