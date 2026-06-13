---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.29 Core Dump Analysis"
---

# 44.29 Core Dump Analysis for Credentials

## 1. Introduction

A core dump (or memory dump) is a file containing a process's memory space at the exact time it terminated unexpectedly. In Linux environments, core dumps are primarily generated to aid developers and system administrators in debugging applications that crash due to segmentation faults, unhandled signals, or other fatal errors. 

However, from a security and penetration testing perspective, core dumps are a goldmine of sensitive information. Because a core dump represents the live RAM footprint of a process, it often contains plaintext credentials, encryption keys, session tokens, database connection strings, and sensitive user data that the application was processing in memory at the time of the crash. 

If an attacker or unprivileged user can trigger a crash in a privileged application (e.g., a process running as `root` or a service account), and if the system is configured to write core dumps to a world-readable directory or a location the user can access, they can analyze the resulting dump file to extract this sensitive data, leading to privilege escalation.

## 2. Architecture and Attack Flow

The following ASCII diagram illustrates the core dump generation process and the subsequent exploitation flow:

```text
+-----------------------------------------------------------------------------+
|                            Target Linux System                              |
|                                                                             |
|  +--------------------+                    +-----------------------------+  |
|  | Privileged Process |                    | Kernel (Core Dump Handler)  |  |
|  | (Running as root)  | 1. Crash/Segfault  |                             |  |
|  | - Passwords in RAM | -----------------> | Uses /proc/sys/kernel/      |  |
|  | - SSH Keys in RAM  |                    | core_pattern to determine   |  |
|  | - API Tokens       |                    | where to write the file.    |  |
|  +--------------------+                    +-----------------------------+  |
|            ^                                              |                 |
|            | 2. Attacker intentionally triggers           | 3. Writes dump  |
|            |    crash (e.g., via long input, DoS)         v                 |
|            |                               +-----------------------------+  |
|  +--------------------+                    | /var/crash/                 |  |
|  | Unprivileged Shell |                    | /tmp/                       |  |
|  | (Attacker Access)  | <----------------- | core.<pid> (dump file)      |  |
|  |                    |  4. Attacker reads +-----------------------------+  |
|  +--------------------+     the core dump file                              |
|            |                                                                |
|            | 5. Extracts credentials                                        |
|            v                                                                |
|  +--------------------+                                                     |
|  | Root Access via    |                                                     |
|  | Extracted Creds!   |                                                     |
|  +--------------------+                                                     |
+-----------------------------------------------------------------------------+
```

## 3. The 'Why': Understanding the Vulnerability

Why does this vulnerability exist, and why is it so prevalent? 

1.  **Memory Management:** Applications typically read sensitive data into memory to use it (e.g., verifying a password hash, establishing a database connection). Many developers fail to securely wipe or zero out this memory after use (`explicit_bzero` or similar functions in C/C++), leaving the sensitive data lingering in the heap or stack.
2.  **Insecure System Defaults:** Some Linux distributions or enterprise configurations enable core dumps by default to assist with telemetry and debugging. 
3.  **Predictable Dump Locations:** The `core_pattern` kernel parameter often directs core dumps to predictable, world-readable locations like `/tmp` or the current working directory of the crashed process.
4.  **Improper File Permissions:** If the system is not configured to restrict permissions on generated core files, they may be created with default permissions (dictated by the application's `umask`), which could allow read access by any user on the system.

## 4. Identifying Core Dump Configurations

Before attempting to force a core dump or search for existing ones, you must understand how the system is configured to handle them.

### 4.1 Checking User Limits (`ulimit`)

The first check is whether the current shell or user is permitted to create core files. The soft and hard limits for core file sizes are governed by `ulimit`.

```bash
# Check the soft limit for core file size
ulimit -c

# Check all limits
ulimit -a
```
If the output is `0`, core dumps are disabled for the current session. If it is `unlimited` or a specific size, they are enabled. Note that a privileged process running as a daemon might have different limits set by its `systemd` service file (`LimitCORE=`).

### 4.2 Checking `core_pattern`

The `core_pattern` file determines the naming convention and destination for core dumps.

```bash
cat /proc/sys/kernel/core_pattern
```
Common outputs and their meanings:
*   `core`: The file will simply be named `core` and placed in the current working directory of the process.
*   `/var/crash/%e.%p.%t.core`: Placed in `/var/crash/` with a name containing the executable name (`%e`), PID (`%p`), and timestamp (`%t`).
*   `|/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h`: Piped to a handler like `systemd-coredump` or `apport`. In these cases, dumps might be managed by a service and stored centrally (e.g., `/var/lib/systemd/coredump/`).

### 4.3 Investigating systemd-coredump

If `systemd-coredump` is in use, you can use the `coredumpctl` utility to list existing crashes:

```bash
# List all registered core dumps
coredumpctl list

# Filter by a specific program
coredumpctl list /usr/sbin/sshd
```

## 5. Locating Existing Core Dumps

Even if you cannot trigger a new core dump, previous crashes may have left artifacts behind. Use `find` to hunt for these files.

```bash
# Search for files named 'core' or starting with 'core.'
find / -type f -name "core*" -exec ls -l {} + 2>/dev/null

# Search common crash directories
ls -la /var/crash/
ls -la /var/lib/systemd/coredump/
ls -la /tmp/
ls -la /var/tmp/
```
Pay close attention to the file owner and permissions. If a dump is owned by `root` but world-readable (`-rw-r--r--`), it is ripe for analysis.

## 6. Triggering a Core Dump

If you have identified a vulnerable service (e.g., an internal tool running as root, a custom SUID binary, or a daemon) that processes sensitive data, you can attempt to crash it.

### 6.1 Process Signaling

If you have sufficient privileges (e.g., the process is running under your UID, but you need to escalate within a container, or you have weak sudo access), you can send a segmentation fault signal directly:

```bash
# Send SIGSEGV (Signal 11) to cause a core dump
kill -11 <PID>

# Send SIGABRT (Signal 6)
kill -6 <PID>
```

### 6.2 Exploiting Application Vulnerabilities

If you cannot signal the process directly, you must trigger a crash via an application flaw:
*   **Buffer Overflows:** Feed excessively long strings to input fields, command-line arguments, or environment variables.
*   **Null Pointer Dereferences:** Provide unexpected input types or deliberately omit required parameters.
*   **Race Conditions:** Exhaust system resources or manipulate files while the target process is accessing them.
*   **Fuzzing:** Use basic fuzzing techniques against network sockets or local APIs exposed by the service.

## 7. Analyzing the Core Dump

Once you have acquired a core dump, you need to extract the sensitive information. Since core files can be gigabytes in size, efficient analysis is crucial.

### 7.1 Using `strings` and `grep`

The most straightforward method is to extract all printable ASCII strings and search for known patterns.

```bash
# Extract strings and search for 'password' (case-insensitive)
strings core.1234 | grep -i "password"

# Look for surrounding context (e.g., 5 lines before and after)
strings core.1234 | grep -i -C 5 "secret"

# Search for SSH private keys
strings core.1234 | grep -E "BEGIN (RSA|OPENSSH|PRIVATE) KEY" -A 30
```

*Pro-Tip:* If you know the format of the credential (e.g., a specific API key prefix like `AKIA` for AWS), grep for that specific regex.

### 7.2 Hex Dumping with `xxd` or `hexdump`

Sometimes data is stored in structural formats (structs) or near specific byte patterns. Hex editors help visualize memory layout.

```bash
# Hex dump and pipe to less for manual review
xxd core.1234 | less
```

### 7.3 Advanced Analysis with GDB (GNU Debugger)

For deeper analysis, especially if you have the original binary, `gdb` is incredibly powerful. It allows you to inspect specific memory registers and variables at the time of the crash.

```bash
# Load the core dump into gdb
gdb /path/to/binary /path/to/core.1234

# Inside GDB:
# View the backtrace (where the program crashed)
(gdb) bt

# Inspect all registers
(gdb) info registers

# Examine a specific memory address (e.g., as a string)
(gdb) x/s 0x7fffffffe000

# Search memory for a specific pattern (e.g., "admin")
(gdb) find 0x00000000, +0xffffffff, "admin"
```

### 7.4 Specialized Memory Forensics Tools

While traditionally used for full system memory dumps, tools like Volatility or custom scripts (like Mimikatz for Linux / `mimipenguin`) can sometimes be adapted or conceptually applied to process core dumps to locate specific credential structures (like shadow hashes or cleartext passwords from PAM).

## 8. Real-World Penetration Testing Scenario

During an internal penetration test, you compromise a low-privileged developer account on a Linux build server. 

1.  **Enumeration:** You notice a custom deployment agent running as `root`: `/opt/deploy/agent`.
2.  **Vulnerability Discovery:** You discover that the agent reads deployment keys from a secure vault into memory. You also notice that running `/opt/deploy/agent --test AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` causes a segmentation fault.
3.  **Core Dump Check:** You run `cat /proc/sys/kernel/core_pattern` and see it is set to `/tmp/core.%e.%p`.
4.  **Exploitation:** You trigger the crash using the long string argument.
5.  **Harvesting:** You navigate to `/tmp/` and find `core.agent.4582`.
6.  **Extraction:** You run `strings /tmp/core.agent.4582 | grep -i -C 5 "vault_token"`. The output reveals the plaintext administrative vault token that the agent had loaded into memory just before crashing.
7.  **Escalation:** You use this vault token to access the central secrets manager and retrieve the root password for the server.

## 9. Defensive Hardening & Mitigation

To prevent core dump exploitation, administrators should:
1.  **Disable Core Dumps System-Wide:** Set `* hard core 0` in `/etc/security/limits.conf`.
2.  **Restrict `core_pattern`:** Ensure core dumps are written to secure, root-only directories (e.g., `/var/crash` with `700` permissions) rather than world-readable locations.
3.  **Use systemd-coredump:** Configure it to compress and restrict access to core dumps strictly to administrators.
4.  **Secure Coding Practices:** Developers must implement secure memory wiping (e.g., `memset_s`, `explicit_bzero`) for all sensitive variables immediately after they are no longer needed.
5.  **SUID Handling:** The Linux kernel feature `fs.suid_dumpable` controls whether setuid/setgid programs can dump core. This should be set to `0` (disabled) or `2` (suidsafe, writes to root-owned files only).

## Chaining Opportunities
- Can be combined with **[[12 - SUID Executable Exploitation]]** to force crashes in privileged binaries.
- Links closely with **[[31 - tmp Race Conditions]]** if core dumps are written to `/tmp/`, allowing symlink attacks during the dump creation.
- Extracted credentials can immediately pivot into **[[08 - SSH Hijacking and Key Theft]]**.

## Related Notes
- [[18 - Memory Corruption Basics]]
- [[22 - Credential Harvesting in Linux]]
- [[35 - Defense File Permission Hardening]]
