---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.03 Designing the Communication Protocol HTTP REST vs Websockets"
---

# 98.03 Designing the Communication Protocol HTTP REST vs Websockets

## Introduction

The communication protocol is the lifeline of a Command and Control (C2) framework. It dictates how the implant (agent) on the compromised system exchanges instructions, data, and telemetry with the remote team server. A poorly designed protocol is loud, easily fingerprinted, and quickly blocked by defensive infrastructure. A well-designed protocol is stealthy, resilient, and blends seamlessly into the target organization's baseline traffic.

When building a custom C2 framework, developers must choose the transport mechanisms and architectural paradigms. This document explores two dominant paradigms for modern C2 communication: HTTP/REST (stateless, polling) and WebSockets (stateful, bidirectional), outlining their mechanics, advantages, and operational considerations from both an offensive and defensive perspective.

## ASCII Diagram: Polling vs. Persistent Connections

```text
+-----------------------------------------------------------------------------------------+
|                        COMMUNICATION PARADIGMS: REST vs. WEBSOCKETS                     |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   [ HTTP / REST (Polling Beacon) ]             [ WEBSOCKETS (Persistent Connection) ]   |
|                                                                                         |
|      AGENT                SERVER                  AGENT                  SERVER         |
|        |                     |                      |                       |           |
|        |--- GET /task ------>|                      |-- HTTP Upgrade ------>|           |
|        |<-- 200 OK (Empty) --|                      |<-- 101 Switching -----|           |
|        |                     |                      |                       |           |
|     (Sleep + Jitter)         |                      |     (Connection Kept Alive)       |
|        |                     |                      |                       |           |
|        |--- GET /task ------>|                      |                       |           |
|        |<-- 200 OK (Cmd) ----|                      |<-- Push Task (Cmd) ---|           |
|        |                     |                      |                       |           |
|   (Executes Command)         |                 (Executes Command)           |           |
|        |                     |                      |                       |           |
|        |--- POST /result --->|                      |--- Push /result ----->|           |
|        |<-- 200 OK ----------|                      |                       |           |
|        |                     |                      |                       |           |
|     (Sleep + Jitter)         |                      |      (Connection Maintained)      |
|        |                     |                      |                       |           |
|                                                                                         |
|   Characteristics:                              Characteristics:                        |
|   - Stateless, discrete requests                - Stateful, continuous TCP stream       |
|   - Blends well with web browsing               - Ideal for interactive shells/proxies  |
|   - Asynchronous by nature                      - Synchronous, real-time feel           |
|   - High latency for task execution             - Near-zero latency                     |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

## 1. HTTP / REST Architectures (The Polling Paradigm)

The vast majority of C2 frameworks utilize HTTP(S) as their primary transport mechanism. HTTP is ubiquitous; almost every corporate network allows outbound HTTP(S) traffic to the internet to support normal business operations.

### 1.1 The Mechanics
- **Beaconing**: The agent operates on a timer. It "wakes up", crafts an HTTP request (usually an encrypted payload disguised as normal web data), and sends it to the server.
- **Task Retrieval (GET)**: Often, a `GET` request to an innocuous URL (e.g., `/api/v1/update` or `/styles/main.css`) is used to request tasks.
- **Data Exfiltration (POST)**: A `POST` request to another URL (e.g., `/images/upload` or `/telemetry/submit`) is used to send command output or stolen files back to the server.

### 1.2 Advantages
- **Ubiquity**: Blends into normal web traffic. HTTP proxies and firewalls rarely block standard web traffic out of the box, assuming it looks legitimate.
- **Statelessness**: If a connection drops, the agent simply tries again on its next cycle. This makes the C2 highly resilient to unstable networks or endpoint roaming (e.g., laptops moving between networks).
- **Malleability**: HTTP is extremely flexible. Attackers can alter headers, URIs, user-agents, and body structures to mimic legitimate services (e.g., mimicking Google Analytics, Windows Update traffic, or specific SaaS APIs).

### 1.3 Disadvantages
- **Latency**: If the agent sleeps for 10 minutes, the operator must wait up to 10 minutes for a command to be retrieved, and another 10 minutes for the result. This makes interactive operations (like a remote shell or rapid lateral movement) painfully slow and operationally difficult.
- **Beaconing Signatures**: The periodic nature of the requests, even with jitter, is a prime target for Network Traffic Analysis (NTA) tools looking for automated periodicity and repetitive connection patterns.

## 2. WebSockets (The Stateful Paradigm)

WebSockets provide a full-duplex communication channel over a single TCP connection. The connection begins as an HTTP request and then "upgrades" to a WebSocket protocol, bypassing traditional stateless HTTP constraints.

### 2.1 The Mechanics
- **Initialization**: The agent sends an HTTP `Upgrade` request to the server. If accepted, the connection remains open indefinitely.
- **Bidirectional Flow**: Both the server and the agent can send frames of data to each other instantly, without waiting for a request-response cycle.

### 2.2 Advantages
- **Real-Time Interaction**: Allows for zero-latency operations. This is crucial for dynamic port forwarding (SOCKS proxies), interactive reverse shells, and rapid lateral movement techniques like executing BloodHound or proxying RDP traffic.
- **Lower Overhead**: Once the connection is established, there is no need to send HTTP headers (cookies, user-agents) with every transmission, significantly reducing the total bandwidth and packet overhead for continuous data streams.
- **Continuous Flow**: Circumvents simple beaconing frequency analysis since there are no discrete periodic requests to measure.

### 2.3 Disadvantages
- **Network Anomalies**: Long-lived TCP connections holding open WebSocket streams to unknown domains are often flagged by advanced firewalls and corporate proxies. Legitimate WebSockets are usually tied to known services (chat apps, financial tickers).
- **State Management**: If the network connection drops, the agent and server must handle complex reconnection logic and ensure state is properly restored without causing application crashes.
- **Proxy Issues**: Some strict corporate proxies block or mishandle WebSocket upgrades, breaking the communication channel entirely.

## 3. Designing a Hybrid Protocol

Advanced custom C2 frameworks often implement both protocols, dynamically switching between them based on operational needs to maximize stealth and utility.

1. **Default Mode (HTTP/REST)**: The agent operates in a high-stealth, high-sleep HTTP polling mode. This minimizes the network footprint and ensures long-term persistence with minimal risk of detection.
2. **Interactive Mode (WebSockets)**: When the operator needs to perform rapid, hands-on-keyboard activities (e.g., pivoting through the network using a SOCKS proxy), they issue a command instructing the agent to "upgrade" its connection. The agent establishes a secure WebSocket channel.
3. **Reversion**: Once the interactive session is no longer needed, the operator drops the WebSocket connection, and the agent reverts to its stealthy HTTP polling schedule.

## Real-World Attack Scenario

### Scenario: The E-Commerce Compromise and Domain Fronting

**Context**: A cybercriminal group breaches an e-commerce platform and needs to maintain a stealthy C2 channel that evades the company's strict egress filtering, which blocks all traffic to unknown domains.

**The Attack**:
1. The attackers configure their custom C2 to use HTTP REST.
2. They utilize a technique called **Domain Fronting** via a major Content Delivery Network (CDN) that the target company already trusts and allows (e.g., Fastly, Cloudflare, AWS CloudFront).
3. The C2 Agent crafts its HTTP request. The `Host` header is set to `c2-backend.attacker.cdn.net`, but the actual IP address it connects to and the TLS SNI (Server Name Indication) are set to `legitimate-site.cdn.net` (a highly trusted site hosted on the same CDN).
4. The company's firewall sees TLS traffic going to a trusted IP and a trusted SNI and allows it.
5. The CDN edge server terminates the TLS connection, reads the encrypted HTTP `Host` header, and routes the malicious traffic to the attacker's hidden Team Server.

**The Hybrid Switch**: Later, the attackers need to exfiltrate a massive multi-gigabyte database quickly. The high latency of HTTP polling through the CDN is too slow. They issue a command to establish a direct WebSocket connection via an alternative, less-monitored secondary network route they discovered during lateral movement, bypassing the CDN entirely for the high-bandwidth exfiltration phase.

## Detection Engineering & Threat Hunting

Understanding protocol mechanics is essential for writing robust detection rules.

1. **Detecting HTTP C2**:
   - **Frequency Analysis**: Identify source IPs communicating with the same destination IP/Domain at regular intervals over long periods. Tools like RITA (Real Intelligence Threat Analytics) specialize in this.
   - **Header Anomalies**: Look for mismatched `User-Agent` strings, missing standard headers (like `Accept-Language`), or hardcoded values that do not match the expected behavior of modern browsers in the environment.
   - **Payload Entropy**: While the traffic may be encrypted over TLS, deep packet inspection (if TLS decryption is enabled) can analyze the entropy of HTTP bodies or headers (like Cookies) to identify encrypted blobs disguised as plain text.

2. **Detecting WebSocket C2**:
   - **Long-Lived Connections**: Monitor for abnormally long-lived HTTP sessions that upgrade to WebSockets to newly observed or uncategorized domains.
   - **Traffic Volume Profiling**: Legitimate WebSockets (like chat applications) have specific traffic patterns (small, bursty packets). C2 WebSockets routing a SOCKS proxy or downloading large files will exhibit massive, sustained data transfers atypical of normal WebSocket usage.
   - **TLS Fingerprinting (JA3/JA4)**: Regardless of HTTP or WebSockets, the underlying TLS connection can be fingerprinted. Custom C2 agents written in Go or Rust often have distinct TLS negotiation patterns compared to standard browsers like Chrome or Edge.

## Chaining Opportunities

- **Protocol Encapsulation**: HTTP and WebSockets can be chained with other techniques. For example, encapsulating the entire HTTP structure inside DNS TXT records for environments where all HTTP egress is blocked (see [[XX - DNS over HTTPS (DoH) for C2]]).
- **Malleable Profiles**: Chaining protocol design with dynamic profile generation allows the C2 to alter its HTTP headers and URL structures on the fly, continually confusing signature-based NIDS (see [[XX - Dynamic Malleable C2 Profiles]]).

## Related Notes

- [[98.01 Why Build a Custom C2 Framework]]
- [[98.02 Core Components Server Agent and Protocol]]
- [[XX - Network Traffic Analysis and Hunting]]
- [[XX - Advanced Evasion with Domain Fronting]]
