---
tags: [stego, text, documents, forensics, ctf, pentesting]
difficulty: intermediate
module: "53 - Steganography and Data Hiding"
topic: "53.04 Text and Document Steganography"
---

# Text and Document Steganography

## Introduction
Text and documents hide data in ways that survive plain copy-paste and look completely normal: **invisible Unicode characters** (zero-width spaces), **whitespace patterns** (trailing spaces/tabs), **homoglyphs** (look-alike letters), **linguistic choices**, and — for office documents/PDFs — **metadata, hidden content, embedded objects, and structural slack**. These techniques are increasingly relevant because zero-width and homoglyph stego is used to **fingerprint/watermark text** (e.g. tracing leaked documents or LLM outputs) and to smuggle data through text-only channels. This note covers text and document hiding and detection.

## Text Hiding Techniques
```text
+---------------------------------------------------------------+
|                   TEXT STEGO TECHNIQUES                      |
+---------------------------------------------------------------+
| Zero-width chars   ZWSP/ZWNJ/ZWJ (U+200B/C/D), U+FEFF —       |
|                    invisible; encode bits between visible chars|
| Whitespace         trailing spaces/tabs, line-end patterns     |
|                    (SNOW tool); spaces encode binary           |
| Homoglyphs         Cyrillic 'а' vs Latin 'a' etc. encode data /|
|                    enable spoofing                            |
| Unicode tags/VS    tag chars / variation selectors as a hidden |
|                    channel (used to watermark/smuggle text)    |
| Linguistic         word/synonym choice, capitalization patterns|
+---------------------------------------------------------------+
```
Zero-width and tag-character stego is the basis of invisible **text watermarking** — a document or AI output can carry an invisible per-recipient fingerprint to trace leaks.

## Detecting Text Stego
```bash
# reveal non-printable / non-ASCII characters
xxd file.txt | grep -iE 'e2 80 8b|e2 80 8c|e2 80 8d|ef bb bf'   # ZW chars
hexdump -C file.txt | less
# show trailing whitespace
cat -A file.txt            # '$' marks line ends; spaces/tabs visible
grep -nP ' +$' file.txt    # trailing spaces
# decode SNOW whitespace stego
snow -C file.txt
# online: zero-width / unicode steganography detectors & decoders
```
Look for: characters outside expected ranges, suspicious trailing whitespace, mixed scripts (homoglyphs), and unusually large text files.

## Document Steganography (Office / PDF)
Office files (`.docx`/`.xlsx`/`.pptx`) are ZIP archives; PDFs have layered structure — both hide data in metadata, hidden/white text, embedded objects, and unused structure:
```bash
# Office = zip: unpack and inspect
unzip -l doc.docx; unzip doc.docx -d out && grep -rEi 'flag|http|base64' out
exiftool doc.docx                 # author/metadata/custom props
# PDF
exiftool file.pdf; pdfinfo file.pdf
strings file.pdf | grep -Ei 'flag|base64'
# pdf-parser / peepdf / mutool -> objects, streams, JS, attachments
pdf-parser -a file.pdf
mutool extract file.pdf           # pull embedded files/images
binwalk -e file.pdf               # embedded/appended data
```
```text
   Common document hiding spots:
     - metadata / custom document properties (exiftool)
     - hidden / white / tiny-font text; off-canvas content
     - embedded objects / attachments / images (-> [[02]])
     - data after %%EOF (PDF) or appended to the zip
     - PDF object streams, incremental-update revisions, JS
     - tracked-changes / comments / speaker notes
```

## Why It Matters
Text/document stego passes through text-only and document channels that block binary attachments, and the zero-width/homoglyph variants are actively used to **watermark leaked documents and trace insiders**, and to smuggle prompts/data (overlaps indirect prompt injection — hidden instructions in documents an LLM reads). In forensics/CTF, "the flag is in invisible characters / document metadata" is a recurring pattern.

## Defensive Notes
- **Normalize/sanitize text** at boundaries: strip zero-width and disallowed Unicode, collapse trailing whitespace, normalize to expected scripts (mitigates hidden channels and homoglyph spoofing).
- **Scrub document metadata and hidden content** before publishing (Office "Inspect Document", flatten PDFs, remove tracked changes/attachments).
- Be aware text you publish may be watermarked; check inbound documents for hidden instructions/data (ties to indirect prompt injection in the AI module).

## Related Notes
- [[01 - Steganography Fundamentals and Steganalysis]]
- [[02 - Image Steganography]]
- [[05 - Stego in Malware and Network Channels]]
- [[04 - Indirect Prompt Injection and RAG Poisoning]]
