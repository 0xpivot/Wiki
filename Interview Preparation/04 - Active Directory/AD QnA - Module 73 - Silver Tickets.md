---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 73"
---

# Active Directory Security Interview QnA: Silver Tickets

## ASCII Diagram: Silver Ticket Attack Flow

```text
+-----------------------------------------------------------------------------+
|                                                                             |
| +-------------------+                                     +---------------+ |
| |                   |  (1) Extract Service Hash           |               | |
| | Attacker Machine  | <---------------------------------- | Target Server | |
| |                   |      (e.g., MS SQL Server)          | / Service     | |
| +-------------------+                                     +---------------+ |
|          |                                                                  |
|          | (2) Offline TGS Forgery                                          |
|          |     (Target Server SPN, Fake PAC, High Privs)                    |
|          v                                                                  |
| +-------------------+                                     +---------------+ |
| |                   |      (3) Present Forged TGS         |               | |
| | Attacker Machine  | ----------------------------------> | Target Server | |
| | (Any User Context)|                                     | (e.g., MSSQL) | |
| +-------------------+ <---------------------------------- +---------------+ |
|                            (4) Access Granted!                              |
|                          (KDC is completely bypassed)                       |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the fundamental mechanics of a Silver Ticket attack. How does it critically differ from a Golden Ticket attack regarding the Kerberos authentication flow and the scope of compromise?**

**Answer:**
A Silver Ticket is a forged Kerberos Service Ticket (TGS). In the Kerberos protocol, once a user has a Ticket Granting Ticket (TGT), they request a TGS from the Key Distribution Center (KDC/Domain Controller) to access a specific service. The KDC encrypts the TGS using the password hash (NTLM/AES) of the service account hosting that target service.

In a Silver Ticket attack, an attacker compromises the password hash of a specific service account (e.g., a computer account hash for CIFS, or a domain user account hash running an MSSQL service). With this hash, the attacker bypasses the KDC entirely. They use tools like Mimikatz or Impacket to cryptographically forge a TGS directly.

The critical differences from a Golden Ticket are:
1. **Scope:** A Golden Ticket (forged TGT) uses the KRBTGT hash and grants access to *any* service in the domain. A Silver Ticket (forged TGS) uses a specific service's hash and grants access *only* to that specific service on that specific server.
2. **KDC Interaction:** A Golden Ticket must be presented to the KDC to request Service Tickets. A Silver Ticket is presented directly to the target server. The KDC is completely bypassed, meaning there are no Kerberos TGT/TGS request logs (Event IDs 4768/4769) generated on the Domain Controller.
3. **Cryptographic Material:** Golden relies on the domain-wide `KRBTGT` key. Silver relies on a localized Service Account key (computer machine account or user service account).

**Q2: What specific components of the Privileged Attribute Certificate (PAC) are manipulated in a Silver Ticket, and how does the target service validate this PAC?**

**Answer:**
Similar to a Golden Ticket, the attacker manipulates the PAC within the forged TGS to grant themselves elevated privileges on the target service.
The attacker typically injects the SID for `Domain Admins` (RID 512) or specific local administrator group SIDs into the PAC's `GroupIds` and `ExtraSids` fields. They also specify a fabricated or legitimate user in the `cname` field.

**Validation:**
When the forged TGS is presented to the target server, the server decrypts the ticket using its own password hash. It then extracts the PAC.
Crucially, by default, the target server *trusts* the contents of the PAC if the ticket was successfully decrypted. It looks at the SIDs in the PAC, sees the `Domain Admins` SID, and creates an access token for the attacker granting them administrative rights over that specific service.

While the PAC contains two signatures (Server Signature and KDC Signature), in a Silver Ticket scenario, the attacker signs the Server Signature with the stolen service hash. By default, the target service does *not* proactively contact the KDC to verify the KDC Signature. It assumes that if the ticket is encrypted with its key, it must have come from the KDC.

**Q3: List common Service Principal Names (SPNs) targeted in Silver Ticket attacks and the corresponding type of access they grant upon successful forgery.**

**Answer:**
Attackers target SPNs that yield highly privileged interaction with the underlying operating system or application:

1. **CIFS (Common Internet File System):** Forging a ticket for `cifs/target-server.domain.com` grants the attacker arbitrary file system access. They can read/write the C$ drive, create scheduled tasks, or use PsExec to gain an interactive SYSTEM shell.
2. **HOST:** Forging a ticket for `host/target-server.domain.com` grants access to several system-level services, including WMI (Windows Management Instrumentation) and the Task Scheduler. This allows for remote code execution via WMI.
3. **LDAP:** Forging a ticket for `ldap/domain-controller.domain.com` (using the DC's machine account hash) allows the attacker to query and modify Active Directory objects directly via LDAP, bypassing normal authentication.
4. **MSSQLSvc:** Forging a ticket for a SQL server SPN grants database administrator access, allowing data exfiltration or potential OS command execution via `xp_cmdshell`.
5. **HTTP:** Forging a ticket for web applications using Windows Authentication allows the attacker to bypass web login portals and access administrative consoles.

## Scenario-Based Questions

**Q4: You are on a Red Team engagement. You have obtained local Administrator access to a standalone web server, but you have no domain privileges. You dump the local SAM and discover the NTLM hash of the machine account (`WEBSERVER$`). How can you use a Silver Ticket to pivot and execute code on this machine remotely from your attacking Linux infrastructure without tripping standard endpoint EDR alerts associated with Mimikatz?**

**Answer:**
Since I have the machine account hash (`WEBSERVER$`), I hold the encryption key for all services hosted by the system itself.
1. From my external Linux attacking infrastructure, I will use Impacket's `ticketer.py`. I do not need Mimikatz on the victim machine.
2. I will forge a Silver Ticket targeting the CIFS service. The command would look like:
   `ticketer.py -nthash <WEBSERVER$_HASH> -domain-sid <DOMAIN_SID> -domain <DOMAIN_NAME> -spn cifs/webserver.domain.com Administrator`
   This creates a `.ccache` file containing a TGS where I am asserting to be the Domain Administrator.
3. I will export the `.ccache` file to my `KRB5CCNAME` environment variable.
4. I will then use Impacket's `smbclient.py` or `psexec.py` (e.g., `psexec.py -k -no-pass webserver.domain.com`).
5. Because I am using `-k`, Impacket uses Kerberos authentication and presents the forged Silver Ticket directly to the web server's SMB service. The server decrypts it, sees the Domain Admin SID in the PAC, and grants me SYSTEM-level code execution via PsExec.

This bypasses EDR because the attack is launched remotely; the Kerberos traffic looks like standard network authentication, and Mimikatz is never dropped to disk or executed in memory on the victim.

**Q5: During a purple team exercise, the Red Team executes a Silver Ticket attack against a critical database server. The Blue Team analyzes the Domain Controller Kerberos logs (Event IDs 4768 and 4769) but finds absolutely no trace of the attacker's simulated user account. How do you explain this visibility gap, and what host-based logs on the *target server* must the Blue Team analyze to detect the forged ticket usage?**

**Answer:**
I would explain that Silver Tickets are a localized attack that completely bypasses the Key Distribution Center (Domain Controller). The attacker forged the Service Ticket offline and presented it directly to the database server. Because the DC was never involved in issuing the ticket, no Event ID 4768 (TGT Request) or 4769 (TGS Request) will ever be generated on the DC logs. The DC is blind to the transaction.

To detect Silver Ticket usage, the Blue Team must shift their focus to the *target server's* local Security Event Logs:
1. **Event ID 4624 (Successful Logon):** They must look for network logons (Logon Type 3) where the `Authentication Package` is `Kerberos`.
2. **Account Name Anomalies:** In the 4624 event, the `Account Name` will reflect the user the attacker specified in the forged ticket (e.g., `Administrator` or a fake name). If a fake name was used, or if the `Administrator` account rarely logs into this specific database server over the network, it's a strong indicator.
3. **Event ID 4672 (Special Privileges Assigned):** Shortly after the 4624 event, a 4672 event will fire indicating that high privileges (like `SeDebugPrivilege` or `SeImpersonatePrivilege`) were assigned to the logged-on session, confirming the PAC successfully granted administrative rights.
4. **Logon ID Correlation:** Correlating the Logon ID from the 4624 event with subsequent process creation events (Event ID 4688) or file share access events (Event ID 5140) to trace what the attacker did with the forged access.

## Deep-Dive Defensive Questions

**Q6: Microsoft introduced a security feature called "PAC Validation" to mitigate forged tickets. Explain how PAC Validation works in the context of a Silver Ticket. Does the default implementation of PAC Validation effectively stop Silver Ticket attacks? Why or why not?**

**Answer:**
PAC Validation, in theory, requires the target service to verify the Privileged Attribute Certificate with the KDC to ensure it hasn't been tampered with.
When a service receives a TGS, it decrypts it and finds the PAC. If PAC Validation is enabled and enforced, the service takes the PAC KDC Signature (which the attacker forged because they don't have the KRBTGT key, they just filled it with garbage or signed it with the service key) and sends a specialized RPC message (`NetrLogonSamLogonWithFlags`) back to the Domain Controller via the Netlogon secure channel.

The DC checks the KDC signature against the actual KRBTGT key. If the signature is invalid (which it will be in a Silver Ticket scenario), the DC tells the service the validation failed, and the service denies access.

**Does it stop Silver Tickets?**
By default, historically, **NO**. For performance reasons and to prevent massive network overhead, Windows services do *not* automatically perform PAC Validation with the DC for every Kerberos authentication. It is an opt-in feature, typically only enforced for highly sensitive services (like other Domain Controllers or services configured explicitly to require it). Furthermore, if an attacker creates a Silver Ticket without a PAC entirely, some older services might still grant access based on the principal name alone, bypassing the check entirely (though modern updates have hardened this).
To effectively mitigate Silver Tickets using this mechanism, organizations must explicitly configure the registry key `ValidateKdcPacSignature` on sensitive servers, accepting the increased RPC traffic load to the DCs.

**Q7: Beyond implementing complex PAC Validation configurations, what is the most foundational, architecturally sound defense against Silver Ticket attacks, specifically focusing on the lifecycle of service account credentials?**

**Answer:**
The most foundational defense is preventing the attacker from obtaining the service account hash in the first place, and ensuring that if they do, its utility is severely limited by time.

1. **Machine Account Password Rotation:** For services running under the context of the computer account (`LocalSystem`, `NetworkService`), Active Directory automatically rotates the machine account password every 30 days. If an attacker extracts a machine hash, the Silver Ticket is only valid until that password rotates.
2. **Group Managed Service Accounts (gMSA):** The ultimate defense for user-based service accounts. Historically, administrators created standard user accounts for services (e.g., `svc_sql`), set the password to "never expire," and documented it. If this hash is stolen, the Silver Ticket is valid *forever*.
Organizations must migrate all services to use gMSAs. gMSAs act like machine accounts; Active Directory automatically manages and rotates their 120-character complex passwords every 30 days without administrator intervention. This drastically reduces the window of opportunity for a Silver Ticket attack.
3. **Restricting Local Admin Access:** Attackers need local administrative rights on a server to dump the local SAM or LSA memory to retrieve the machine hash or service account hashes. Implementing strict Tiered Administration, limiting lateral movement, and enforcing Just-In-Time (JIT) access prevents the initial compromise of the hashes.

## Real-World Attack Scenario
During a penetration test against a healthcare provider, the Red Team compromised a low-tier helpdesk workstation. They discovered an exposed file share containing a legacy PowerShell script used for automated server deployments. The script contained hardcoded, plaintext credentials for a domain user account named `svc_sccm_deploy`.
The Red Team queried Active Directory and found that `svc_sccm_deploy` had a Service Principal Name (SPN) registered for `cifs/primary-fileserver.med.local`.

Instead of attempting to log in as the service account and risk triggering anomalous logon alerts, the Red Team used the hardcoded password to generate its NTLM hash. They then forged a Silver Ticket for the CIFS service on the primary file server, injecting the Domain Admins SID into the PAC.
From their attacking machine, they presented the Silver Ticket directly to the file server. The KDC logged nothing. The file server accepted the ticket, granting them SYSTEM-level access to the C$ share. They deployed ransomware encryptors directly to the file server's storage arrays, completely bypassing the domain's heavily monitored authentication perimeter.

## Chaining Opportunities
- **Kerberoasting -> Silver Ticket:** Requesting a TGS for a vulnerable service, cracking the hash offline (Kerberoasting), and then using that cracked hash to forge a Silver Ticket for persistent, localized administrative access to that service.
- **Local SAM Dump -> Silver Ticket:** Compromising a web server, dumping the local SAM to obtain the Machine Account hash, and forging a Silver Ticket for the `HOST` SPN to execute WMI commands and move laterally to other systems trusting that machine.
- **Silver Ticket -> DCSync:** Forging a Silver Ticket for the `LDAP` service on a Domain Controller (using the DC's machine hash obtained via an alternate vector) to perform a DCSync attack without needing a Golden Ticket or Domain Admin credentials.

## Related Notes
- [[72 - Golden Tickets]]
- [[68 - Kerberoasting Attacks]]
- [[60 - Kerberos Authentication Deep Dive]]
- [[55 - Group Managed Service Accounts (gMSA)]]
