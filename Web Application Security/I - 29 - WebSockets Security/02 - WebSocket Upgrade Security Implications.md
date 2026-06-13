---
tags: [vapt, websockets, hijack, intermediate]
difficulty: intermediate
module: "29 - WebSockets Security"
topic: "29.02 WebSocket Upgrade Security Implications"
---

# 29.02 — WebSocket Upgrade Security Implications

## 1. Introduction: The Bridge Between Two Worlds
Every WebSocket connection begins its lifecycle as a standard HTTP `GET` request, universally referred to as the **Upgrade Request**. This initial request is the critical bridge that spans the gap between the heavily regulated, stateless HTTP ecosystem and the free-flowing, stateful, persistent WebSocket ecosystem.

The security implications of the Upgrade Request cannot be overstated. It is the gatekeeper. Once the server responds with `HTTP/1.1 101 Switching Protocols`, all standard HTTP security checks (like CORS preflight requests, traditional WAF packet inspection, and HTTP-only cookie restrictions) simply cease to apply to the data flowing through that socket.

Therefore, if the server makes a mistake during the evaluation of the Upgrade Request, the resulting WebSocket connection is fundamentally compromised from inception. The root cause of almost all severe WebSocket vulnerabilities stems from developers misunderstanding how the browser handles authentication and Origin validation during this crucial handshake phase.

## 2. The Anatomy of the Upgrade Request
To understand the implications, we must dissect the request itself. When Javascript in the browser executes `let ws = new WebSocket("wss://api.bank.com/live");`, the browser automatically constructs and dispatches the following HTTP request.

**The Client's Automated HTTP Request:**
```http
GET /live HTTP/1.1
Host: api.bank.com
Origin: https://attacker-website.com       <-- 1. The Context (Where did the JS run?)
User-Agent: Mozilla/5.0 ...
Cookie: session_id=SECURE_JWT_TOKEN_99     <-- 2. The Authentication (Automatically attached!)
Upgrade: websocket                         <-- 3. The Protocol Switch Request
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Notice two critical automated behaviors by the browser:
1. **The Origin Header:** The browser explicitly tells the server *where* the Javascript execution originated. In this case, the script is running on `attacker-website.com`.
2. **The Cookie Header:** The browser *automatically* attaches any valid cookies belonging to `api.bank.com`, even though the request originated from `attacker-website.com`.

## 3. The Three Core Security Implications

### Implication A: The Same-Origin Policy (SOP) Exception
In the traditional HTTP world, if Javascript running on `attacker-website.com` tries to make a cross-origin AJAX/XHR `GET` or `POST` request to `api.bank.com`, the browser enforces the Same-Origin Policy (SOP). The browser will send a CORS preflight request (OPTIONS), and unless the bank explicitly responds with `Access-Control-Allow-Origin: https://attacker-website.com`, the browser will block the attacker's Javascript from reading the response.

**Crucially, the Same-Origin Policy DOES NOT apply to WebSockets.**
The W3C specification for WebSockets dictates that Javascript from *any* domain is perfectly permitted to open a WebSocket connection to *any* other domain, and the browser will not block the connection and will not restrict the reading of the response.

Because the browser's built-in protections are disabled, the burden of security falls entirely on the backend server. The server *must* explicitly read the `Origin` header during the Upgrade Request and manually terminate the connection if it comes from an untrusted domain. If the developer forgets to write this check, the endpoint is wide open.

### Implication B: Ambient Credential Dependency (The CSWSH Vector)
"Ambient Credentials" refers to authentication tokens that the browser attaches to requests automatically (namely, Cookies and HTTP Basic Auth credentials).

Because the browser attaches these ambient credentials to the HTTP Upgrade Request, many developers mistakenly believe that checking the `Cookie` header during the handshake is a sufficient authentication mechanism for the WebSocket.

The logic seems sound to a junior developer:
*Server logic:* "I received a request to upgrade to a WebSocket. Does the request have a valid session cookie? Yes. Okay, I will grant the connection and associate this socket with User 123."

This logic completely ignores Implication A. If `attacker-website.com` initiates the connection, the browser attaches User 123's cookie. The server validates the cookie, ignores the Origin, and grants `attacker-website.com` a fully authenticated, bidirectional communication channel to the bank acting as User 123. This is the exact mechanism of **Cross-Site WebSocket Hijacking (CSWSH)**.

### Implication C: The Missing CSRF Token
In traditional HTTP, we prevent cross-site actions by requiring an anti-CSRF token in the body of a `POST` request. Since the attacker cannot read the token from the target site (due to SOP), they cannot forge a valid `POST` request.

However, WebSocket connections are initiated with an HTTP `GET` request. Web frameworks traditionally do not enforce CSRF token checks on `GET` requests, as `GET` requests are supposed to be safe and idempotent. 

If an application allows state-changing actions (like "transfer funds" or "update password") to occur over the WebSocket connection, the developer *must* implement a mechanism to ensure the initial Upgrade Request wasn't forged by a third party. If they don't, the entire CSRF protection scheme of the application is rendered useless via the WebSocket backdoor.

## 4. Extensive ASCII Diagram: The Vulnerable Logic Flow
```text
================================================================================
                    THE UPGRADE REQUEST LOGIC FLAW
================================================================================

[Attacker's Actions]
1. Attacker hosts a malicious blog at `https://hackers-blog.com`.
2. Attacker embeds JS: `new WebSocket('wss://crypto-exchange.com/api/trade');`
3. Attacker lures Victim to the blog.

[Victim's Browser]
1. Victim is already logged into `crypto-exchange.com` in another tab.
2. Victim visits the blog.
3. Browser executes the JS.
4. Browser generates the Upgrade Request.
   ├── Host: crypto-exchange.com
   ├── Origin: https://hackers-blog.com  <-- The Truth
   └── Cookie: session=VICTIM_ADMIN      <-- The Keys to the Kingdom

[The Vulnerable Backend Server (Node.js/Express)]

function handleUpgrade(request, socket) {
    // FLAW 1: The developer checks the cookie, but ignores the Origin!
    let user = verifyCookie(request.headers.cookie);
    
    if (user) {
        // FLAW 2: The server accepts the upgrade and binds the user session 
        // to the socket, granting the attacker's script full authority!
        socket.accept();
        socket.userSession = user;
        console.log("Authenticated WebSocket established for " + user);
    } else {
        socket.reject(401);
    }
}

[The Aftermath]
The script on `hackers-blog.com` now holds an open, authenticated TCP socket 
directly to the exchange's trading engine. The script sends `{"action":"sell_all"}` 
and the backend processes it as the victim.
================================================================================
```

## 5. How to Audit and Test the Upgrade Request
When testing a WebSocket implementation, the very first step is to thoroughly audit the Upgrade Request. This dictates the security posture of the entire service.

**Methodology using Burp Suite:**
1. **Locate the Handshake:** Navigate the target application while proxying traffic through Burp Suite. Go to the `Proxy -> HTTP history` tab. Look for requests with a `101 Switching Protocols` response, or filter by the `Upgrade: websocket` header.
2. **Send to Repeater:** Right-click the Upgrade Request and select `Send to Repeater`.
3. **The Origin Fuzzing Test:**
   - Modify the `Origin` header. Change `Origin: https://target.com` to `Origin: https://target.com.evil.com`.
   - Send the request.
   - If the server responds with `403 Forbidden`, the server is utilizing strict Origin validation. The application is likely secure against CSWSH.
   - If the server responds with `101 Switching Protocols`, the Origin check is either missing or implemented via a flawed regex (e.g., it checks if `target.com` is *anywhere* in the string).
4. **The Null Origin Test:**
   - Change the header to `Origin: null`.
   - Send the request. Many developers write regexes that fail open when a null origin is presented (which can be generated by local HTML files or iframes with sandbox attributes). If it returns 101, it is vulnerable.
5. **The Unauthenticated Access Test:**
   - Remove the `Cookie` header entirely.
   - Remove any `Authorization` headers.
   - Send the request.
   - If it returns `101 Switching Protocols`, the WebSocket is unauthenticated. You must now determine if the socket allows access to sensitive data without further authentication in the subsequent binary frames.

## 6. Real-World Bug Bounty Insights
During a bug bounty program for a major streaming platform, a researcher discovered that the "Live Watch Party" feature utilized WebSockets to sync video playback between friends. 

The Upgrade Request correctly utilized cookies for authentication. The developer, attempting to be secure, wrote an Origin check. However, the regex was flawed:
`if (request.headers.origin.includes("streaming-site.com")) { accept(); }`

The researcher registered the domain `streaming-site.com.attacker.net`. By hosting a payload on this domain, the `Origin` header sent by the victim's browser was `https://streaming-site.com.attacker.net`. The backend regex evaluated to `true`, and the upgrade was accepted. The researcher used this hijacked socket to issue administrative commands to the Watch Party, kicking users and altering the video feed for everyone in the room.

## 7. How to Fix It (Developer Remediation)
Securing the Upgrade Request requires a defense-in-depth approach.

1. **Strict Origin Validation:**
   The backend code must explicitly and strictly validate the `Origin` header against an exact, hardcoded whitelist of trusted domains. Do not use loose regexes.
   *Secure Node.js Example:*
   ```javascript
   const allowedOrigins = ['https://www.bank.com', 'https://app.bank.com'];
   if (!allowedOrigins.includes(request.headers.origin)) {
       socket.destroy(); // Terminate connection immediately
       return;
   }
   ```

2. **Decouple Authentication from the Handshake (Token-Based Auth):**
   The most robust defense is to completely ignore ambient credentials (Cookies) during the HTTP handshake. Instead, rely on a **Ticket-Based** or **Message-Based** authentication flow.
   - **Ticket-Based:** When the user loads the frontend page, the frontend makes an authenticated HTTP API call to request a short-lived, single-use, cryptographically secure ticket (e.g., a JWT). The frontend then includes this ticket in the WebSocket URL: `wss://api.bank.com/live?ticket=SECURE_JWT_HERE`. An attacker cannot initiate the socket because they cannot read the ticket from the DOM due to the Same-Origin Policy.
   - **Message-Based:** The server accepts all WebSocket connections regardless of origin or cookies. However, the socket is placed in an "unauthenticated" quarantine state. The server ignores all commands until the client explicitly sends an authentication frame: `{"action": "auth", "token": "SECURE_JWT_HERE"}`. Again, the attacker cannot steal the token to send this frame.

## Related Notes
- [[01 - WebSocket Protocol — How It Works]]
- [[03 - Cross-Site WebSocket Hijacking (CSWSH)]]
