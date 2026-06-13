---
tags: [darkweb, scraping, automation, vapt]
difficulty: advanced
module: "87 - Automated Dark Web Monitoring and Scraping"
topic: "87.12 Automated PGP Key Discovery and Tracking"
---

# Automated PGP Key Discovery and Tracking

## 1. Introduction to PGP in the Dark Web

Pretty Good Privacy (PGP) is the backbone of trust, identity, and secure communication on the dark web. Due to the inherent lack of trust in anonymous environments, threat actors, vendors, and market administrators rely heavily on public-key cryptography. PGP is used to:
1. **Encrypt Communications:** Ensuring private messages (e.g., shipping addresses, exploit details) cannot be read by forum admins or law enforcement if the server is seized.
2. **Authenticate Identity:** Proving that an actor on a newly launched market is the same highly-rated vendor from a defunct market.
3. **Sign Contraband/Software:** Guaranteeing that purchased malware or data dumps have not been tampered with.

Because PGP keys are designed to be public and shared, they represent a highly reliable and persistent artifact for Cyber Threat Intelligence (CTI) tracking. Automating the discovery, extraction, and analysis of these keys is critical for tracking threat actors across different forums and platforms.

## 2. Technical Deep Dive: The PGP Tracking Pipeline

An automated pipeline for PGP tracking consists of several distinct stages: scraping, extraction, parsing, cryptanalysis, and correlation.

### 2.1 Extraction from Raw Text
PGP public keys are typically shared as ASCII-armored text blocks. They are easily identifiable via standard headers. A robust dark web scraper must continuously run regex operations against all collected text to identify these blocks.

**Standard Regex for PGP Public Key:**
```regex
-----BEGIN PGP PUBLIC KEY BLOCK-----[a-zA-Z0-9+/=\s]+-----END PGP PUBLIC KEY BLOCK-----
```
However, threat actors often make formatting errors, add spaces, or truncate lines. The extraction logic must be fault-tolerant, capable of stripping out BBCode (e.g., `[code]...[/code]`) or HTML tags that might interrupt the key block.

### 2.2 Parsing and Metadata Extraction
Once an ASCII-armored block is extracted, it must be parsed to extract cryptographic metadata. Python libraries like `python-gnupg` or `pgpy` are typically used.

Key metadata to extract includes:
- **Fingerprint:** The unique 40-character hexadecimal string representing the key. This is the primary index for tracking.
- **Key ID:** The short (8 chars) or long (16 chars) subset of the fingerprint.
- **User IDs (UIDs):** Typically containing a Name, Comment, and Email address (e.g., `DarkVendor (Main Key) <darkvendor@protonmail.com>`).
- **Creation Date:** When the key was generated.
- **Expiration Date:** If set, when the key expires.
- **Algorithm & Key Size:** e.g., RSA 4096-bit, Ed25519.

## 3. Architecture Diagram

```ascii
+-----------------------+      +---------------------------+
|                       |      |                           |
|  Darknet Scrapers     |      |  Clearweb Key Servers     |
| (Forums, Markets,     |      | (Ubuntu, MIT, OpenPGP)    |
|  Paste Sites)         |      |                           |
+-----------+-----------+      +-------------+-------------+
            |                                |
            v                                v
+----------------------------------------------------------+
|                 PGP Ingestion Engine                     |
|                                                          |
|  1. Regex Extraction (`-----BEGIN PGP...`)               |
|  2. Cleansing (Stripping HTML/BBCode)                    |
|  3. Parsing (Extracting Fingerprint, UIDs, Dates)        |
+---------------------------+------------------------------+
                            |
                            v
+----------------------------------------------------------+
|                 Cryptanalysis & Storage                  |
|                                                          |
|  - Weak Key Detection (e.g., Debian Weak Keys)           |
|  - Cross-referencing Fingerprints                        |
|  - Graph Database Insertion (Actor -> Uses -> Key)       |
+----------------------------------------------------------+
```

## 4. Advanced Tracking and Analysis Techniques

### 4.1 Cross-Platform Correlation
The primary value of PGP tracking is cross-platform correlation. If a vendor named `PharmaKing` operates on Market A, and a vendor named `PillPrince` operates on Market B, but both utilize a PGP key with the exact same fingerprint, the CTI system can automatically merge these profiles, determining they are the same individual.

### 4.2 Clear-Web Key Server Polling
Many threat actors inadvertently upload their darknet PGP keys to public clear-web keyservers (like `keyserver.ubuntu.com`), or they generated the key years ago for legitimate purposes and are reusing it. 
An automated system should take every newly discovered darknet PGP fingerprint and query public keyservers via the HashKilled or SKS APIs. This can frequently expose real-world email addresses associated with the key's creation.

### 4.3 Cryptographic Weaknesses and OpSec Failures
Automated analysis can identify OpSec failures:
- **Small Key Sizes:** Keys generated with RSA 1024-bit are considered insecure and might be crackable.
- **Debian Weak Keys:** Checking if the key was generated using the compromised OpenSSL PRNG (CVE-2008-0166). If so, the private key can be mathematically derived.
- **Metadata Leakage:** Some PGP implementations leak the version of the software and the operating system (e.g., `Version: GnuPG v2.2.19 (MingW32)`), providing fingerprinting data about the actor's local machine.

## 5. Step-by-Step Implementation Guide

### Step 1: Automated Extraction Script
Here is a Python example using `pgpy` to parse an extracted PGP block.

```python
import pgpy
import re

def parse_pgp_block(ascii_block):
    try:
        # Load the key from the ASCII block
        key, _ = pgpy.PGPKey.from_blob(ascii_block)
        
        fingerprint = key.fingerprint.replace(" ", "")
        creation_date = key.created
        
        uids = []
        for uid in key.userids:
            uids.append({
                "name": uid.name,
                "email": uid.email,
                "comment": uid.comment
            })
            
        algorithm = key.key_algorithm.name
        
        return {
            "valid": True,
            "fingerprint": fingerprint,
            "creation_date": str(creation_date),
            "uids": uids,
            "algorithm": algorithm
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Simulated extracted block
raw_text = """
Some forum post content...
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBGF... [Truncated for brevity]
-----END PGP PUBLIC KEY BLOCK-----
"""

# Regex to find block
match = re.search(r'-----BEGIN PGP PUBLIC KEY BLOCK-----.*?-----END PGP PUBLIC KEY BLOCK-----', raw_text, re.DOTALL)
if match:
    parsed_data = parse_pgp_block(match.group(0))
    print(parsed_data)
```

### Step 2: Database Storage
Store the parsed data in your CTI database. Ensure the `fingerprint` is heavily indexed. If using a graph database, create a `PGPKey` node and link it to the `ThreatActor` node.

## 6. Real-World Attack Scenario

### Scenario: The Fall of a Ransomware Affiliate
An affiliate for a prominent Ransomware-as-a-Service (RaaS) operation, known as `GhostRider`, uses an exclusive darknet forum to recruit network insiders. `GhostRider` strictly enforces OpSec, using Tor, VPNs, and clean cryptocurrency mixes.

However, the automated CTI scraper picks up `GhostRider`'s PGP public key from their forum profile.
1. The system extracts the fingerprint: `3F4A...9B2C`.
2. The automated pipeline queries the MIT public key server for this fingerprint.
3. A match is found. Five years ago, a university student generated this exact PGP key and uploaded it to the MIT server. The original UID contains the student's real name and a `.edu` email address.
4. Because PGP key generation relies on massive prime numbers, collisions are practically impossible. `GhostRider` is mathematically proven to be the individual who generated that key. The threat actor reused an old key instead of generating a fresh, anonymous one for criminal activity, leading directly to their unmasking.

## 7. Chaining Opportunities
- **[[11 - Network Graphing of Criminal Relationships]]:** PGP fingerprints serve as the anchor points for merging fragmented threat actor profiles into a unified graph.
- **[[13 - Dark Web Data Enrichment using MISP]]:** PGP fingerprints and extracted email addresses should be pushed to MISP as distinct attributes for broader intelligence sharing.
- **[[15 - Legal and Storage Considerations for Malicious Data]]:** While PGP public keys are not illegal to possess, the communications decrypted using seized private keys represent highly sensitive evidence requiring strict chain-of-custody.

## 8. Related Notes
- [[Public Key Infrastructure (PKI) Vulnerabilities]]
- [[Cryptography in Malware and C2]]
- [[Regex for Threat Hunters]]
- [[Open Source Intelligence (OSINT) Techniques]]
