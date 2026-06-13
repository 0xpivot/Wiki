---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.21 John the Ripper"
---

# 21 - John the Ripper

## 1. Introduction and Core Philosophy

John the Ripper (often abbreviated as JtR) is a fast, versatile, and open-source password security auditing and password recovery tool.
It was initially developed for UNIX systems but now supports multiple platforms including Windows, DOS, BeOS, and OpenVMS.
Its primary purpose is to detect weak UNIX passwords, although the community-enhanced "Jumbo" edition now supports hundreds of hash and cipher types.
This makes it one of the most widely used and respected password cracking utilities in the cybersecurity industry.

John the Ripper operates by taking an input file containing hashed passwords and attempting to guess the original plaintext passwords using various configurable modes.
The tool is particularly famous for its immense customizability, allowing advanced users to write custom rules, use complex character mutation engines, and even write external cracking modules in C.

Unlike online brute-force tools, John operates strictly offline.
This allows it to bypass account lockout policies, rate limiting, and network latency, constrained only by the computational power of the host machine.

## 2. Architecture and Internal Mechanics

The internal architecture of John the Ripper is highly optimized for performance.
It relies on a modular approach where the hash format detection, candidate generation, and cryptographic comparison are strictly separated but tightly integrated for maximum execution speed.

```text
+-----------------------------------------------------------------------+
|                          John The Ripper Core                         |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ Input Hashes ] -----> [ Hash Format Detector / Loader ]           |
|                                     |                                 |
|                                     v                                 |
|   [ Wordlist / Rules ] -> [ Candidate Generator Engine ]              |
|   [ Incremental Data ]              |                                 |
|   [ External C Code  ]              v                                 |
|                                                                       |
|                       [ Cryptographic Engine ]                        |
|                                     ^                                 |
|                                     |                                 |
|                                     v                                 |
|                           [ Hash Comparator ]                         |
|                                     |                                 |
|                                     v                                 |
|                       [ Cracked Passwords (john.pot) ]                |
|                                                                       |
+-----------------------------------------------------------------------+
```

The core loop involves generating a candidate password, hashing it using the specific cryptographic engine required by the target hash, and comparing the result.
If a match is found, the result is saved to a file called `john.pot`, which prevents the tool from wasting time cracking the same hash twice in future sessions.

## 3. Detailed Modes of Operation

### 3.1 Single Crack Mode

This is the most fundamental and often the first mode John uses during an engagement.
It relies on the user's login name, GECOS information (like full name, room number, phone number), and other contextual data from the password file to guess passwords.

For example, if the username is `admin`, it will try variations such as:
- `admin`
- `Admin`
- `admin123`
- `nimda`
- `adminadmin`

```bash
# Running single crack mode explicitly
john --single hashes.txt
```

### 3.2 Wordlist Mode (Dictionary Attack)

In this mode, John the Ripper reads words sequentially from a specified dictionary file and tests them against the loaded hashes.
Wordlists can be augmented with rules to mutate the words (e.g., appending numbers, changing case).

```bash
# Standard wordlist attack
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Wordlist attack with rules applied
john --wordlist=rockyou.txt --rules hashes.txt
```

### 3.3 Incremental Mode (Brute Force)

Incremental mode is the most powerful but time-consuming mode.
It tries all possible character combinations up to a certain length.
It is highly optimized using character frequency tables (`.chr` files) to guess the most likely characters first, rather than proceeding in strict alphabetical order.

```bash
# Running incremental mode (all characters)
john --incremental hashes.txt

# Using a specific character set (e.g., digits only)
john --incremental=Digits hashes.txt
```

### 3.4 External Mode

External mode allows users to define custom functions in a subset of C within the `john.conf` file.
These functions generate candidates dynamically or filter them before they are tested.
This is useful for highly specific password policies (e.g., "must contain a company name, a prime number, and a symbol").

## 4. Hash Identification and Formatting

John the Ripper automatically detects many hash formats.
However, sometimes it requires explicit specification, especially when multiple hash types share the same signature length (e.g., MD5 and NTLM).

```bash
# Listing all supported formats
john --list=formats

# Specifying a format manually
john --format=nt hashes.txt
john --format=raw-md5 hashes.txt
john --format=bcrypt hashes.txt
```

Understanding hash formats is crucial.
If John assumes a hash is MD5 when it is actually NTLM, it will never find the correct plaintext, wasting valuable time.

## 5. Advanced Configuration and Rules

Rules are arguably one of the most powerful features of John the Ripper.
They allow dynamic, on-the-fly mutation of dictionary words.
A rule can instruct John to:
- Capitalize the first letter
- Append a digit or a special character
- Reverse the word
- Duplicate the word
- Replace specific letters (e.g., 'a' with '@')

Example rule definition in the `john.conf` file:
```text
[List.Rules:MyCustomRule]
# Do nothing (try the base word)
:
# Lowercase the word
l
# Capitalize the word
c
# Append 123
$1$2$3
# Replace 'e' with '3'
se3
```

Applying the custom rule during a cracking session:
```bash
john --wordlist=words.txt --rules=MyCustomRule hashes.txt
```

## 6. Performance Optimization and Hardware Acceleration

To maximize the performance of John the Ripper, attackers and auditors must consider hardware acceleration.
The Jumbo version of JtR supports OpenCL, allowing it to leverage GPUs for significantly faster cracking.

```bash
# Listing available OpenCL devices
john --list=opencl-devices

# Using a specific OpenCL device for cracking
john --format=raw-md5-opencl --device=1 hashes.txt
```

Forking and OpenMP are also supported for CPU-based multithreading, maximizing resource utilization on multi-core systems:
```bash
# Using multiple processes (forking)
john --fork=4 hashes.txt
```

## 7. Session Management and Resumption

Cracking sessions can take days, weeks, or even months depending on the complexity of the hash and the speed of the hardware.
John automatically saves its state, allowing users to pause and resume without losing progress.

```bash
# Viewing session status (press spacebar while running, or use this command)
john --status

# Restoring a paused or interrupted session
john --restore
```

## 8. Practical Assessment Scenarios

### 8.1 Active Directory Audits
During internal penetration tests, auditors often dump the NTDS.dit file.
Extracting NTLM hashes and running them through JtR helps identify weak domain passwords.

### 8.2 Linux Shadow Files
Combining `/etc/passwd` and `/etc/shadow` using the `unshadow` utility.
Then, cracking the resulting file to escalate privileges from a low-level user to root.
```bash
unshadow /etc/passwd /etc/shadow > mypasswd.txt
john mypasswd.txt
```

### 8.3 File Format Cracking
Using tools like `zip2john`, `rar2john`, or `pdf2john` to extract the hash from a protected file, then cracking it.
```bash
# Extracting hash from a ZIP file
zip2john protected.zip > zip.hash

# Cracking the ZIP hash
john --format=pkzip zip.hash
```

## 9. Chaining Opportunities

- **[[11 - Hashcat]]**: Hashes that John struggles with or that require complex mask attacks on GPUs can be passed to Hashcat. Both tools use the same underlying concepts but differ in execution optimization.
- **[[31 - Hydra]]**: Once a password is cracked locally via John, the credentials can be used in Hydra for active online brute-forcing across SSH, FTP, or HTTP portals.
- **[[24 - theHarvester]]**: Usernames gathered from theHarvester can be fed into John's single mode to generate highly targeted dictionaries.
- **[[04 - Responder]]**: NTLMv1/v2 hashes captured over the local network using Responder can be cracked offline using John the Ripper to obtain domain credentials.

## 10. Related Notes

- [[02 - Password Cracking Methodologies]]
- [[12 - NTLM and Active Directory Authentication]]
- [[09 - Dictionary Generation and Rules]]
- [[15 - Local Privilege Escalation via Weak Credentials]]
- [[22 - Amass]]
- [[26 - Arjun]]
