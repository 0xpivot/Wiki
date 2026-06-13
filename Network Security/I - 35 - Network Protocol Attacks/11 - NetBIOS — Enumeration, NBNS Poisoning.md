---
tags: [netbios, nbns, poisoning, spoofing, network, responder]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.11 NetBIOS"
---

# NetBIOS and LLMNR Poisoning Attacks

Network Basic Input/Output System (NetBIOS) and Link-Local Multicast Name Resolution (LLMNR) are legacy, broadcast-based name resolution protocols in Windows environments. They act as fallbacks when Domain Name System (DNS) fails to resolve a hostname. While designed to improve user experience on local networks, these protocols are inherently insecure and form the foundation for some of the most reliable and devastating attacks in Active Directory penetration testing.

## Protocol Mechanics and The Flaw

When a Windows user attempts to access a network resource (e.g., `\\FILESERVER01\Share`), the system goes through a hierarchy of resolution steps to find the IP address of `FILESERVER01`:
1. Check the local `hosts` file.
2. Query the local DNS cache.
3. Query the configured DNS server.
4. **Fallback 1: LLMNR (Link-Local Multicast Name Resolution)** - UDP 5355.
5. **Fallback 2: NBT-NS (NetBIOS Name Service)** - UDP 137.

If the user makes a typo (e.g., `\\FILESRV01` instead of `\\FILESERVER01`), DNS will fail. The system will then broadcast an LLMNR and NetBIOS query to the entire local subnet, essentially yelling, *"Hey everyone, does anyone know the IP address for FILESRV01?"*

### The Vulnerability: Lack of Authentication
Neither LLMNR nor NBT-NS possesses any mechanism to verify the identity of the host answering the broadcast. Any machine on the network can respond to the broadcast and say, *"Yes, I am FILESRV01, here is my IP address."*

---

## The Attack Flow: Spoofing and Poisoning

```ascii
+--------------------+                                      +--------------------+
|   Victim (Alice)   |                                      |  Attacker (Kali)   |
|   IP: 10.10.10.5   |                                      |  IP: 10.10.10.99   |
+--------------------+                                      +--------------------+
          |                                                            |
          | 1. User types \\PRNTER01 (typo)                            |
          | 2. DNS query fails (NXDOMAIN)                              |
          |                                                            |
          | 3. LLMNR Broadcast: "Who is PRNTER01?"                     |
          |----------------------------------------------------------->|
          |                                                            |
          | 4. Attacker replies: "I am PRNTER01! I am at 10.10.10.99"  |
          |<-----------------------------------------------------------| (Spoofed Reply)
          |                                                            |
          | 5. Victim attempts SMB connection to Attacker (10.10.10.99)|
          |----------------------------------------------------------->|
          |                                                            |
          | 6. Attacker demands NTLM authentication                    |
          |<-----------------------------------------------------------|
          |                                                            |
          | 7. Victim sends NTLMv2 Hash automatically                  |
          |----------------------------------------------------------->|
          |                                                            |
          | 8. Attacker captures the NTLMv2 hash for cracking/relaying |
          +------------------------------------------------------------+
```

---

## Tools of the Trade: Responder

`Responder`, developed by Laurent Gaffié, is the undisputed king of poisoning attacks. It is a highly robust Python tool that listens for LLMNR, NBT-NS, and MDNS broadcasts and automatically sends spoofed responses. It also stands up rogue listening services (SMB, HTTP, FTP, SQL, etc.) to capture the resulting authentication hashes.

### Executing an LLMNR/NBT-NS Poisoning Attack

Running Responder on the local network interface (e.g., `eth0`):
```bash
sudo responder -I eth0 -rdw
```
**Flag Breakdown:**
- `-I eth0`: Specifies the network interface.
- `-r`: Enable NetBIOS wredir answers.
- `-d`: Enable NetBIOS domain answers.
- `-w`: Enable WPAD (Web Proxy Auto-Discovery) rogue proxy server.

Once running, Responder sits quietly. As soon as any user on the network mistypes a share name, searches for a missing printer, or executes a script looking for a defunct server, Responder intercepts the request. The victim's machine transparently attempts to authenticate to Responder's rogue SMB or HTTP server, handing over the user's `NTLMv2` hash.

**Example Responder Output:**
```text
[SMB] NTLMv2-SSP Client   : 10.10.10.5
[SMB] NTLMv2-SSP Username : CORP\Alice
[SMB] NTLMv2-SSP Hash     : Alice::CORP:0101000000000000...
```

---

## Beyond Capture: NTLM Relaying

While capturing and cracking NTLMv2 hashes offline with Hashcat or John the Ripper is highly effective, it relies on the user having a weak password. 
If the password is too complex to crack, the attacker can leverage an **NTLM Relay Attack** (often using `ntlmrelayx.py`).

Instead of just capturing the hash, the attacker intercepts the broadcast, tells the victim to authenticate, and simultaneously forwards that live authentication attempt to a *third* machine (the target). If the victim is a Local Administrator on the target machine, the attacker instantly gains SYSTEM-level code execution on the target, without ever knowing the victim's password.

*(Note: SMB Relaying requires that SMB Signing is disabled on the target server).*

---

## Active Exploitation: Inveigh

While Responder requires a Linux machine (typically Kali), red teamers who have established a foothold on a Windows workstation can use `Inveigh`.
`Inveigh` is a PowerShell/C# implementation of Responder. It allows an attacker to perform LLMNR/NBT-NS spoofing directly from a compromised Windows host, seamlessly blending into the environment without dropping non-native executables.

```powershell
# Running Inveigh within a PowerShell session
Invoke-Inveigh -ConsoleOutput Y -NBNS Y -LLMNR Y
```

---

## WPAD Spoofing (Web Proxy Auto-Discovery)

A closely related attack handled by Responder is WPAD spoofing. Browsers on Windows default to "Automatically detect settings" for proxy configurations. They do this by querying DNS and LLMNR/NBT-NS for the hostname `wpad`.

1. Responder listens for requests for `wpad`.
2. It responds, claiming to be the WPAD server.
3. It serves a malicious `.pac` (Proxy Auto-Configuration) file to the victim.
4. The victim's browser begins routing all HTTP/HTTPS traffic through the attacker's rogue proxy.
5. The attacker can then inject credential prompts (HTTP Basic Auth) into legitimate web traffic, forcing the user to type their cleartext password.

---

## Defensive Countermeasures & Hardening

Securing a network against LLMNR and NBT-NS poisoning is straightforward but requires network-wide configuration changes.

1. **Disable LLMNR**:
   Deploy a Group Policy Object (GPO):
   `Computer Configuration > Administrative Templates > Network > DNS Client > Turn off multicast name resolution` -> Set to **Enabled**.

2. **Disable NetBIOS over TCP/IP**:
   This must be done either via DHCP scope options (Option 1, set to `0x2`) or manually on the network adapters of the endpoints via script/GPO.

3. **Disable WPAD**:
   Use a GPO or registry push to disable "Automatically detect settings" in Internet Explorer/Edge/Chrome proxy configurations. Additionally, create a DNS sinkhole record for `wpad` pointing to `127.0.0.1`.

4. **Require SMB Signing**:
   While this doesn't stop the initial spoofing or hash capture, enforcing SMB Signing across the domain prevents attackers from successfully executing SMB Relay attacks using the captured credentials.

5. **Network Access Control (NAC) & Port Security**:
   Prevent unauthorized devices (like an attacker's rogue Kali box) from connecting to the internal LAN and injecting broadcast traffic in the first place.

---

## Chaining Opportunities

- **Responder -> Hashcat**: Capture NTLMv2 hashes from the network -> Crack them offline to obtain cleartext AD credentials.
- **Responder -> NTLMRelayx -> Secretsdump**: Poison an LLMNR request from a Domain Admin -> Relay the authentication to a Domain Controller -> Execute `secretsdump.py` to dump the NTDS.dit (entire domain database) resulting in complete domain compromise.
- **Responder -> WPAD Spoofing -> Cleartext Creds**: Use WPAD spoofing to prompt the user for proxy authentication, catching their password in cleartext rather than a cryptographic hash.

## Related Notes
- [[10 - SMB — EternalBlue, Null Session, Relay Attacks]]
- [[07 - Password Attacks and Hash Cracking]]
- [[13 - Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden-Silver Ticket, Kerberoasting, AS-REP Roasting]]
- [[02 - Active Directory Architecture and Trust Relationships]]
