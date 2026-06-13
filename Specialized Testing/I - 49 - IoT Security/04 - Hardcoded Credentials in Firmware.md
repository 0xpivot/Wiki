---
tags: [iot, pentesting, hardware, vapt]
difficulty: intermediate
module: "49 - IoT Security"
topic: "49.04 Hardcoded Credentials in Firmware"
---

# 49.04 Hardcoded Credentials in Firmware

## Introduction to Hardcoded Secrets

One of the most pervasive, severe, and frequently exploited vulnerabilities in the Internet of Things (IoT) ecosystem is the presence of hardcoded credentials and cryptographic secrets within device firmware. This vulnerability falls squarely under the OWASP IoT Top 10 (specifically, "Insecure Default Settings" and "Insecure Data Transfer/Storage"). 

A "hardcoded secret" refers to authentication data—such as usernames, passwords, API keys, SSL/TLS private keys, or symmetric encryption keys—that is statically compiled into the executable binaries, written in plain text within configuration scripts, or stored unencrypted on the device's local filesystem.

Because these secrets are embedded into the firmware image, they are identical across every single device manufactured in that specific product line or hardware revision. If a security researcher or malicious actor manages to extract the firmware from a single physical device (e.g., via SPI flash dumping or downloading an OTA update), they instantly possess the keys to compromise every other device of the same model globally.

---

## The Developer's Mindset: Why Does This Happen?

Understanding why hardcoded credentials exist requires looking at the constraints and pressures of embedded systems engineering:
1.  **Debugging and Maintenance:** Developers often leave "backdoor" accounts or hardcoded root passwords in the firmware to ensure that field technicians or customer support agents can easily log into devices deployed in the field without needing the user's personal password.
2.  **Factory Provisioning:** During mass manufacturing, devices must be programmed quickly. Injecting unique, cryptographically secure keys per device (e.g., via a Hardware Security Module during flashing) increases manufacturing time and costs. Thus, vendors often bake a single "master" key into the universal firmware image.
3.  **Lack of Security Awareness:** In aggressive time-to-market scenarios, developers may temporarily hardcode API tokens for cloud communication during the prototyping phase and simply forget to remove them or implement a dynamic provisioning system before production release.
4.  **Misguided "Security by Obscurity":** Vendors often assume that because firmware is compiled into a `.bin` file, compressed, and sometimes obfuscated, attackers cannot read the underlying filesystem. Firmware extraction tools like `binwalk` completely invalidate this assumption.

---

## ASCII Diagram: The Lifecycle of a Hardcoded Secret Leakage

```text
  [DEVELOPMENT PHASE]               [MANUFACTURING]                [DEPLOYMENT]
  
  Developer embeds:                 Firmware flashed               1,000,000 devices
  - root:admin123          ----->   to all devices in    ----->    shipped globally
  - AWS_S3_KEY=xyz                  factory. Same keys             with identical
  - vendor_priv.pem                 on every unit.                 static secrets.
                                                                        |
                                                                        |
                                                                        v
   +--------------------------------------------------------------------+
   |                                                                    |
   v                                                                    v
[ATTACKER RECONNAISSANCE]                                       [EXPLOITATION & SCALE]

 1. Attacker buys ONE device.                                    6. Attacker maps internet (Shodan)
 2. Extracts firmware via UART/SPI.                                 for device fingerprints.
 3. Unpacks RootFS with Binwalk.                                 7. Automates botnet script using
 4. Greps /etc/ for 'root' or 'aws'.                                the extracted root:admin123.
 5. Recovers global keys.                                        8. Mass exploitation (e.g., Mirai).
```

---

## Common Locations for Hardcoded Secrets

Once an attacker has extracted and unpacked the firmware filesystem (e.g., `squashfs-root/`), identifying hardcoded secrets becomes an exercise in automated searching and manual code review.

### 1. The Linux Shadow and Passwd Files
The most obvious place to look in embedded Linux firmware is the system credential files.
*   **`/etc/passwd`:** Lists user accounts. Frequently reveals hidden accounts (e.g., `vendor_support`, `debug`, `factory`).
*   **`/etc/shadow`:** Contains the hashed passwords. In many poorly configured IoT devices, the hash might be extremely weak (DES or MD5) or the password itself might be guessable.
    *   *Example:* If the hash is `$1$xyz$abcde...`, the `$1$` indicates MD5. An attacker can load this into `Hashcat` or `John the Ripper` and crack it using wordlists or brute-force, eventually yielding the universal root password.

### 2. Initialization Scripts and Configuration Files
During boot, the system relies on shell scripts to start services. These are written in plain text.
*   **`/etc/init.d/` and `/etc/rc.local`:** Often contain startup commands for proprietary daemons. For example: `/usr/sbin/custom_telnetd -u root -p SuperSecretAdmin! &`.
*   **`/etc/config/` (OpenWrt environments):** Contains plain text configurations for wireless interfaces, sometimes revealing the default factory Wi-Fi WPA2 pre-shared key.
*   **`.ini`, `.json`, `.yaml`, `.xml` files:** Scattered throughout `/opt/` or `/var/`, these files frequently hold API endpoints, MQTT broker credentials, or database connection strings for the cloud backend.

### 3. Web Root Directories
IoT devices often host local web interfaces.
*   **`/var/www/`, `/htdocs/`:** Search through HTML, JavaScript, and CGI scripts.
*   **JavaScript:** Developers sometimes hardcode backend API keys directly into front-end JS files delivered to the browser.
*   **CGI/PHP:** Scripts may contain hardcoded local database credentials or logic that bypasses authentication if a specific HTTP header is present.

### 4. Cryptographic Certificates and Keys
*   Search for `.pem`, `.crt`, `.key`, `.der` files.
*   **SSL/TLS Private Keys:** If the device hosts an HTTPS server, its private key is on the device. Since all devices share the firmware, they all share the private key. An attacker can use this key to perform MITM attacks on the local network, stripping TLS encryption.
*   **Cloud Authentication Keys:** Many IoT ecosystems use Mutual TLS (mTLS) to authenticate devices to the cloud broker (like AWS IoT Core). If the private key is extracted, the attacker can spoof any device or create phantom devices to poison the cloud database.

### 5. Compiled Binaries (Executables and Libraries)
If secrets are not in plain text files, they are likely compiled directly into proprietary binaries (C/C++).
*   **Using `strings`:** Running `strings libcustom_crypto.so | grep "key"` might reveal hardcoded AES keys used to encrypt local SQLite databases or network payloads.
*   **Using Ghidra / IDA Pro:** If the key is obfuscated (e.g., constructed at runtime via XOR operations), static analysis and decompilation of the binary are required. You must trace the execution path of the encryption function to observe how the key string is assembled in memory.

---

## Automated Discovery Tools

Manually navigating a filesystem with thousands of files is inefficient. Security analysts rely on automated tools to grep for entropy and known secret patterns:

1.  **TruffleHog / Gitrob:** While designed for Git repositories, running TruffleHog against the extracted `squashfs-root/` directory will use regex patterns to hunt for AWS keys, Slack tokens, high-entropy strings, and Private RSA keys.
2.  **Firmwalker:** A simple bash script specifically designed for IoT firmware. It automatically searches the extracted filesystem for:
    *   Passwords, shadow files, configuration files.
    *   SSL/TLS certificates and keys.
    *   Common web server directories and CGI scripts.
    *   Email addresses, URLs, and IP addresses (helpful for finding cloud C2 endpoints).
3.  **Grep:** The most reliable tool.
    *   `grep -rnEi 'password|passwd|pwd|key|secret|token|api_key' ./squashfs-root/`
    *   `find . -name "*.key" -o -name "*.pem"`

---

## Case Study: The Mirai Botnet

The most infamous example of the catastrophic impact of hardcoded credentials is the Mirai botnet (2016).
*   **The Flaw:** Dozens of manufacturers of cheap IP cameras and DVRs shipped devices running embedded Linux with Telnet and SSH exposed to the public internet by default. Crucially, they all utilized a small set of hardcoded, unchangeable default credentials (e.g., `root:xc3511`, `admin:admin`, `root:vizxv`).
*   **The Exploit:** The Mirai malware simply scanned the internet for port 23/22 and attempted a dictionary attack using a list of 60+ known hardcoded IoT credentials.
*   **The Impact:** Mirai infected millions of devices, turning them into a massive Distributed Denial of Service (DDoS) army that successfully took down major DNS providers (Dyn), rendering vast swaths of the internet (Twitter, Netflix, Reddit) inaccessible.

---

## Chaining Opportunities

*   **Firmware Extraction -> Credential Harvesting -> RCE:** Dump firmware via UART `->` Extract RootFS `->` Crack the weak MD5 hash found in `/etc/shadow` using Hashcat `->` Use the recovered plaintext password to SSH into the physical device as root `->` Install persistent backdoor.
*   **Key Extraction -> Cloud Pivot:** Use Binwalk to unpack firmware `->` Find hardcoded AWS IoT certificates and MQTT endpoints in `/var/config` `->` Connect to the cloud backend using a Python MQTT client and the stolen certs `->` Subscribe to `#` to intercept telemetry from all global users, executing a massive data breach.

## Related Notes
*   [[02 - IoT Device Firmware Extraction]]
*   [[03 - Firmware Analysis and Reverse Engineering]]
*   [[05 - Telnet SSH Exposed on IoT Devices]]
