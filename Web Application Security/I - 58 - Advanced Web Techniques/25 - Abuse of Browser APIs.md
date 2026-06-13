---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.25 Abuse of Browser APIs"
---

# Abuse of Browser APIs

## Introduction
Modern web browsers are incredibly powerful platforms, offering a vast array of APIs (Application Programming Interfaces) that allow web applications to interact with the underlying operating system, hardware, and network environment. While these APIs enable rich web experiences (like video conferencing, offline storage, and Bluetooth device management), they also introduce significant attack surfaces.

"Abuse of Browser APIs" refers to techniques where attackers leverage these legitimate built-in functions—often via Cross-Site Scripting (XSS) or malicious websites—to exfiltrate sensitive data, track users, exhaust resources, or interact with local network devices in unintended ways.

## Technical Deep Dive

### 1. WebRTC (Web Real-Time Communication) Abuse
WebRTC allows peer-to-peer audio, video, and data sharing between browsers without plugins.
**The Threat:** WebRTC can leak a user's real, internal IP address, even if they are behind a VPN or NAT.
**The Exploit:** An attacker uses the `RTCPeerConnection` API to create a connection. During the ICE (Interactive Connectivity Establishment) candidate gathering process, the browser queries local interfaces and STUN servers. By parsing the generated SDP (Session Description Protocol), the attacker extracts the internal IP (e.g., `192.168.1.5`).

```javascript
// Simplified WebRTC IP Leak
let pc = new RTCPeerConnection({iceServers: []});
pc.createDataChannel("");
pc.createOffer().then(offer => pc.setLocalDescription(offer));
pc.onicecandidate = function(ice) {
    if (ice && ice.candidate && ice.candidate.candidate) {
        let ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
        let match = ipRegex.exec(ice.candidate.candidate);
        if (match) {
            console.log("Leaked IP: " + match[1]);
            // Send to attacker C2
        }
    }
};
```
*Note: Modern browsers have implemented mDNS to obscure local IPs, but misconfigurations or older browsers remain vulnerable.*

### 2. Web Bluetooth & Web USB API Abuse
These APIs allow web pages to communicate directly with nearby Bluetooth devices or connected USB devices.
**The Threat:** If a user is tricked into granting permission, an attacker can interact with vulnerable physical devices (e.g., unlocking a smart lock, extracting data from a fitness tracker, or flashing malicious firmware to a USB device).
**Defense:** These APIs require secure contexts (HTTPS), user gesture requirements (must be triggered by a click), and a native browser prompt. However, social engineering ("Click 'Allow' to update your mouse drivers") is highly effective.

### 3. Geolocation API
`navigator.geolocation.getCurrentPosition()` provides precise GPS coordinates of the user.
**The Threat:** Tracking and stalking. If an application suffers from XSS, the attacker can silently request geolocation (if permission was previously granted to the site) and track the user's movements continuously.

### 4. MediaDevices API (Camera/Microphone)
`navigator.mediaDevices.getUserMedia()` accesses the camera and mic.
**The Threat:** Covert surveillance. Similar to geolocation, if a site already has permission (e.g., a vulnerable video conferencing app), an injected XSS payload can silently record audio/video and stream it to a C2 server via WebSockets without triggering a new permission prompt, though the browser's recording indicator (red dot) will usually illuminate.

### 5. Web Share API
`navigator.share()` invokes the native sharing mechanism of the OS.
**The Threat:** Phishing and malware distribution. An attacker can use this API to prompt the user to share a malicious link or file via their native apps (WhatsApp, SMS, Email), lending false credibility to the malicious payload because the prompt comes from the OS itself.

### ASCII Diagram: API Abuse via XSS

```text
+-----------------------+
| Victim Browser        |
| (Trusted Site)        |
|                       |
|  [ XSS Payload ]      |
|         |             |
|         v             |
|  Query Permissions    |---> (If already granted for Camera/Location)
|         |             |
|         v             |
|  Invoke navigator.    |
|  geolocation /        |
|  mediaDevices         |
|         |             |
|         v             |
|  Extract Data         |---> [ GPS Coords, Audio Blob, Local IP ]
|         |             |
|         v             |
|  Fetch API (Exfil)    |=================> +-----------------------+
+-----------------------+                   | Attacker C2 Server    |
                                            | (Receives sensitive   |
                                            |  hardware/env data)   |
                                            +-----------------------+
```

### 6. CacheStorage & IndexedDB Abuse
These APIs provide massive amounts of client-side storage.
**The Threat:**
- **Resource Exhaustion (Storage DoS):** An attacker can silently fill the user's hard drive by continuously writing junk data to IndexedDB.
- **Cache Poisoning:** Overwriting legitimate application assets in the CacheStorage API to achieve persistent XSS (often chained with Service Workers).

### 7. Credential Management API
This API allows web apps to store and retrieve passwords and federated credentials.
**The Threat:** If an attacker achieves XSS on a login page, they can intercept the `navigator.credentials.store()` call to steal the plaintext password before it is hashed or sent over the network, or use `navigator.credentials.get()` to silently log the user in and hijack the session.

### Mitigation and Defense strategies

1. **Permissions Policy (formerly Feature Policy):**
   This is the primary defense mechanism against API abuse. The `Permissions-Policy` HTTP response header allows site administrators to explicitly declare which APIs can be used in the document and in embedded iframes.
   
   *Example:* `Permissions-Policy: geolocation=(), microphone=(), camera=(), usb=()`
   This completely disables geolocation, microphone, camera, and USB access for the site, neutralizing any XSS payload attempting to use them.

2. **Strict Content Security Policy (CSP):**
   While CSP doesn't stop API calls directly, it prevents the exfiltration of the stolen data. If an XSS payload grabs the user's location, a strict CSP will block the `fetch()` or `XMLHttpRequest` required to send that data to the attacker's server.

3. **Secure Contexts:**
   Most powerful APIs (WebCrypto, Service Workers, Bluetooth, USB, Camera) are restricted to Secure Contexts (HTTPS). Ensuring HTTPS everywhere reduces the risk of network-level MitM attackers injecting API abuse payloads.

4. **User Awareness and Prompt Fatigue:**
   Browsers rely heavily on user consent prompts. Training users to deny unexpected hardware requests is crucial, as technical controls can be bypassed via social engineering.

### Testing Methodology
During a VAPT engagement, assessing API abuse involves:
1. **Header Analysis:** Checking for the presence and configuration of the `Permissions-Policy` header.
2. **XSS Escalation:** If XSS is discovered, attempting to escalate the impact by reading `navigator.permissions` to see what hardware access the current origin possesses.
3. **Reviewing Third-Party Iframes:** Ensuring that iframes (e.g., ads, widgets) are sandboxed and do not have unneeded `allow` attributes (e.g., `allow="camera; microphone"`).

## Chaining Opportunities
- **Cross-Site Scripting (XSS):** The ultimate gateway. API abuse is the *payload* delivered via XSS.
- **Clickjacking:** Used to trick users into granting permissions (e.g., aligning a fake "Play Game" button over the browser's native "Allow Camera" prompt).
- **Service Workers:** Malicious service workers rely heavily on the Cache and Fetch APIs to maintain persistence and control.

## Related Notes
- [[04 - Cross-Site Scripting (XSS)]]
- [[08 - Clickjacking]]
- [[24 - Service Worker Attacks]]
