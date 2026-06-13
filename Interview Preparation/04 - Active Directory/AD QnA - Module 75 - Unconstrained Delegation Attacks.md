---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 75"
---

# Active Directory Security Interview QnA: Unconstrained Delegation Attacks

## ASCII Diagram: Unconstrained Delegation Attack Flow

```text
+-----------------------------------------------------------------------------+
|                                                                             |
| +-------------------+ (1) Admin authenticates to Server  +----------------+ |
| |                   | ---------------------------------> |                | |
| | Domain Admin      |                                    | Compromised    | |
| | (Target Victim)   | (2) KDC sends TGT inside TGS       | Server         | |
| +-------------------+                                    | (Unconstrained)| |
|                                                          +----------------+ |
|                                                                   |         |
|                              (3) Attacker extracts TGT from memory|         |
|                              (Mimikatz: sekurlsa::tickets /export)v         |
| +-------------------+                                    +----------------+ |
| |                   | <--------------------------------- |                | |
| | Attacker Machine  |                                    | Attacker C2    | |
| | (DA Privileges)   | (4) Pass-The-Ticket (PtT)          | Session        | |
| +-------------------+ ---------------------------------> |                | |
|         |             (5) Access ANY resource as DA      +----------------+ |
|         v                                                                   |
| +-------------------+                                                       |
| |                   |                                                       |
| | Domain Controller |                                                       |
| +-------------------+                                                       |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Define Unconstrained Delegation in Active Directory. From a Kerberos protocol perspective, explain exactly what happens when a user authenticates to a server configured with Unconstrained Delegation.**

**Answer:**
Unconstrained Delegation is a legacy Active Directory configuration designed to solve the "double-hop" problem, where a front-end server needs to access a back-end resource (like a database) on behalf of a user.
When a server is configured with Unconstrained Delegation (the "Trust this computer for delegation to any service" option in ADUC), the Domain Controller places immense trust in that server.

From a Kerberos perspective, when a user authenticates to a server configured with Unconstrained Delegation, the KDC does something highly dangerous: it embeds a copy of the user's Ticket Granting Ticket (TGT), along with the session key, directly inside the Service Ticket (TGS) it issues for the connection.
When the user connects, this TGT is cached in the Local Security Authority (LSA) memory of the delegated server. The intent is that the server can extract this TGT and use it to request *new* Service Tickets to *any* other service in the domain on behalf of that user.

**Q2: Why is Unconstrained Delegation considered a massive security risk, and what is the primary attack vector an adversary will exploit upon discovering such a server?**

**Answer:**
The security risk is catastrophic because the delegated server effectively caches the master authentication token (the TGT) of anyone who connects to it.
If an attacker compromises a server configured with Unconstrained Delegation (by gaining local Administrator or SYSTEM privileges), they gain access to its LSA memory space.

The primary attack vector is credential theft and impersonation. The attacker uses tools like Mimikatz (specifically the `sekurlsa::tickets /export` command) or Rubeus to dump all Kerberos tickets cached in memory. If a Domain Admin or a highly privileged service account recently authenticated to that server (e.g., via RDP, SMB, WMI, or even HTTP), their TGT will be present in the dump.

The attacker extracts this TGT and performs a Pass-the-Ticket (PtT) attack. By injecting the DA's TGT into their own session, the attacker instantly assumes the identity and privileges of the Domain Admin across the entire domain, allowing them to compromise the Domain Controllers and the rest of the forest.

**Q3: Discuss the "Printer Bug" (Spooler Service abuse) and how it is weaponized in conjunction with Unconstrained Delegation to achieve a rapid domain compromise.**

**Answer:**
The "Printer Bug" (or similar coercion techniques like PetitPotam) revolutionized Unconstrained Delegation attacks.
Historically, an attacker had to patiently wait on a compromised Unconstrained Delegation server for a highly privileged user to naturally authenticate to it.
Coercion techniques remove the wait time. The Spooler service (`MS-RPRN` RPC interface) has a function called `RpcRemoteFindFirstPrinterChangeNotificationEx`. An attacker can send an RPC call to a target machine (like a Domain Controller), instructing it to send an authentication request back to a machine specified by the attacker.

**The Weaponized Chain:**
1. The attacker compromises a server configured with Unconstrained Delegation (e.g., `APP-SRV`).
2. The attacker uses a tool (like `SpoolSample.exe` or `dementor.py`) to trigger the Printer Bug against a Domain Controller (`DC01`), telling it to authenticate to `APP-SRV`.
3. The Domain Controller's machine account (`DC01$`) authenticates to `APP-SRV`. Because `APP-SRV` has Unconstrained Delegation, the DC leaves a copy of its own TGT in `APP-SRV`'s memory.
4. The attacker extracts the TGT for `DC01$`.
5. Using the `DC01$` TGT, the attacker executes a DCSync attack, directly pulling the `KRBTGT` hash or any other password hash from the domain. The entire domain is compromised in seconds.

## Scenario-Based Questions

**Q4: You are performing an internal network penetration test. You run BloodHound and identify a server, `SQL-LEGACY-01`, configured with Unconstrained Delegation. You manage to exploit a web application vulnerability on this server and gain a local SYSTEM shell. However, the environment is highly inactive, and no administrators log into this box. You attempt the Printer Bug against the Domain Controller, but the Print Spooler service is disabled on all DCs. Detail an alternative, modern coercion technique you would use to force a privileged authentication to your compromised server.**

**Answer:**
If the Spooler service is disabled, the Printer Bug is mitigated. I must pivot to alternative MS-RPC coercion methods.
The most prominent and reliable modern alternative is **PetitPotam** (abusing the Encrypting File System Remote Protocol, MS-EFSR).

1. From my attacker infrastructure (or directly from the compromised `SQL-LEGACY-01` if tools are present), I will utilize the PetitPotam exploit script.
2. The MS-EFSR protocol contains functions like `EfsRpcOpenFileRaw`. I will send a crafted RPC request utilizing this interface to the target Domain Controller.
3. The payload forces the Domain Controller's machine account to attempt an SMB/RPC authentication back to the IP address I specify—in this case, the IP of my compromised `SQL-LEGACY-01` server.
4. When the DC connects to `SQL-LEGACY-01`, because of the Unconstrained Delegation setting, the DC deposits its TGT into the LSA memory.
5. I will then use Rubeus (`Rubeus.exe triage` followed by `Rubeus.exe dump /luid:...`) to extract the `DC01$` TGT and proceed with a DCSync attack.

Other alternatives include ShadowCoerce (MS-FSRVP) or DFSCoerce (MS-DFSNM), depending on which RPC endpoints are exposed and enabled on the DC.

**Q5: During an incident response engagement, you identify that an attacker compromised a web server with Unconstrained Delegation. You find evidence of Mimikatz execution and suspect TGT extraction. You analyze the Domain Controller Kerberos logs (Event ID 4768 and 4769). What specific anomaly will indicate that the attacker is successfully using a stolen TGT via a Pass-the-Ticket attack, rather than a legitimate administrator logging in?**

**Answer:**
Detecting the *extraction* of the TGT is difficult on the DC side, but detecting the *usage* (Pass-the-Ticket) of the stolen TGT is highly viable through Kerberos log analysis.

When a legitimate administrator logs in, the standard flow is:
- **Event 4768 (TGT Request):** Originates from the Administrator's workstation IP address.
- **Event 4769 (TGS Request):** Originates from the Administrator's workstation IP address shortly after the TGT request.

When an attacker performs a Pass-the-Ticket attack using a stolen TGT:
1. The attacker does not need to request a new TGT. They inject the stolen one into their session on their attacking machine (or the compromised web server).
2. The attacker immediately uses the TGT to request Service Tickets.

**The Anomaly:**
You will see a surge of **Event ID 4769 (TGS Requests)** for a highly privileged account (e.g., Domain Admin) originating from the IP address of the compromised server (or the attacker's pivot box).
Crucially, if you look backward in time for the Kerberos ticket lifetime (usually 10 hours), you will find **no corresponding Event ID 4768 (TGT Request)** for that user originating from that specific IP address. The presence of TGS requests without a matching, logically preceding TGT request from the same source IP is the definitive signature of Pass-the-Ticket utilizing a stolen TGT.

## Deep-Dive Defensive Questions

**Q6: From an Active Directory architecture perspective, how do you completely eliminate the risk of Unconstrained Delegation attacks while maintaining necessary application functionality? Describe the migration path and the specific AD features utilized.**

**Answer:**
The only way to eliminate the risk is to remove Unconstrained Delegation entirely from the environment.
The migration path involves moving services to more secure delegation models:

1. **Identify Unconstrained Assets:** Use PowerShell (`Get-ADComputer -Filter {TrustedForDelegation -eq $true}`) to find all servers with Unconstrained Delegation.
2. **Application Analysis:** Work with application owners to understand *why* delegation is needed. Often, it was turned on by default or lazily configured, and the app doesn't actually require it.
3. **Migrate to Constrained Delegation (Kerberos Only):** If delegation is required, configure Constrained Delegation. This restricts the server to only impersonate users to a specific, predefined list of target services (SPNs). It does *not* cache the user's TGT.
4. **Migrate to Resource-Based Constrained Delegation (RBCD):** For modern architectures, especially across forest trusts, implement RBCD. As discussed previously, this places the control on the target resource rather than the front-end server, providing better isolation.
5. **Disable Unconstrained Delegation:** Once migrated, uncheck "Trust this computer for delegation to any service" on the AD object.

**The Ultimate Failsafe (Protected Users / Account is Sensitive):**
Regardless of the delegation type used, all highly privileged accounts (DA, EA, core service accounts) must be placed in the `Protected Users` security group, or have the "Account is sensitive and cannot be delegated" attribute checked. If a DA accidentally RDPs into a server that still has Unconstrained Delegation enabled, the KDC will explicitly refuse to embed the TGT in the Service Ticket, neutralizing the credential theft vector instantly.

**Q7: Explain how the implementation of Windows Defender Credential Guard impacts an attacker's ability to extract TGTs from a server configured with Unconstrained Delegation. Does it neutralize the attack completely?**

**Answer:**
Windows Defender Credential Guard utilizes Virtualization-Based Security (VBS) to isolate secrets. It moves the storage of Kerberos tickets and NTLM hashes out of the standard Local Security Authority (LSA) process (`lsass.exe`) and into a hypervisor-protected container called LSAIso (Isolated LSA).

**Impact on Attackers:**
Credential Guard severely impacts the attack. If a server configured with Unconstrained Delegation has Credential Guard enabled, when a user authenticates, the TGT is cached inside the protected LSAIso memory space, not the standard LSA.
When an attacker gains SYSTEM privileges and runs Mimikatz (`sekurlsa::tickets`), Mimikatz attempts to read the standard LSA memory. Because it cannot penetrate the hypervisor boundary into LSAIso, it will fail to extract the plaintext TGT. The core extraction phase of the Unconstrained Delegation attack is blocked.

**Does it neutralize it completely?**
It makes it significantly harder, but not entirely impossible for a highly sophisticated adversary.
1. **Downgrade Attacks:** If the attacker can gain persistent access, they might attempt to disable Credential Guard (modifying registry keys, UEFI variables) and force a reboot. If successful, subsequent logins will cache tickets in standard LSA.
2. **Custom SSPs/APCs:** Advanced attackers might attempt to inject custom Security Support Providers (SSPs) or use Asynchronous Procedure Calls (APCs) to intercept authentication material before it reaches LSAIso, though this is complex and highly monitored.

However, practically speaking, Credential Guard effectively neutralizes the automated, rapid-extraction techniques used by most commodity malware and standard penetration testing frameworks, breaking the easy attack chain.

## Real-World Attack Scenario

During an incident involving a logistics company, threat actors gained initial access via a phishing email containing a malicious macro, giving them a foothold on a standard user's laptop.
The actors used a lightweight LDAP query tool and quickly identified an old IIS web server (`WEB-INT-02`) configured with Unconstrained Delegation. They used an unpatched privilege escalation vulnerability (PrintNightmare) to gain local SYSTEM access on the web server.

Knowing that waiting for a Domain Admin to log into an intranet web server could take months, the attackers utilized the MS-DFSNM coercion technique (DFSCoerce). They sent a crafted RPC request from the compromised web server to the primary Domain Controller, forcing the DC's machine account to authenticate back to the web server over SMB.
Because of the Unconstrained Delegation configuration, the DC's TGT was deposited into the web server's memory. The attackers immediately ran Rubeus, extracted the TGT for `DC01$`, applied it to their session, and executed a DCSync attack. Within 45 minutes of the initial phishing click, they had extracted the NTDS.dit hashes of all 15,000 employees and administrators, leading to full forest compromise.

## Chaining Opportunities
- **Coercion (PetitPotam/PrinterBug) -> Unconstrained Delegation:** The most common chain. Forcing a high-privileged account (like a DC) to authenticate to the compromised delegated server to force the caching of a powerful TGT.
- **Unconstrained Delegation -> DCSync:** Using the extracted TGT of a Domain Controller to natively request replication data from other DCs, dumping the entire credential database.
- **Unconstrained Delegation -> Pass-the-Ticket (PtT):** Extracting user TGTs to access disparate systems across the domain seamlessly without needing to crack passwords or pass hashes.

## Related Notes
- [[74 - Resource-Based Constrained Delegation RBCD]]
- [[82 - MS-RPC Coercion Techniques]]
- [[70 - DCSync Attacks]]
- [[60 - Kerberos Authentication Deep Dive]]
