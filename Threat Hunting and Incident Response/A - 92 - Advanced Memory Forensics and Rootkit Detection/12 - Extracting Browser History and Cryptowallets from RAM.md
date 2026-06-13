---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.12 Extracting Browser History and Cryptowallets from RAM"
---

# 12 - Extracting Browser History and Cryptowallets from RAM

## 1. Introduction

Physical memory represents the ultimate ground truth of a running system. While disk forensics relies on files that may be encrypted, deleted, or obfuscated, RAM contains data in its decrypted, executing state. This makes it an incredibly lucrative target for both threat actors (via Infostealers) and forensic investigators. Two of the highest-value targets within user-space memory are web browsers (containing session tokens, history, and passwords) and cryptocurrency wallets (containing unencrypted private keys and seed phrases).

When an application processes sensitive data, it must eventually exist in plaintext within the process's Virtual Address Descriptor (VAD) nodes (in Windows) or `vm_area_struct` mappings (in Linux). Unless the application explicitly wipes the memory (via `SecureZeroMemory` or `memset`), data often persists long after it has been "deleted" or the window has been closed, lingering in heap allocations, stack frames, or cached memory pages.

## 2. Browser Forensics in Memory

Modern browsers (Chrome, Firefox, Edge) are intensely complex, multi-process architectures. For example, Chromium utilizes separate processes for the browser UI, GPU rendering, and individual tabs/extensions. This sandboxing improves security but scatters artifacts across multiple memory spaces.

### 2.1 SQLite Database Carving

Browsers store nearly all their persistent data (History, Cookies, Autofill, Logins) in SQLite databases. When a browser accesses these databases, the SQLite engine pages them into memory.

Forensic tools can scan physical memory for SQLite file signatures and internal structures. The SQLite database header always begins with the magic string `SQLite format 3\000`. 
By searching for this 16-byte magic header, analysts can carve out entire, uncorrupted SQLite databases directly from RAM.

```python
# YARA rule for SQLite database header carving
rule SQLite_Database_Carve {
    meta:
        description = "Identifies SQLite databases in memory"
    strings:
        $magic = { 53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00 }
    condition:
        $magic at 0
}
```

Once carved, the investigator can parse the database to retrieve active session cookies, which may have been decrypted in memory to be sent over the wire, bypassing DPAPI (Data Protection API) protections that secure the cookies on disk.

### 2.2 JSON and Session Token Extraction

Modern web apps rely heavily on JWT (JSON Web Tokens) and OAuth tokens stored in `localStorage` or `sessionStorage`. These are held in the browser's heap memory. Using Volatility or basic strings analysis combined with regular expressions, investigators can extract active, valid session tokens.

```bash
# Extracting a specific Chrome tab's memory and hunting for JWTs
vol -f memdump.raw windows.memmap --pid 4452 --dump-dir ./dump/
strings ./dump/4452.dmp | grep -E "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"
```

## 3. Cryptowallet Forensics

Cryptocurrency wallets present a unique challenge. Unlike browsers, wallets are specifically designed to protect their most sensitive data: the master private key (often represented as a BIP39 seed phrase, e.g., 12 or 24 words).

### 3.1 Memory Handling of Keys

When a user unlocks their wallet (e.g., Electrum, MetaMask, Bitcoin Core) to sign a transaction, the encryption password must be provided, and the private key is decrypted into RAM.

Well-designed wallets utilize specific OS primitives to protect these keys:
- **`mlock()` / `VirtualLock()`:** Pins the memory page to physical RAM, preventing the OS from swapping the unencrypted key out to the paging file (`pagefile.sys` or swap partition) where it could be recovered via disk forensics.
- **Secure Allocators:** Using specialized memory allocators that zero out the memory immediately after the signing operation is complete (e.g., libsodium's `sodium_malloc`).

However, human error in software development, garbage collection languages (like JavaScript in MetaMask), and residual memory buffers often lead to keys persisting in memory longer than intended.

### 3.2 Extracting MetaMask and Browser-based Wallets

MetaMask operates within the browser extension process space. Because it is written in JavaScript, it is subject to V8 engine garbage collection. Cryptographic operations often leave traces of strings in the V8 heap. 

A forensic investigator (or an infostealer) can dump the extension process memory and search for the BIP39 wordlist or regex patterns matching private keys.

```regex
# Regular expression to match a 64-character Hexadecimal Ethereum Private Key
\b[0-9a-fA-F]{64}\b
```

By correlating high-entropy strings or sequences of words found in the standardized BIP39 dictionary, an analyst can reconstruct the master seed.

## 4. Architectural Diagram: Memory Carving Flow

```text
+-------------------------------------------------------------+
|                     PHYSICAL RAM DUMP                       |
|                                                             |
|  +-------------------+               +-------------------+  |
|  | Process: chrome.exe               | Process: electrum |  |
|  | PID: 9021         |               | PID: 4055         |  |
|  |                   |               |                   |  |
|  | [Heap Segment]    |               | [Secure Heap]     |  |
|  | "session_id=..."  | <--- Regex -- | "apple banana..." |  |
|  |                   |               | (BIP39 Seed)      |  |
|  | [SQLite Page]     |               |                   |  |
|  | "SQLite format 3" | <--- Magic -- | [Stack Segment]   |  |
|  |                   |      Header   | 0x1A2B3C...       |  |
|  +-------------------+               +-------------------+  |
+-------------------------------------------------------------+
           |                                  |
           v                                  v
+------------------------+         +--------------------------+
|  Volatility yarascan   |         |   Entropy Analysis &     |
|  String Extraction     |         |   BIP39 Dictionary Match |
+------------------------+         +--------------------------+
           |                                  |
           v                                  v
+------------------------+         +--------------------------+
|  Session Hijacking     |         |  Wallet Compromise /     |
|  Account Takeover      |         |  Fund Recovery           |
+------------------------+         +--------------------------+
```

## 5. Entropy Analysis and Key Discovery

When standard string searches fail (for example, when looking for raw binary keys rather than hex-encoded strings), investigators use **entropy analysis**. 

Cryptographic keys have extremely high Shannon entropy (close to 8.0). By scanning the memory dump in sliding windows and calculating the entropy, investigators can pinpoint regions of memory containing compressed or encrypted data, or raw cryptographic keys. Once high-entropy blocks are identified, structural analysis (looking for ASN.1 DER encoding headers or elliptic curve parameters) can verify if the block is a key.

## 6. Real-World Attack Scenario

### 6.1 The Breach
A high-net-worth individual is targeted by a sophisticated spear-phishing campaign. They execute a seemingly benign PDF that triggers a zero-day exploit, dropping the "RedLine" infostealer variant onto their system.

### 6.2 The Extraction
Instead of merely exfiltrating files, RedLine is highly memory-aware. It iterates through running processes, specifically hunting for `chrome.exe`, `firefox.exe`, and common wallet executables (`electrum.exe`, `exodus.exe`). 

Using Windows API calls like `OpenProcess` and `ReadProcessMemory`, the malware dumps the heap of the browser extension processes. It streams this memory directly into a YARA-like scanning engine running purely in memory, searching for the BIP39 wordlist.

### 6.3 The Forensic Investigation
The victim notices unauthorized transfers of their cryptocurrency. An incident response firm captures the physical memory of the machine.

```bash
# Scanning the memory dump for the presence of the infostealer's YARA engine
vol -f DESKTOP-MEM.raw windows.malfind

# Extracting the injected payload that was reading process memory
vol -f DESKTOP-MEM.raw windows.vadinfo --pid 3320
```

The investigators discover the injected payload in a hollowed process. By analyzing the memory of the malware itself, they find the command-and-control server IP address and the specific regex patterns it was using to scrape the victim's MetaMask seed phrase from the Chrome process space, providing proof of exactly how the funds were stolen despite the keys never being stored unencrypted on disk.

## 7. Extended Technical Details: DPAPI and Cryptography

### 7.1 Understanding Windows DPAPI in RAM
Most modern browsers on Windows protect their SQLite files using the Data Protection API (DPAPI). For instance, the Chrome `Cookies` file contains an `encrypted_value` column. DPAPI relies on the user's Master Key, which is derived from the Windows login password. 

In memory, this Master Key is stored in the `lsass.exe` (Local Security Authority Subsystem Service) process. Advanced forensic analysts can use Volatility plugins like `windows.lsadump` or `mimikatz` integrated with memory images to extract the plaintext Master Key.

```bash
# Extracting DPAPI Master Keys from memory
vol -f WIN10-MEM.raw windows.lsadump
```
Once the Master Key is recovered from `lsass.exe`, the analyst can use off-the-shelf tools to manually decrypt the Chrome SQLite database carved from memory or recovered from the disk image, bridging the gap between volatile memory extraction and persistent disk forensics.

### 7.2 Countermeasures for Developers
Developers writing secure applications must ensure that sensitive data like seed phrases are purged. 
In C/C++, use `SecureZeroMemory`. In .NET, use the `SecureString` class, which automatically pins and encrypts data in memory, preventing it from being trivially dumped or swept up by the garbage collector.

## 8. Extended Analysis: Memory Carving Scripts

When hunting for BIP39 seed phrases, automated carving via Python scripts operating on raw memory dumps can be highly effective. The following script snippet demonstrates how an analyst might iterate over a memory dump to find potential seed phrases using a loaded BIP39 wordlist:

```python
import mmap
import re

# Load the BIP39 English wordlist
with open('bip39_english.txt', 'r') as f:
    bip39_words = set(f.read().splitlines())

def scan_memory_for_seed(memory_dump_path):
    with open(memory_dump_path, 'rb') as f:
        # Memory-map the raw dump for efficient searching
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        
        # Regex to find consecutive sequences of 12 or 24 lowercase words
        # (Simplified example for demonstration)
        pattern = re.compile(b'([a-z]+ ){11,23}[a-z]+')
        
        for match in pattern.finditer(mm):
            decoded_string = match.group().decode('utf-8')
            words = decoded_string.split()
            
            # Verify if all words are in the BIP39 dictionary
            if all(word in bip39_words for word in words):
                print(f"[*] Potential Seed Phrase Found at offset {hex(match.start())}:")
                print(f"    {decoded_string}")

# Usage: scan_memory_for_seed("memdump.raw")
```
This brute-force approach bypasses all OS structures and is highly resilient against DKOM or memory unlinking, directly reading the raw physical pages.

## 9. Deep Dive: The V8 Javascript Engine Memory Layout

MetaMask and Chrome extension-based wallets run inside the Google V8 JavaScript engine. To effectively extract keys from these processes, one must understand the V8 heap layout.
V8 manages memory in Spaces:
1. **New Space:** Where newly allocated objects live (very volatile, high garbage collection rate).
2. **Old Space:** Where long-lived objects are moved. Seed phrases often end up here if the user leaves the tab open for an extended period.
3. **Large Object Space:** Objects larger than the size limit of other spaces.

Because JavaScript uses utf-16 string encoding internally (`TwoByteString` class in V8), memory analysts must ensure their string searches and YARA rules account for wide-character strings (e.g., searching for `a\x00p\x00p\x00l\x00e\x00` instead of just `apple`). Failing to account for V8 string representations is a common cause of false negatives during cryptocurrency wallet forensics.

## 10. Chaining Opportunities
- Extracting browser history and tokens can directly feed into [[15 - YARA Scanning over Memory Images]] to automate the discovery of IOCs.
- If the target system employs anti-dumping techniques to protect its memory (e.g., banking trojans or advanced EDRs protecting their own memory), refer to [[13 - Defeating Anti-Forensic and Anti-Dumping Techniques]].
- Recovered tokens can be used for session hijacking and API abuse, linking to API security modules.

## 11. Related Notes
- [[11 - Memory Forensics on Linux Volatility Linux Profiles]]
- [[YARA Rule Development]]
- [[Windows DPAPI Forensics]]
- [[Cryptographic Entropy Analysis]]
- [[Browser Extension Security and Forensics]]

## 12. Conclusion
As infostealers continue to focus heavily on volatile memory to grab session tokens and wallet seeds, understanding how to extract and parse these artifacts from a physical memory dump is crucial. Relying solely on disk analysis will miss the ephemeral but vital data processed by modern web browsers and cryptocurrency wallets.
