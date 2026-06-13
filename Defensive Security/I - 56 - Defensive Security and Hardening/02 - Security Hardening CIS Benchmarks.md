---
tags: [defense, hardening, security, vapt]
difficulty: intermediate
module: "56 - Defensive Security and Hardening"
topic: "56.02 Security Hardening CIS Benchmarks"
---

# Security Hardening: CIS Benchmarks

## Introduction to CIS Benchmarks

The Center for Internet Security (CIS) Benchmarks are recognized globally as the gold standard for IT system, network, software, and cloud infrastructure security hardening. While compliance frameworks (like PCI-DSS, HIPAA, or SOC2) tell you *what* you need to do at a high level (e.g., "Implement strong access control"), CIS Benchmarks tell you *exactly how* to do it on a technical level (e.g., "Set 'Enforce password history' to '24 or more password(s)' in `secpol.msc`").

Security hardening is the process of reducing an asset's attack surface. Out of the box, operating systems and applications are configured for maximum usability and compatibility, which often leaves numerous insecure default settings enabled. The CIS Benchmarks provide prescriptive, consensus-based guidance to lock down these systems against modern cyber threats.

For VAPT professionals, understanding CIS benchmarks is a two-way street:
1.  **Defensively**: Using the benchmarks to harden infrastructure and prevent exploitation.
2.  **Offensively**: Exploiting systems where organizations have failed to implement these benchmarks (e.g., exploiting enabled LLMNR/NBT-NS or weak SSH configurations).

---

## Architectural ASCII Diagram: CIS Control Mapping Flow

```text
  [Threat Landscape] ----> informs ----> [CIS Controls (v8)]  (The "What")
                                              |
                                              | mappings & implementation
                                              v
                                      [CIS Benchmarks]        (The "How")
                                              |
               +------------------------------+------------------------------+
               |                              |                              |
      Level 1 Profile                Level 2 Profile                   STIG Mapping
   (Practical Security)           (Defense-in-Depth)             (Gov/Mil Compliance)
               |                              |                              |
               v                              v                              v
      +-----------------+            +-----------------+            +-----------------+
      | OS Configuration|            | App Configuration|           | Cloud Resources |
      | (Win/Linux/Mac) |            | (DB, Web Server) |           | (AWS, GCP, Az)  |
      +--------+--------+            +--------+--------+            +--------+--------+
               |                              |                              |
               +------------------------------+------------------------------+
                                              |
                                              v
                                    [Assessment Tools]
                            (CIS-CAT Pro, OpenSCAP, Nessus, Qualys)
                                              |
                                              v
                               [Remediation & Automation]
                            (Ansible, Chef, Puppet, GPO, MDM)
```

---

## CIS Benchmark Profiles (Levels)

CIS Benchmarks are divided into distinct profiles based on the level of security required and the potential impact on usability.

### 1. Level 1 Profile (Practical/Base Security)
The Level 1 profile provides baseline security recommendations that are highly practical and designed to be implemented rapidly without causing severe performance impacts or breaking core functionalities.
*   **Goal**: Lower the attack surface while keeping the machine entirely usable for typical business operations.
*   **Examples**: Enforcing password complexity, disabling guest accounts, ensuring automatic updates are enabled, and restricting remote registry access.
*   **Audience**: All organizations. This should be the absolute minimum standard.

### 2. Level 2 Profile (Defense-in-Depth/Strict)
The Level 2 profile is considered "defense-in-depth" and is intended for environments where security is paramount (e.g., critical infrastructure, financial institutions, defense contractors).
*   **Goal**: Maximum security. Implementing Level 2 can and will break certain legacy applications and severely restrict user convenience.
*   **Examples**: Disabling IPv6 entirely if not needed, implementing rigorous audit logging for every file system action, restricting local execution via AppLocker/SELinux strict modes.
*   **Audience**: High-security environments. Requires rigorous testing in staging environments prior to production rollout.

### 3. STIG Mapping Profile
Security Technical Implementation Guides (STIGs) are configuration standards dictated by the US Defense Information Systems Agency (DISA). Many CIS benchmarks offer a "STIG Profile" that maps directly to these DoD requirements, bridging the gap between civilian best practices and military compliance.

---

## Core CIS Controls (The Framework)

While the Benchmarks provide the technical steps, they are rooted in the **CIS Critical Security Controls (v8)**. The controls are prioritized into Implementation Groups (IG1, IG2, IG3) based on organizational maturity. The top foundational controls include:

### Control 1: Inventory and Control of Enterprise Assets
You cannot protect what you don't know exists.
*   **Benchmark Action**: Actively identifying all devices connected to the network, utilizing DHCP logging, and employing 802.1X NAC.

### Control 2: Inventory and Control of Software Assets
Identifying and managing all software, mitigating shadow IT.
*   **Benchmark Action**: Utilizing application whitelisting (WDAC/AppLocker) and auditing installed software registries.

### Control 3: Data Protection
Safeguarding sensitive data at rest and in transit.
*   **Benchmark Action**: Enforcing Full Disk Encryption (BitLocker, LUKS) and ensuring only TLS 1.2+ is used on endpoints.

### Control 4: Secure Configuration of Enterprise Assets and Software
This is the heart of the CIS Benchmarks—ensuring systems are not left in default configurations.
*   **Benchmark Action**: Disabling unused ports, removing default accounts, disabling legacy protocols (SMBv1, Telnet).

### Control 5: Account Management
Managing the lifecycle of user credentials and privileges.
*   **Benchmark Action**: Disabling dormant accounts after 45 days, enforcing multi-factor authentication (MFA).

### Control 6: Access Control Management
Enforcing the Principle of Least Privilege.
*   **Benchmark Action**: Removing standard users from the Local Administrators group.

---

## Auditing Systems Against CIS Benchmarks

Manually checking hundreds of registry keys, file permissions, and configuration files is impossible at scale. Automated auditing is essential.

### 1. OpenSCAP (Security Content Automation Protocol)
OpenSCAP is an open-source framework used predominantly in Linux environments to parse SCAP data feeds (like CIS and STIGs) and evaluate the system.
*   **Command Example**:
    ```bash
    # Running an OpenSCAP scan against a RHEL 8 system using standard CIS profile
    oscap xccdf eval \
      --profile xccdf_org.ssgproject.content_profile_cis \
      --results /tmp/scan-results.xml \
      --report /tmp/scan-report.html \
      /usr/share/xml/scap/ssg/content/ssg-rhel8-ds.xml
    ```
*   **Output**: Generates a detailed HTML report showing `Pass`, `Fail`, or `Not Applicable` for every control, along with the exact bash script or Ansible playbook needed to fix the failures.

### 2. CIS-CAT Pro
The official CIS Configuration Assessment Tool (CIS-CAT). It is a Java-based application that ingests the latest CIS XML definitions and scans endpoints (Windows, Linux, macOS) locally or remotely.

### 3. Vulnerability Scanners (Nessus, Qualys, Rapid7)
Most commercial vulnerability scanners have built-in "Compliance Mapping" modules that execute authenticated scans via SSH/WinRM to audit the system against selected CIS baselines.

---

## Anatomy of a Benchmark Recommendation

To understand how rigorous the benchmark is, consider the anatomy of a single recommendation from the **CIS Microsoft Windows Server Benchmark**:

*   **Section**: 2.3.1.5 (Local Policies \> Security Options \> Accounts)
*   **Title**: *Ensure 'Accounts: Limit local account use of blank passwords to console logon only' is set to 'Enabled'*
*   **Profile Applicability**: Level 1
*   **Description**: This policy setting determines whether local accounts that are not password protected can be used to log on from locations other than the physical console.
*   **Rationale**: If a local account has a blank password, an attacker could remotely connect via RDP, SMB, or PowerShell Remoting without authentication.
*   **Audit Method**:
    *   Open `secpol.msc` -> Local Policies -> Security Options
    *   Verify the setting is enabled.
*   **Remediation**:
    *   Using Group Policy: Edit the GPO linked to the servers and enable the policy.
    *   Using Registry: Set `HKLM\System\CurrentControlSet\Control\Lsa\LimitBlankPasswordUse` to `1`.

---

## VAPT Perspective: Weaponizing Benchmark Failures

When organizations fail to implement CIS benchmarks, penetration testers leverage these misconfigurations.

1.  **Failure to Implement Control 4.1 (Disable SMBv1/NetBIOS/LLMNR)**:
    *   *Attacker Action*: The pentester fires up Responder. Without CIS hardening, Windows will blindly broadcast LLMNR requests when DNS fails. Responder poisons this request, captures the NTLMv2 hash, and the attacker cracks it offline or relays it to another machine.
2.  **Failure to Implement Control 5.4 (Restrict Local Admin)**:
    *   *Attacker Action*: The pentester compromises a low-level workstation. Because CIS Level 1 was not followed, the user is a local admin. The pentester dumps LSASS using Mimikatz, grabs Domain Administrator credentials left in memory, and achieves complete domain compromise.
3.  **Failure to Implement Control 14.6 (Secure SSH Configuration)**:
    *   *Attacker Action*: A Linux server allows password authentication and root login over SSH (against CIS guidelines). The pentester brute-forces the root password via Hydra, gaining immediate unrestricted access.

---

## Remediation and Automation Challenges

Applying benchmarks is challenging because applying a blanket Level 1 policy via Windows Group Policy (GPO) or Linux Ansible playbooks will often cause operational outages.

### Best Practices for Rollout:
1.  **Audit Mode First**: Always run a compliance scan first to see what *would* fail without changing anything.
2.  **Phased GPOs / Playbooks**: Break down the remediation into chunks (e.g., "Account Policies" first, then "Network Policies").
3.  **Exemptions via Organizational Units (OUs)**: Move legacy servers that cannot handle strict cryptography to isolated OUs with custom, slightly relaxed policies, but wrap those servers in intense network-level monitoring.
4.  **Configuration Management Drift**: A server hardened today might drift out of compliance tomorrow if an administrator manually changes a setting. Use tools like Chef, Puppet, or Ansible in "enforcing" mode to automatically revert unauthorized changes.

## Chaining Opportunities & Related Notes
*   `[[01 - Defense-in-Depth Layered Security Model]]` - CIS benchmarks represent the implementation of the Host Security layer in the DiD model.
*   `[[03 - Linux Hardening]]` - Technical implementation details mapping to CIS Linux benchmarks.
*   `[[04 - Windows Hardening]]` - Active Directory and GPO-based implementation mapping to CIS Windows benchmarks.
*   `[[05 - Web Server Hardening]]` - Applying CIS principles to Apache, Nginx, and IIS.
