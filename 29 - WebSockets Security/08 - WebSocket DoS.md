---
tags: [vapt, websockets, dos, intermediate, deepdive]
difficulty: intermediate
module: "29 - WebSockets Security"
topic: "29.08 WebSocket DoS"
---

# 29.08 — WebSocket DoS (Denial of Service)

## 1. Introduction: The Asymmetry of Persistent Connections
**WebSocket Denial of Service (DoS)** is a class of attacks that exploits the persistent, stateful nature of the WebSocket protocol to exhaust the finite resources of the backend infrastructure.

In traditional HTTP, a Denial of Service attack (like an HTTP flood) requires the attacker to continuously blast the server with thousands of requests per second. The server processes the request, returns a response, and instantly closes the TCP connection, freeing up RAM and file descriptors. To keep the server down, the attacker must sustain the massive volume of traffic, requiring a large botnet.

WebSockets fundamentally alter this asymmetry. A WebSocket connection is designed to remain open indefinitely. Every open WebSocket connection consumes a finite amount of memory on the server and occupies a socket (a file descriptor on Linux systems). If an attacker can rapidly open thousands of connections and simply leave them open, the server will quickly exhaust its file descriptors or RAM. Once this capacity is reached, the server cannot accept any new connections—from WebSockets or standard HTTP—rendering the entire application inaccessible to legitimate users.

This allows a single attacker with a single laptop and a simple Python script to take down an enterprise application that lacks proper connection limits.

## 2. The Three Primary Vectors of WebSocket DoS

WebSocket DoS attacks generally fall into three distinct categories based on the resource they target:

### Vector A: Connection Exhaustion (File Descriptor Starvation)
Every operating system has a hard limit on the number of open files (sockets) a single process can maintain simultaneously (often controlled by `ulimit -n` on Linux). 
- The attacker writes a script to rapidly initiate 65,000 WebSocket Upgrade Requests.
- The server accepts the upgrades and holds 65,000 TCP sockets open.
- The server hits its `ulimit` or runs out of RAM.
- The web server crashes or begins rejecting all new legitimate traffic.

### Vector B: Payload Amplification (CPU Starvation)
This targets the processing power of the backend parsing engine (often Node.js or a Python worker).
- The attacker opens a *single* WebSocket connection.
- The attacker crafts a massive JSON payload (e.g., a 100MB string containing 10 million `"A"` characters).
- The attacker sends this massive frame over the socket.
- The backend server's JSON parser attempts to allocate memory and parse the 100MB string synchronously.
- The Node.js event loop blocks entirely. CPU usage spikes to 100%. The server becomes entirely unresponsive to all other users until the parsing completes (or the process crashes due to an Out-Of-Memory exception).

### Vector C: Broadcast Amplification (O(N²) State Starvation)
This exploits the business logic of real-time broadcasting applications (like collaborative drawing boards or massive chat rooms).
- The application is designed to receive a message from User A and broadcast it to the other 1,000 users in the room.
- The attacker opens a single connection to a massive room.
- The attacker writes a script to send 5,000 small messages per second.
- The server must process those 5,000 messages and broadcast each one to 1,000 users, resulting in 5,000,000 outbound WebSocket frames per second.
- The server's network interface and CPU are instantly overwhelmed by the sheer volume of internal routing, causing a catastrophic failure.

## 3. Extensive ASCII Diagram: Connection Exhaustion
```text
================================================================================
                    WEBSOCKET CONNECTION EXHAUSTION (DoS)
================================================================================

[ The Vulnerable Server ]
OS Configuration: `ulimit -n 10000` (Max 10,000 open file descriptors)
Current Load: 500 legitimate users connected.

[ The Attacker's Script (Running on a single laptop) ]
import websocket
import threading

def attack():
    try:
        # Initiate the handshake
        ws = websocket.create_connection("wss://target-startup.com/live")
        # Do absolutely nothing. Just keep the TCP socket open.
        while True: pass 
    except: pass

# Spawn 15,000 concurrent threads, each opening a connection
for i in range(15000):
    threading.Thread(target=attack).start()

[ The Result over 30 Seconds ]
Attacker Thread 1: OPEN (Socket #501 consumed)
Attacker Thread 2: OPEN (Socket #502 consumed)
...
Attacker Thread 9500: OPEN (Socket #10000 consumed!)

[ The Denial of Service ]
Legitimate User: "Let me log into my account." -> Sends HTTP GET request.
Server Kernel: "ERROR: Too many open files. Cannot accept new TCP connection."
Server: Drops the connection silently. 
Application is totally offline for everyone.
================================================================================
```

## 4. Methodological Discovery and Exploitation

**WARNING:** Denial of Service testing is inherently destructive. It should NEVER be performed on production systems without explicit, written authorization from the client, as it will almost certainly cause an outage.

### Testing Connection Exhaustion
If authorization is granted, testing is straightforward:
1. Write a multithreaded Python script (as shown in the diagram above) using the `websocket-client` library.
2. If the endpoint requires authentication, you must extract a valid session cookie from your browser and include it in the `create_connection(url, header=["Cookie: session=xyz"])` call.
3. Slowly ramp up the connections (e.g., blocks of 1,000).
4. Monitor the application from a separate, normal browser window. Try to navigate the site. If the site hangs indefinitely or returns 502/503 errors, the attack is successful.

### Testing Payload Amplification
This can sometimes be tested safely without taking down the entire server, provided you target a non-critical endpoint.
1. Intercept a legitimate WebSocket JSON message in Burp Repeater.
2. Identify a string parameter (e.g., `{"chat_msg": "Hello"}`).
3. Modify the string to contain a massive amount of data. You can use Burp's "Paste from file" feature to inject a 5MB text file.
   `{"chat_msg": "AAAAA...[5 million characters]...AAAA"}`
4. Send the frame.
5. Observe the response time. Does the server take 20 seconds to reply? Does the connection drop with a 1006 status code? Does the server return a `500 Internal Server Error` on subsequent HTTP requests? If so, the parser is vulnerable to exhaustion.

## 5. Real-World Case Study
A bug bounty hunter targeted a newly launched cryptocurrency exchange. The exchange featured an "Order Book" that streamed live trades to the frontend via WebSockets. 

The developer had properly configured Nginx to handle 100,000 concurrent connections, mitigating basic Connection Exhaustion. However, the developer failed to implement a payload size limit on the incoming frames. The backend Node.js application simply called `JSON.parse(message)` on whatever arrived over the socket.

The hunter intercepted an outbound message and replaced it with a 200MB string. Nginx passed the massive frame to Node.js. Node.js, being single-threaded, attempted to load the 200MB string into memory and parse it synchronously. This caused the V8 JavaScript engine to hit its hard memory limit (default ~1.5GB) and crash with an `Allocation failed - JavaScript heap out of memory` error. The entire backend trading engine went offline, requiring a manual restart by the sysadmins.

## 6. How to Fix It (Developer Remediation)

Defending against WebSocket DoS requires strict resource management at multiple layers of the infrastructure stack.

**1. Infrastructure Level: Strict Connection Limits**
The load balancer (e.g., Nginx, HAProxy) must be configured to strictly limit the number of active WebSocket connections allowed from a single IP address.
*Example Nginx configuration:*
```nginx
# Limit to 10 connections per IP
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;
```

**2. Application Level: Message Rate Limiting**
The backend application must track the number of messages received per socket per second. If a socket sends 500 messages in a single second, the backend should forcefully terminate the connection (`ws.close(1008, "Rate limit exceeded")`) and temporarily ban the IP or user ID.

**3. Application Level: Payload Size Restrictions**
The WebSocket server library must be configured to reject frames that exceed a reasonable maximum size (e.g., 64KB). The server should drop the connection immediately if a massive frame arrives, preventing the JSON parser from attempting to allocate memory for it.
*Secure Node.js Example (using `ws` library):*
```javascript
const wss = new WebSocket.Server({ 
    port: 8080,
    maxPayload: 65536 // Strictly limit payload size to 64KB
});
```

**4. Application Level: Aggressive Idle Timeouts**
Do not allow sockets to remain open indefinitely if they are not communicating. Implement a Heartbeat (Ping/Pong) mechanism. If the server does not receive a Pong response from the client within 30 seconds, the server must unilaterally close the socket. This purges "zombie" connections created by attackers attempting connection exhaustion.

## Related Notes
- [[29.01 WebSocket Protocol — How It Works]]
- [[29.04 WebSocket Message Manipulation]]
