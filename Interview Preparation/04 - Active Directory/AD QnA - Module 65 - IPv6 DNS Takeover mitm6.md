---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 65"
---

# Expert Active Directory Q&A: IPv6 DNS Takeover mitm6

```text
+-------------------+       DHCPv6 Solicit       +-------------------+
|                   | -------------------------> |                   |
|   Victim Windows  |                            |   Attacker Node   |
|     Workstation   | <------------------------- |      (mitm6)      |
|                   |       DHCPv6 Reply         |                   |
+-------------------+      (Spoofed DNS IP)      +-------------------+
         |
         | IPv6 DNS Query for WPAD
         +--------------------------------------->
                                                 | Spoofed DNS Response
                                                 v
                                        +-------------------+
                                        |   Attacker Node   |  (Captures/Relays Auth)
                                        |   (ntlmrelayx)    | -------------------------> Domain Controller
                                        +-------------------+
```

## Formal Technical Questions

### Q1: Explain the default behavior of IPv6 and DHCPv6 in modern Windows Active Directory environments and why it introduces a critical vulnerability.
**Expert Answer:**
By default, all modern Windows operating systems (since Windows Vista/7) have IPv6 enabled and prefer IPv6 over IPv4. 
In a typical enterprise environment, network administrators heavily configure and secure the IPv4 infrastructure (DHCP snooping, ARP inspection), but completely ignore IPv6 because they don't actively route it. 
When a Windows machine boots, it broadcasts a DHCPv6 Solicit message looking for an IPv6 configuration. Since there is usually no legitimate IPv6 DHCP server on the corporate network, an attacker running `mitm6` can respond to this broadcast. The attacker assigns the victim an IPv6 address and, crucially, sets the attacker's own IP as the primary IPv6 DNS server. Because Windows prefers IPv6, it will route all subsequent DNS queries through the attacker, achieving a silent, unauthenticated DNS takeover on the local subnet.

### Q2: Discuss the role of WPAD (Web Proxy Auto-Discovery) in network evasion and how it is weaponized in conjunction with mitm6.
**Expert Answer:**
WPAD is a protocol used by Windows and browsers to automatically discover a proxy configuration file (`wpad.dat`). By default, Windows periodically sends out DNS queries searching for the hostname `wpad` or `wpad.domain.local`.
Once `mitm6` has hijacked the victim's IPv6 DNS, it listens for these specific `wpad` DNS queries. When the victim asks, "What is the IP of WPAD?", `mitm6` responds with the attacker's IPv6 address.
The victim's machine then connects to the attacker (usually on port 80) asking for the `wpad.dat` file. The attacker, using a tool like `ntlmrelayx` or `Responder`, replies with an HTTP `407 Proxy Authentication Required` challenge. The victim machine automatically responds with the user's NTLMv2 password hash to authenticate. The attacker captures this hash or relays it to another server.

### Q3: Contrast NTLM relaying over IPv4 versus IPv6. Why does mitm6 often succeed where Responder and LLMNR/NBT-NS poisoning fail?
**Expert Answer:**
LLMNR and NBT-NS poisoning (via Responder) rely on broadcast name resolution. They only trigger when a DNS query fails (e.g., a user mistypes a server name). Furthermore, most mature organizations have disabled LLMNR and NBT-NS via Group Policy, rendering Responder largely ineffective.
`mitm6` does not rely on broadcast failures. It hijacks the primary DNS architecture itself over IPv6. Every single DNS query the machine makes routes through the attacker. When the attacker spoofs WPAD, they don't have to wait for a user to make a mistake; Windows natively searches for WPAD in the background automatically. This makes `mitm6` highly reliable and capable of bypassing standard IPv4 network defenses.

## Scenario-Based Questions

### Q4: You are on a Red Team engagement deployed on a segmented VLAN. You launch mitm6, but you are not capturing any credentials. What are the common environmental factors that break mitm6, and how do you troubleshoot?
**Expert Answer:**
If `mitm6` fails to yield results, several factors could be at play:
1. **Network Segmentation/Switch Port Security:** Enterprise switches might have DHCPv6 Guard enabled, dropping rogue DHCPv6 replies before they reach the victim.
2. **Legitimate IPv6 Infrastructure:** If the organization *does* use IPv6, a legitimate DHCPv6 server might be responding faster than my attacker machine, or the victims are already configured.
3. **Disabled WPAD:** The organization may have disabled WPAD via GPO or disabled the "WinHttpAutoProxySvc" service, preventing the automated HTTP authentication requests.
**Troubleshooting:** I would run `Wireshark` or `tcpdump` to observe the DHCPv6 Solicit/Reply traffic. If my replies aren't reaching the victim, the switch is blocking them. If they are reaching the victim, but I'm not getting HTTP traffic, WPAD is likely disabled, and I must spoof other heavily trafficked internal hostnames instead of WPAD.

### Q5: You have successfully used mitm6 to hijack the DNS of a high-privilege IT Administrator's workstation. You want to escalate to Domain Admin. Walk through the cross-protocol relay attack path utilizing LDAPS.
**Expert Answer:**
Capturing the hash is good, but relaying is better. I will combine `mitm6` with `ntlmrelayx`.
1. **Setup:** I run `mitm6 -d domain.local`. This poisons the DNS and forces WPAD traffic to me.
2. **Relay Configuration:** I run `ntlmrelayx -6 -t ldaps://domain_controller -wh wpad.domain.local -l lootdir`. The `-6` enables IPv6 support, and `-wh` specifies the WPAD hostname to ensure the HTTP authentication prompts properly.
3. **Execution:** The admin's machine queries WPAD, connects to my HTTP server, and sends its NTLM auth.
4. **LDAPS Pivot:** `ntlmrelayx` intercepts the NTLM auth and relays it to the Domain Controller over LDAPS (port 636). Because I used LDAPS, the connection is encrypted, bypassing LDAP signing restrictions (though LDAP Channel Binding might still block it).
5. **Exploitation:** With the IT Admin's context relayed to the DC, `ntlmrelayx` can dump the Active Directory structure, or, more lethally, I can instruct it to create a new Domain Admin account or assign `DCSync` rights to a user I control.

### Q6: During execution, you notice that while mitm6 is running, internet access and internal network connectivity for the victims are severely degraded or dropping entirely. Why is this happening, and how do you fix your OPSEC?
**Expert Answer:**
This is a classic OPSEC failure with `mitm6`. If I hijack the primary DNS for a workstation, I am responsible for resolving *all* of its DNS queries, not just WPAD.
By default, `mitm6` attempts to selectively spoof WPAD and ignore other requests, but if the network relies heavily on external lookups, the IPv6 DNS sinkhole can cause timeouts, breaking the victim's connectivity and alerting the Blue Team.
**Correction:** To maintain stealth, I must ensure my attacker machine is acting as a proper upstream DNS forwarder. I would configure `mitm6` (or a supplementary DNS tool) to forward all non-targeted DNS queries (e.g., `google.com`, `office.com`) back to the legitimate internal IPv4 DNS servers. This ensures the victim's internet and local network access remain seamless, keeping the attack invisible.

## Deep-Dive Defensive Questions

### Q7: How can Network Engineers mitigate the mitm6 vector at the switch and routing layer, rather than relying on endpoint configuration?
**Expert Answer:**
Relying on endpoint configuration is difficult at scale. Network-level controls are highly effective:
1. **DHCPv6 Guard (RFC 7113):** This is the IPv6 equivalent of IPv4 DHCP Snooping. When enabled on enterprise switches, the switch drops DHCPv6 Reply messages originating from untrusted ports (e.g., user workstations). Only designated ports connected to legitimate infrastructure routers are allowed to send DHCPv6 configurations.
2. **RA Guard (Router Advertisement Guard):** Similar to DHCPv6 Guard, it blocks malicious ICMPv6 Router Advertisement messages from untrusted ports, preventing attackers from re-routing traffic at the network layer.
3. **VLAN ACLs (VACLs):** If the organization fundamentally does not use IPv6, implementing ACLs at the switch layer to drop all IPv6 traffic (EtherType 0x86DD) completely neutralizes the attack surface.

### Q8: What specific behaviors and logs should the SOC monitor to detect an ongoing mitm6 and WPAD spoofing attack?
**Expert Answer:**
Detecting `mitm6` requires correlating network and endpoint logs:
- **Network Traffic Analysis:** NDR (Network Detection and Response) tools should trigger alerts on anomalous spikes in DHCPv6 traffic or new IPv6 DNS servers appearing on a segment that historically only uses IPv4.
- **Endpoint Event Logs (Sysmon):** Monitor for anomalous DNS queries. If Sysmon Event ID 22 (DNS Query) shows internal machines suddenly querying the IPv6 address of an unknown machine for `wpad.domain.local`, it is a critical indicator.
- **Proxy Authentication Anomalies:** Monitor firewall and proxy logs for mass HTTP `407 Proxy Authentication Required` responses originating from an internal client IP, rather than the legitimate corporate proxy.
- **Relay Detection:** Correlate Event ID 4624 Type 3 logons where the source IP is an IPv6 address that does not map to the legitimate hostname of the authenticating user.

### Q9: Discuss the process of comprehensively auditing and disabling IPv6 and WPAD enterprise-wide via Group Policy, and the potential operational risks involved.
**Expert Answer:**
To eradicate this attack vector architecturally:
1. **Disabling WPAD:** Create a GPO setting the registry key `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\WpadOverride` to `1` to disable proxy auto-discovery. Ensure the WPAD DNS record is legitimately registered to a sinkhole IP so it cannot be hijacked.
2. **Disabling IPv6:** Microsoft technically advises against disabling IPv6, as certain internal OS components rely on it. However, in high-security environments, it can be disabled via a GPO modifying the registry key: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters\DisabledComponents` set to `0xFF`.
**Risks:** Disabling WPAD will break internet access for roaming laptops if they rely on it when off-network. Disabling IPv6 can occasionally break features like DirectAccess or specific Microsoft clustering services. A phased rollout and thorough testing in a staging environment are mandatory before enterprise-wide deployment.

## Real-World Attack Scenario
During a Black Box penetration test, the Red Team lacked valid domain credentials and could not perform standard enumeration. LLMNR poisoning yielded zero results due to strict GPOs. The team deployed `mitm6` on the IT sub-vlan. Within 10 minutes, several helpdesk workstations broadcasted DHCPv6 requests. `mitm6` hijacked their DNS. When the workstations attempted to locate the proxy via WPAD, the attacker's `ntlmrelayx` served a 407 challenge. The HTTP NTLM authentication was relayed to the primary Domain Controller over LDAPS. A helpdesk user, who happened to have `Account Operator` privileges, unknowingly created a new Domain Admin account via the relayed LDAP connection. The Red Team moved from zero access to Domain Admin in under 20 minutes without ever cracking a hash.

## Chaining Opportunities
- **mitm6 + SMB Relaying to AD CS:** Hijacking IPv6 to coerce HTTP authentication, then relaying it to the Active Directory Certificate Services (AD CS) endpoint to generate certificates for domain persistence.
- **mitm6 + C2 Deployment:** Spoofing internal update servers via IPv6 DNS to deliver malicious payloads or C2 beacons directly to workstations expecting legitimate software updates.
- **mitm6 + Pass-the-Hash:** If relaying is blocked by LDAP signing and EPA, the attacker can simply downgrade the captured WPAD authentication to NTLMv1, crack it via rainbow tables, and utilize Pass-the-Hash to gain network access.

## Related Notes
- [[01 - Active Directory Basics]]
- [[64 - SMB Relaying]]
- [[Responder and Broadcast Protocols]]
- [[Active Directory Certificate Services (AD CS) Attacks]]
- [[Defensive Security - Active Directory Hardening]]
