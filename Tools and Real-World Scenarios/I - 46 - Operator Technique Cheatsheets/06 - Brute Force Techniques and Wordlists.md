---
tags: [tools, brute-force, credentials, pentesting, red-team]
difficulty: intermediate
module: "46 - Operator Technique Cheatsheets"
topic: "46.06 Brute Force Techniques and Wordlists"
---

# Brute Force Techniques and Wordlists

## Introduction
**Brute forcing** — systematically trying credentials, paths, parameters, or tokens until something works — is a foundational technique across the whole kill chain: login pages, SSH/SMB/RDP, directory/file discovery, subdomains, parameters, and offline hash cracking. The art is less about the tools (covered in [[50 - Hydra All Protocols Reference]], [[51 - Medusa Parallel Login Brute Forcer]], [[65 - hashcat Full Mode and Rule Reference]], [[66 - John the Ripper Complete Guide]]) and more about **strategy**: choosing the right wordlist, the right mode, and a rate that succeeds without locking accounts or getting blocked. This note is the strategic cheatsheet.

## Types of Brute Force
```text
+---------------------------------------------------------------+
|  Type                |  Target                | Tool           |
+---------------------------------------------------------------+
|  Online credential   | login/ssh/smb/rdp/http | hydra, medusa, |
|                      |                        | netexec, ffuf  |
|  Password spraying   | many users, few pass   | (avoid lockout)|
|  Content discovery   | dirs/files/vhosts      | ffuf, gobuster,|
|                      |                        | feroxbuster    |
|  Parameter discovery | hidden GET/POST params | arjun, x8      |
|  Subdomain brute     | DNS names              | puredns,gobuster|
|  Offline hash crack  | captured hashes        | hashcat, john  |
+---------------------------------------------------------------+
```

## Online: Spraying vs Brute (avoid lockouts)
**Password spraying** — one (or few) common passwords across MANY usernames — is the safe default against account-lockout policies; classic per-account brute force trips lockouts fast.
```bash
# spray: one password, many users (low and slow)
netexec smb TARGET -u users.txt -p 'Spring2026!' --continue-on-success
hydra -L users.txt -p 'Welcome1' ssh://TARGET -t 4 -W 30
# targeted brute (only when no lockout policy)
hydra -l admin -P rockyou.txt rdp://TARGET
```
**Rules:** know the lockout threshold first; stay 1 attempt under it per window; add delays (`-W`); spray at most a couple passwords per policy window; prefer seasonal/company-themed passwords.

## Content & Parameter Discovery
```bash
# directories/files
ffuf -u https://TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -mc 200,301,302,403
feroxbuster -u https://TARGET -w wordlist.txt -x php,txt,bak
# vhosts
ffuf -u https://TARGET -H "Host: FUZZ.target.com" -w subdomains.txt -fs 0
# hidden parameters
arjun -u https://TARGET/api
```
Filter noise with `-mc`/`-fc` (match/filter codes) and `-fs`/`-fw` (filter by size/words).

## Wordlists — the Real Lever
```text
   SecLists (github.com/danielmiessler/SecLists) = the standard kit:
     Passwords/   rockyou.txt, common, leaked sets
     Discovery/Web-Content/  raft-*, directory lists
     Discovery/DNS/          subdomain lists
     Usernames/              name lists
   Custom/targeted:
     cewl  https://TARGET           # scrape site -> themed wordlist
     username-anarchy               # name -> username permutations
     hashcat rules on a base list   # mutate (Leet, append year)
```
A **targeted** list (company terms via `cewl`, employee names, breach data for the org) beats a giant generic list almost every time — smaller, faster, higher hit rate.

## Offline Hash Cracking Strategy
```bash
hashcat -m <mode> hashes.txt rockyou.txt -r rules/best64.rule   # wordlist + rules
hashcat -m <mode> hashes.txt -a 3 '?u?l?l?l?l?d?d?d'            # mask (known pattern)
john --format=<fmt> --wordlist=rockyou.txt --rules hashes.txt
```
Order of attack: **wordlist → wordlist+rules → mask/hybrid → pure brute** (last resort). Identify the hash mode first (`hashid`, `hashcat --identify`).

## Why It Matters
Weak/reused credentials and exposed content remain among the most common real-world entry points. Brute forcing done *well* (spraying within policy, targeted wordlists, right hash mode) is high-yield; done badly it locks accounts, triggers alerts, and wastes days — so strategy matters more than raw tool knowledge.

## Defensive Notes
- Enforce **account lockout / throttling**, MFA, and detection of spray patterns (many users, same password, short window).
- Rate-limit and monitor login endpoints; deploy CAPTCHAs/anomaly detection; alert on 401/403 floods and directory-scan signatures.
- Use strong password policies + breach-password screening; monitor for offline-crack indicators (mass hash access — e.g. NTDS/SAM/shadow reads).

## Related Notes
- [[50 - Hydra All Protocols Reference]]
- [[65 - hashcat Full Mode and Rule Reference]]
- [[66 - John the Ripper Complete Guide]]
- [[05 - Finding and Vetting Exploits]]
