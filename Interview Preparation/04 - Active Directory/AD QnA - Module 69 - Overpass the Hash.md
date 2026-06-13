---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 69"
---

# QnA - AD Module 69: Overpass the Hash / Pass the Key

## Architecture Overview: Overpass the Hash (Pass the Key)

```text
+-------------------------------------------------------------+
|               Overpass the Hash Architecture                |
+-------------------------------------------------------------+
| [Attacker Machine]                                          |
|  1. Compromise User's Secret Key                            |
|     (NTLM Hash / RC4, AES-128, or AES-256 Key)              |
|                                                             |
|  2. Execute Rubeus asktgt (Pass the Key)                    |
|     Rubeus.exe asktgt /user:Admin /rc4:<Hash> /ptt          |
|                                                             |
+-------------------------------------------------------------+
               |
               | 3. AS-REQ (Encrypted with compromised key)
               v
+-------------------------------------------------------------+
| [Key Distribution Center / Domain Controller]               |
|  4. Validates pre-authentication using stored user key      |
|                                                             |
|  5. Generates Ticket Granting Ticket (TGT)                  |
|                                                             |
|  <-- 6. AS-REP (Contains TGT and Session Key)               |
+-------------------------------------------------------------+
               |
               | 7. Attacker receives valid TGT
               v
+-------------------------------------------------------------+
| [Attacker Machine]                                          |
|  8. Attacker is now using pure Kerberos (PtT)               |
|     (NTLM protocol is entirely bypassed)                    |
+-------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: What is the fundamental difference between "Pass the Hash" (PtH) and "Overpass the Hash" (PtK)?
**Answer:**
**Pass the Hash (PtH):** Involves reusing a stolen NTLM hash to authenticate via the **NTLM authentication protocol** (Challenge/Response). The attacker injects the hash, and the system uses it to answer NTLM challenges from target servers over protocols like SMB or WMI.
**Overpass the Hash (Pass the Key):** Involves using a stolen hash (RC4/NTLM) or AES keys to seamlessly transition into the **Kerberos protocol**. The attacker uses the stolen cryptographic key to manually encrypt a Kerberos AS-REQ (Authentication Service Request) timestamp. The KDC validates this and returns a valid Kerberos TGT. The attacker effectively "upgrades" an NTLM hash into a Kerberos ticket, entirely avoiding NTLM network traffic.

### Q2: Explain the significance of Kerberos Encryption Types (RC4 vs AES) in an Overpass the Hash attack.
**Answer:**
Kerberos supports multiple encryption algorithms for generating tickets and encrypting pre-authentication data. 
- **RC4 (Type 23):** Historically, Kerberos used RC4-HMAC. The RC4 key is mathematically identical to the user's NTLM hash. Therefore, if an attacker has an NTLM hash, they actually hold the Kerberos RC4 key.
- **AES-128 (Type 17) and AES-256 (Type 18):** Modern Windows environments default to AES. AES keys are derived from the user's plaintext password combined with a salt (typically the domain name and username).
**Significance in Attack:** If an environment has disabled RC4 encryption (a common hardening practice), an attacker *cannot* perform Overpass the Hash using only an NTLM hash. They must dump and utilize the user's AES-256 key from LSASS memory to construct a valid AS-REQ that the KDC will accept.

### Q3: How does Rubeus's `asktgt` module work under the hood during an Overpass the Hash attack?
**Answer:**
When an attacker runs `Rubeus.exe asktgt /user:Target /rc4:HASH /ptt`, Rubeus performs the following low-level operations:
1. **Timestamp Generation:** It generates a current UTC timestamp.
2. **Pre-Authentication Encryption:** It encrypts this timestamp using the provided key (RC4/AES). This forms the PA-ENC-TIMESTAMP structure required for Kerberos pre-authentication.
3. **AS-REQ Construction:** It builds a raw Kerberos AS-REQ packet, appending the encrypted timestamp and requesting a TGT for the target user.
4. **Network Transmission:** It sends the raw UDP/TCP packet to port 88 on the Domain Controller.
5. **Decryption and Injection:** Upon receiving the AS-REP, Rubeus uses the provided key to decrypt the reply, extracting the TGT and the Logon Session Key. If the `/ptt` flag is used, it injects the resulting `.kirbi` ticket directly into the current session's LSA cache.

---

## Scenario-Based Questions

### Scenario 1: You are on an engagement and have dumped the SAM database of a compromised server. You possess the NTLM hash of a Domain Admin account. You try standard PtH via SMB, but it fails because the organization has enforced a strict "Deny NTLM" policy domain-wide. How do you leverage the hash to gain access?
**Answer:**
Because NTLM authentication is blocked, I must use Overpass the Hash to transition to Kerberos.
1. I will use the Domain Admin's NTLM hash as the RC4 Kerberos key.
2. I execute Rubeus locally: `Rubeus.exe asktgt /user:AdminUser /domain:corp.local /rc4:<NTLM_Hash> /ptt`
3. Rubeus crafts an AS-REQ encrypted with the RC4 key. Even if NTLM is disabled, if RC4 is still supported for Kerberos pre-authentication, the DC will accept the request and return a TGT.
4. Once the TGT is injected into my session, I have successfully authenticated via Kerberos. I can now access target systems using standard tools (like `psexec` or `wmiexec`) and they will natively use Kerberos (TGS-REQ) instead of NTLM.

### Scenario 2: You attempt the Overpass the Hash attack from Scenario 1 using the RC4 key, but the Domain Controller responds with a `KDC_ERR_ETYPE_NOTSUPP` error. What does this mean, and what is your next operational step?
**Answer:**
**Meaning:** `KDC_ERR_ETYPE_NOTSUPP` (Error 14) means the requested encryption type is not supported. The organization has successfully hardened Active Directory by disabling RC4-HMAC (`msds-supportedencryptiontypes` registry key or GPO) for Kerberos. The KDC refuses to negotiate or accept pre-authentication encrypted with RC4 (the NTLM hash).
**Next Operational Step:**
Since the NTLM/RC4 hash is useless for Kerberos authentication in this environment, I must obtain the **AES keys** (specifically AES-256). 
1. If I obtained the NTLM hash from an offline SAM dump or NTDS.dit, I cannot derive the AES key without the plaintext password. I would need to crack the NTLM hash offline to retrieve the plaintext password, and then use a tool to calculate the AES-256 key using the password and the domain salt.
2. If I dumped the hash from active LSASS memory, modern credential dumpers (like Mimikatz `sekurlsa::ekeys`) also extract the AES-128 and AES-256 keys. I would extract the AES-256 key and rerun the attack: `Rubeus.exe asktgt /user:AdminUser /aes256:<AES_KEY> /ptt`.

### Scenario 3: You want to perform Overpass the Hash to blend in with normal network traffic. You notice that all legitimate AS-REQ traffic uses AES-256, but your offensive tool defaults to RC4 when providing an NTLM hash. Why is this a major OPSEC risk, and how does the Blue Team detect it?
**Answer:**
**OPSEC Risk:** Modern Windows environments prefer AES-256 for all Kerberos traffic. If a user normally authenticates with AES-256 (Encryption Type `0x12`), but suddenly an AS-REQ is sent requesting a TGT using RC4 (Encryption Type `0x17`), it stands out vividly in the telemetry as an anomalous cryptographic downgrade.
**Blue Team Detection:** 
The Blue Team monitors **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested)** on the Domain Controllers. They analyze the `Ticket Encryption Type` field. An alert is triggered whenever a highly privileged account (or any account on a modern OS) requests a TGT using `0x17` (RC4) instead of `0x12` (AES-256). To avoid this, an attacker *must* use the AES-256 key (`sekurlsa::ekeys`) when crafting the `asktgt` request, ensuring the cryptographic signature matches expected behavioral baselines.

---

## Deep-Dive Defensive Questions

### Q1: How do you completely eliminate the Overpass the Hash risk associated with NTLM hashes in an Active Directory environment?
**Answer:**
The only way to completely sever the link between an NTLM hash and a Kerberos ticket is to **disable RC4 encryption** domain-wide.
1. **GPO Hardening:** Navigate to `Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> Security Options`.
2. Configure `Network security: Configure encryption types allowed for Kerberos`.
3. Uncheck `RC4_HMAC_MD5` and ensure only `AES128_HMAC_SHA1` and `AES256_HMAC_SHA1` are selected.
4. **Active Directory Attribute:** Ensure that user accounts do not have the "Use Kerberos DES encryption types for this account" or "Do not require Kerberos preauthentication" flags checked.
By disabling RC4, an attacker who steals an NTLM hash (which is mathematically identical to the RC4 key) can no longer use it to forge an AS-REQ. They are forced to acquire the AES keys, which are not stored in standard password databases like NTDS.dit or SAM, limiting the attack surface strictly to live LSASS memory extraction.

### Q2: Detail the forensic analysis of a system where an attacker used Mimikatz `sekurlsa::pth` to perform an Overpass the Hash attack. What artifacts are left on the local endpoint?
**Answer:**
When Mimikatz performs PtH/Overpass the Hash locally:
1. **Process Injection:** Mimikatz opens a handle to `lsass.exe`. Sysmon Event ID 10 (Process Access) will show the attacker process requesting `PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION` access to LSASS.
2. **Suspicious Logon:** Mimikatz calls `LogonUser()` with `LOGON32_LOGON_NEW_CREDENTIALS`. This generates a local Event ID 4624 with **Logon Type 9**.
3. **Blank/Dummy Credentials:** The Logon Type 9 event will often show the Target Username, but if Mimikatz replaces the Kerberos keys dynamically in memory, the initial logon event might show suspicious dummy names or domains depending on how the tool was executed.
4. **Memory Artifacts:** The injected keys reside in LSASS memory. Advanced memory forensics (e.g., using Volatility) can identify floating, unbacked Kerberos ticket structures or mismatched cryptographic keys associated with the user's LSA session.

### Q3: What is Kerberos Pre-Authentication, and why does disabling it (AS-REP Roasting) essentially bypass the need for Overpass the Hash entirely?
**Answer:**
**Kerberos Pre-Authentication** requires a user to encrypt a timestamp with their secret key (RC4/AES) and send it to the KDC in the AS-REQ. The KDC attempts to decrypt it; if successful, it proves the user knows their password, and the KDC replies with a TGT. This is the exact mechanism Overpass the Hash abuses.
If an administrator checks the **"Do not require Kerberos preauthentication"** flag on a user account, the KDC does not require the encrypted timestamp. Anyone can send a blank AS-REQ for that user, and the KDC will immediately reply with an AS-REP containing the TGT (encrypted with the user's password) and the session key.
This allows **AS-REP Roasting**. An attacker doesn't need to perform Overpass the Hash because they don't need a hash or key to request the ticket. They simply request the AS-REP, capture it, and brute-force the encrypted portion offline to recover the user's plaintext password.

---

## Real-World Attack Scenario
**Bypassing the NTLM Ban:**
A Red Team was operating in a highly mature environment where NTLM authentication had been aggressively disabled (`Restrict NTLM: Deny All`). Furthermore, the organization utilized tiering, preventing Domain Admins from logging into standard workstations.
The Red Team compromised a Tier 1 server administrator. They dumped the NTDS.dit database from a backup server and extracted the NTLM hash for a highly privileged Service Account (`svc_sql_admin`).
Because NTLM was disabled across the network, they could not pass the hash via SMB. Because they obtained the hash offline (NTDS.dit), they did not have the AES keys from LSASS.
However, the Blue Team had failed to disable RC4 encryption for Kerberos. The Red Team utilized Rubeus to perform an Overpass the Hash attack (`asktgt /rc4:HASH`). The KDC accepted the RC4-encrypted pre-authentication and returned a valid Kerberos TGT for the `svc_sql_admin` account. The Red Team loaded the TGT and used pure Kerberos to authenticate to the primary SQL cluster, successfully exfiltrating the target database while completely avoiding the NTLM network restrictions.

---

## Chaining Opportunities
- **Pass the Ticket:** Overpass the Hash generates a TGT. The immediate next step is injecting that TGT into memory, which is the definition of [[AD QnA - Module 68 - Pass the Ticket PtT]].
- **Kerberoasting:** Once a TGT is acquired via PtK, the attacker can request TGS tickets for any service account in the domain, allowing them to perform offline password cracking via Kerberoasting.
- **Domain Dominance:** If the hash used belongs to a Domain Admin, the resulting TGT can be used to perform a remote [[AD QnA - Module 70 - DCSync Attacks]] to dump the entire Active Directory forest secrets.

---

## Related Notes
- [[Kerberos Pre-Authentication Mechanisms]]
- [[Kerberos Encryption Types and Weaknesses]]
- [[Rubeus Tool Usage Guide]]
- [[NTLM to Kerberos Migration Strategies]]
