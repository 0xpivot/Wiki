import subprocess
import os

scenarios = {
    "06 - Enumerating SMB Shares and Null Sessions.md": """## Real-World Attack Scenario

In a recent internal penetration test for a mid-sized healthcare provider, the objective was to identify initial access vectors from an unauthenticated network perspective. The environment consisted of a flat `/24` subnet populated with both modern Windows Server 2019 machines and legacy Windows Server 2008 R2 systems used for old medical imaging software.

**Thought Process:**
Given the presence of legacy systems, there was a high probability of misconfigured SMB shares and potentially enabled Null Sessions. My first priority was to sweep the subnet to identify active SMB services and immediately check if any host permitted anonymous access. If a Null Session was allowed, I could extract the domain's password policy and a complete list of users, which would perfectly set up a targeted password spraying attack without triggering account lockouts.

**Execution:**
I began by sweeping the subnet using NetExec to rapidly identify SMB hosts and test for Null Session capabilities in a single command:
```bash
nxc smb 192.168.50.0/24 -u '' -p '' --shares
```
The output highlighted several hosts, but one legacy file server (`FS-ARCHIVE.medcorp.local` at `192.168.50.45`) returned `[+] medcorp.local\ : (Pwn3d!)` indicating a successful Null Session and listed multiple accessible shares, including `IPC$` and `IT_Backups`.

Realizing I had unauthenticated RPC access, I used `rpcclient` to enumerate domain users and the password policy:
```bash
rpcclient -U "" -N 192.168.50.45
rpcclient $> querydominfo
rpcclient $> enumdomusers
```
The `querydominfo` command revealed a password lockout threshold of 5 attempts. The `enumdomusers` command provided a list of over 300 valid domain usernames. 

Simultaneously, I connected to the readable `IT_Backups` share using `smbclient`:
```bash
smbclient -N //192.168.50.45/IT_Backups
```
Inside the share, I found an old PowerShell script named `Map-Drives.ps1`. Downloading and inspecting the script revealed hardcoded credentials for a service account (`svc_storage : Storage@Admin2019!`).

**Outcome:**
Without ever having to guess a password or risk account lockouts, the Null Session misconfiguration provided both the entire domain user roster and an initial set of valid credentials. I immediately validated the `svc_storage` account using NetExec:
```bash
nxc smb 192.168.50.0/24 -u 'svc_storage' -p 'Storage@Admin2019!'
```
The credentials were valid across multiple servers, granting an authenticated foothold into the Active Directory environment and setting the stage for further privilege escalation and lateral movement.
""",
    "07 - Discovering GPOs and Analyzing Passwords in SYSVOL.md": """## Real-World Attack Scenario

During an internal security assessment for a regional financial institution, I established an initial unauthenticated foothold. My goal was to escalate privileges by identifying misconfigurations in Active Directory Group Policy Objects (GPOs), specifically looking for legacy Group Policy Preferences (GPP) that might expose encrypted passwords. The environment was mature, but had undergone numerous migrations over the last decade.

**Thought Process:**
The `SYSVOL` share is accessible to any authenticated domain user and contains all the GPOs for the domain. Historically, administrators used GPP to push out local administrator passwords or map drives, which stored the password (known as `cPassword`) in an AES-256 encrypted format. However, Microsoft accidentally published the static AES private key in 2012. If I could locate an old `Groups.xml` or `Printers.xml` file within SYSVOL, I could decrypt the `cPassword` and potentially gain local administrator access across multiple endpoints.

**Execution:**
First, I authenticated to the domain controller's SYSVOL share to verify access using my low-privileged compromised account:
```bash
smbclient -U 'jsmith' //192.168.100.10/SYSVOL
```
Instead of manually crawling through the complex `{GUID}` folder structures, I leveraged NetExec to automate the search for `cPassword` attributes within the SYSVOL share across the domain controller:
```bash
nxc smb 192.168.100.10 -u 'jsmith' -p 'Welcome2023!' -M gpp_password
```
The module successfully identified a `Groups.xml` file located in `\domain.local\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\`. NetExec automatically extracted the `cPassword` hash and decrypted it using the well-known static Microsoft AES key.

The decrypted password was `Admin!@#2015`. I immediately checked where this password was valid by spraying it across the server subnet:
```bash
nxc smb 192.168.100.0/24 -u 'Administrator' -p 'Admin!@#2015' --local-auth
```

**Outcome:**
The command returned `(Pwn3d!)` on over 40 servers, including the primary backup server. The organization had created a GPO years ago to set the local administrator password and never removed the GPP file after the Microsoft patch. By exploiting this legacy SYSVOL misconfiguration, I escalated from a standard domain user to local administrator on a significant portion of the server infrastructure in under ten minutes.
""",
    "08 - Enumerating SPNs and Finding Service Accounts.md": """## Real-World Attack Scenario

In a recent engagement for an e-commerce platform, I was operating from a standard developer's compromised workstation. To progress laterally and escalate privileges without relying on noisy exploit attempts, I focused on identifying high-value Service Principal Names (SPNs). Service accounts are often highly privileged and, critically, their passwords rarely change due to fear of breaking production services.

**Thought Process:**
By querying the Active Directory for accounts with registered SPNs, I could map out the internal infrastructure—identifying where MSSQL, Exchange, and IIS services were running. Furthermore, finding a user account (rather than a machine account) with an SPN would directly set up a Kerberoasting attack. My objective was to quietly extract all SPNs using built-in Windows tools or LDAP queries to avoid triggering endpoint detection and response (EDR) alerts associated with aggressive network scanning.

**Execution:**
To remain stealthy and "live off the land," I utilized the native `setspn.exe` utility, which is installed by default on Windows workstations, to list all SPNs in the domain:
```cmd
setspn.exe -T ecommerce.local -Q */*
```
The output generated a massive list of registered services. I redirected the output to a text file and filtered it for interesting services like SQL servers and web applications.
```cmd
setspn.exe -T ecommerce.local -Q */* > spns.txt
findstr /i "MSSQLSvc" spns.txt
```
I noticed a specific SPN: `MSSQLSvc/sql-prod-01.ecommerce.local:1433` registered to a domain user account named `svc_sql_admin` instead of a computer account. 

To gather more context about this service account without triggering alerts, I executed a targeted LDAP query using PowerShell's ADSI capabilities to check the account's group memberships and description:
```powershell
$Searcher = New-Object DirectoryServices.DirectorySearcher
$Searcher.Filter = "(samaccountname=svc_sql_admin)"
$Searcher.FindOne().Properties
```
The description field literally read: "Service account for PROD SQL - DO NOT CHANGE PWD".

**Outcome:**
By enumerating SPNs, I successfully mapped the location of the critical production database (`sql-prod-01`) and identified that it was running under the context of a highly privileged domain user account (`svc_sql_admin`). This discovery bypassed the need for network port scanning entirely. It immediately provided the exact target for a subsequent Kerberoasting attack, ultimately leading to the extraction and offline cracking of the `svc_sql_admin` password, granting administrative access to the sensitive customer database.
""",
    "09 - Identifying Domain Controllers and Global Catalogs.md": """## Real-World Attack Scenario

During a red team engagement for a large manufacturing enterprise, I was dropped into an isolated VLAN with no prior knowledge of the network architecture. Before any offensive actions could be taken, I needed to precisely locate the Active Directory Domain Controllers (DCs) and Global Catalog (GC) servers. Identifying these core infrastructure assets is the critical first step for any AD-based attacks, such as password spraying, AS-REP roasting, or dumping NTDS.dit.

**Thought Process:**
Randomly scanning the `/16` network for port 389 (LDAP) or 53 (DNS) would be incredibly noisy and likely trigger immediate SOC alerts. Instead, I opted to passively leverage the environment's own DNS infrastructure. Domain computers rely on specific DNS Service (SRV) records to locate DCs and GCs. By querying these standard records, I could map out the forest hierarchy and identify the primary authentication servers completely legitimately, blending in with normal network traffic.

**Execution:**
Using the standard Linux `dig` utility on my attack box, I first queried the SOA (Start of Authority) record to confirm the domain name of the environment, which was `corp.manufacturing.local`.
```bash
dig SOA corp.manufacturing.local
```
Next, to locate the Domain Controllers, I queried the `_ldap._tcp.dc._msdcs` SRV records:
```bash
dig _ldap._tcp.dc._msdcs.corp.manufacturing.local SRV
```
The response returned three distinct IP addresses, indicating multiple DCs (e.g., `dc01.corp...`, `dc02.corp...`). 

Knowing that multi-domain forests heavily rely on Global Catalogs for cross-domain searches, I specifically queried the GC SRV records to find the servers holding the universal group membership information:
```bash
dig _gc._tcp.corp.manufacturing.local SRV
```
This revealed that only `dc01.corp.manufacturing.local` was acting as the Global Catalog. 

To verify connectivity and exact OS version without an intrusive scan, I used NetExec to perform an anonymous SMB connection check against the identified DCs:
```bash
nxc smb 10.50.10.10 10.50.10.11
```

**Outcome:**
Through legitimate DNS queries alone, I mapped the entire AD hierarchy, pinpointing the primary DCs and the sole Global Catalog server. This allowed me to perfectly target my subsequent LDAP enumeration and Kerberos-based attacks (like Kerberoasting) directly at `dc01`, maximizing efficiency and remaining entirely under the radar of network intrusion detection systems that look for broad port scans.
""",
    "10 - Enumerating AD Trusts and Forest Boundaries.md": """## Real-World Attack Scenario

While conducting a penetration test for a recently merged logistics company, I compromised a low-privileged user account in the `apac.logistics.local` child domain. The ultimate objective was to compromise the overarching parent domain, `global.logistics.local`, which housed the critical financial and administrative infrastructure. 

**Thought Process:**
Active Directory environments often utilize trusts to allow users in one domain to access resources in another. However, these trust relationships—especially two-way transitive trusts or poorly configured external trusts—can provide a pathway for lateral movement and privilege escalation across domain boundaries. My goal was to enumerate all domain trusts to identify a path from the child domain (`apac`) up to the parent domain (`global`), looking specifically for SID History vulnerabilities or overly permissive cross-domain group memberships.

**Execution:**
Operating from a compromised Windows 10 workstation within the `apac` domain, I needed to perform the enumeration stealthily. I used the native PowerShell Active Directory module (which was already installed for administrative purposes) to list all trusts for the current domain.
```powershell
Import-Module ActiveDirectory
Get-ADTrust -Filter *
```
The output confirmed a two-way transitive trust with `global.logistics.local` and an unexpected one-way outgoing trust to a seemingly legacy domain, `acquired-company.local`.

To gain deeper insight from my Linux attack machine, I used BloodHound's Python ingestor (`bloodhound-python`) to map the trust relationships and cross-domain group memberships visually, pointing it at the child DC.
```bash
bloodhound-python -u 'jdoe' -p 'Summer2025!' -ns 192.168.10.10 -d apac.logistics.local -c All
```
Upon importing the data into the BloodHound GUI, the attack graph revealed a critical misconfiguration: the `Domain Admins` group of the `apac.logistics.local` domain was nested inside the `Server Operators` group of the parent `global.logistics.local` domain.

**Outcome:**
By enumerating the AD trusts and mapping cross-domain group memberships, I discovered a direct exploitation path. Because the child domain admins were effectively server operators in the parent domain, compromising the child domain (which had weaker security controls) immediately allowed me to take over the parent domain. I elevated privileges to Domain Admin in `apac`, and then trivially used those credentials to compromise the primary `global` Domain Controller, entirely bypassing the parent domain's strict security perimeter.
""",
    "11 - Identifying Local Administrators via RPC.md": """## Real-World Attack Scenario

During a targeted internal red team exercise for a technology firm, I obtained initial access as a standard, unprivileged user. To advance the attack, I needed to compromise an account with higher privileges. The most effective way to achieve this is to find a workstation where a highly privileged IT administrator is currently logged in, but to do so, I first needed to find a machine where my current low-privileged user had Local Administrator rights to extract credentials from memory (e.g., using Mimikatz or Procdump).

**Thought Process:**
Instead of blindly attempting to exploit every machine on the network—which is noisy and easily detected—I needed to systematically map out where my compromised account had administrative privileges. Organizations frequently misconfigure Active Directory by granting excessive local admin rights via Group Policy or manual assignments. By querying the Service Control Manager (SCM) or the SAM-Remote (SAMR) protocol over RPC, I could check my administrative access across the entire subnet without triggering traditional authentication failure alerts.

**Execution:**
I utilized NetExec, which leverages the Impacket library to interact directly with MSRPC. I configured it to check local administrative privileges across the `/24` workstation subnet using my compromised credentials (`jdoe` : `Winter2025!`).
```bash
nxc smb 192.168.200.0/24 -u 'jdoe' -p 'Winter2025!'
```
NetExec automatically attempts to connect to the ADMIN$ share or open the Service Control Manager (SCM) on each host. After scanning the subnet, the output displayed several endpoints, but specifically flagged `WS-DEV-04` and `WS-HELP-09` with the highly sought-after `(Pwn3d!)` tag, confirming my user had Local Administrator rights on those specific machines.

To verify and gather intelligence on who else was using those machines, I queried the active sessions via RPC:
```bash
nxc smb 192.168.200.45 -u 'jdoe' -p 'Winter2025!' --sessions
```

**Outcome:**
The RPC enumeration confirmed I was a local administrator on `WS-HELP-09`. Crucially, the `--sessions` check revealed that a Tier 1 Helpdesk Administrator (`admin_tsmith`) currently had an active session on that machine. Because I possessed local admin rights, I laterally moved to `WS-HELP-09`, dumped the LSASS process memory, and successfully extracted the cleartext password of the Helpdesk Administrator. This targeted RPC enumeration provided the exact stepping stone needed to dramatically escalate my privileges within the domain.
""",
    "12 - Password Spraying Basics and Lockout Policies.md": """## Real-World Attack Scenario

In a security assessment for an educational institution, I had mapped the network but lacked any valid domain credentials. The environment heavily utilized Office 365, meaning users likely had the same passwords for their local AD and external services. To gain an initial foothold, I decided to execute a password spraying attack. The challenge was to execute this attack without triggering the organization's account lockout policies, which would alert the IT department and lock legitimate users out of their accounts.

**Thought Process:**
A brute-force attack (many passwords against one user) guarantees a lockout. Password spraying flips this: trying one carefully chosen password against many users. However, before I could spray, I absolutely had to know the domain's password lockout policy. If the threshold was 3 attempts in 30 minutes, spraying 4 times within that window would cause widespread disruption. My plan was to anonymously query the domain controller for the lockout policy, generate a clean list of valid users, and then spray a highly probable password (e.g., the current season and year).

**Execution:**
I first attempted to establish a Null Session to the primary Domain Controller to query the domain password policy anonymously.
```bash
nxc smb 10.10.10.5 -u '' -p '' --pass-pol
```
The command was successful, revealing a `LockoutThreshold` of 5 attempts and a `LockoutDuration` of 30 minutes. This meant I could safely attempt 4 passwords per user every 30 minutes. 

Next, I used an open SMB share I found earlier to extract a list of 500 employee usernames and saved them to `users.txt`. Knowing the threshold, I selected a single, common password: `Autumn2025!`. I used NetExec to perform the password spray against the Domain Controller:
```bash
nxc smb 10.10.10.5 -u users.txt -p 'Autumn2025!' --continue-on-success
```
The `--continue-on-success` flag ensured the tool didn't stop at the first success, allowing me to compromise as many accounts as possible in a single pass.

**Outcome:**
By strictly adhering to the queried lockout policy, the attack remained entirely undetectable by standard lockout monitoring systems. The single spray of `Autumn2025!` successfully authenticated against 14 different user accounts, including a mid-level IT manager's account. This careful, policy-aware approach instantly transitioned the engagement from unauthenticated external reconnaissance to an authenticated internal foothold, providing multiple redundant access vectors.
""",
    "13 - AS-REP Roasting Basics and Detection.md": """## Real-World Attack Scenario

During a compromise assessment for a retail company, I sought to escalate my initial unauthenticated access. I had captured a list of valid domain usernames during my passive enumeration phase but lacked passwords. Active Directory provides a unique attack vector called AS-REP Roasting, which targets a specific, often legacy-driven misconfiguration in Kerberos authentication.

**Thought Process:**
By default, Kerberos requires pre-authentication (sending an encrypted timestamp) before the Domain Controller will issue a Ticket Granting Ticket (TGT). However, administrators sometimes disable the "Do not require Kerberos preauthentication" setting for specific service accounts or applications that do not support modern Kerberos flows. If this setting is disabled, anyone can request a TGT for that user. The DC will respond with an AS-REP message containing a chunk of data encrypted with the user's password hash. I could request this offline, requiring zero authentication, and then crack the hash at my leisure.

**Execution:**
 Armed with a text file containing over 1,000 valid domain usernames (`domain_users.txt`), I used Impacket's `GetNPUsers.py` script. This tool automatically requests TGTs for the provided users and parses the responses, looking for accounts where pre-authentication is disabled.
```bash
impacket-GetNPUsers retail.local/ -usersfile domain_users.txt -format hashcat -outputfile asrep_hashes.txt -dc-ip 192.168.100.10
```
The script immediately returned a hit for a user named `svc_scanner`, appending the extracted AS-REP hash string (starting with `$krb5asrep$23$`) to the output file. 

To recover the plaintext password, I transferred the `asrep_hashes.txt` file to my dedicated GPU cracking rig and used Hashcat with a robust wordlist and ruleset.
```bash
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

**Outcome:**
The Hashcat process cracked the AS-REP hash in under 45 minutes, revealing the password `Sc@nn3r!2018`. Because AS-REP Roasting does not require the attacker to send any login failures, the attack completely bypassed the domain's account lockout policies and generated no standard authentication failure logs. The compromised `svc_scanner` account granted me an authenticated foothold, proving that legacy Kerberos configurations present a massive, unauthenticated risk to the entire domain.
""",
    "14 - Kerberoasting Basics and Identification.md": """## Real-World Attack Scenario

During a penetration test for a healthcare provider, I had compromised a standard nurse's workstation and obtained low-privileged domain user credentials. To access the highly restricted patient database, I needed to escalate privileges. The most effective post-authentication attack in Active Directory is Kerberoasting, which exploits the way Kerberos issues service tickets.

**Thought Process:**
When an authenticated user requests access to a service (like an MSSQL database or an IIS web server), the Domain Controller issues a Kerberos Ticket Granting Service (TGS) ticket. A portion of this TGS is encrypted using the NTLM hash of the Service Account running that service. Because any valid domain user can request a TGS for any registered Service Principal Name (SPN), I could request tickets for high-value service accounts, export them, and crack them offline. Service accounts often have elevated privileges and weak, never-changing passwords.

**Execution:**
Using my compromised low-privileged account, I utilized Impacket's `GetUserSPNs.py` script to query the Domain Controller for all user accounts associated with an SPN, and simultaneously request their TGS tickets formatted for Hashcat.
```bash
impacket-GetUserSPNs healthcare.local/nurse_jdoe:Password123! -request -dc-ip 10.20.30.40 -outputfile kerberoast_hashes.txt
```
The script quickly identified several SPNs and successfully requested TGS tickets for them. One ticket was specifically tied to the `svc_sql_clinical` account, which ran the primary MSSQL database.

I transferred the `kerberoast_hashes.txt` file (containing the `$krb5tgs$23$*` formatted hashes) to my offline cracking machine. Using Hashcat and a targeted dictionary, I began the offline brute-force attack:
```bash
hashcat -m 13100 kerberoast_hashes.txt custom_wordlist.txt -O -w 3
```

**Outcome:**
The offline cracking succeeded in two hours, revealing the service account password: `Clin1calDB_!`. I immediately used these credentials to authenticate directly to the MSSQL server using `mssqlclient.py`. Because the service account was a member of the SQL `sysadmin` role, I enabled `xp_cmdshell` and executed operating system commands with SYSTEM privileges on the database server. Kerberoasting allowed me to turn a low-privileged domain user into a database administrator entirely offline, without generating any suspicious brute-force traffic on the network.
""",
    "15 - LLMNR and NBT-NS Poisoning Basics Responder.md": """## Real-World Attack Scenario

On the first day of an internal corporate network assessment, I connected my attack laptop to an open Ethernet jack in a conference room. I had zero credentials and no knowledge of the internal IP scheme. My objective was to intercept network traffic to capture authentication hashes, leveraging the noisy nature of Windows local name resolution protocols.

**Thought Process:**
When a Windows machine attempts to connect to a network resource (like `\\fileserver1`) and the primary DNS server fails to resolve the name, the machine falls back to broadcast protocols: LLMNR (Link-Local Multicast Name Resolution) and NBT-NS (NetBIOS Name Service). The machine essentially shouts to the entire local subnet, "Does anyone know where `fileserver1` is?" By running a tool like Responder, I could listen for these broadcasts, maliciously claim "I am `fileserver1`!", and force the victim machine to authenticate to my rogue server, capturing its NTLMv2 hash in the process.

**Execution:**
I launched Responder on my attack machine, configuring it to listen on my active network interface (`eth0`) and enabling the standard SMB and HTTP rogue authentication servers.
```bash
sudo responder -I eth0 -rdw
```
Almost immediately, the console began lighting up with intercepted LLMNR requests for mistyped share names like `\\printers_corp` and `\\hr-share-new`. Responder automatically poisoned the requests, directing the victim machines to connect to my IP address.

Within minutes, an IT Administrator mistyped a server name while attempting to map a network drive. The victim's machine transparently attempted to authenticate to my Responder instance using NTLMv2. Responder captured the challenge-response and displayed the IT Admin's NTLMv2 hash in the terminal.

To crack the hash, I saved it to a file and ran Hashcat offline:
```bash
hashcat -m 5600 admin_hash.txt /usr/share/wordlists/rockyou.txt
```

**Outcome:**
The IT administrator's password, `Admin@2024!`, was cracked within seconds due to its presence in standard wordlists. Through a completely passive attack utilizing LLMNR poisoning, I escalated from a physical network connection with zero access to possessing the plaintext credentials of a highly privileged IT administrator. This immediately granted me administrative access to multiple servers and a direct path to domain compromise, highlighting the critical flaw of leaving legacy broadcast protocols enabled.
"""
}

with open('/home/sanchit/Notes/VAPT/ad_chunk_ak', 'r') as f:
    files = f.read().strip().split('\n')

for filepath in files:
    filename = os.path.basename(filepath)
    if filename in scenarios:
        scenario_text = scenarios[filename]
        
        with open('/tmp/scenario.txt', 'w') as sf:
            sf.write(scenario_text)
            
        print(f"Processing {filename}...")
        cmd = ['python3', '/home/sanchit/Notes/VAPT/add_scenario.py', filepath]
        with open('/tmp/scenario.txt', 'r') as sf:
            subprocess.run(cmd, stdin=sf, check=True)
            
print("All files processed successfully.")
