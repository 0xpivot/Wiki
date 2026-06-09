---
tags: [vapt, websockets, auth, intermediate, deepdive]
difficulty: intermediate
module: "29 - WebSockets Security"
topic: "29.09 Lack of Authentication on WebSocket Endpoints"
---

# 29.09 — Lack of Authentication on WebSocket Endpoints

## 1. Introduction: The Forgotten Backdoor
**Lack of Authentication on WebSocket Endpoints** occurs when developers successfully secure their traditional HTTP REST API (requiring valid JWTs or session cookies for all endpoints), but completely forget to implement similar authentication checks on the custom backend logic that handles incoming WebSocket messages.

This vulnerability often stems from a fundamental misunderstanding of network architecture. Because a WebSocket connection represents a persistent tunnel between the client and the server, developers frequently treat the socket itself as an "internal" or "trusted" channel. They assume that if a user managed to load the frontend web application, they must be somewhat authorized. 

In reality, the WebSocket endpoint (e.g., `wss://api.target.com/stream`) is publicly exposed to the entire internet. Anyone with a basic script or Burp Suite can initiate a connection to that endpoint. If the server accepts the connection and processes subsequent messages without explicitly verifying the identity of the sender, the attacker gains unauthenticated access to the backend business logic, bypassing all perimeter authentication controls.

## 2. The Vulnerable Architecture
The flaw can manifest in two distinct phases of the WebSocket lifecycle:

### Scenario A: Unauthenticated Handshake (Data Exposure)
The server accepts the HTTP Upgrade Request without checking for any cookies, tokens, or origin headers. Once the connection is open, the server immediately begins streaming sensitive data to the socket (e.g., a live feed of all system logs or all user trades). The attacker simply connects and passively listens, achieving a massive data breach without ever sending a message.

### Scenario B: Unauthenticated Message Processing (Action Execution)
The server accepts the unauthenticated handshake, but doesn't send data immediately. Instead, it waits for the client to send a command via a JSON frame.
When the JSON frame arrives, the backend router uses a `switch` statement to process the command. Crucially, the router *fails to check if the socket belongs to an authenticated user session* before executing the command.

```javascript
// Extremely Vulnerable Node.js Implementation
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

// FLAW 1: Accepts ALL connections. No cookie or token checks during the handshake.
wss.on('connection', function connection(ws) {
    
    ws.on('message', function incoming(message) {
        let data = JSON.parse(message);
        
        // FLAW 2: Processing sensitive actions without verifying WHO is asking.
        if (data.action === 'view_private_document') {
            let doc = database.getDocument(data.doc_id); // Returns any document!
            ws.send(JSON.stringify(doc));
        }
        
        if (data.action === 'delete_user') {
            database.deleteUser(data.user_id); // Allows unauthenticated deletion!
            ws.send("User deleted");
        }
    });
});
```

## 3. Extensive ASCII Diagram: Bypassing the Front Door
```text
================================================================================
                    BYPASSING AUTHENTICATION VIA WEBSOCKETS
================================================================================

[ The Application Architecture ]
Target operates a secure HR portal.
HTTP API: `https://hr.corp.com/api/*` (Protected by strict OAuth2 JWT checks)
WebSocket: `wss://hr.corp.com/live` (Used for real-time notifications)

[ The Attacker's Strategy ]
The attacker attempts to view sensitive employee records via the HTTP API.

    [ HTTP REQUEST ]
    GET /api/employee/99 HTTP/1.1
    Host: hr.corp.com
    (No Authorization Header)

    [ HTTP RESPONSE ]
    HTTP/1.1 401 Unauthorized
    {"error": "Missing JWT Token"}

The attacker notices the WebSocket endpoint in the frontend JavaScript code.
The attacker uses a Python script to connect directly to the socket.

    [ WEBSOCKET HANDSHAKE ]
    GET /live HTTP/1.1
    Upgrade: websocket

    [ SERVER RESPONSE ]
    HTTP/1.1 101 Switching Protocols
    (Connection Established! The server failed to require a token.)

[ The Unauthenticated Execution ]
The attacker sends a crafted JSON frame mimicking the frontend's behavior.

    [ OUTBOUND WEBSOCKET FRAME ]
    {"type": "fetch_record", "employee_id": 99}

    [ THE BACKEND FLAW ]
    The backend WebSocket handler processes the JSON. It has no code 
    to check for a JWT. It simply queries the database and returns the data.

    [ INBOUND WEBSOCKET FRAME ]
    {"employee_id": 99, "salary": "$150,000", "ssn": "XXX-XX-XXXX"}

[ The Result ]
The attacker has completely bypassed the enterprise OAuth2 system by utilizing 
the forgotten, unauthenticated WebSocket backdoor.
================================================================================
```

## 4. Methodological Discovery and Exploitation

**Step 1: Endpoint Discovery**
- While using the target application normally (as an authenticated user), observe the `Proxy -> WebSockets history` tab in Burp Suite.
- Note the endpoint URL (e.g., `wss://api.com/stream`).
- Note the exact JSON structure of the messages being sent and received. Copy a few valid requests to your notepad.

**Step 2: Unauthenticated Connection Attempt**
- You must attempt to establish a connection to that endpoint *without* any credentials.
- In Burp Repeater, take the initial HTTP Upgrade Request (the `GET` request with `Upgrade: websocket`).
- **Remove all authentication markers:** Delete the `Cookie` header. Delete any `Authorization` headers.
- Send the request.
- If the server responds with `401 Unauthorized` or `403 Forbidden`, the handshake is secure.
- If the server responds with `101 Switching Protocols`, you have successfully established an unauthenticated socket.

**Step 3: Probing for Functionality**
- Even if the socket connects, it might be heavily restricted (e.g., an unauthenticated socket might only be allowed to receive public system announcements). You must prove impact.
- Use a local WebSocket client (like a Python script, or the "Simple WebSocket Client" browser extension) to connect to the URL without cookies.
- Send the JSON payloads you copied in Step 1.
  - Send: `{"action": "get_profile", "user_id": 1}`
  - Send: `{"action": "send_message", "target": "admin", "msg": "test"}`
- If the server processes these commands and returns sensitive data or alters state, you have confirmed a critical Lack of Authentication vulnerability.

## 5. Real-World Case Study
A penetration testing team was evaluating a cloud-based fleet management platform. The platform allowed logistics companies to track the GPS locations of thousands of delivery trucks in real-time. 

The main web dashboard was heavily secured with Multi-Factor Authentication (MFA). Once authenticated, the browser opened a WebSocket connection to `wss://fleet-api.com/tracking`.

The testers discovered that the WebSocket endpoint did not verify session cookies during the handshake. Anyone on the internet could open a socket to `/tracking`. Upon connecting, the server required the client to send a subscription message: `{"action": "subscribe", "fleet_id": "105"}`.

Because the WebSocket handler lacked any authorization checks, it blindly accepted the subscription request. The testers wrote a simple script that connected to the socket without credentials, iterated through `fleet_id` 1 to 5000, and subscribed to all of them. The server happily began streaming the real-time, high-precision GPS coordinates of every single delivery truck managed by the entire platform directly to the unauthenticated testers, resulting in a catastrophic exposure of sensitive logistics data.

## 6. How to Fix It (Developer Remediation)

WebSocket endpoints must be subjected to the exact same rigorous authentication requirements as the most sensitive HTTP REST API endpoints.

**1. Handshake Authentication (The Gatekeeper)**
Do not allow the connection to establish (`101 Switching Protocols`) unless the client proves their identity.
- **Using Cookies:** The server should parse the `Cookie` header during the Upgrade Request and validate the session token. If invalid, return `401 Unauthorized` immediately. (Note: This must be paired with strict Origin checks to prevent CSWSH, see Module 29.03).
- **Using Tokens (Recommended):** Require the client to pass a short-lived authentication token (like a JWT) in the WebSocket URL or in a custom header (if supported by the client library). Example: `wss://api.com/stream?auth_token=eyJhb...`

**2. Message-Level Authorization (Defense in Depth)**
Even if the socket is authenticated, the backend must map the active socket object to the specific user session. Every single time a JSON message is processed, the backend router must verify that the user associated with that socket actually has the permission to execute the requested action.
- *Secure Logic:* "Socket ID 942 just requested to view Document 55. Let me check the session attached to Socket 942. It belongs to User Alice. Does Alice have read access to Document 55? Yes. Okay, return the data."

## Related Notes
- [[29.01 WebSocket Protocol — How It Works]]
- [[29.02 WebSocket Upgrade Security Implications]]
- [[29.10 Defense — Origin Check, Authentication per Message]]
