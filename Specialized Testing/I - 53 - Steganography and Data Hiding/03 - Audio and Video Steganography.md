---
tags: [stego, audio, video, forensics, ctf, pentesting]
difficulty: intermediate
module: "53 - Steganography and Data Hiding"
topic: "53.03 Audio and Video Steganography"
---

# Audio and Video Steganography

## Introduction
Audio and video files are high-capacity stego carriers. Audio hides data in sample LSBs, in **spectrogram images** (text/pictures drawn in the frequency domain — a CTF favorite), in echo/phase, or via tones (DTMF/SSTV). Video, being a container of image frames plus audio plus metadata, inherits **all image and audio techniques** ([[02 - Image Steganography]]) plus container-level tricks. This note covers analyzing audio/video for hidden data, building on the workflow in [[01 - Steganography Fundamentals and Steganalysis]].

## Audio Hiding Techniques
```text
+---------------------------------------------------------------+
|                  AUDIO STEGO TECHNIQUES                      |
+---------------------------------------------------------------+
| LSB (samples)   hide bits in least-significant bits of PCM    |
|                 samples (WAV) -> steghide, manual             |
| Spectrogram     draw text/image in the frequency spectrum —   |
|                 invisible when listening, visible in a        |
|                 spectrogram view (very common in CTFs)        |
| Echo / phase    encode bits in echo delay or phase shifts     |
| Tones           DTMF (phone tones), SSTV (slow-scan TV ->      |
|                 decodes to an IMAGE), Morse                   |
| Metadata        ID3 tags / container comments                 |
| Appended data   payload after audio stream                    |
+---------------------------------------------------------------+
```

## Audio Analysis Workflow
```bash
file a.wav; exiftool a.wav               # type, ID3/metadata
binwalk -e a.wav; strings a.wav          # embedded/appended + strings
steghide extract -sf a.wav -p PASS       # WAV/AU steghide payload
stegseek a.wav wordlist.txt              # brute-force passphrase
```
```text
   SPECTROGRAM (the key audio technique):
     - Audacity: open file -> track menu -> Spectrogram view
     - Sonic Visualiser: add Spectrogram layer
     - look for text/shapes hidden in the high frequencies
   TONES:
     - SSTV -> decode with QSSTV / RX-SSTV to recover an image
     - DTMF -> decode tones to digits
     - Morse -> decode by ear/tool
```
Always **look at the spectrogram** for any CTF audio file — hidden text/images there are extremely common and invisible to the ear.

## Video Analysis Workflow
Video = frames + audio + container, so decompose first:
```bash
ffprobe v.mp4                            # streams, codecs, metadata
exiftool v.mp4                           # container metadata
ffmpeg -i v.mp4 frames/%05d.png          # extract frames -> image stego ([[02]])
ffmpeg -i v.mp4 audio.wav                # extract audio -> audio analysis above
binwalk -e v.mp4; strings v.mp4          # embedded files / appended data
# inspect individual frames (a single frame may hold the payload/QR)
```
Then apply [[02 - Image Steganography]] to the frames and the audio techniques above to the soundtrack; check for an odd frame (hidden QR code/text), subtitle tracks, and container metadata.

## Detection Signals
```text
   - audible artifacts / hidden content visible only in spectrogram
   - file size disproportionate to duration/quality
   - extra/odd streams (subtitles, data tracks) or container metadata
   - data appended after the media stream
   - a single anomalous video frame
```

## Why It Matters
Audio/video carry large payloads and the spectrogram/SSTV tricks are staple CTF and forensics challenges; in operations, media files are a plausible-looking exfil/C2 carrier ([[05 - Stego in Malware and Network Channels]]). Knowing to decompose video into frames+audio and to *view the spectrogram* resolves most of these quickly.

## Defensive Notes
- **Transcode/re-encode** media at the boundary to destroy sample-LSB and frame-LSB payloads; strip metadata and extra streams.
- Flag media files disproportionately large for their content or carrying unexpected data tracks/appended data.
- DLP/monitoring on outbound media uploads as an exfil channel.

## Related Notes
- [[01 - Steganography Fundamentals and Steganalysis]]
- [[02 - Image Steganography]]
- [[05 - Stego in Malware and Network Channels]]
- [[04 - Data Exfiltration Techniques]]
