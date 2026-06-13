---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.27 D-Bus Misconfigurations"
---

# D-Bus Interface Misconfigurations

## Introduction
The Desktop Bus, commonly known as **D-Bus**, is an inter-process communication (IPC) and remote procedure call (RPC) mechanism that allows multiple processes communicating on a Linux operating system to interact with one another. It has become a foundational component of modern Linux desktop environments (like GNOME and KDE) and system management daemons (like Systemd, NetworkManager, and snapd).

D-Bus operates primarily on two buses:
1. **The System Bus:** A single, heavily restricted bus used for system-wide communication, usually running as `root`. System daemons listen on this bus to receive commands (e.g., adding a network interface, installing a package).
2. **The Session Bus:** Created per-user login, used for communication between desktop applications (e.g., a media player talking to the desktop notification system).

Privilege escalation occurs when a service running as `root` on the **System Bus** exposes methods that can be invoked by unprivileged users, and those methods perform dangerous actions (like executing commands, modifying files, or altering system state) without proper authorization checks like Polkit.

## D-Bus Architecture and Vulnerability Mechanics
D-Bus uses a structured naming convention:
- **Bus Name (Destination):** The registered name of the service (e.g., `org.freedesktop.systemd1`).
- **Object Path:** The specific instance within the service (e.g., `/org/freedesktop/systemd1`).
- **Interface:** The group of methods/signals (e.g., `org.freedesktop.systemd1.Manager`).
- **Method:** The specific action to execute (e.g., `StartUnit`).

Services define XML-based security policies in `/etc/dbus-1/system.d/`. If a policy allows an unprivileged user (or `default` allow policy) to send messages to a privileged interface, and the backend daemon trusts the input without validating the user's authority, it results in privilege escalation.

### ASCII Diagram: D-Bus Exploitation Flow

```text
+----------------------------------------------------------------------------------+
|                            D-BUS EXPLOITATION PATH                               |
+----------------------------------------------------------------------------------+
|                                                                                  |
|   Unprivileged User Space                  System Bus (Root Context)             |
|   =======================                  =========================             |
|                                                                                  |
|  1. Attacker queries D-Bus services                                              |
|     $ busctl tree                                                                |
|          |                                                                       |
|          v                                                                       |
|  2. Attacker identifies a vulnerable service                                     |
|     Destination: com.ubuntu.LanguageSelector                                     |
|     Interface:   com.ubuntu.LanguageSelector                                     |
|     Method:      SetSystemDefaultLanguage                                        |
|          |                                                                       |
|          | (Sends malicious D-Bus message via dbus-send or busctl)               |
|          v                                                                       |
|  +---------------------------+        +--------------------------------------+   |
|  | D-Bus Daemon (dbus-daemon)| -----> | Target Service (Root Daemon)         |   |
|  | Checks Policy: ALLOWED    |        | /usr/lib/language-selector-daemon    |   |
|  +---------------------------+        +--------------------------------------+   |
|                                                         |                        |
|                                                         v                        |
|                                       3. Daemon executes action using input      |
|                                          e.g., writes attacker's input to        |
|                                          /etc/default/locale or exec()           |
|                                                         |                        |
|                                                         v                        |
|                                       4. Root Shell or Arbitrary File Write!     |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

## Enumeration and Interaction Tools

To interact with D-Bus, penetration testers use command-line utilities like `busctl` (provided by systemd) and `dbus-send`.

### 1. Listing Services and Objects
To list all active services on the system bus:
```bash
busctl --system list
```

To see the object tree of a specific service:
```bash
busctl --system tree org.freedesktop.NetworkManager
```

### 2. Introspecting Interfaces
Introspection asks the object to reveal what interfaces and methods it supports.
```bash
busctl --system introspect org.freedesktop.systemd1 /org/freedesktop/systemd1
```
This outputs the methods, signatures (the data types they expect, such as `s` for string, `b` for boolean, `a{ss}` for an array of dicts), and properties.

## Exploitation Scenarios

### Scenario 1: Abusing Unauthenticated Systemd Methods
Historically, specific versions of `systemd` or wrapper services lacked proper Polkit validation. If an attacker finds an exposed method that alters system configuration or triggers executions, they can invoke it directly.

Example: A custom backup daemon (`com.corp.backup`) exposes a `StartBackup` method that takes a string argument (the path to backup) and passes it directly to a shell command without sanitization.

**Exploitation:**
```bash
dbus-send --system --print-reply --dest=com.corp.backup /com/corp/backup \
com.corp.backup.Manager.StartBackup string:"; chmod +s /bin/bash #"
```
The daemon runs as root, parses the string, and executes the injected command.

### Scenario 2: Vulnerable Daemons (e.g., `aptdaemon` or `snapd`)
Many critical Linux CVEs originate from D-Bus interactions. 
- **CVE-2020-11901 (snapd):** Attackers could bypass access controls on the `snapd` D-Bus API to install malicious packages from the store, leading to root execution.
- **CVE-2015-1328 (OverlayFS/Apport):** While primarily a kernel issue, D-Bus interactions with crash handlers like `apport` often allow local users to manipulate root processes via predictable file paths and D-Bus signaling.

### Scenario 3: Bypassing Polkit via D-Bus Timing/UID Spoofing (CVE-2021-3560)
A highly notable D-Bus vulnerability involved `polkit`. Polkit checks permissions by asking D-Bus for the UID of the process making the request. 
If an attacker initiates a D-Bus request (e.g., creating a new user via `org.freedesktop.Accounts`) and immediately kills the requesting process before Polkit finishes validating it, Polkit attempts to look up the UID of a PID that no longer exists. Due to an error in error handling, Polkit would default to `UID 0` (root), allowing the unprivileged request to pass as if it came from root.

**Exploit Flow for CVE-2021-3560:**
1. Start a `dbus-send` command to create a new `sudo` user via `accounts-daemon`.
2. Determine the time it takes to reach Polkit.
3. Send the command again and kill the process exactly halfway through the validation window.
4. The user is created and added to the `sudo` group.

## Defensive Posture and Mitigations

### 1. Strict D-Bus Policy Configuration
System administrators and developers must ensure that `/etc/dbus-1/system.d/` configurations follow the principle of least privilege.
A vulnerable policy might contain:
```xml
<policy context="default">
  <allow send_destination="com.corp.daemon"/>
</policy>
```
A secure policy must restrict access to `root` or specific groups:
```xml
<policy user="root">
  <allow send_destination="com.corp.daemon"/>
</policy>
<policy context="default">
  <deny send_destination="com.corp.daemon"/>
</policy>
```

### 2. Mandatory Access Control (MAC) Authorization
Simply hiding D-Bus endpoints is insufficient. The backend daemon processing the D-Bus message *must* use `polkit` (or equivalent checks) to verify that the requesting user is authorized to perform the requested action. Never trust that D-Bus policy alone will secure the application.

### 3. Fuzzing and Code Review
Organizations developing custom Linux daemons must fuzz their D-Bus interfaces. Passing anomalous strings, extremely large integers, or special characters via `busctl` should not crash the daemon or result in command injection.

## Summary
D-Bus represents a massive, often overlooked attack surface on modern Linux systems. Because it bridges the gap between unprivileged desktop environments and root-level system management daemons, any misstep in authorization checks, string parsing, or IPC timing can yield an immediate root shell.

## Chaining Opportunities
- Deeply tied to [[24 - PwnKit CVE-2021-4034]], as Polkit is the primary authorization mechanism for D-Bus services.
- Can be chained with [[26 - Systemd Service File Abuse]] if D-Bus exposes methods to restart or modify system units.
- Information leaks via [[28 - proc Filesystem Information Leakage]] can assist in timing attacks against D-Bus.

## Related Notes
- [[13 - Capabilities Misconfigurations]]
- [[21 - Bash Script Weaknesses]]
