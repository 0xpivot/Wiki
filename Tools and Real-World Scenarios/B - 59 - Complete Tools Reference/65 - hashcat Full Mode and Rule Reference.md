---
tags: [tools, cracking, cryptography, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.65 hashcat Full Mode and Rule Reference"
---

# 65 - hashcat Full Mode and Rule Reference

## 1. Executive Summary

Hashcat is the world's fastest and most advanced password recovery utility, supporting five unique modes of attack for over 300 highly-optimized hashing algorithms. It relies on OpenCL and CUDA to offload cryptographic calculations to GPUs, achieving billions of hashes per second. In a VAPT engagement, Hashcat is the ultimate bottleneck breaker—translating the encrypted or hashed artifacts gathered by tools like Responder, Mimikatz, and Rubeus into usable plaintext credentials.

## 2. Architecture & Cracking Pipeline

```text
[Input Artifacts]                                    [Transformations]
  (Hashes, Kerberoast)                                (Rules, Masks)
          |                                                  |
          v                                                  v
+-------------------------------------------------------------------------+
|                              Hashcat Engine                             |
|                                                                         |
|  +-----------------+     +-----------------------+     +-------------+  |
|  |   Candidate     |     |   OpenCL / CUDA GPU   |     |  Comparator |  |
|  |   Generator     |---->|   Acceleration Core   |---->|   Logic     |  |
|  | (Dictionaries)  |     |  (Massive Parallelism)|     |             |  |
|  +-----------------+     +-----------------------+     +-------------+  |
+-------------------------------------------------------------------------+
                                      |
                                      v
                             [Cracked Plaintexts]
                             (hashcat.potfile)
```

## 3. Core Attack Modes (`-a`)

Hashcat supports different methods for generating candidate passwords.
| Mode | Name | Description |
|------|------|-------------|
| `-a 0` | Straight (Dictionary) | Reads candidates sequentially from a wordlist. Often paired with Rules. |
| `-a 1` | Combinator | Combines two wordlists. (e.g., List A = "Summer", List B = "2024" -> "Summer2024"). |
| `-a 3` | Brute-force / Mask | Generates candidates based on a specific character mask (e.g., `?u?l?l?l?d?d?d`). |
| `-a 6` | Hybrid (Dict + Mask) | Appends a mask to a dictionary word. (e.g., `wordlist.txt ?d?d?d?d` -> `Password1234`). |
| `-a 7` | Hybrid (Mask + Dict) | Prepends a mask to a dictionary word. (e.g., `?d?d?d?d wordlist.txt` -> `1234Password`). |
| `-a 9` | Association | Used for combining multiple attributes. |

## 4. Critical Hash Types (`-m`)

Hashcat supports hundreds of modes. Here are the most critical ones for Active Directory and VAPT contexts.
| Mode (`-m`) | Hash Type | Common Source Tool |
|-------------|-----------|--------------------|
| `1000` | NTLM | Mimikatz (`sekurlsa::msv`), SAM Dump |
| `5500` | NetNTLMv1 | Responder (WPAD, LLMNR) |
| `5600` | NetNTLMv2 | Responder, Inveigh, ntlmrelayx |
| `13100` | Kerberos 5 TGS-REP etype 23 (RC4) | Rubeus (`kerberoast`) |
| `18200` | Kerberos 5 AS-REP etype 23 (RC4) | Rubeus (`asreproast`) |
| `19600` | Kerberos 5 TGS-REP etype 17/18 (AES) | Rubeus (`kerberoast` without rc4opsec) |
| `3200` | bcrypt ($2a$, $2b$, $2y$, $2x$) | Web app DB dumps |
| `1800` | SHA-512 (Unix) | `/etc/shadow` |

## 5. Deep Dive: Mask Attacks (`-a 3`)

Mask attacks are a highly optimized form of brute force, defining exactly what character sets are expected at specific positions.
- `?l` = lowercase `a-z`
- `?u` = uppercase `A-Z`
- `?d` = digit `0-9`
- `?s` = special `!"#$%&'()*+,-./:;<=>?@[\]^_\`{|}~`
- `?a` = all of the above

### Custom Masks
You can define custom character sets using `-1`, `-2`, `-3`, `-4`.
```bash
# Brute force an 8-character password. First char is Upper, next 5 are Lower, last 2 are either Digit or Special.
# -1 defines a custom set of Digits + Specials
hashcat -m 1000 -a 3 hashes.txt -1 ?d?s ?u?l?l?l?l?l?1?1
```

## 6. Deep Dive: Rule Based Attacks

Rules mutate wordlists in memory without permanently modifying the dictionary file. They are incredibly powerful.

### Common Rule Syntax
| Rule | Action | Example (Input: `password`) |
|------|--------|-----------------------------|
| `c` | Capitalize first letter | `Password` |
| `u` | Uppercase all | `PASSWORD` |
| `l` | Lowercase all | `password` |
| `r` | Reverse string | `drowssap` |
| `d` | Duplicate string | `passwordpassword` |
| `$`*x* | Append character *x* | `$!`: `password!` |
| `^`*x* | Prepend character *x* | `^#`: `#password` |
| `]` / `[` | Append/Prepend character | Truncates or manipulates ends. |

### Top Rule Files
Included in the default Hashcat installation (`/usr/share/hashcat/rules/`):
- `best64.rule`: Essential, fast mutations. Always try this first.
- `rockyou-30000.rule`: Excellent balance of speed and coverage.
- `dive.rule`: Deep, heavy mutations. Takes significantly longer but catches highly complex patterns.
- `OneRuleToRuleThemAll.rule`: (Custom community rule) Phenomenal success rate against AD passwords.

```bash
# Example rule attack against Kerberoast hashes
hashcat -m 13100 -a 0 kerberoast.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

## 7. Performance Tuning and Optimization

Maximizing Hashcat's performance is crucial for large assessments.

### Hardware & Acceleration Flags
- `-O` (Optimized Kernels): Limits password length to 32 characters but increases speed by 15-30%. Use this always unless you suspect a huge passphrase.
- `-w 3` or `-w 4`: Workload profile. 
  - `1`: Low (desktop usage)
  - `2`: Default
  - `3`: High (ties up the GPU completely)
  - `4`: Nightmare (Maximum performance, OS UI will lag heavily)
- `--hwmon-temp-abort=90`: Stops cracking if GPU temp exceeds 90C. Protects hardware.

### Distributed Cracking
For massive jobs, use **Hashcat Brain**. It sets up a client-server architecture where multiple GPU rigs check out workloads to prevent duplicate candidate calculation.
```bash
# Server
hashcat --brain-server --brain-host 192.168.1.100 --brain-password Secret

# Client
hashcat --brain-client --brain-host 192.168.1.100 --brain-password Secret -m 1000 -a 0 ...
```

## 8. Potfiles and Analytics

Hashcat stores cracked passwords in a "potfile" (usually `~/.local/share/hashcat/hashcat.potfile`). 
When displaying cracked passwords, use `--show`.
```bash
hashcat -m 1000 hashes.txt --show
```
*Pro Tip:* Use `--username` if your input file is structured as `User:Hash`. This helps map the plaintext back to the compromised account instantly.

## 9. Chaining Opportunities

- **With Responder**: Responder captures NetNTLMv2 hashes. Feed them into Hashcat with `-m 5600`. See [[61 - Responder All Modes and Config]].
- **With Mimikatz**: Dump the SAM database or MSV memory (yielding NTLM hashes), feed into Hashcat with `-m 1000`. If cracking fails, use `sekurlsa::pth` to Pass-the-Hash instead. See [[62 - Mimikatz All Modules]].
- **With Rubeus**: Rubeus dumps RC4 and AES Kerberos tickets. Feed RC4 tickets into Hashcat with `-m 13100` or `-m 18200`. See [[63 - Rubeus Kerberos Attack Toolkit]].

## 10. Related Notes

- [[61 - Responder All Modes and Config]]
- [[62 - Mimikatz All Modules]]
- [[63 - Rubeus Kerberos Attack Toolkit]]
- [[45 - Password Spraying Strategies]]
- [[18 - Cryptography and Hash Reversing]]
