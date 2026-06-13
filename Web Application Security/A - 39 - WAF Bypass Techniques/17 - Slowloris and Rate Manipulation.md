---
tags: [waf, evasion, bypass, vapt]
difficulty: advanced
module: "39 - WAF Bypass Techniques"
topic: "39.17 Slowloris and Rate Manipulation"
---

# Slowloris and Rate Manipulation Techniques

While the majority of Web Application Firewall (WAF) bypass techniques focus on obfuscating malicious payloads (like SQLi or XSS) or launching massive distributed volumetric attacks, Slowloris and related rate manipulation attacks exploit the fundamental architectural nature of TCP/IP connection handling in web servers. These techniques are explicitly designed to fly under the radar of traditional volumetric DDoS protections and WAF rate limits by utilizing exceptionally low bandwidth and slow, deliberate data transmission.

## The Principle of Asymmetric Slow-Rate Attacks

Traditional web server architecture requires the server to keep a network connection open while waiting for the client to complete its HTTP request. If a client deliberately sends data extremely slowly, the server must keep the connection thread, process, or memory buffer open. When an attacker opens hundreds or thousands of these slow connections simultaneously, the server's connection pool (e.g., Apache's `MaxRequestWorkers`) is completely exhausted, preventing any legitimate users from accessing the service.

### Why WAFs Struggle with Slow Attacks

Most WAFs are optimized to detect high-frequency, high-volume requests (Layer 3/4 volumetric DDoS) or deeply inspect fully formed malicious payloads (Layer 7). 

Slow attacks present a unique challenge:
1. They send perfectly valid, well-formed HTTP requests.
2. They do so over an extended period, meaning the data transfer rate is so low (e.g., 1 byte per 10 seconds) that it does not trigger bandwidth-based alarms.
3. Because the requests are technically incomplete until the final byte is transmitted, WAFs that perform full-request inspection (buffering the request before sending it to the backend) are forced to hold the connection open themselves, inadvertently becoming the bottleneck and failing gracefully.

## The Slowloris Attack Mechanics (Slow Headers)

The classic Slowloris attack focuses entirely on the HTTP header section of a GET request. The client initiates a TCP connection and sends a partial HTTP request. It then sends subsequent HTTP headers at regular, slow intervals, but crucially, it never sends the final blank line (`\r\n\r\n`) that signals the end of the HTTP header block.

### ASCII Architecture of Slowloris Connection State

```text
Attacker Network                                   Target Web Server (e.g., Apache MPM Worker)
       |                                                          |
       |---[SYN]------------------------------------------------->|
       |<--[SYN/ACK]----------------------------------------------|
       |---[ACK]------------------------------------------------->|
       |                                                          | (TCP Connection Established)
       |---[GET / HTTP/1.1\r\nHost: target.com\r\n]-------------->| (Incomplete Request Received)
       |                                                          |
       |      ... (Attacker Waits 14 seconds) ...                 | (Server thread blocked waiting for \r\n\r\n)
       |                                                          |
       |---[X-Random-Keepalive-1: 8f7d9a\r\n]-------------------->| (Keep alive received, timer reset)
       |                                                          |
       |      ... (Attacker Waits 14 seconds) ...                 | (Server thread still blocked)
       |                                                          |
       |---[X-Random-Keepalive-2: 2b4c1e\r\n]-------------------->| (Keep alive received, timer reset)
       |                                                          |
       |   (Process repeats indefinitely. \r\n\r\n never sent)    |
```

Because the server receives data before its internal timeout is reached (e.g., Apache's default `TimeOut` might be 60 seconds, but the attacker sends a header every 14 seconds), the connection is never forcefully closed by the server. By repeating this across 500 connections, a standard web server is rendered entirely unresponsive.

## Variants of Slow-Rate Attacks

The core concept of "slow transmission" has been adapted to other parts of the HTTP protocol.

### 1. Slow POST (R.U.D.Y. - R-U-Dead-Yet)

Instead of sending slow headers, the Slow POST attack sends slow HTTP body data. The attacker initiates a valid HTTP POST request (often targeting forms like `/login` or `/search`) and specifies a massive `Content-Length` in the headers.

```http
POST /api/v1/upload HTTP/1.1
Host: target.com
Content-Length: 5000000
Content-Type: application/x-www-form-urlencoded

a
... (attacker waits 10 seconds) ...
b
... (attacker waits 10 seconds) ...
```

The WAF or backend web server reads the `Content-Length` header and expects five million bytes of data. The attacker trickles the data in, one byte at a time. WAFs configured to buffer the entire request body before inspection (to check for SQLi or malicious file uploads) are particularly vulnerable, as they will consume significant memory and connection state waiting for a payload that will take days to complete.

### 2. Slow Read Attack

In a Slow Read attack, the attacker flips the paradigm. They send a complete, valid, fast HTTP request, but they read the HTTP response from the server extremely slowly. 

This is achieved at the TCP layer by advertising a very small TCP Window Size in the TCP acknowledgement packets. The server is forced to buffer the response payload in its own memory and send it in tiny chunks, tying up server resources as it waits for the attacker to acknowledge receipt before transmitting the next chunk.

## WAF Bypass via Rate Manipulation and Timing

Beyond Denial of Service, rate manipulation can be used specifically to bypass WAF brute-force and scraping protections.

### Jitter and Randomized Delays

WAFs often detect automated tools (like DirBuster, Ffuf, or Hydra) by analyzing the precise mathematical interval between requests. If a script sends a request exactly every 1.000 seconds, the variance is zero, and it is instantly flagged as a bot. 

Implementing **Jitter** means adding a randomized mathematical variance to the sleep interval, mimicking the inconsistent pacing of a human clicking links.

```python
import time
import random
import requests

def stealth_brute_force(wordlist):
    base_delay = 2.0  # Base wait time of 2 seconds
    jitter_factor = 0.6 # 60% variance

    for payload in wordlist:
        requests.get(f"https://target.com/api/{payload}")
        
        # Calculate dynamic delay: between 0.8s and 3.2s
        delay = base_delay * (1 + random.uniform(-jitter_factor, jitter_factor))
        print(f"Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)
```

### Burst Traffic (Token Bucket Exhaustion and Race Conditions)

Many WAFs use token bucket algorithms that replenish tokens over time. If an attacker wants to bypass rate limits for a brief moment to execute a specific race condition or a parallel brute-force attack, they utilize burst traffic.

The attacker waits for the token bucket to fill completely, then sends a massive, highly concurrent parallel burst of requests simultaneously. Because distributed WAF edge nodes (e.g., a Cloudflare node in NY and another in LA) take a few milliseconds to synchronize their global rate limit counters, a burst of 200 requests might be processed entirely before the WAF consensus is reached to block the IP.

## Advanced Configuration: Mitigating Slow Attacks

Mitigating slow-rate attacks requires careful, deep configuration of both the WAF and the origin server infrastructure.

1. **Absolute Connection Timeouts:** Configure an absolute maximum time a connection can remain open, regardless of whether data is flowing. 
   - *Apache:* Use the `reqtimeout` module. Set `RequestReadTimeout header=20-40,MinRate=500 body=20,MinRate=500`. This forces the client to send at least 500 bytes per second, or the connection is dropped.
2. **Event-Driven Architectures:** Transitioning backend servers from thread-based architectures (like Apache MPM Prefork) to event-driven architectures (like Nginx, Node.js, or HAProxy). Event-driven servers use asynchronous I/O, meaning an idle, slow connection consumes merely a few bytes of memory rather than an entire OS thread. Nginx can handle tens of thousands of Slowloris connections without breaking a sweat.
3. **WAF Request Buffering Limits:** Configure the WAF to only buffer the first `N` kilobytes of a request body. If the payload exceeds this, the WAF should either inspect the chunk immediately and pass it along, or forcefully drop the connection if it violates expected behavior for that endpoint.
4. **TCP Tweak (Deferred Accept):** Enable TCP Deferred Accept (`TCP_DEFER_ACCEPT` in Linux). This tells the OS kernel not to wake up the web server process until actual data (not just a TCP handshake) has arrived, mitigating some forms of slow connection establishment.

## Summary

Slowloris and rate manipulation techniques highlight the vulnerability of stateful connection tracking. By subverting the expected pacing and flow of network traffic, attackers can evade high-speed signature detection, bypass rigid rate limiters, and exhaust server hardware resources using minimal bandwidth, proving that speed is not always the key to a successful breach.

### Chaining Opportunities
- Combine with [[16 - IP Rotation]] to initiate slow connections from thousands of different IP addresses simultaneously, making IP-based blacklisting completely ineffective.
- Use Burst Traffic techniques alongside [[14 - Race Conditions and WAF Desync]] to exploit Time-of-Check to Time-of-Use (TOCTOU) vulnerabilities in the backend database or the WAF's state machine.

### Related Notes
- [[08 - Protocol Level Evasion]]
- [[21 - Denial of Service against WAF Infrastructure]]
- [[04 - Bypassing Connection Limits]]
- [[25 - Backend Desynchronization Attacks]]
