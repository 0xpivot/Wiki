---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 72"
---

# Active Directory Security Interview QnA: Golden Tickets

## ASCII Diagram: Golden Ticket Attack Flow

```text
+-----------------------------------------------------------------------------+
|                                                                             |
| +-------------------+                                     +---------------+ |
| |                   |  (1) Extract KRBTGT Hash (DCSync)   |               | |
| | Attacker Machine  | <---------------------------------- | Domain        | |
| | (DA Privileges)   |                                     | Controller    | |
| +-------------------+                                     +---------------+ |
|          |                                                                  |
|          | (2) Offline TGT Forgery                                          |
|          |     (Inject Target User, Fake PAC, High Privs)                   |
|          v                                                                  |
| +-------------------+      (3) Present Forged TGT         +---------------+ |
| |                   | ----------------------------------> |               | |
| | Attacker Machine  |      (4) Receive Valid TGS          | Domain        | |
| | (Any User Context)| <---------------------------------- | Controller    | |
| +-------------------+                                     +---------------+ |
|                                                                    |        |
|                            (5) Access Resource via TGS             v        |
|                         --------------------------------> +---------------+ |
|                                                           | Target Server | |
|                                                           | / Service     | |
|                                                           +---------------+ |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the precise mechanism of a Golden Ticket attack. What cryptographic material is required, and why does this attack compromise the entire Kerberos trust architecture?**

**Answer:**
A Golden Ticket attack is a catastrophic post-compromise persistence technique where an attacker forges a Kerberos Ticket Granting Ticket (TGT). The Kerberos authentication protocol relies heavily on a centralized Key Distribution Center (KDC), which in Active Directory is the Domain Controller. The KDC encrypts and signs all valid TGTs using the NTLM hash (or AES keys) of a specialized, hidden domain account called the `KRBTGT` account.

To execute this attack, the attacker must first compromise the domain and extract the password hash (NTLM, AES128, or AES256) of the `KRBTGT` account, typically via a DCSync attack or by extracting the NTDS.dit file from a DC.

Once the attacker possesses the KRBTGT hash, they possess the "master key" to the kingdom. They can use tools like Mimikatz, Rubeus, or Impacket's `ticketer.py` to cryptographically forge TGTs completely offline. This compromises the entire Kerberos trust architecture because the KDC inherently trusts any TGT that is validly encrypted and signed with its own KRBTGT key. The attacker can embed arbitrary identity information within the forged ticket's Privileged Attribute Certificate (PAC), claiming to be any user (even non-existent ones) and granting themselves membership in any group (like Domain Admins or Enterprise Admins).

**Q2: Dissect the anatomy of a forged Golden Ticket. Specifically, what fields within the Ticket Granting Ticket (TGT) and the Privileged Attribute Certificate (PAC) does the attacker manipulate to achieve persistence and lateral movement?**

**Answer:**
A forged Golden Ticket heavily manipulates the inner workings of Kerberos structures.

1. **User Identity (cname):** The attacker specifies the username they want to masquerade as. This can be a legitimate administrator (e.g., `Administrator`) or a completely fabricated username (e.g., `FakeAdmin`). The KDC generally does not verify if the user actually exists in AD when validating the TGT; it only verifies the cryptographic signature.
2. **Domain SID:** The Security Identifier of the target domain is embedded to ensure the ticket is valid for that specific environment.
3. **Privileged Attribute Certificate (PAC):** This is the most critical component. The PAC contains the authorization data. The attacker manipulates the PAC to include high-privileged SIDs. Specifically, they inject the SIDs for `Domain Admins` (RID 512), `Domain Controllers` (RID 516), `Enterprise Admins` (RID 519), and `Schema Admins` (RID 518) into the `GroupIds` and `ExtraSids` fields.
4. **Timestamps:** The attacker sets custom `AuthTime`, `StartTime`, `EndTime`, and `RenewTill` values. By default, standard TGTs expire in 10 hours. An attacker can set a Golden Ticket to be valid for 10 years (though modern AD implementations have introduced some mitigations regarding maximum ticket lifetimes).
5. **Signatures:** The PAC must be digitally signed to prevent tampering. In a Golden Ticket, both the PAC Server Signature and the PAC KDC Signature are generated by the attacker using the stolen KRBTGT key.

**Q3: How does the introduction of Credential Guard in Windows 10/11 impact the execution and usage of Golden Tickets on compromised endpoints?**

**Answer:**
Windows Defender Credential Guard utilizes virtualization-based security (VBS) to isolate the Local Security Authority (LSA) subsystem into a secure, hypervisor-protected container called LSAIso (Isolated LSA).

Credential Guard heavily impacts the *usage* of Golden Tickets on a local endpoint. Traditionally, an attacker would use Mimikatz's `kerberos::ptt` (Pass-the-Ticket) to inject the forged Golden Ticket directly into the LSA memory space of the compromised workstation, making it available for subsequent network authentication.

With Credential Guard enabled, the standard LSA process no longer holds Kerberos ticket-granting keys or plaintext tickets in accessible memory. It communicates with LSAIso via RPC. Because Mimikatz operates in the user/kernel space and cannot access the hypervisor-protected LSAIso memory, it cannot easily inject the forged ticket. The attacker must either disable Credential Guard (which requires a reboot and often physical/console access depending on UEFI locks) or execute the attack from an external, non-protected machine (like a Kali Linux C2 server) using tools like proxychains or Impacket to pass the ticket over the network without ever touching the victim's LSA.

## Scenario-Based Questions

**Q4: You are performing a Red Team engagement. You have successfully compromised the `KRBTGT` hash. You forge a Golden Ticket for the `Administrator` user and set the validity to 10 years. However, when you attempt to use the ticket to access a highly sensitive file server 30 days later, access is denied. What Active Directory mechanisms could have caused your Golden Ticket to fail, despite the 10-year expiration date?**

**Answer:**
If the Golden Ticket failed 30 days later, several mechanisms could be responsible:

1. **KRBTGT Password Reset:** This is the most common reason. If the Blue Team detected the breach or performed routine credential rotation, they may have reset the `KRBTGT` account password. Because the password history for the `KRBTGT` account is kept at 2, it must be reset *twice* to fully invalidate all previously issued (and forged) tickets. If the password was rotated twice, the KDC will reject the Golden Ticket because it is signed with a key the KDC no longer recognizes.
2. **User Account Disablement/Deletion:** Modern Domain Controllers (Windows Server 2012+) perform PAC validation during the TGS-REQ phase. When the forged TGT is presented to request a Service Ticket (TGS), the KDC checks if the user specified in the PAC (in this case, `Administrator`) is disabled, locked out, or deleted. If the Blue Team disabled the `Administrator` account, the KDC will refuse to issue the TGS, effectively neutralizing the Golden Ticket.
3. **Smart Card Required for Interactive Logon:** If the target account was recently configured with the "Smart card is required for interactive logon" attribute, the KDC expects the TGT to have specific flags indicating PKINIT was used. A standard forged Golden Ticket lacks these flags and will be rejected.
4. **Ticket Lifetime Policies:** While the attacker sets a 10-year expiration in the forged ticket, AD domain policies enforce maximum ticket lifetimes (Default: 10 hours for TGT, 7 days renewal). If the KDC strictly enforces policy checks against the forged timestamps, it may reject tickets that wildly exceed domain policies, depending on the OS version and specific patch levels.

**Q5: During an incident response, you suspect threat actors are utilizing Golden Tickets. The environment generates millions of Kerberos logs daily. You cannot simply look for "Domain Admin logins." What specific anomalies within Event ID 4769 (A Kerberos service ticket was requested) would you hunt for to definitively identify the use of a forged Golden Ticket?**

**Answer:**
Hunting for Golden Tickets requires deep analysis of Kerberos TGS-REQ logs (Event ID 4769). Since the attacker is using the TGT to request Service Tickets, the anomalies will manifest here.

1. **Non-Existent Usernames:** Attackers often forge tickets for users that don't exist in AD (e.g., `backdoor_admin`). Querying Event ID 4769 where the `TargetUserName` does not match any known, valid AD object is a massive red flag.
2. **Mismatched Account Domains:** If the forged ticket specifies a user but uses a NetBIOS domain name instead of a FQDN, or if the domain fields are inconsistent, it can indicate forgery by tools like Mimikatz which historically had hardcoded defaults or handled domains differently.
3. **Anomalous Ticket Encryption Types:** By default, modern AD environments utilize AES256 (Type 18) for Kerberos encryption. If an attacker extracts only the NTLM hash of the KRBTGT and forges a ticket, the resulting TGS request might utilize RC4 (Type 23). While RC4 is still seen, an RC4 ticket request for a highly privileged account in an otherwise AES-enforced environment is highly suspicious.
4. **Lifetime Anomalies:** Look for TGS requests where the ticket times (if logged or captured via PCAP) significantly violate the domain's maximum lifetime policies.
5. **No Corresponding Event ID 4768:** A legitimate TGS request (4769) is always preceded by a TGT request (4768) when the user initially authenticates. A forged Golden Ticket is created offline; therefore, there will be an influx of 4769 events for a user *without* any corresponding 4768 event originating from that same IP/source within the expected TGT lifetime window.

## Deep-Dive Defensive Questions

**Q6: To permanently eradicate a Golden Ticket threat after a domain compromise, the standard advice is to "reset the KRBTGT password twice." Architecturally, explain why it must be reset *twice*, and detail the operational risks and required delays associated with this process in a large, multi-site Active Directory forest.**

**Answer:**
The `KRBTGT` password must be reset twice due to how Active Directory handles Kerberos ticket decryption and password history.
Architecturally, the KDC retains the current `KRBTGT` password and the *previous* `KRBTGT` password. This is designed for high availability and fault tolerance. If the password is changed, legitimate TGTs issued just prior to the change (encrypted with the old key) will still be honored by the KDC for a grace period.
Therefore, if you reset the password only once, the attacker's Golden Ticket (signed with the original, now "previous" key) will still be accepted by the KDCs. By resetting it a second time, the original compromised key is pushed entirely out of the history, and any tickets signed with it are immediately rejected.

**Operational Risks and Delays:**
In a large, multi-site forest, resetting the KRBTGT password carries significant risk of breaking authentication.
When the password is reset on the Primary Domain Controller (PDC) Emulator, it must replicate to all other DCs globally. If you execute the second reset before the first reset has fully replicated to a remote site, the remote DCs might have an inconsistent view of the password history.
If replication is delayed, legitimate users at remote sites holding TGTs signed by the "first reset" key might attempt to request a TGS from a DC that only knows the "second reset" key, causing widespread authentication failures.

Therefore, the standard operating procedure mandates:
1. Reset the KRBTGT password once.
2. Wait for full AD replication to complete across all sites (verifying with `repadmin /replsummary`).
3. Wait for the standard Kerberos ticket lifetime to expire (typically 10 hours) to allow legitimate users to naturally request new TGTs.
4. Reset the KRBTGT password the second time.
5. Verify replication again.

**Q7: Explain the concept of "PAC Validation" (Privileged Attribute Certificate Validation) introduced in newer versions of Windows Server. How does it mitigate certain aspects of Golden Ticket attacks, and what are its limitations against a sophisticated adversary?**

**Answer:**
Historically, KDCs implicitly trusted the PAC within a TGT as long as the cryptographic signature (using the KRBTGT key) was valid. They did not verify if the user account actually still existed or if the group memberships claimed in the PAC were accurate.

PAC Validation (specifically when a TGT is used to request a TGS) introduced a mechanism where the KDC validates the identity information. When a TGS request is received, the KDC checks the user specified in the PAC against the Active Directory database to ensure the account is not disabled, locked out, deleted, or restricted by authentication policies.

**Mitigations:** It prevents an attacker from using a Golden Ticket crafted for a user account that the Blue Team has subsequently disabled or deleted in response to the breach.

**Limitations:** PAC Validation has severe limitations against a sophisticated attacker.
1. **Valid User Compromise:** If the attacker forges the ticket using a valid, active user account (e.g., a standard employee) but injects the Domain Admin SID into the PAC, PAC Validation will pass. The KDC checks if the user is active, but it does *not* query AD to verify if the user is *actually* a member of the groups claimed in the forged PAC. It trusts the cryptographically signed PAC for group membership.
2. **Service Ticket Forgery (Silver Tickets):** PAC Validation on the KDC does nothing to protect against Silver Tickets, where the attacker bypasses the KDC entirely and forges the Service Ticket directly for the target service, as the target server rarely has the capability or configuration to perform its own out-of-band PAC validation with the DC.

## Real-World Attack Scenario
During a long-term espionage campaign targeting a telecommunications provider, an APT group gained initial access via a zero-day in a perimeter VPN appliance. They stealthily escalated privileges over two months, eventually using a DCSync attack to dump the `KRBTGT` hash.
Anticipating discovery, the actors did not use their Domain Admin access to create new accounts or modify groups. Instead, they forged a Golden Ticket for a dormant, valid service account used by an obsolete backup system. They embedded Enterprise Admin SIDs within the PAC and set the ticket validity to 10 years.
When the incident response team finally detected the lateral movement, they initiated a massive password reset for all user and admin accounts but crucially failed to execute the double-reset procedure for the `KRBTGT` account.
The threat actors went silent during the remediation. Four months later, they returned via a low-privileged compromised vendor VPN. They injected their previously forged Golden Ticket into their session. Because the `KRBTGT` key had not been fully rotated out of history, the KDC accepted the ticket. The actors immediately regained full Enterprise Admin control, bypassing all newly implemented EDR and MFA controls, and successfully exfiltrated the core customer database.

## Chaining Opportunities
- **DCSync -> Golden Ticket:** The classic chain. Utilizing `DS-Replication-Get-Changes` to pull the KRBTGT hash, enabling the offline forging of the ticket.
- **Golden Ticket -> DCShadow:** Using the Golden Ticket to authenticate to the primary DC with Enterprise Admin privileges in order to register a rogue DC and establish deeper, database-level persistence.
- **Golden Ticket -> Silver Ticket:** Using the ultimate authority of the Golden Ticket to request service principal hashes, which can then be used to forge localized Silver Tickets for specific, high-value servers, reducing the footprint on the KDC logs.

## Related Notes
- [[70 - DCSync Attacks]]
- [[73 - Silver Tickets]]
- [[60 - Kerberos Authentication Deep Dive]]
- [[85 - Incident Response in Active Directory]]
