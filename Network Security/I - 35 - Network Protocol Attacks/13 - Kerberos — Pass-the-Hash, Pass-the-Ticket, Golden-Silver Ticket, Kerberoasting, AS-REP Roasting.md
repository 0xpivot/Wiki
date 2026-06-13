---
tags: [kerberos, active-directory, ptt, pth, kerberoasting, as-rep-roasting, golden-ticket]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.13 Kerberos"
---

# Kerberos Exploitation: Forging, Roasting, and Relaying

Kerberos is the default and most critical authentication protocol in modern Windows Active Directory environments, operating primarily over TCP/UDP port 88. Designed to be more secure than NTLM, Kerberos relies on a trusted third party—the Key Distribution Center (KDC), functioning on the Domain Controller—to verify identities and issue cryptographic tickets. 

Despite its robust mathematical foundations, Kerberos is vulnerable to a myriad of severe, architecture-level attacks due to implementation flaws, legacy backward compatibility, and poor password policies. Understanding Kerberos exploitation is the absolute pinnacle of Active Directory penetration testing.

## Protocol Architecture: The Kerberos Dance

Authentication in Kerberos involves a complex sequence of requests and encrypted tickets.

1. **AS-REQ (Authentication Service Request):** The client sends a request to the KDC. A timestamp encrypted with the user's password hash (Pre-Authentication) is included to prove the user knows the password.
2. **AS-REP (Authentication Service Reply):** The KDC verifies the timestamp. If valid, it replies with a **Ticket Granting Ticket (TGT)** (encrypted with the `krbtgt` account hash) and a session key.
3. **TGS-REQ (Ticket Granting Service Request):** The client wants to access a service (e.g., a file share). It sends the TGT to the KDC, requesting a ticket for that specific service.
4. **TGS-REP (Ticket Granting Service Reply):** The KDC validates the TGT and sends back a **Ticket Granting Service (TGS) ticket**, encrypted with the target service's password hash.
5. **AP-REQ (Application Request):** The client presents the TGS ticket to the destination service server.
6. **AP-REP (Application Reply):** The service decrypts the TGS ticket, verifies the client's identity, and grants access.

---

## Attack Surface Overview

```ascii
+-------------+                       +-----------------------+                      +---------------+
|             | --1. AS-REQ (PreAuth)->|                       |                     |               |
|   Client    | <-2. AS-REP (TGT)------|  Domain Controller    |                     |   Target      |
| (Attacker)  |                        |  (KDC / krbtgt)       |                     |   Server      |
|             | --3. TGS-REQ (TGT)---->|                       |                     |  (SMB/SQL)    |
|             | <-4. TGS-REP (TGS)-----|                       |                     |               |
|             |                        +-----------------------+                     |               |
|             |                                                                      |               |
|             | --5. AP-REQ (Present TGS)------------------------------------------->|               |
|             | <-6. AP-REP (Access Granted)-----------------------------------------|               |
+-------------+                                                                      +---------------+
      |
      | *Attacker Interventions:*
      | - Pass-the-Hash (Forging AS-REQ)
      | - AS-REP Roasting (Capturing step 2 if PreAuth is disabled)
      | - Kerberoasting (Capturing step 4 to crack service hashes)
      | - Golden Ticket (Forging step 2 TGT entirely using krbtgt hash)
      | - Pass-the-Ticket (Stealing a TGT/TGS from memory and using it)
```

---

## 1. Kerberoasting

Kerberoasting takes advantage of how the KDC issues TGS tickets. When a user requests a TGS for a specific Service Principal Name (SPN), the KDC encrypts that TGS using the password hash of the account associated with that service.

**The Flaw:** Any authenticated domain user can request a TGS ticket for *any* SPN in the directory. The KDC will hand them the encrypted TGS. The attacker takes this ticket offline and brute-forces the encryption to reveal the service account's plaintext password.

**Execution:**
Service accounts often have high privileges (e.g., Domain Admin) and passwords that never expire.
```bash
# Using Impacket's GetUserSPNs to request and extract roastable hashes
impacket-GetUserSPNs -request -dc-ip 10.10.10.10 corp.local/jdoe:Password123 -outputfile hashes.txt

# Cracking the hash offline with Hashcat
hashcat -m 13100 hashes.txt wordlist.txt
```

---

## 2. AS-REP Roasting

AS-REP Roasting targets users who have the `Do not require Kerberos preauthentication` flag enabled in Active Directory.

**The Flaw:** Without Pre-Authentication, an attacker doesn't need the user's password to send an AS-REQ. The KDC will blindly respond with an AS-REP containing a piece of data encrypted with the user's password hash. The attacker captures this AS-REP and cracks it offline.

**Execution:**
```bash
# Using Impacket to find and roast AS-REP vulnerable accounts
impacket-GetNPUsers -dc-ip 10.10.10.10 corp.local/ -usersfile users.txt -format hashcat -outputfile asrep.txt

# Cracking with Hashcat
hashcat -m 18200 asrep.txt wordlist.txt
```

---

## 3. Pass-the-Hash (PtH) & Overpass-the-Hash

**Pass-the-Hash (NTLM):** While traditionally an NTLM attack, it relates closely to Kerberos. If an attacker has a user's NTLM hash, they can authenticate directly to services without needing the plaintext password.
**Overpass-the-Hash (Pass-the-Key):** The attacker uses a stolen NTLM hash (or AES key) to encrypt the Pre-Authentication timestamp, requesting a full Kerberos TGT from the KDC. This converts an NTLM hash into a valid Kerberos ticket.

```bash
# Using Impacket's Rubeus (on Windows) or ticketer
# Converting an NTLM hash to a Kerberos Ticket
Rubeus.exe asktgt /user:Administrator /rc4:<NTLM_HASH> /ptt
```

---

## 4. Pass-the-Ticket (PtT)

If an attacker compromises a machine (e.g., a workstation) with local Administrator or SYSTEM privileges, they can dump the memory of the Local Security Authority Subsystem Service (`LSASS.exe`). LSASS caches active Kerberos tickets (TGTs and TGSs) for users logged into the machine.

**The Flaw:** The attacker extracts these `.kirbi` or `ccache` tickets from memory and injects them into their own session. If a Domain Admin logged into the compromised workstation, the attacker steals their TGT and assumes their identity across the entire domain.

**Execution (Mimikatz):**
```text
mimikatz # sekurlsa::tickets /export
mimikatz # kerberos::ptt [ticket_filename.kirbi]
```

---

## 5. Golden and Silver Tickets

These are persistence mechanisms used after an attacker has completely compromised a domain.

### Golden Ticket
If an attacker compromises a Domain Controller, they can dump the NTLM hash of the `krbtgt` account. This account's hash is the master key used to encrypt all TGTs.
With the `krbtgt` hash, the attacker can forge completely valid TGTs for any user (real or fake) with any permissions (Domain Admin, Enterprise Admin) lasting for 10 years.
```bash
impacket-ticketer -nthash <krbtgt_hash> -domain-sid <domain_SID> -domain corp.local Administrator
```

### Silver Ticket
Instead of forging a TGT (which requires the `krbtgt` hash), a Silver Ticket forges a TGS ticket for a specific service using the NTLM hash of the *Service Account* (or computer account). This grants administrative access to that specific service (e.g., a SQL server, an SMB share) without ever interacting with the KDC, making it highly stealthy.

---

## Defensive Countermeasures & Hardening

1. **Strong Service Account Passwords:** Kerberoasting is mitigated by generating complex, 25+ character, randomly generated passwords for Service Accounts, or using Group Managed Service Accounts (gMSA) which rotate passwords automatically.
2. **Enforce Pre-Authentication:** Audit AD for any users with `DONT_REQ_PREAUTH` set and disable it to neutralize AS-REP roasting.
3. **Credential Guard:** Enable Windows Defender Credential Guard to isolate LSASS and prevent attackers from dumping plaintext passwords and Kerberos tickets from memory (thwarting Pass-the-Ticket).
4. **Tiered Administration:** Prevent Domain Admins from logging into lower-tier workstations. If a DA never logs into a workstation, their TGT cannot be stolen from that workstation's LSASS memory.
5. **Rotate `krbtgt` Password:** To invalidate existing Golden Tickets, the `krbtgt` account password must be rotated twice consecutively (due to password history caching).

---

## Chaining Opportunities

- **LDAP Enumeration -> Kerberoasting**: Map the domain via LDAP, extract users with SPNs, Kerberoast them, crack the hash, and log in via RDP or WinRM.
- **Local Admin -> Pass-the-Ticket -> DCSync**: Gain local admin on a workstation, dump LSASS to find a Domain Admin TGT, inject it via Pass-the-Ticket, and execute a DCSync attack to pull all password hashes from the Domain Controller.
- **AS-REP Roasting -> Silver Ticket**: Roast an AS-REP hash for a computer account, crack it, and use that machine account's NTLM hash to forge a Silver Ticket, gaining complete access to its local file shares over SMB.

## Related Notes
- [[12 - LDAP — Anonymous Bind, Enumeration, Injection]]
- [[10 - SMB — EternalBlue, Null Session, Relay Attacks]]
- [[02 - Active Directory Architecture and Trust Relationships]]
- [[07 - Password Attacks and Hash Cracking]]
- [[11 - NetBIOS — Enumeration, NBNS Poisoning]]
