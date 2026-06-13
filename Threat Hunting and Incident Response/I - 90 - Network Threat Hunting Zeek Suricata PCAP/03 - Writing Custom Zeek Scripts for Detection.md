---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.03 Writing Custom Zeek Scripts for Detection"
---

# Writing Custom Zeek Scripts for Detection

## 1. The Power of Zeek Scripting

The true power of Zeek lies not in its default log generation, but in its fully functional, domain-specific, Turing-complete scripting language. 

While Suricata rules match static patterns and byte sequences, Zeek scripts execute complex logic based on network state and parsed protocol structures. 

This programmatic approach allows threat hunters and detection engineers to write scripts that identify anomalous behavior mathematically, extract payloads dynamically, track state across hours of traffic, or integrate seamlessly with external threat intelligence systems.

## 2. Event-Driven Architecture Deep Dive

Zeek scripting is fundamentally **event-driven**. The underlying C++ Event Engine (protocol analyzers) parses the raw network packets and emits "events." 

Zeek scripts contain event handlers that "listen" for these events and execute code when they occur.

For example:
- When a TCP three-way handshake completes, the engine emits `connection_established`.
- When an HTTP GET request is fully parsed, it emits `http_request`.
- When a file transfer begins, it emits `file_sniff`.

### 2.1 Zeek Script Execution Diagram

```text
    Network Traffic
         |
         v
+-----------------------+
|  C++ Protocol Parsers | (e.g., HTTP Analyzer)
+-----------------------+
         |
         | (Emits Event: http_request(c: connection, method: string, ...))
         v
+-----------------------+
|   Event Queue         |
+-----------------------+
         |
         v
+-----------------------+      +--------------------------------+
|  Zeek Script Engine   | ---> |  event http_request(c: connection) |
+-----------------------+      |  {                             |
                               |    if (c$http$uri == "/admin") |
                               |       ...                      |
                               |  }                             |
                               +--------------------------------+
```

## 3. Syntax and Core Data Types

Zeek script syntax resembles a hybrid of C, Python, and JavaScript.

**Core Data Types:**

- `string`: Standard text strings.
- `count`: Unsigned integers (often used for bytes and counters).
- `addr`: IP addresses (IPv4 and IPv6). Supports subnet masking.
- `port`: Network ports, defined with the protocol (e.g., `80/tcp`).
- `time` and `interval`: Absolute timestamps and durations.
- `record`: Complex data structures similar to structs in C. The ubiquitous `connection` record (referenced as `c`) contains all metadata about a flow.
- `set` and `table`: Hash sets and hash maps for extremely fast O(1) lookups.

### 3.1 Example: Basic Event Handler

Let's write a simple script that logs a message to stdout every time an HTTP request to an `.exe` file is observed.

```zeek
# Listen for HTTP requests
event http_request(c: connection, method: string, original_URI: string,
                   unescaped_URI: string, version: string)
    {
    # We use the unescaped URI for accurate regex matching
    if ( /\.exe$/ in unescaped_URI )
        {
        print fmt("Alert! Executable download attempt: %s -> %s%s", 
                  c$id$orig_h, c$http$host, unescaped_URI);
        }
    }
```

## 4. Advanced Scripting: Automated File Extraction

One of the most powerful features of Zeek is the File Analysis framework. 

We can instruct Zeek to automatically carve, reassemble, and save files traversing the network based on complex conditional logic.

Let's write a script that extracts executable files, but *only* if they originate from an internal IP range, indicating lateral movement.

```zeek
@load base/frameworks/files
@load base/utils/site

export {
    # Define our internal network range using a set of subnets
    redef Site::local_nets += { 10.0.0.0/8, 192.168.0.0/16 };
}

# Hook into the file identification event
event file_sniff(f: fa_file, meta: fa_metadata)
    {
    # Only process if the file has a derived MIME type (magic bytes)
    if ( ! meta?$mime_type ) return;

    # Look for Windows PE executables
    if ( meta$mime_type == "application/x-dosexec" )
        {
        # Check if the sender (originator) is in our local network
        for ( c in f$conns )
            {
            if ( Site::is_local_addr(c$id$orig_h) )
                {
                # Instruct Zeek to extract this specific file to disk
                Files::add_analyzer(f, Files::ANALYZER_EXTRACT);
                print fmt("Lateral Movement indicator: Exe extracted from %s", c$id$orig_h);
                break; # Prevent duplicate extractions if file spans multiple connections
                }
            }
        }
    }
```

## 5. The Notice Framework for Alerting

Using `print` is unacceptable for production alerting. Zeek provides the Notice Framework to handle alerts securely, consistently, and without flooding logs. 

Notices can be routed to `notice.log`, emailed to administrators, or forwarded to a SIEM.

To create a Notice, we define an `enum` of Notice Types, and use the `NOTICE()` function.

```zeek
module MyCustomDetections;

export {
    # Define a custom notice type
    redef enum Notice::Type += {
        Suspicious_SSH_Port
    };
}

# Listen for connection state removal (end of connection)
event connection_state_remove(c: connection)
    {
    # If Dynamic Protocol Detection identified SSH, but the port is NOT 22
    if ( c?$ssh && c$id$resp_p != 22/tcp )
        {
        NOTICE([
            $note = Suspicious_SSH_Port,
            $msg = fmt("SSH traffic detected on non-standard port %s", c$id$resp_p),
            $conn = c,
            $identifier = cat(c$id$orig_h, c$id$resp_p), # Deduplication key
            $suppress_for = 1hrs # Suppress identical alerts for 1 hour
        ]);
        }
    }
```

## 6. Extending Records and State Tracking

Zeek allows you to add custom fields to existing records dynamically. 

If you want to track a custom flag across an entire HTTP session, you can add a field to the `connection` record.

```zeek
redef record connection += {
    my_custom_flag: bool &default=F;
};
```

This is vital for tracking state across multiple packets or events within the same flow.

## 7. Performance Considerations

Zeek scripts run synchronously within the event engine. 

- Avoid loops over massive datasets within an event handler.
- Use `set` and `table` lookups (which are highly optimized) instead of arrays.
- Offload heavy computing or external API queries to asynchronous functions where possible.

## 8. Real-World Attack Scenario

**Scenario:** A threat actor uses a custom command-and-control tool that communicates over HTTP, but standardizes its beacon by always including an unusual HTTP Header: `X-Cmd-Response: AuthSuccess`.

1. A standard IDS (Suricata) could write a signature for this, but the SOC wants to log the *entire payload* of only those specific malicious responses for immediate forensic review.
2. The team writes a Zeek script hooking the `http_header` event.
3. The script checks if `name == "X-Cmd-Response"`. If true, it modifies the connection state (`c$my_c2_flag = T`).
4. A subsequent event handler, `http_entity_data` (which fires iteratively as the HTTP body is transferred), checks if `c$my_c2_flag` is true. 
5. If true, the script concatenates the payload chunks and writes the decoded C2 commands directly into a custom `c2_commands.log` file.
6. The Threat Hunter monitors `c2_commands.log` in their SIEM and immediately sees the attacker issuing `whoami` and `tasklist` commands in real-time.

## 9. Chaining Opportunities

- **Intelligence Framework:** Custom scripts can query internal state tables against dynamic threat intelligence feeds loaded into Zeek.
- **Log Correlation:** Data parsed by custom scripts can be directly injected into standard logs (like adding custom JA3 hashes directly into `conn.log`).

## 10. Related Notes

- [[01 - Packet Capture PCAP Analysis at Scale]]
- [[02 - Introduction to Zeek Network Security Monitor]]
- [[04 - Suricata IDS IPS Rule Writing and Tuning]]
- [[05 - Hunting for C2 Beacons and Jitter]]
