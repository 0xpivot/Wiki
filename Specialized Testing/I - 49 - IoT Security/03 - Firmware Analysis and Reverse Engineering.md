---
tags: [iot, pentesting, hardware, vapt]
difficulty: intermediate
module: "49 - IoT Security"
topic: "49.03 Firmware Analysis and Reverse Engineering"
---

# 49.03 Firmware Analysis and Reverse Engineering

## Introduction to Firmware Analysis

Once a firmware image has been successfully extracted from an IoT device—whether downloaded from a vendor's website, captured in transit during an OTA update, or physically dumped from an EEPROM/Flash chip—the next critical phase is Firmware Analysis and Reverse Engineering. 

This phase represents the transition from hardware manipulation to software exploitation. The ultimate goal is to dissect the monolithic binary blob, understand its internal structure, extract the underlying file system, and analyze the proprietary executable files and scripts for vulnerabilities. This process is essential for identifying hardcoded secrets, backdoors, command injection flaws, memory corruption vulnerabilities (like buffer overflows), and insecure cryptographic implementations.

Firmware analysis is fundamentally an exercise in puzzle-solving. An analyst receives a raw stream of bytes and must systematically apply heuristics, pattern matching, and reverse engineering tools to reconstruct the operating environment of the embedded device.

---

## The Anatomy of an Embedded Firmware Image

Unlike standard ISO images or Windows executables, an IoT firmware file is typically a custom, vendor-specific concatenation of several distinct components. A typical embedded Linux firmware image consists of:

1.  **Firmware Header:** Contains metadata such as the vendor ID, firmware version, target hardware architecture, checksums (CRC32, MD5), and offsets to the other components. This is often proprietary.
2.  **Bootloader (e.g., U-Boot):** The low-level initialization code responsible for configuring the hardware and loading the kernel into RAM.
3.  **OS Kernel (e.g., `vmlinux`, `uImage`):** The core operating system, often compressed (LZMA, GZIP).
4.  **Root Filesystem (RootFS):** The directory structure containing the system libraries, utilities (like BusyBox), configuration files (`/etc`), and custom vendor applications. Common filesystems include `SquashFS`, `JFFS2`, `CramFS`, `UBIFS`, and `YAFFS2`.

---

## ASCII Diagram: Firmware Unpacking and Analysis Flow

```text
                                [RAW FIRMWARE BINARY (.bin)]
                                             |
                                             v
                           +-----------------------------------+
                           | STEP 1: INITIAL RECONNAISSANCE    |
                           | tools: file, strings, hexdump,    |
                           |        binwalk, entropy analysis  |
                           +-----------------------------------+
                                             |
                                 Is the firmware encrypted?
                                /                          \
                              YES                           NO
                              /                              \
            [Hardware extraction required]                    |
            [to find decryption keys]                         v
                                             +-----------------------------------+
                                             | STEP 2: EXTRACTION / UNPACKING    |
                                             | tools: binwalk -Me, dd, sasquatch,|
                                             |        jefferson, ubi_reader      |
                                             +-----------------------------------+
                                                              |
                                                              v
                                             +-----------------------------------+
                                             | STEP 3: FILESYSTEM ANALYSIS       |
                                             | - Inspect /etc/shadow, /etc/passwd|
                                             | - Look for API keys, hardcoded    |
                                             |   credentials, hidden web roots   |
                                             +-----------------------------------+
                                                              |
                                                              v
                           +-----------------------------------+-----------------------------------+
                           |                                                                       |
                           v                                                                       v
         +-----------------------------------+                                   +-----------------------------------+
         | STEP 4: STATIC BINARY ANALYSIS    |                                   | STEP 5: DYNAMIC EMULATION         |
         | tools: Ghidra, IDA Pro, Radare2   |                                   | tools: QEMU, Firmadyne, FAT       |
         | - Reverse engineer custom daemons |                                   | - Boot the firmware in a VM       |
         | - Identify Buffer Overflows, UAF  |                                   | - Fuzz exposed web/binary ports   |
         | - Trace insecure cryptography     |                                   | - Attach debuggers (gdbserver)    |
         +-----------------------------------+                                   +-----------------------------------+
```

---

## Step 1: Initial Reconnaissance

Before attempting to blindly extract the binary, it is crucial to understand its structure and composition. 

### Basic Linux Utilities
*   `file firmware.bin`: Determines if the file has a recognizable magic number or standard header.
*   `strings -n 10 firmware.bin | less`: Extracts printable characters. Looking for strings like "U-Boot", Linux kernel versions (e.g., `Linux version 2.6.36`), or web server directories can quickly indicate the OS type.
*   `hexdump -C firmware.bin | head`: Viewing the raw hex can help identify proprietary headers or known magic bytes.

### Entropy Analysis
If `strings` returns gibberish and `binwalk` finds no known signatures, the firmware might be compressed or encrypted.
*   Tool: `binwalk -E firmware.bin` generates an entropy graph.
*   **High Entropy (approx 1.0):** The data is highly random. If the *entire* file is high entropy, it is likely encrypted. If it has high entropy but starts with a recognizable header, it is likely compressed (e.g., LZMA).
*   **Low/Variable Entropy:** Indicates uncompressed code or file systems, which are prime targets for extraction.

---

## Step 2: Automated Extraction and Unpacking

The industry standard tool for firmware extraction is **Binwalk**. It scans the binary against a vast database of known file signatures (magic bytes) to identify embedded filesystems, compressed kernels, and bootloaders, and calculates their exact offsets.

### Using Binwalk
```bash
# Scan the firmware for known signatures
binwalk firmware.bin

# Output Example:
# DECIMAL       HEXADECIMAL     DESCRIPTION
# --------------------------------------------------------------------------------
# 512           0x200           U-Boot version string, "U-Boot 1.1.4"
# 65636         0x10064         LZMA compressed data, properties: 0x5D, dictionary size: 8388608 bytes
# 1310720       0x140000        Squashfs filesystem, little endian, version 4.0, compression:lzma
```

To automatically extract the contents, use the "Matryoshka" and extract flags:
```bash
binwalk -Me firmware.bin
```
*   `-e`: Extract known file types.
*   `-M`: Recursively scan extracted files (Matryoshka doll style).

### Specialized Filesystem Tools
Sometimes `binwalk` fails to cleanly extract specific embedded file systems due to vendor modifications or corruption. In these cases, manual extraction using `dd` to carve the binary and specialized tools is required:
*   **SquashFS:** A highly compressed, read-only file system. Use `unsquashfs` or `sasquatch` (a modified unsquashfs tool to handle vendor-specific non-standard implementations).
*   **JFFS2:** A journaling flash file system. Use `jefferson` to extract.
*   **UBIFS:** Unsorted Block Image File System. Use `ubi_reader` to unpack.

---

## Step 3: Filesystem Analysis (The "Treasure Hunt")

Once the RootFS is unpacked into a local directory structure (e.g., `_firmware.bin.extracted/squashfs-root/`), the static analysis phase begins.

### Key Targets for Review:
1.  **Configuration and Credentials:**
    *   `/etc/passwd` and `/etc/shadow`: Hunt for weak, hardcoded, or crackable password hashes for system users (root, admin, backdoors).
    *   `/etc/config/`, `/nvram/`: Look for plaintext Wi-Fi passwords, PPPoE credentials, or vendor API tokens.
2.  **Web Application Root:**
    *   `/var/www/`, `/usr/www/`, `/htdocs/`: IoT devices often feature a local web UI. Extract the HTML/JS, CGI scripts (often written in C, Shell, or Lua), and PHP files. Analyze these for Command Injections and XSS without even needing to run the device.
3.  **Startup Scripts:**
    *   `/etc/init.d/`, `/etc/rc.local`: These scripts reveal exactly which daemons start on boot. Finding an undocumented Telnet daemon starting on port 2323 here is a common discovery.
4.  **Cryptographic Material:**
    *   `/etc/ssl/`, `.pem`, `.crt`, `.key` files. Finding the private key used for the device's web server, or the private key used for mutual TLS authentication with the cloud, is a critical compromise.

---

## Step 4: Dynamic Emulation

Static analysis has limits, especially when dealing with complex binaries. To observe runtime behavior, you can emulate the firmware architecture on your host machine using **QEMU** (Quick Emulator).

### User-Mode Emulation
Allows you to run a single executable from the extracted firmware, utilizing your host kernel but translating the architecture (e.g., ARM to x86).
```bash
# Copy the static QEMU binary into the extracted root filesystem
cp $(which qemu-arm-static) ./squashfs-root/usr/bin/

# Use chroot to change the root directory, then run the target binary
sudo chroot ./squashfs-root /usr/bin/qemu-arm-static /bin/busybox
```

### Full System Emulation (Firmadyne / FAT)
Tools like **Firmadyne** or the **Firmware Analysis Toolkit (FAT)** attempt to emulate the entire device, booting the extracted kernel and root filesystem inside a virtual network.
*   If successful, you can interact with the emulated device's web server in your local browser, run port scans against the virtual IP, and run dynamic web exploitation tools (like Burp Suite or Nikto) as if you were attacking the real physical hardware.

---

## Step 5: Static Binary Analysis

Proprietary compiled binaries (often C/C++) found in `/bin/` or `/usr/sbin/` (such as custom web servers like `httpd` or UPnP daemons like `miniupnpd`) are prime targets for vulnerability discovery.

### Reverse Engineering Frameworks
*   **Ghidra:** The NSA's open-source SRE framework. It includes a powerful decompiler that handles obscure architectures common in IoT (MIPS, ARM, PowerPC, SuperH) natively.
*   **IDA Pro:** The industry standard, highly capable but expensive.
*   **Radare2 / Cutter:** Excellent lightweight, CLI-first (or GUI with Cutter) open-source alternatives.

### Identifying Vulnerabilities
1.  **Architecture:** Determine the architecture (e.g., 32-bit ARM, Little Endian) using the `file` command. Load the binary into Ghidra.
2.  **String References:** Search for strings like `admin`, `password`, or `%s` to find authentication routines or format string vulnerabilities.
3.  **Dangerous Functions:** Check the "Symbol Tree" for imported functions like `system()`, `popen()`, `strcpy()`, `sprintf()`, and `gets()`.
    *   A call to `system()` taking unsterilized input from a web HTTP GET parameter (handled by a CGI binary) is a classic recipe for Remote Code Execution (RCE) via Command Injection.
    *   Calls to `strcpy()` on user input into fixed-size buffers lead to Buffer Overflows, allowing an attacker to overwrite the Return Address on the stack and execute shellcode or Return-Oriented Programming (ROP) chains.

---

## Chaining Opportunities

*   **Extraction -> Analysis -> RCE:** Extract firmware via UART `->` Unpack RootFS with Binwalk `->` Emulate the custom `httpd` binary with QEMU `->` Use Ghidra to discover an unauthenticated `system()` command injection flaw in the password reset logic `->` Exploit it dynamically against the physical device.
*   **RootFS Analysis -> Cryptographic Pivot:** Grep the extracted `/etc/` directory for `.key` files `->` Discover a hardcoded RSA private key used by all devices of this model to authenticate to the vendor's MQTT broker `->` Use the key to spoof devices, intercepting thousands of user telemetry streams.

## Related Notes
*   [[02 - IoT Device Firmware Extraction]]
*   [[04 - Hardcoded Credentials in Firmware]]
*   [[05 - Telnet SSH Exposed on IoT Devices]]
