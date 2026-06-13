import subprocess

scenarios = {
    "01 - Active Directory Overview.md": """## Real-World Attack Scenario

The engagement began with a successful spear-phishing campaign that dropped a lightweight beacon on a standard user's workstation.
The attacker, operating as the unprivileged user `jdoe` within the `megacorp.local` environment, needed to gain situational awareness without triggering the heavily monitored EDR solutions.
Instead of immediately attempting privilege escalation, the attacker focused on mapping the Active Directory landscape to understand the target's topology.
The attacker started by identifying the primary domain controllers using built-in Windows commands to blend in with normal administrative traffic.
Running `nltest /dsgetdc:` provided the name and IP address of the primary DC (`DC01.megacorp.local`), establishing the central authority of the domain.
Next, the attacker needed to understand the domain's size and complexity.
Using `net user /domain`, they pulled a complete list of active user accounts, saving the output to a local text file for offline parsing.
They followed this by querying the domain's administrative groups to identify high-value targets.
Executing `net group "Domain Admins" /domain` revealed three key accounts: `Administrator`, `jsmith_adm`, and `bkhan_adm`.
The attacker noticed that `jsmith_adm` was actively used based on the last logon timestamps.
To check the password policy and determine the viability of password spraying or brute-forcing, the attacker ran `net accounts /domain`.
The results showed a lockout threshold of 5 attempts and a minimum password length of 12 characters.
Realizing that brute-forcing was too noisy and risky, the attacker shifted their strategy towards finding misconfigurations or extracting credentials from memory.
They also queried the domain trusts using `nltest /domain_trusts` to see if `megacorp.local` was part of a larger forest.
The command revealed a two-way trust with a parent domain, `global.megacorp.local`, expanding the potential attack surface.
With this foundational knowledge, the attacker had a clear map of the environment.
They knew the IP addresses of the DCs, the names of the domain admins, and the strictness of the password policy.
This intelligence was gathered entirely using Living off the Land (LotL) binaries, generating zero alerts in the SIEM.
The attacker's next phase would involve more targeted enumeration, specifically looking for kerberoastable accounts and vulnerable ACLs, using the initial overview as their guide.
The ultimate outcome of this phase was a comprehensive understanding of the AD structure, allowing the attacker to plan a precise, stealthy route to Domain Admin.
""",
    
    "02 - AD Enumeration.md": """## Real-World Attack Scenario

Operating from a compromised developer workstation, the attacker aimed to map out the `megacorp.local` domain to find a path to Domain Admin.
They decided to use BloodHound, a graph theory-based tool, to identify hidden relationships and misconfigurations.
To avoid dropping the C# `Sharphound.exe` binary directly onto the disk, which would likely be flagged by the local AV, the attacker used a PowerShell-based ingestor.
They bypassed AMSI and executed the script in memory: `Invoke-BloodHound -CollectionMethod All -Domain megacorp.local`.
The script queried LDAP and the local SAM databases of accessible machines, gathering data on users, groups, computers, and active sessions.
The process took approximately 15 minutes, generating a ZIP file containing several JSON files.
The attacker exfiltrated this ZIP file over a covert C2 channel to their local analyzing machine.
Upon importing the data into the BloodHound GUI, they ran the built-in query: "Find Shortest Paths to Domain Admins."
The graph revealed a complex, non-obvious path to compromise.
The compromised user, `dev_jdoe`, was a member of the `IT_Support` group.
The `IT_Support` group had `GenericWrite` privileges over the `Helpdesk_Admins` group.
Furthermore, the `Helpdesk_Admins` group was part of the local `Administrators` group on `SRV-UTIL-01`.
Crucially, BloodHound showed that a Domain Admin, `bkhan_adm`, had an active, disconnected RDP session on `SRV-UTIL-01`.
The attacker's path was clear: escalate privileges to control the `Helpdesk_Admins` group, take over `SRV-UTIL-01`, and dump the Domain Admin's credentials.
To confirm the `GenericWrite` privilege, the attacker used PowerView: `Get-ObjectAcl -Identity "Helpdesk_Admins" | Where-Object {$_.SecurityIdentifier -eq "S-1-5-21-..."}`.
The output confirmed the misconfiguration.
The attacker then used PowerView's `Add-DomainGroupMember` cmdlet to add `dev_jdoe` to the `Helpdesk_Admins` group.
With the new group membership, the attacker laterally moved to `SRV-UTIL-01` using WinRM.
Once on the server, they dumped the LSASS memory, extracting the plaintext credentials of the `bkhan_adm` account.
The AD enumeration phase successfully transformed a low-privileged developer account into a Domain Admin by exposing hidden permission chains.
""",

    "03 - Kerberosable Accounts — SPN Scanning.md": """## Real-World Attack Scenario

Having established a foothold in the `megacorp.local` domain, the attacker needed to identify valuable target services.
Instead of running a noisy `nmap` scan across the /16 subnet, which would immediately trigger the IDS/IPS, they opted for an OPSEC-safe SPN scan.
The attacker knew that enterprise applications often run under the context of standard domain user accounts.
These service accounts require Service Principal Names (SPNs) to function within the Kerberos authentication framework.
From the compromised Windows host, the attacker used the built-in `setspn.exe` utility to query Active Directory.
They executed `setspn.exe -T megacorp.local -Q */*`, redirecting the output to a text file for offline analysis.
The LDAP query asked the Domain Controller for all objects with a populated `servicePrincipalName` attribute.
The DC responded with a massive list, which the attacker meticulously filtered.
They ignored any SPNs ending with a `$` character, as these belonged to machine accounts with uncrackable 120-character passwords.
Instead, they focused on user accounts associated with high-value services.
They discovered an SPN formatted as `MSSQLSvc/sql01.megacorp.local:1433`, mapped to the user account `svc_sqladmin`.
This single LDAP query revealed four critical pieces of intelligence:
1. An MS SQL Server was running in the environment.
2. The service was hosted on `sql01.megacorp.local`.
3. It was listening on the default port `1433`.
4. It was running under the context of the `svc_sqladmin` domain user account.
All of this was achieved without sending a single packet to the `sql01` server itself.
The attacker realized that `svc_sqladmin` was a prime target for a Kerberoasting attack.
Because the account was a standard user account, its password was likely set by a human and potentially weak.
Furthermore, as an SQL administrator account, compromising it could lead to code execution on the database server via `xp_cmdshell`.
The SPN scanning phase was completed in seconds, leaving virtually no footprint, and perfectly setting the stage for the next phase of the attack.
The attacker now had a precise target list, prioritizing the `svc_sqladmin` account for immediate exploitation.
""",

    "04 - Kerberoasting.md": """## Real-World Attack Scenario

Following the successful SPN scan, the attacker identified the `svc_sqladmin` account as a high-value target.
This account had the SPN `MSSQLSvc/sql01.megacorp.local:1433` registered to it.
The attacker's goal was to extract the Service Ticket (TGS) for this service and crack it offline to obtain the account's plaintext password.
Since the attacker had a foothold on a Linux machine within the network, they decided to use Impacket's `GetUserSPNs.py` script.
They executed the command: `GetUserSPNs.py megacorp.local/jdoe:Password123 -dc-ip 10.0.0.5 -request`.
This script authenticated to the Domain Controller using the compromised `jdoe` credentials.
It then requested a TGS for the `MSSQLSvc/sql01.megacorp.local:1433` service.
The Domain Controller, following the Kerberos protocol, retrieved the password hash of the `svc_sqladmin` account.
The DC used this hash to encrypt the TGS and sent it back to the attacker's machine.
The script outputted the encrypted ticket in a format ready for Hashcat (`$krb5tgs$23$*...`).
The attacker immediately disconnected from the target network to perform the cracking offline, ensuring zero risk of detection during this intensive process.
They loaded the hash into a specialized cracking rig equipped with multiple high-end GPUs.
Using Hashcat with a massive wordlist and rule-based mutations, they executed: `hashcat -m 13100 hashes.txt rockyou.txt -r rules/best64.rule`.
The cracking process was intense, leveraging the parallel processing power of the GPUs.
After approximately 45 minutes, Hashcat successfully cracked the hash, revealing the password: `Winter2023!`.
The password was relatively complex but had been reused across seasons, a common organizational flaw.
The attacker now possessed the plaintext credentials for `svc_sqladmin`.
They reconnected to the target network and used `psexec.py` to authenticate to the `sql01` server using the cracked credentials.
Because the account had administrative privileges on the SQL server, the attacker gained an interactive SYSTEM shell.
The Kerberoasting attack had successfully escalated the attacker's privileges from a standard user to a local administrator on a critical database server.
From there, they could access sensitive financial data stored in the SQL databases.
""",

    "05 - AS-REP Roasting.md": """## Real-World Attack Scenario

During the initial reconnaissance phase, the attacker sought to identify misconfigured user accounts that could be exploited without needing to interact with target services.
They focused on finding accounts with the "Do not require Kerberos preauthentication" attribute enabled (`DONT_REQ_PREAUTH`).
This misconfiguration allows anyone to request an Authentication Service Response (AS-REP) for the user directly from the Domain Controller.
The AS-REP contains a piece of data encrypted with the user's password hash, which can be cracked offline.
From their compromised Windows workstation, the attacker loaded the PowerView module into memory.
They executed `Get-DomainUser -PreauthNotRequired -Properties sAMAccountName` to sweep the domain for vulnerable accounts.
The query quickly returned a single result: `svc_backup`.
This account was likely configured without preauthentication to support a legacy backup application that did not fully support the Kerberos standard.
Realizing the opportunity, the attacker switched to their Linux attacking machine to extract the hash.
They used Impacket's `GetNPUsers.py` tool, executing: `GetNPUsers.py megacorp.local/svc_backup -no-pass -dc-ip 10.0.0.5`.
The script sent a crafted AS-REQ to the Domain Controller on behalf of the `svc_backup` user.
Because preauthentication was disabled, the DC did not require the attacker to prove they knew the password.
The DC responded with the AS-REP, and the script parsed it, outputting the hash in Hashcat format (`$krb5asrep$23$...`).
The attacker took the hash offline to their dedicated cracking rig.
They ran Hashcat against a targeted wordlist containing common corporate passwords and permutations: `hashcat -m 18200 hash.txt corp_wordlist.txt`.
Within minutes, the weak password `Backup1!` was recovered.
The attacker quickly analyzed the privileges of the `svc_backup` account using BloodHound data gathered previously.
They discovered that the backup service account was a member of the `Backup Operators` domain group.
This group membership granted the account the ability to bypass file system security to back up files on all domain controllers.
The attacker used the compromised credentials to connect to the primary DC via SMB and extract the `NTDS.DIT` database.
The AS-REP roasting attack, exploiting a single legacy misconfiguration, led directly to a full domain compromise.
""",

    "06 - Pass the Hash (PtH).md": """## Real-World Attack Scenario

The attacker had successfully compromised a mid-level manager's laptop (`LAPTOP-104`) via a malicious macro in an Excel document.
After escalating privileges locally to SYSTEM using a kernel exploit, they dumped the local SAM database and LSASS memory.
Among the extracted credentials was the NTLM hash for the built-in local `Administrator` account: `31d6cfe0d16ae931b73c59d7e0c089c0`.
The environment strictly enforced complex, randomly generated passwords for domain users, making cracking impractical.
However, the attacker suspected that the IT department might have reused the same local `Administrator` password across multiple workstations.
This is a common misconfiguration known as local admin password reuse.
To test this hypothesis and move laterally without needing the plaintext password, the attacker employed a Pass the Hash (PtH) attack.
They used CrackMapExec (CME) from their attacking machine, targeting the entire `/24` workstation subnet.
The command executed was: `cme smb 10.0.1.0/24 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0 --local-auth`.
CME systematically attempted to authenticate to the SMB service on every IP address using the provided NTLM hash.
The results scrolled across the screen, showing "Pwn3d!" on 15 different workstations.
The attacker's suspicion was correct; the local administrator hash was valid across a significant portion of the network.
They focused on one of the compromised machines, `LAPTOP-210`, which belonged to a senior network engineer.
Using the Impacket suite, the attacker executed `psexec.py megacorp/Administrator@10.0.1.210 -hashes :31d6cfe0d16ae931b73c59d7e0c089c0`.
The PtH authentication succeeded, granting the attacker a highly privileged SYSTEM shell on the engineer's machine.
From this new vantage point, they dumped the LSASS memory of `LAPTOP-210`.
The engineer had recently logged in with their highly privileged Domain Admin account, `admin_engineer`.
The LSASS dump revealed the plaintext password for the `admin_engineer` account.
By passing a local hash, the attacker had hopped across the network, targeted a high-value user, and captured the keys to the kingdom.
The PtH technique proved invaluable in an environment where cracking complex passwords was not feasible.
""",

    "07 - Pass the Ticket (PtT).md": """## Real-World Attack Scenario

Having compromised a critical file server (`FS01.megacorp.local`) used by the IT department, the attacker sought a way to escalate privileges to Domain Admin.
They had local SYSTEM access but no highly privileged passwords.
They knew that IT administrators frequently accessed this server to manage shares and permissions.
If a Domain Admin had logged in recently, their Kerberos tickets might still be cached in the Local Security Authority Subsystem Service (LSASS) memory.
To investigate, the attacker uploaded a customized, obfuscated version of Mimikatz to bypass the server's endpoint protection.
They executed Mimikatz and ran `privilege::debug` to ensure they had the necessary permissions to interact with LSASS.
Next, they executed `sekurlsa::tickets /export` to dump all Kerberos tickets currently cached in memory.
Mimikatz successfully wrote several `.kirbi` files to the current directory.
The attacker reviewed the filenames, looking for high-value targets.
They spotted a file named `[0;12a34]-2-0-40e10000-DA_Admin@krbtgt-MEGACORP.LOCAL.kirbi`.
This indicated a Ticket Granting Ticket (TGT) belonging to the Domain Admin account `DA_Admin`.
This was the jackpot; the attacker didn't need the password or the hash if they had a valid TGT.
Before injecting the ticket, the attacker cleared their current session's tickets using `kerberos::purge` to avoid conflicts.
They then injected the Domain Admin TGT into their current session using `kerberos::ptt "C:\\path\\to\\DA_Admin.kirbi"`.
To verify the injection was successful, they ran `klist`, which displayed the `DA_Admin` ticket in the cache.
Now acting under the context of the Domain Admin, the attacker attempted to access the C$ share of the primary Domain Controller.
They executed `dir \\\\DC01.megacorp.local\\C$`, and the directory listing was successfully returned.
The Pass the Ticket attack had worked flawlessly.
The attacker bypassed all authentication mechanisms by reusing a legitimately issued, cached ticket.
They immediately used this access to perform a DCSync attack, extracting the `krbtgt` hash to establish long-term persistence.
The PtT technique turned a transient administrative login into a full domain compromise.
""",

    "08 - Overpass the Hash.md": """## Real-World Attack Scenario

The attacker had compromised a workstation (`WKSTN-05`) and extracted the NTLM hash for the user `jdoe`: `cf3a5525ee9414229e66279623ed5c58`.
They needed to access an internal web application that hosted sensitive financial documents.
However, the environment was hardened: NTLM authentication was strictly disabled across the domain to prevent Pass the Hash attacks.
All services, including the target web app, required Kerberos authentication.
A standard PtH attack using tools like CrackMapExec or Impacket's SMB clients would fail because the target servers would reject the NTLM negotiation.
To bypass this restriction, the attacker needed to "upgrade" their NTLM hash into a valid Kerberos Ticket Granting Ticket (TGT).
This technique is known as Overpass the Hash or Pass the Key.
The attacker used Rubeus, a powerful C# toolset for Kerberos manipulation, executing it in memory to evade detection.
They ran the command: `Rubeus.exe asktgt /user:jdoe /domain:megacorp.local /rc4:cf3a5525ee9414229e66279623ed5c58 /ptt`.
Rubeus used the provided NTLM hash (the RC4 key) to encrypt the timestamp required for the initial Authentication Service Request (AS-REQ).
The Domain Controller received the AS-REQ, successfully decrypted the timestamp using `jdoe`'s stored hash, and validated the request.
The DC then issued an AS-REP containing a valid TGT for `jdoe`.
The `/ptt` flag in the Rubeus command automatically injected this newly acquired TGT into the attacker's current logon session.
The attacker verified the ticket's presence using `klist`.
With a valid TGT injected, the attacker opened a browser session from the compromised workstation.
They navigated to the internal web application (`https://finance.megacorp.local`).
The browser transparently presented the TGT to the KDC, requested a Service Ticket (TGS) for the web service, and authenticated seamlessly via Kerberos.
The attacker successfully bypassed the NTLM restriction, gaining access to the sensitive documents.
This attack demonstrated that disabling NTLM is not a silver bullet if attackers can extract the hashes and use them to forge Kerberos requests.
""",

    "09 - Golden Ticket Attack.md": """## Real-World Attack Scenario

Having achieved Domain Admin privileges through a lateral movement campaign, the attacker knew their access was fragile.
If the IT team detected the breach and reset the compromised Domain Admin password, the attacker would lose their foothold.
To ensure long-term, undetectable persistence, the attacker decided to forge a Golden Ticket.
This required the NTLM hash of the `krbtgt` account, the cryptographic core of the domain's trust.
From a compromised Domain Controller, the attacker executed Mimikatz and performed a DCSync attack: `lsadump::dcsync /user:krbtgt /domain:megacorp.local`.
This command simulated a DC replication request and extracted the `krbtgt` NTLM hash: `b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`.
They also retrieved the domain SID (`S-1-5-21-123456789-987654321-1122334455`) during this process.
With these critical components, the attacker had everything needed to forge Kerberos tickets offline.
They retreated to their attacking machine to construct the Golden Ticket.
To blend in, they decided to create the ticket for a fictitious user, `svc_updater`, to avoid anomalies associated with real users.
They used Mimikatz to forge the ticket and save it to disk: `kerberos::golden /domain:megacorp.local /sid:S-1-5-21... /rc4:b1a2c3... /user:svc_updater /id:500 /groups:512 /ticket:golden.kirbi`.
The `groups:512` argument ensured the fictitious user was effectively a Domain Admin.
The resulting `golden.kirbi` file was a fully valid Ticket Granting Ticket (TGT), signed by the `krbtgt` hash, with a default lifespan of 10 years.
Months later, the Blue Team finally detected the initial breach, eradicated the malware, and forced a global password reset for all users.
They believed the network was secure.
However, they failed to reset the `krbtgt` account password twice, leaving the old hash valid.
The attacker returned, loaded Mimikatz on a newly compromised low-level workstation, and executed `kerberos::ptt golden.kirbi`.
The injected Golden Ticket allowed them to instantly request service tickets as a Domain Admin for any machine in the network.
They connected to the primary Domain Controller using WMI and regained total control of the environment.
The Golden Ticket attack provided ultimate persistence, bypassing all standard password-based remediation efforts.
""",

    "10 - Silver Ticket Attack.md": """## Real-World Attack Scenario

The attacker had infiltrated a branch office and compromised a print server (`PRINT-SRV-02`).
While exploring the server, they managed to extract the local SAM database, which contained the NTLM hash of the machine account: `e52cac67419a9a224a3b108f3fa6cb6d`.
The attacker's ultimate goal was to access the CEO's workstation (`CEO-WKS-01`) to steal confidential merger documents.
However, the Domain Controllers were heavily monitored, and any suspicious TGT requests (like Golden Tickets or Overpass the Hash) would trigger SIEM alerts.
To maintain absolute stealth, the attacker opted for a Silver Ticket attack, which bypasses the Domain Controller entirely.
A Silver Ticket is a forged Service Ticket (TGS) that is presented directly to the target service.
The attacker first needed the NTLM hash of the CEO's workstation machine account (`CEO-WKS-01$`).
They used their access on the print server to run a targeted Kerberoasting attack against a weak service account that had administrative rights on the CEO's machine, eventually dumping the `CEO-WKS-01$` hash.
With the target machine's hash in hand, the attacker moved to their offline cracking rig.
They used Mimikatz to forge a TGS specifically for the CIFS (Common Internet File System) service on the CEO's workstation.
The command was: `kerberos::golden /domain:megacorp.local /sid:S-1-5-21... /target:ceo-wks-01.megacorp.local /service:cifs /rc4:[CEO-WKS-01_HASH] /user:Administrator /ptt`.
This command constructed a TGS containing a Privilege Attribute Certificate (PAC) that falsely claimed the user was a Domain Admin.
Crucially, the ticket was encrypted with the `CEO-WKS-01$` hash, not the `krbtgt` hash.
The `/ptt` flag injected this forged Silver Ticket into the attacker's current session memory on the compromised print server.
The attacker then executed `dir \\\\ceo-wks-01.megacorp.local\\C$`.
The CEO's workstation received the request, decrypted the TGS using its own machine hash, and trusted the forged PAC.
It granted the attacker full administrative access to the file system.
The attacker navigated to the CEO's Documents folder and exfiltrated the sensitive merger files.
Because the Domain Controller was completely bypassed in this interaction, no Kerberos ticket request logs (Event ID 4768 or 4769) were generated on the DC.
The Silver Ticket attack achieved the objective with surgical precision and zero central logging, demonstrating the danger of compromised service or machine account hashes.
"""
}

import sys
import subprocess

for filepath, scenario in scenarios.items():
    full_path = f"/home/sanchit/Notes/VAPT/Active Directory/A - 36 - Active Directory Attacks/{filepath}"
    with open("/home/sanchit/Notes/VAPT/scenario.txt", "w") as f:
        f.write(scenario)
    
    cmd = ["python3", "/home/sanchit/Notes/VAPT/add_scenario.py", full_path]
    with open("/home/sanchit/Notes/VAPT/scenario.txt", "r") as f:
        subprocess.run(cmd, stdin=f, check=True)
    print(f"Injected into {filepath}")
