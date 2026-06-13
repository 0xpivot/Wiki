---
tags: [vapt, websockets, defense, intermediate, deepdive]
difficulty: intermediate
module: "29 - WebSockets Security"
topic: "29.10 Defense — Origin Check, Authentication per Message"
---

# 29.10 — Defense: Origin Check, Authentication per Message

## 1. Introduction: The Paradigm Shift in Defense
Securing WebSockets requires a fundamental paradigm shift for developers. When securing a standard HTTP application, developers rely heavily on the browser's built-in security mechanisms (like the Same-Origin Policy and CORS) and perimeter defenses (like WAFs). 

Because the WebSocket protocol bypasses the Same-Origin Policy and communicates via binary frames that WAFs generally cannot inspect, the burden of security shifts entirely inward. **The application itself must become the firewall.**

A robust defense strategy for WebSockets requires a defense-in-depth approach spanning three distinct layers:
1. **The Handshake Layer:** Preventing unauthorized connections and Cross-Site Hijacking.
2. **The Session Layer:** Managing state, decoupling authentication from ambient credentials, and enforcing timeouts.
3. **The Messaging Layer:** Validating schemas, sanitizing input, and enforcing strict, per-message authorization controls.

## 2. Layer 1: Securing the Handshake

The HTTP Upgrade Request is the only time you have access to standard HTTP headers. You must perform rigorous checks before returning a `101 Switching Protocols` response.

### Defense 1A: Strict Origin Validation (Mitigating CSWSH)
Because the browser does not enforce the Same-Origin Policy for WebSockets, malicious sites can attempt to initiate connections to your server using your users' cookies. The server MUST manually verify the `Origin` header.

**Implementation Rules:**
- Read the `Origin` header from the Upgrade Request.
- Compare it against a strict, hardcoded whitelist of allowed domains.
- **NEVER** use loose regular expressions (e.g., do not use `origin.contains("mybank.com")` as attackers will use `mybank.com.evil.com`).
- If the Origin does not exactly match the whitelist, reject the connection with HTTP 403 Forbidden.

*Secure Implementation (Node.js/Express):*
```javascript
const allowedOrigins = ['https://www.secure-app.com', 'https://internal.secure-app.com'];

server.on('upgrade', function upgrade(request, socket, head) {
    const origin = request.headers.origin;
    if (!allowedOrigins.includes(origin)) {
        socket.write('HTTP/1.1 403 Forbidden\r\n\r\n');
        socket.destroy();
        return;
    }
    // Proceed with authentication...
});
```

### Defense 1B: Ticket-Based Authentication (The Gold Standard)
Relying solely on cookies during the handshake is dangerous. The most secure way to authenticate a WebSocket is to use a **Ticket-Based** system.

1. The frontend Javascript makes an authenticated, standard HTTP POST request to `/api/ws-ticket`.
2. The server verifies the user's session cookie and generates a cryptographically random, single-use ticket (valid for 30 seconds). It saves this ticket in a cache (like Redis) tied to the user's ID.
3. The frontend receives the ticket and opens the socket: `new WebSocket('wss://api.com/stream?ticket=XYZ123')`.
4. During the handshake, the server extracts `XYZ123` from the URL, checks Redis, authenticates the socket, and immediately deletes the ticket.
*Why this is secure:* An attacker on `evil.com` cannot steal the ticket because CORS prevents them from reading the response of the POST request to `/api/ws-ticket`. Therefore, they cannot initiate the socket.

## 3. Layer 2: Securing the Session

Once the connection is established, the server must manage the lifecycle of that socket securely.

### Defense 2A: Binding State to the Socket
When the socket is authenticated (via a ticket or token), the backend must explicitly bind the authenticated user's identity to the memory object representing that socket.
```javascript
// Bind the user object to the socket for future reference
ws.userSession = { userId: 54, role: 'standard_user' };
```
You must never trust the client to tell you who they are in subsequent messages. If a message arrives containing `{"action": "update", "user_id": 99}`, the server must ignore the `99` and rely entirely on `ws.userSession.userId`.

### Defense 2B: State Synchronization and Revocation
WebSockets are persistent. If a user changes their password, or an administrator bans a user, their existing HTTP session cookies might be invalidated, but their active WebSocket connections will remain open indefinitely unless explicitly closed.
**Implementation:** When a high-privilege action occurs (password change, logout, account suspension), the backend must loop through the pool of active WebSocket connections, find any sockets bound to that user's ID, and forcefully terminate them (`ws.close()`).

## 4. Layer 3: Securing the Messaging Layer

The most critical layer. Every message arriving over the socket must be treated as hostile input.

### Defense 3A: Strict Schema Validation (The WAF Replacement)
Because a network WAF cannot inspect the JSON payload inside the binary frame, the application must implement a strict schema validator at the very entry point of the WebSocket router.

**Implementation Rules:**
- Define exact JSON schemas for every permitted `action` type.
- If a message contains unexpected fields, reject it.
- If a field is expected to be an integer, ensure it is strictly an integer, not a string or an array.
- Limit the maximum string length of all fields to prevent Payload Amplification DoS.

*Secure Implementation (using Joi in Node.js):*
```javascript
const Joi = require('joi');

const betSchema = Joi.object({
    action: Joi.string().valid('place_bet').required(),
    amount: Joi.number().integer().min(1).max(10000).required() // Strict typing and bounds
});

ws.on('message', function(msg) {
    let data = JSON.parse(msg);
    const { error } = betSchema.validate(data);
    
    if (error) {
        ws.send(JSON.stringify({ error: "Invalid message format" }));
        return; // Drop the message entirely
    }
    processBet(ws.userSession, data.amount);
});
```

### Defense 3B: Authentication and Authorization PER MESSAGE
A common mistake is assuming that because the socket was authenticated during the handshake, the user is authorized to perform any action requested over that socket.

You must implement **Per-Message Authorization**. Every time the router processes an `action`, it must check the `ws.userSession` object and verify that the specific user has the correct permissions (Role-Based Access Control) to execute that specific action.

### Defense 3C: Input Sanitization and Parameterization
Treat the extracted data exactly as you would an HTTP POST body.
- **Prevent SQLi:** Never concatenate WebSocket data into SQL strings. Always use Prepared Statements.
- **Prevent Command Injection:** Never pass WebSocket data to shell execution functions (`exec()`). Use native APIs.
- **Prevent XSS:** If the data will be broadcast to other users (like a chat app), strictly HTML-encode the data on the server side before broadcasting it, and ensure the frontend uses safe DOM sinks (`textContent`).

## 5. Extensive ASCII Diagram: The Secure WebSocket Architecture
```text
================================================================================
                    THE SECURE WEBSOCKET ARCHITECTURE
================================================================================

[ 1. The Ticket Request (CORS Protected) ]
Client --(HTTP POST /api/ticket)--> Server
Server verifies Cookie, generates short-lived Ticket XYZ.
Client <--(HTTP 200 OK: {"ticket":"XYZ"})-- Server

[ 2. The Secure Handshake ]
Client --(GET /stream?ticket=XYZ)--> Server

Server Validation Logic:
  1. Check Origin: Is it exactly 'https://my-app.com'? (YES)
  2. Check Ticket: Is XYZ valid in Redis? (YES)
  3. Action: Delete Ticket XYZ from Redis.
  4. Action: Bind UserID to the Socket Object.

Server <--(HTTP 101 Switching Protocols)-- Client

[ 3. The Secure Messaging Loop ]
Client --(WS Frame: {"action":"delete", "target_id":55})--> Server

Server Router Logic:
  1. Schema Check: Does JSON exactly match the 'delete' schema? (YES)
  2. AuthZ Check: Does Socket.UserID have 'admin' role? (YES)
  3. Execution: db.query("DELETE FROM items WHERE id=$1", [55]) <-- Parameterized!
  4. Broadcast: Sanitize output and send confirmation.

Server <--(WS Frame: {"status":"deleted"})-- Client
================================================================================
```

## 6. Developer Checklist
- [ ] Is the `Origin` header explicitly validated against a hardcoded whitelist during the upgrade request?
- [ ] Is authentication handled via a short-lived ticket system rather than relying solely on ambient cookies during the handshake?
- [ ] Does the application forcefully sever active WebSocket connections when a user logs out or their session is revoked?
- [ ] Is every incoming JSON message validated against a strict schema for type, length, and format before processing?
- [ ] Are permissions explicitly checked *per message* based on the bound socket session, rather than trusting client-provided IDs?
- [ ] Is all data extracted from the socket parameterized before hitting the database?

## Related Notes
- [[02 - WebSocket Upgrade Security Implications]]
- [[03 - Cross-Site WebSocket Hijacking (CSWSH)]]
- [[04 - WebSocket Message Manipulation]]
