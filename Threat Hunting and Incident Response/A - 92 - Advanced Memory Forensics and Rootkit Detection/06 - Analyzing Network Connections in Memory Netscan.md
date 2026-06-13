---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.06 Analyzing Network Connections in Memory Netscan"
---

# 92.06 Analyzing Network Connections in Memory Netscan

## Introduction

Memory forensics provides an unparalleled view into the volatile state of an operating system, making it an essential discipline for advanced threat hunting and incident response. One of the most critical aspects of memory forensics is the analysis of network connections. Unlike traditional network forensics, which relies on packet captures (PCAP) that might miss encrypted traffic or short-lived connections, memory forensics allows analysts to extract active, closed, and listening network connections directly from RAM. This includes mapping these connections to their respective processes, identifying rogue listening ports, and uncovering command-and-control (C2) communications that attempt to hide from live system utilities like `netstat`.

The `netscan` plugin in Volatility 3 (and its predecessor in Volatility 2) is a cornerstone tool for this type of analysis. It leverages pool tag scanning and internal operating system data structures to rebuild the network state of the machine at the exact moment the memory snapshot was acquired. Understanding how `netscan` works internally, the artifacts it recovers, and how malware authors attempt to subvert it is crucial for an elite threat hunter.

## The Architecture of Network Structures in Memory

To fully grasp how `netscan` operates, we must first understand how modern Windows operating systems manage network connections internally. In Windows Vista and later (including Windows 10 and 11), network state information is primarily managed by the Windows Filtering Platform (WFP) and the Transmission Control Protocol/Internet Protocol (TCP/IP) driver stack (`tcpip.sys`).

When a process initiates a network connection or binds to a port, `tcpip.sys` allocates specific data structures in the kernel non-paged pool. These structures include:
- `_TCP_ENDPOINT_CREATION_INFO`
- `_TCP_LISTENER_ENDPOINT`
- `_UDP_ENDPOINT`

These structures hold metadata about the connection, such as the local IP address, remote IP address, local port, remote port, connection state (e.g., ESTABLISHED, LISTENING, TIME_WAIT), and the owning process ID (PID). 

Because these structures are allocated in the non-paged pool, they are marked with specific 4-byte pool tags. For example, TCP endpoints might be tagged with `TCPT`, `TCPe`, or `UDPv`.

### How Netscan Works

The `netscan` plugin does not rely on the standard Windows APIs or linked lists (like the ones used by `netstat.exe` under the hood), because rootkits can easily manipulate these lists to hide their connections. Instead, `netscan` performs a **pool tag scan**. It scans the entire physical memory for the specific pool tags associated with network structures. 

Once a pool tag is found, the plugin validates the structure by checking internal pointers and field alignments. If the structure is valid, `netscan` parses the local/remote IP and ports, the state, and the associated PID. This approach makes `netscan` incredibly resilient against Direct Kernel Object Manipulation (DKOM), a common rootkit technique used to unlink objects from active lists.

```text
+-----------------------------------------------------------------------------------+
|                            Network Connection Analysis                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  Live System (Rootkit Active)                 Memory Image (Post-Acquisition)     |
|                                                                                   |
|  +-----------------+  <Hidden>                +-----------------------------+     |
|  | netstat.exe     |--------------------X     | Physical RAM (Dump.raw)     |     |
|  +-----------------+                          |                             |     |
|          | Queries API                        | +-------------------------+ |     |
|          v                                    | | Non-Paged Pool          | |     |
|  +-----------------+                          | |                         | |     |
|  | TCP/IP Stack    |                          | | [ Pool Tag: 'TCPT' ]    | |     |
|  | Linked List     | <--- Rootkit             | | [ Local IP: 10.0.0.5]   | |     |
|  +-----------------+      unlinks C2          | | [ Rem IP: 192.168.1.100]| |     |
|                           connection          | | [ State: ESTABLISHED]   | |     |
|                                               | | [ PID: 1337 ]           | |     |
|                                               | +-------------------------+ |     |
|                                               |              ^              |     |
|                                               +--------------|--------------+     |
|                                                              |                    |
|                                                       +-------------+             |
|                                                       | Volatility  |             |
|                                                       | 'netscan'   |             |
|                                                       +-------------+             |
|                                                       (Scans physical memory      |
|                                                        for pool tags, bypassing   |
|                                                        unlinked API lists)        |
+-----------------------------------------------------------------------------------+
```

## Advanced Analysis Techniques with Netscan

When analyzing the output of `netscan`, a threat hunter must look beyond the obvious. Malware often uses sophisticated techniques to blend in with legitimate traffic.

### 1. Process and Port Mismatches
One of the most immediate indicators of compromise is a mismatch between the process executable and the expected network activity. 
- `svchost.exe` communicating over port 4444.
- `lsass.exe` initiating outbound connections to external IP addresses.
- `notepad.exe` listening on a port.

In standard environments, processes have predictable network behaviors. Threat hunters must establish a baseline of "normal" behavior for core Windows processes. For example, `lsass.exe` rarely needs to communicate over the external network unless it is actively authenticating against a Domain Controller (which is usually internal).

### 2. Terminated Processes with Active Connections
Because `netscan` recovers closed or in-memory structures that haven't been overwritten yet, you may find network connections associated with a PID that no longer exists in the active process list (`pslist`). This could indicate:
- A short-lived malware execution that established a C2 channel, delivered a payload, and then exited to evade detection.
- Malware that injected code into a process, established a network connection, and then terminated the host process after the connection was no longer needed or if the injection failed gracefully.

### 3. Rogue Listening Ports
Rootkits and backdoors often bind to specific ports to await commands from the attacker (bind shells). These ports might be hidden from live analysis tools. By analyzing the `LISTENING` state in `netscan` output, hunters can identify these hidden backdoors. Always map the listening port to the PID, and then use tools like `malfind` or `psxview` to investigate the process further. Keep an eye out for high-numbered, random-looking ports, or conversely, ports attempting to blend in (e.g., an unapproved web server listening on 8080).

### 4. Correlation with Threat Intelligence
The remote IP addresses extracted by `netscan` should immediately be enriched with threat intelligence data. While an IP might appear benign, passive DNS records, BGP routing data, and reputation scores can reveal if the infrastructure is associated with known APT groups, bulletproof hosting, or malicious Tor exit nodes. 

### 5. Time-Wait and Close-Wait States
Connections in `TIME_WAIT` or `CLOSE_WAIT` states are highly valuable. These represent connections that were active shortly before the memory dump was taken. They can reveal temporal information about when an attacker was interacting with the system, helping to narrow down the timeline of the attack. They also provide insight into intermittent beaconing behavior that might not be fully established at the exact moment of acquisition.

## Rootkit Subversion Tactics

While `netscan` is highly effective, advanced rootkits are not defenseless. They continuously evolve to evade detection by security tools, including memory forensic plugins.

### Pool Tag Alteration
Since `netscan` relies on pool tag scanning, a sophisticated kernel-level rootkit could manually alter the pool tags of its network structures after allocation. By changing the `TCPT` tag to a random 4-byte string, the structure would effectively become invisible to `netscan`. However, altering pool tags is extremely dangerous for the rootkit; it can easily cause system instability or Blue Screens of Death (BSODs) if the Windows Memory Manager attempts to free or interact with the corrupted tag during normal system operations. Thus, this technique is rare but highly impactful.

### Custom Network Stacks
Some extreme forms of malware bypass the Windows `tcpip.sys` stack entirely. They implement their own custom Network Driver Interface Specification (NDIS) drivers or raw socket implementations to communicate directly with the network interface card (NIC) hardware. Since these connections are never registered with the standard Windows TCP/IP structures, `netscan` will simply not find them. In these cases, hunters must rely on `pcap` analysis at the network perimeter or perform complex manual memory analysis to identify custom protocol signatures within driver memory spaces.

### Process Hollowing and Masquerading
To evade the "mismatch" analysis technique, malware will often perform process hollowing. It will spawn a legitimate process (like `iexplore.exe` or `edge.exe`), unmap its legitimate code from memory, and inject malicious code. The network connection will then appear to originate from a legitimate browser, making it harder to spot an anomaly in the `netscan` output alone. This is precisely why `netscan` must always be chained with memory anomaly detection plugins like `malfind` or `hollowfind` to verify the integrity of the communicating process.

## Real-World Attack Scenario

### Initial Compromise
An employee in the finance department receives a highly targeted spear-phishing email containing a malicious Microsoft Word document masquerading as an invoice. The document exploits a zero-day vulnerability in the Equation Editor, executing a sophisticated shellcode payload that downloads a secondary, stealthy stager into memory.

### Persistence and Privilege Escalation
The memory-resident stager executes and utilizes an unpatched local privilege escalation vulnerability (e.g., in `win32k.sys`) to gain `NT AUTHORITY\SYSTEM` privileges. It then drops an advanced kernel-level rootkit designed to maintain stealthy persistence across reboots.

### C2 Communication and Evasion
The rootkit injects its primary payload into a newly spawned `svchost.exe` process, masquerading as a standard Windows service. The injected thread establishes an outbound TLS connection to a compromised WordPress site serving as a C2 proxy (IP: 198.51.100.22). 
To hide this connection from the local administrator and endpoint detection and response (EDR) solutions, the rootkit hooks the SSDT (System Service Descriptor Table) and manipulates the linked lists used by `netstat` and `GetExtendedTcpTable` APIs to filter out any connections matching the C2 IP address.

### Detection via Memory Forensics
An incident response team is called in due to suspicious lateral movement alerts elsewhere in the network. They acquire a full physical memory dump of the suspected initial compromise system.

The analyst runs `volatility -f memdump.raw windows.netscan`.
Because `netscan` bypasses the user-mode APIs and the kernel-mode linked lists, scanning for pool tags directly in physical RAM, it successfully uncovers the hidden C2 connection:
```text
Offset(V)          Local Address        Remote Address           State        PID      Owner        Created
0xfffffa8012345678 192.168.1.50:49152   198.51.100.22:443        ESTABLISHED  2048     svchost.exe  2023-10-27 14:02:00
```
The analyst notes that `svchost.exe` (PID 2048) is communicating with an external IP, which is anomalous behavior for the specific services hosted within that particular process instance. The analyst then runs `windows.malfind` on PID 2048, uncovering the injected executable memory segment containing the C2 communication logic. 
By correlating the `netscan` output with the `malfind` results, the IR team pieces together the full attack chain, isolates the machine, and pivots to hunt for the C2 IP across the broader network environment.

## Advanced Data Structure Parsing

For forensic analysts writing custom tools or extending Volatility, understanding the raw structure is vital. Let's look at a simplified `_TCP_ENDPOINT_CREATION_INFO` structure representation in memory:

```c
typedef struct _TCP_ENDPOINT_CREATION_INFO {
    // Basic metadata
    PVOID OwnerProcess; // Pointer to EPROCESS structure
    ULONG LocalAddress;
    ULONG RemoteAddress;
    USHORT LocalPort;
    USHORT RemotePort;
    // ... WFP specific fields ...
    ULONG ConnectionState;
} TCP_ENDPOINT_CREATION_INFO, *PTCP_ENDPOINT_CREATION_INFO;
```

A threat hunter could manually traverse physical memory using a hex editor or a custom Python script (e.g., using Rekall or Volatility APIs directly), searching for the hex signature of the `TCPT` tag, and then parse the subsequent bytes according to this structure definition. This manual approach is necessary if automated tools fail due to an unknown OS build or a particularly destructive rootkit technique. Furthermore, identifying the `OwnerProcess` pointer allows the analyst to directly trace back to the `_EPROCESS` block, bypassing any spoofed PIDs.

## Conclusion

The analysis of network connections in memory via tools like `netscan` is an indispensable skill in the modern threat hunter's arsenal. By understanding the underlying mechanics of pool tag scanning and the operating system's network data structures, analysts can uncover stealthy rootkits, identify sophisticated C2 channels, and reconstruct the actions of advanced adversaries. This technique, when combined with process memory analysis and threat intelligence, forms a robust defense against even the most evasive threats. Always trust physical memory over live system APIs when dealing with kernel-level compromises.

## Chaining Opportunities
- Correlate anomalous PIDs found in `netscan` with `[[01 - Process Memory Analysis and Injection Detection]]` to identify process hollowing or DLL injection.
- Use the remote IPs discovered to hunt for associated dropped files using `[[02 - Fileless Malware and Registry Forensics]]`.
- If the network structures appear corrupted or manually unlinked, transition to `[[08 - Kernel Level Rootkits SSDT Hooking Detection]]` to identify the underlying rootkit mechanism.
- Cross-reference listening ports with `[[05 - Analyzing Scheduled Tasks and Services in Memory]]` to see if the malicious process is maintaining persistence via a hidden service.
- Investigate the DNS cache in memory `[[11 - DNS Cache and ARP Table Forensics]]` to find the domain associated with the suspicious IP address.

## Related Notes
- `[[01 - Process Memory Analysis and Injection Detection]]`
- `[[02 - Fileless Malware and Registry Forensics]]`
- `[[03 - Memory Acquisition and Preservation Techniques]]`
- `[[08 - Kernel Level Rootkits SSDT Hooking Detection]]`
- `[[09 - Direct Kernel Object Manipulation DKOM Detection]]`
