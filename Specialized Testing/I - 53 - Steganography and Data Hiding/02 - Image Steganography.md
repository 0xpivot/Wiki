---
tags: [stego, images, forensics, ctf, pentesting]
difficulty: intermediate
module: "53 - Steganography and Data Hiding"
topic: "53.02 Image Steganography"
---

# Image Steganography

## Introduction
Images are the most common steganography carrier: large, full of redundancy the human eye can't perceive, and everywhere on the internet. Data can be hidden in an image's **least-significant bits**, its **metadata**, its **transform coefficients** (JPEG DCT), its **color palette**, or simply **appended after the image data**. This note covers the image-specific hiding techniques and the tooling to detect and extract them, building on the workflow in [[01 - Steganography Fundamentals and Steganalysis]].

## Hiding Techniques
```text
+---------------------------------------------------------------+
|                 IMAGE STEGO TECHNIQUES                       |
+---------------------------------------------------------------+
| LSB (spatial)   replace least-significant bit(s) of pixel RGB |
|                 values -> imperceptible color change (PNG/BMP)|
| DCT (transform) embed in JPEG DCT coefficients (survives JPEG |
|                 compression) -> steghide, JSteg, F5          |
| Palette         manipulate indexed-color palette (GIF/PNG-8)  |
| Metadata        EXIF/comment fields hold text/base64          |
| Appended data   payload after the IEND/EOI marker            |
| Bit-plane       hide in specific bit planes / channels         |
| Color/alpha     data in the alpha channel or one color plane  |
+---------------------------------------------------------------+
```

## Extraction Workflow
```bash
# 1. surface + structure first
file img.png; exiftool img.png            # metadata, comments
binwalk -e img.png                        # appended/embedded files
strings -n 8 img.png | grep -Ei 'flag|base64|http|=$'
xxd img.png | tail                         # data after IEND?

# 2. PNG/BMP LSB & bit-planes
zsteg -a img.png                          # tries many LSB/bit-plane configs
# stegsolve (GUI): cycle color planes / bit planes / data extract

# 3. JPEG (DCT) — usually password-based tools
steghide info img.jpg                      # detect steghide payload
steghide extract -sf img.jpg -p PASS       # extract with passphrase
stegseek img.jpg wordlist.txt              # brute-force steghide passphrase (fast)

# 4. online all-in-one
# aperisolve / StegOnline run many of the above at once
```

## Tool Cheatsheet
```text
   zsteg        PNG/BMP LSB + bit-plane + channel detection (best first
                pass for PNG/BMP)
   steghide     embed/extract in JPG/BMP/WAV/AU, passphrase + encryption
   stegseek     ultra-fast steghide passphrase cracker (use rockyou)
   stegsolve    GUI: view bit planes, color channels, XOR, data extract
   exiftool     metadata read/write
   pngcheck     PNG structure / anomalies / extra chunks
   binwalk      carve embedded/appended files
   foremost     file carving by signature
```

## Detection Signals
```text
   - LSB statistical anomalies (zsteg/chi-square) -> hidden data likely
   - JPEG double-compression / abnormal DCT histograms -> JSteg/F5
   - file larger than expected for its visual content
   - extra PNG chunks / data after IEND/EOI
   - steghide/OpenStego signatures
```

## Why It Matters
Image stego is the default covert channel for hiding payloads (exfil, malware config/C2 — [[05 - Stego in Malware and Network Channels]]) and the most frequent CTF/forensics carrier. The extraction workflow — metadata → carve → LSB/zsteg → steghide+crack — resolves the large majority of image stego challenges and surfaces real hidden data in investigations.

## Defensive Notes
- **Re-encode/transcode uploaded images** at the boundary (resize/re-compress) — destroys LSB and most DCT payloads; **strip metadata**.
- Flag images whose size is disproportionate to content, that contain data after EOI/IEND, or that match known stego-tool signatures.
- Apply DLP to outbound images and monitor for automated image uploads consistent with exfil.

## Related Notes
- [[01 - Steganography Fundamentals and Steganalysis]]
- [[03 - Audio and Video Steganography]]
- [[05 - Stego in Malware and Network Channels]]
- [[04 - Data Exfiltration Techniques]]
