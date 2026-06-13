---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 68"
---

# QnA - AD Module 68: Pass the Ticket (PtT)

## Architecture Overview: Kerberos and Pass the Ticket

```text
+-------------------------------------------------------------+
|               Pass the Ticket (PtT) Architecture            |
+-------------------------------------------------------------+
| [Attacker Machine]                                          |
|  1. Harvest Ticket (Kirbi / Ccache file)                    |
|     (From LSASS memory, network interception, or forged)    |
|                                                             |
|  2. Inject Ticket into Memory (Rubeus / Mimikatz)           |
|     Rubeus.exe ptt /ticket:base64_ticket_data               |
|                                                             |
+-------------------------------------------------------------+
               |
               | (Kerberos TGS-REQ or AP-REQ)
               v
+-------------------------------------------------------------+
| [Active Directory / Target Service]                         |
|                                                             |
|  If injected ticket is a TGT:                               |
|  --> 3. Attacker requests TGS from KDC using stolen TGT     |
|  <-- 4. KDC grants TGS for target service                   |
|                                                             |
|  If injected ticket is a TGS (Service Ticket):              |
|  --> 3. Attacker sends AP-REQ directly to Target Service    |
|  <-- 4. Target Service decrypts TGS, grants access          |
+-------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: Differentiate between a Ticket Granting Ticket (TGT) and a Ticket Granting Service (TGS) ticket. How does Passing the Ticket apply to both?
**Answer:**
A **Ticket Granting Ticket (TGT)** is the master ticket issued by the Key Distribution Center (KDC) upon successful pre-authentication. It is encrypted with the `KRBTGT` account hash. It proves the user's identity and is used to request further access to specific services.
A **Ticket Granting Service (TGS)** ticket is a service-specific ticket (e.g., for CIFS, HTTP, WSMAN) issued by the KDC upon presentation of a valid TGT. It is encrypted with the target service account's hash.

**Passing the Ticket (PtT) Application:**
- **Passing a TGT:** An attacker extracts a user's TGT from memory and injects it. This allows the attacker to request TGS tickets for *any* service in the domain as that user. This provides broad, dynamic access but requires communication with the Domain Controller (KDC).
- **Passing a TGS:** An attacker extracts a specific TGS (e.g., `cifs/fileserver.corp.local`) and injects it. The attacker can only access that specific service on that specific machine. However, this attack is stealthier because it bypasses the KDC entirely—the attacker communicates directly with the target server.

### Q2: What formats do Kerberos tickets take when extracted by offensive tools, and how are they translated between Windows and Linux attacker environments?
**Answer:**
Kerberos tickets typically exist in two formats in the offensive security landscape:
1. **.kirbi (Kerberos Credential Manager):** This is the native format used by Windows LSASS and outputted by tools like Mimikatz and Rubeus. It is a binary format containing the ticket data, session keys, and metadata.
2. **.ccache (Credential Cache):** This is the native format used by Linux/Unix Kerberos implementations (MIT Kerberos). Tools like Impacket and evil-winrm on Linux natively consume `.ccache` files.

**Translation:**
If an attacker dumps a `.kirbi` file from a compromised Windows host but wants to use Impacket on their Kali Linux machine, they must convert the ticket. Tools like `ticketConverter.py` (part of Impacket) or Rubeus can translate `.kirbi` to `.ccache` and vice versa. On Linux, the attacker then exports the ticket into their environment variables (`export KRB5CCNAME=/path/to/ticket.ccache`) so that Impacket tools will inherently use the ticket for authentication instead of prompting for a password.

### Q3: Explain the fundamental difference between a Silver Ticket and a Golden Ticket in the context of Pass the Ticket.
**Answer:**
While both involve forging Kerberos tickets, they target different trust boundaries and require different cryptographic keys.
- **Golden Ticket (Forged TGT):** Requires the `KRBTGT` account NTLM hash (or AES keys). An attacker forges a TGT. Because the KDC trusts the `KRBTGT` hash, it accepts the forged TGT and will issue TGS tickets for *any* service in the entire domain. The forged ticket can have an arbitrary lifespan (e.g., 10 years) and grant Domain Admin privileges to a non-existent user.
- **Silver Ticket (Forged TGS):** Requires the NTLM hash (or AES keys) of a specific **Target Service Account** (e.g., a computer account hash for a file server, or a user account hash running SQL Server). The attacker forges a TGS ticket directly. They completely bypass the KDC and present the forged TGS directly to the target server. The target server decrypts it with its own hash, trusts the forged PAC (Privilege Attribute Certificate) within it, and grants access. A Silver Ticket only compromises the specific service/machine, not the entire domain.

---

## Scenario-Based Questions

### Scenario 1: You have successfully dumped a Domain Administrator's TGT from a compromised workstation. You inject it using `Rubeus ptt`, but when you try to access the Domain Controller's C$ share, you receive an "Access Denied" error. The ticket has not expired. What Kerberos protection mechanism is likely preventing your access?
**Answer:**
This is likely caused by **Kerberos Delegation restrictions**, specifically the **"Account is sensitive and cannot be delegated"** flag, or more commonly in modern environments, the presence of **Protected Users Security Group**.
If the Domain Administrator is part of the `Protected Users` group:
1. Their TGT lifespan is drastically reduced, and their tickets cannot be renewed.
2. Most importantly, Kerberos delegation is completely disabled for accounts in this group. 
However, if it's purely a PtT scenario and the ticket is completely valid, another potential issue is **Kerberos Armoring (FAST)** or the target machine strictly enforcing IP restrictions embedded in the TGT. When a TGT is generated, it *can* include the source IP address. While Windows ignores this by default, strict Kerberos policies might enforce IP binding, causing the KDC to reject TGS requests from the attacker's IP address.
Additionally, check if the TGT was exported from a high-integrity LSASS session and injected into a medium-integrity attacker shell, which might prevent seamless network traversal.

### Scenario 2: You are operating on a Kali Linux machine. You extracted a Service Account's NTLM hash and want to create a Silver Ticket to access a MSSQL database (`MSSQLSvc/db01.corp.local`). How do you forge this ticket natively on Linux and execute queries against the DB?
**Answer:**
1. **Forge the Silver Ticket:** I would use Impacket's `ticketer.py`. I need the Service Account's NTLM hash, the domain SID, the target SPN, and the user I want to impersonate (e.g., Administrator).
   ```bash
   ticketer.py -nthash <Service_NTLM_Hash> -domain-sid <Domain_SID> -domain corp.local -spn MSSQLSvc/db01.corp.local Administrator
   ```
   This generates an `Administrator.ccache` file.
2. **Set the Environment Variable:** Instruct the Linux OS to use this specific Kerberos cache.
   ```bash
   export KRB5CCNAME=/path/to/Administrator.ccache
   ```
3. **Execute Queries:** Use Impacket's `mssqlclient.py` with the `-k` (use Kerberos) and `-no-pass` flags.
   ```bash
   mssqlclient.py Administrator@db01.corp.local -k -no-pass
   ```
   The tool will automatically pull the forged Silver Ticket from the environment variable and present it to the MSSQL service, granting DBA access.

### Scenario 3: During an engagement, you execute `Rubeus.exe triage` and notice multiple TGTs for highly privileged users. However, the EDR aggressively blocks `sekurlsa::pth` and detects any attempts to inject tickets directly into LSASS. How can you utilize these tickets without injecting them into the local machine's memory?
**Answer:**
To avoid touching LSASS memory (which triggers immediate EDR alerts like Credential Access / API hooking on `LsaRegisterLogonProcess`), I would leverage **Over-the-Pass-the-Hash** locally or execute tools completely externally.
However, for pure PtT without LSASS injection:
1. **Rubeus `/create netonly`:** Rubeus can spawn a hidden process (like `cmd.exe`) using the `CreateProcessWithLogonW` API (creating a Logon Type 9 session) and apply the ticket *only* to that specific new logon session's credential cache, rather than injecting it into the global LSASS pool. 
   ```cmd
   Rubeus.exe createnetonly /program:"C:\windows\system32\cmd.exe"
   Rubeus.exe ptt /luid:<LUID_of_new_process> /ticket:base64_ticket
   ```
2. **Exfiltration to Attacker Infrastructure:** Export the tickets to base64 (`Rubeus.exe dump /nowrap`), exfiltrate them via standard C2 channels, convert them to `.ccache`, and perform the lateral movement from an attacker-controlled Linux machine (e.g., pivoting through a SOCKS proxy). This keeps all offensive Kerberos telemetry off the EDR-monitored endpoint.

---

## Deep-Dive Defensive Questions

### Q1: How can a SOC reliably differentiate between a legitimate Kerberos authentication event and a Pass the Ticket attack in the Windows Event Logs?
**Answer:**
Detecting pure PtT (where a valid, stolen ticket is reused) is exceptionally difficult because the cryptographic material is valid. However, behavioral anomalies exist:
1. **Event ID 4624 (Logon):** Look for Logon Type 3 (Network) using Kerberos. 
2. **Source IP Mismatch:** The most reliable indicator. If a user's TGT was issued (Event ID 4768) to Workstation A (IP: 10.0.0.5), but subsequent TGS requests (Event ID 4769) or Network Logons using that ticket originate from Workstation B (IP: 10.0.0.99), it is highly indicative of a stolen ticket being passed.
3. **Event ID 4769 (Kerberos Service Ticket Requested):** If an attacker passes a TGT, they will request TGS tickets. Anomalous requests (e.g., a standard HR user suddenly requesting a TGS for `cifs/DomainController`) stand out.
4. **Encryption Downgrades:** If attackers forge tickets (Golden/Silver) using weak encryption (RC4, Ticket Encryption Type `0x17`) while the domain enforces AES-256 (`0x12`), Event ID 4769 will flag the anomalous downgrade.

### Q2: Detail the mechanics of the Privilege Attribute Certificate (PAC) and how PAC Validation mitigates forged Silver Tickets.
**Answer:**
The **PAC (Privilege Attribute Certificate)** is an extension within a Kerberos ticket that contains the user's authorization data (User SID, Group SIDs, User Account Control flags). 
When an attacker creates a Silver Ticket, they forge the PAC to include high-privileged SIDs (like Domain Admins). Because the attacker has the Service Account's hash, they encrypt the ticket properly, and the target service trusts it.
**PAC Validation:**
To mitigate this, Microsoft implemented PAC Validation. When a service receives a TGS, instead of blindly trusting the PAC contained within it, the service securely forwards the PAC signature to the Domain Controller via a Netlogon RPC call (Event ID 4769 on the DC). The DC verifies the PAC signature using the `KRBTGT` key. Since the attacker does not have the `KRBTGT` key (only the service account key), they cannot forge a valid KDC signature on the PAC. The DC returns a failure, and the target service denies access.

### Q3: What is Kerberos Armoring (FAST) and how does it protect against offline ticket cracking and ticket harvesting?
**Answer:**
**Flexible Authentication Secure Tunneling (FAST)**, or Kerberos Armoring, establishes a secure, encrypted tunnel between the client and the KDC before any actual credential material is exchanged.
1. **Protection Mechanism:** The client machine first uses its own Computer Account credentials to establish an encrypted channel with the KDC. All subsequent Kerberos requests (AS-REQ for the user's TGT, TGS-REQ) are wrapped inside this armored tunnel.
2. **Mitigating Offline Cracking (AS-REP Roasting):** Because the pre-authentication data is encrypted inside the FAST tunnel, attackers cannot sniff the network to capture AS-REP hashes.
3. **Mitigating Harvesting:** It enforces constraints on how and where tickets are delivered, making Man-in-the-Middle (MitM) ticket harvesting impossible, as the attacker lacks the machine's computer account key required to decrypt the outer FAST tunnel.

---

## Real-World Attack Scenario
**Bypassing EDR with External PtT:**
A Red Team compromised a developer's workstation. The EDR solution immediately killed Mimikatz and flagged any anomalous local process memory access. The team deployed a custom, unmanaged PowerShell script utilizing native Windows APIs (`LsaCallAuthenticationPackage`) to silently query the Kerberos ticket cache. 
They discovered a valid TGT for a backup service account. Instead of injecting it locally, they base64-encoded the `.kirbi` file and exfiltrated it over DNS. On their external C2 infrastructure, they converted the ticket to `.ccache`. 
They established a reverse SOCKS proxy through the compromised developer workstation. Configuring their local ProxyChains and `KRB5CCNAME` environment variable, they ran `wmiexec.py` through the proxy directly against the Domain Controller. The external attacker machine negotiated the Kerberos authentication natively, passed the ticket through the SOCKS tunnel, and obtained a SYSTEM shell on the DC without generating a single suspicious process execution or memory injection alert on the developer's workstation.

---

## Chaining Opportunities
- **Overpass the Hash:** If an attacker cannot find a TGT but has an NTLM hash, they will perform [[AD QnA - Module 69 - Overpass the Hash]] to generate a valid TGT, which is then used in a PtT attack.
- **Kerberoasting / AS-REP Roasting:** Passing the ticket grants authenticated access to the domain, enabling attackers to query LDAP and execute SPN discovery for Kerberoasting.
- **Silver/Golden Tickets:** PtT is the execution mechanism for forged tickets. Once a Silver Ticket is forged, PtT is used to present it to the target service.

---

## Related Notes
- [[Kerberos Authentication Deep Dive]]
- [[Golden and Silver Ticket Forgery]]
- [[Rubeus Tool Usage Guide]]
- [[Kerberos PAC Architecture]]
- [[Active Directory Persistence Mechanisms]]
