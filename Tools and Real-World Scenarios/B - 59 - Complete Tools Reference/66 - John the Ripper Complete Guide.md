---
tags: [tools, enumeration, exploitation, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.66 John the Ripper Complete Guide"
---

# John the Ripper Complete Guide

## 1. Introduction to John the Ripper (JtR)

John the Ripper (often abbreviated as John or JtR) is one of the most renowned and versatile password recovery tools available to penetration testers, security auditors, and system administrators. Originally developed for UNIX systems to detect weak passwords, it has evolved over the years into a comprehensive multi-platform cracking suite.

The primary objective of John the Ripper is to perform offline password cracking. This means that instead of interacting with a live authentication service (like SSH or FTP) which could lock out an account or trigger an alert, John works against local cryptographic hash files. The attacker or auditor captures these hashes—such as `/etc/shadow` entries, NTLM hashes from a Windows SAM database, or extracted hashes from a captured Kerberos ticket—and feeds them to John.

Unlike online brute-force tools (e.g., Hydra or Medusa), offline cracking tools like John are limited only by the computational power of the attacking machine and the complexity of the hash algorithm, rather than network latency or application rate-limiting.

### 1.1 CPU vs. GPU Cracking
While the standard John the Ripper is highly optimized for CPU-based cracking using specialized instruction sets (like AVX2, AVX-512), modern versions, especially the "Jumbo" patch edition, offer robust support for GPU acceleration via OpenCL (`--format=opencl`). 

Understanding when to use CPU vs GPU is critical for efficiency:
*   **CPU Cracking**: CPUs excel at complex, heavily salted hashes (e.g., bcrypt, scrypt) because these algorithms are designed to be memory-hard and branch-heavy, making them inefficient on GPUs.
*   **GPU Cracking**: GPUs completely dominate fast, unsalted or simple salted hashes like MD5, SHA1, and NTLM, often achieving billions of hashes per second.

## 2. Architecture and Attack Flow Diagram

Below is an ASCII diagram detailing the typical workflow and architecture involved when using John the Ripper.

```text
+---------------------------------------------------------+
|                Target System Environment                |
|                                                         |
|  +--------------+   +---------------+   +------------+  |
|  | /etc/shadow  |   | Windows SAM   |   | PCAP File  |  |
|  | (Linux Hashes|   | (NTLM Hashes) |   | (WPA/WPA2) |  |
|  +-------+------+   +-------+-------+   +-----+------+  |
+----------|------------------|-----------------|---------+
           |                  |                 |
           v                  v                 v
+---------------------------------------------------------+
|                   Hash Extraction Phase                 |
|                                                         |
|  unshadow         samdump2 / secretsdump   hcxpcapngtool|
|  (Merges passwd/  (Extracts NTLM from      (Extracts PMK|
|   shadow into 1)   registry hives)          from PCAP)  |
+--------------------------+------------------------------+
                           |
                           v
+---------------------------------------------------------+
|                  John the Ripper Suite                  |
|                                                         |
|  +---------------------------------------------------+  |
|  | Input File Preparation (JtR Formats)              |  |
|  +---------------------------------------------------+  |
|                           |                             |
|  +-------------------+    |    +-------------------+    |
|  | Wordlist Mode     |    |    | Incremental Mode  |    |
|  | (Dictionary +     |<---+--->| (Brute-force /    |    |
|  |  Mangling Rules)  |         |  Markov Chains)   |    |
|  +-------------------+         +-------------------+    |
|                           |                             |
|  +-------------------+    |                             |
|  | Single Crack Mode |<---+                             |
|  | (Uses GECOS/Users)|                                  |
|  +-------------------+                                  |
|                           |                             |
|  +---------------------------------------------------+  |
|  | Execution Engine (CPU / OpenCL GPU)               |  |
|  +---------------------------------------------------+  |
|                           |                             |
|  +---------------------------------------------------+  |
|  | Output Storage (john.pot)                         |  |
|  +---------------------------------------------------+  |
+---------------------------------------------------------+
```

## 3. Core Cracking Modes

John operates primarily in distinct modes, each designed to tackle passwords from a different angle.

### 3.1 Single Crack Mode
The Single Crack mode (`--single`) is typically the first mode you should run. It is lightning fast because it uses the username, GECOS field (full name, room number, etc.), and home directory name as the basis for guessing the password. It applies a large set of permutation rules specifically designed to alter these personal details.
- **Why it works**: Users frequently base their passwords on their own names or usernames (e.g., `admin123`, `JohnDoe2023!`).
- **Syntax**: `john --single hashes.txt`

### 3.2 Wordlist (Dictionary) Mode
This is the most common mode used in password cracking. You provide John with a dictionary file (like the famous `rockyou.txt`), and it tries every word in the list against the target hash.
- **Syntax**: `john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt`

#### 3.2.1 Wordlist Rules
The true power of wordlist mode comes from "Rules." Instead of just trying the raw words in the dictionary, John can apply mutation rules (mangling). For example, changing "password" to "Password123!".
- **Syntax**: `john --wordlist=rockyou.txt --rules=Jumbo hashes.txt`
- **Custom Rules**: You can define custom rules in `john.conf`. A rule like `c A0"123"` capitalizes the first letter and appends "123". This drastically increases the coverage of a small dictionary without needing a multi-gigabyte text file.

### 3.3 Incremental Mode
Incremental mode (`--incremental`) is John's implementation of a pure brute-force attack. However, it's not a dumb brute-force. It uses Markov chains based on character frequencies observed in real passwords. It will try the most statistically probable character combinations first.
- **Syntax**: `john --incremental hashes.txt`
- **Use Case**: Use this as a last resort when wordlists and rules have failed, or when you know the password is short (e.g., 6 characters) but completely random.

### 3.4 Mask Mode
Mask mode is used when you know certain parts of the password or its specific structure. For example, if you know a company password policy requires exactly 8 characters starting with a capital letter followed by 5 lowercase letters and 2 digits.
- **Syntax**: `john --mask=?u?l?l?l?l?l?d?d hashes.txt`
- **Placeholders**:
  - `?l`: Lowercase letter
  - `?u`: Uppercase letter
  - `?d`: Digit
  - `?s`: Symbol

## 4. Advanced Usage and Configuration

### 4.1 Format Specification
While John is generally very good at automatically detecting the hash format, there are times when hashes are ambiguous (e.g., an MD5 hash could be raw MD5, MD5(Unix), or an NTLM hash). Explicitly defining the format saves time and prevents false negatives.
- **List available formats**: `john --list=formats`
- **Specify format**: `john --format=NT hashes.txt` (for Windows NTLM hashes)
- **Specify OpenCL format**: `john --format=nt-opencl hashes.txt` (to use the GPU for NTLM)

### 4.2 Session Management
Cracking sessions can take days or weeks. John automatically saves its state in a `.rec` (recovery) file. If the process is interrupted, you can resume exactly where you left off.
- **Start a named session**: `john --session=ntlm_crack --wordlist=rockyou.txt hashes.txt`
- **Resume a session**: `john --restore=ntlm_crack`

### 4.3 The Pot File (`john.pot`)
When John successfully cracks a hash, it stores the plaintext password alongside the hash in a file called `john.pot` (usually located in `~/.john/john.pot`). This prevents John from wasting time re-cracking hashes it has already solved in future runs.
- **Viewing cracked passwords**: `john --show hashes.txt` (This reads the input hash file and cross-references it with `john.pot` to display cracked accounts).

### 4.4 Tuning and Performance
Performance tuning is essential when dealing with millions of hashes.
- **Forking**: You can instruct John to utilize multiple CPU cores using the `--fork` argument.
  - **Syntax**: `john --fork=8 hashes.txt` (Uses 8 CPU cores).
- **Node/MPI**: For distributed cracking across multiple distinct physical machines, John supports MPI (Message Passing Interface).
  - **Syntax**: `mpirun -np 4 john --wordlist=rockyou.txt hashes.txt`

## 5. Pre-Processing: Extracting Hashes

John cannot directly read `/etc/shadow` and `/etc/passwd` out of the box because the username and the hash are in separate files. You must combine them using John's auxiliary tools.

### 5.1 Unshadow
The `unshadow` command combines the standard `/etc/passwd` file with the restricted `/etc/shadow` file into a single file formatted perfectly for John.
- **Usage**: `unshadow /tmp/passwd /tmp/shadow > combined_hashes.txt`

### 5.2 Zip2John, Rar2John, Pdf2John
The "Jumbo" version of John includes numerous perl/python/C scripts designed to extract crackable hashes from encrypted files.
- **Encrypted ZIP**: `zip2john secret.zip > zip_hash.txt`
- **Encrypted RAR**: `rar2john secret.rar > rar_hash.txt`
- **SSH Private Keys**: `ssh2john id_rsa > ssh_hash.txt`
- **Kerberos TGS**: `kirbi2john ticket.kirbi > kerb_hash.txt`

## 6. Troubleshooting Common Issues

### 6.1 "No password hashes loaded"
This error typically means John could not auto-detect the hash format, or the file is malformed.
*   **Fix**: Manually specify the format using `--format=`. Ensure the file is strictly formatted as `user:hash`. Check for trailing spaces or hidden characters (e.g., CRLF issues if copied from Windows).

### 6.2 "OpenCL device not found"
If you are trying to use GPU acceleration (`-format=opencl`) and it fails, it implies your graphics drivers or OpenCL runtimes are missing.
*   **Fix**: Install `ocl-icd-libopencl1`, `nvidia-opencl-icd` (for NVIDIA), or the appropriate AMD ROCm packages.

### 6.3 Extremely Slow Cracking
If an unsalted MD5 hash is cracking very slowly, you might be using the CPU instead of the GPU, or you are running in a constrained virtual machine.
*   **Fix**: Use `--format=raw-md5-opencl`, and ensure you aren't running JtR inside a VM that lacks GPU passthrough.

## 7. Real-World Scenario: Cracking a Linux Local Privilege Escalation

Imagine you have obtained low-privileged shell access to a Linux machine. You discover a backup of the `/etc/shadow` file in `/var/backups/`.

1.  **Retrieve Files**: Download `/etc/passwd` and the backup `/var/backups/shadow.bak` to your local attacking machine.
2.  **Combine Files**:
    ```bash
    unshadow passwd shadow.bak > linux_hashes.txt
    ```
3.  **Identify Format**: You inspect `linux_hashes.txt` and see hashes starting with `$6$`. This indicates SHA-512 crypt.
4.  **Run Single Mode**:
    ```bash
    john --single linux_hashes.txt
    ```
5.  **Run Wordlist Mode with Rules**:
    ```bash
    john --wordlist=/usr/share/wordlists/rockyou.txt --rules --format=sha512crypt linux_hashes.txt
    ```
6.  **Review Results**:
    ```bash
    john --show linux_hashes.txt
    ```
    Output:
    ```
    root:SuperSecretAdmin2023:0:0:root:/root:/bin/bash
    1 password hash cracked, 4 left
    ```
7.  **Pivot**: Now you have the root password and can `su - root` on the target machine.

## 8. Chaining Opportunities
- **[[54 - Hashcat Deep Dive]]**: Once you reach the limits of John's CPU cracking for fast hashes (like NTLM), pivot to Hashcat for highly optimized GPU cracking using large rule sets and mask attacks.
- **[[12 - Privilege Escalation via Weak Permissions]]**: Finding readable shadow backups is a classic local privilege escalation vector that directly feeds into John the Ripper.
- **[[23 - Kerberoasting Attacks]]**: Tools like Impacket's `GetUserSPNs.py` extract Kerberos TGS tickets. These tickets can be formatted for John (using `kirbi2john` or directly) to crack the service account's plaintext password.

## 9. Related Notes
- [[10 - Password Cracking Methodology]]
- [[45 - Dictionary Generation and Mutation]]
- [[09 - NTLM and SMB Authentication Mechanics]]

























