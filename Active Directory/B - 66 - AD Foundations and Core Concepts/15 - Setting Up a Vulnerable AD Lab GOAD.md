---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.15 Setting Up a Vulnerable AD Lab GOAD"
---

# Setting Up a Vulnerable AD Lab (GOAD)

To effectively master Active Directory penetration testing, you cannot rely on theoretical reading or standard, secure default installations of Windows Server. Modern AD attacks exploit misconfigurations, legacy protocol support, and complex trust relationships. 

To practice these securely and legally, security researchers use the **Game of Active Directory (GOAD)**. Created by Mayfly, GOAD is an automated Infrastructure-as-Code (IaC) project that deploys a complex, deeply flawed, multi-domain Active Directory forest tailored specifically for red teaming and VAPT practice.

## Why GOAD?

A default installation of Windows Server 2022 is reasonably secure. To practice attacks like Kerberoasting, AS-REP Roasting, or Unconstrained Delegation, a tester would have to manually create users, alter registry keys, assign SPNs, and break permissions. 

GOAD automates this entirely. It uses **Vagrant** to provision the virtual machines and **Ansible** to configure the operating systems, join the domains, and inject dozens of deliberate vulnerabilities.

### Key Vulnerabilities Provisioned by GOAD
*   **Kerberoasting & AS-REP Roasting:** Multiple accounts configured with SPNs and pre-authentication disabled.
*   **Unconstrained / Constrained / Resource-Based Constrained Delegation:** Intricate delegation paths allowing for ticket manipulation and impersonation.
*   **SMB Signing Disabled:** Allows for NTLM Relay attacks.
*   **IPv6 and LLMNR/NBT-NS Enabled:** Ideal for poisoning attacks via Responder or mitm6.
*   **Vulnerable Certificate Templates (AD CS):** ESC1, ESC2, ESC3, etc., allowing for domain escalation via PKI abuse.
*   **Complex Trust Relationships:** Parent/child domains and external forest trusts for SID History injection and cross-trust lateral movement.

## ASCII Diagram: GOAD v2 Architecture (Game of Thrones Theme)

The standard GOAD lab simulates an enterprise environment split into multiple forests and domains, famously themed after Game of Thrones.

```text
+---------------------------------------------------------------+
|                       FOREST: essos.local                     |
|                                                               |
|   +-----------------------+                                   |
|   |      BRAAVOS DC       |                                   |
|   |     (Domain Ctlr)     |                                   |
|   | IP: 192.168.56.12     |                                   |
|   +-----------------------+                                   |
+---------------------------------------------------------------+
            ^
            |  External Forest Trust (Two-Way)
            v
+---------------------------------------------------------------+
|                      FOREST: sevenkingdoms.local              |
|                                                               |
|   +-----------------------+        +-----------------------+  |
|   |  KINGS LANDING DC     |        |     WINTERFELL DC     |  |
|   | (Forest Root/Parent)  |<------>|     (Child Domain)    |  |
|   | IP: 192.168.56.10     | Trust  |  north.sevenkingdoms  |  |
|   +-----------------------+        |  IP: 192.168.56.11    |  |
|             |                      +-----------------------+  |
|             |                                                 |
|   +-----------------------+        +-----------------------+  |
|   |    CASTEL BLACK       |        |       MEEREEN         |  |
|   |   (Windows Server)    |        |   (Windows Server)    |  |
|   | IP: 192.168.56.22     |        | IP: 192.168.56.23     |  |
|   +-----------------------+        +-----------------------+  |
|                                                               |
+---------------------------------------------------------------+
```

## Setup and Provisioning Workflow

Setting up GOAD requires a robust host machine (Minimum 16GB RAM, 32GB+ highly recommended, 100GB+ SSD storage) and virtualization software. The standard deployment uses VirtualBox or Proxmox.

### 1. Prerequisites (Linux Host)
You need to install Vagrant, VirtualBox, and Ansible.
```bash
sudo apt update
sudo apt install virtualbox vagrant ansible git python3-pip
# Install required Ansible collections
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows
```

### 2. Cloning the Repository
```bash
git clone https://github.com/Orange-Cyberdefense/GOAD.git
cd GOAD
```

### 3. Provisioning the Virtual Machines (Vagrant)
Vagrant reads the `Vagrantfile` and downloads the necessary base Windows images (boxes), sets up the internal network (typically `192.168.56.x`), and boots the VMs.
```bash
cd vagrant/providers/virtualbox
vagrant up
```
*Note: This process can take a significant amount of time depending on internet speed and disk I/O.*

### 4. Injecting Vulnerabilities (Ansible)
Once the base OS is running, Ansible is used to build the Active Directory structure and insert the vulnerable configurations.
```bash
cd ../../../ansible
# Run the main playbook to build the lab
ansible-playbook main.yml -i inventory/goad.ini
```

## Verifying the Deployment

After the Ansible playbook finishes (it takes roughly 1-2 hours), it is critical to verify that the lab is functioning correctly before starting an assessment.

**Using NetExec (formerly CrackMapExec):**
From your Kali/Parrot attacker VM (which must be bridged or NAT'd to the `192.168.56.x` subnet):
```bash
# Check SMB connectivity and domain enumeration
netexec smb 192.168.56.10-23
```
You should see output detailing the domains (e.g., `sevenkingdoms.local`), machine names (e.g., `KINGS-LANDING`), and OS versions. SMB signing should ideally show as `False` on several machines.

## Ethical and Security Warnings

**DO NOT DEPLOY GOAD ON A PRODUCTION NETWORK.**
The GOAD environment is explicitly designed to be vulnerable to highly aggressive, zero-click network attacks (like EternalBlue, ZeroLogon, or PetitPotam). 
*   Always deploy GOAD on an isolated Host-Only adapter.
*   Ensure the virtual machines do not have bridging access to your physical LAN or the internet once provisioned.
*   Treat the lab as actively hostile.

---

## Real-World Attack Scenario

A penetration tester needs to validate a complex Resource-Based Constrained Delegation (RBCD) attack chain before executing it in a client's production environment. To do this safely, they spin up the Game of Active Directory (GOAD) lab on their local hypervisor. After deploying the vulnerable VMs using Vagrant and Ansible, they verify connectivity using NetExec against the `192.168.56.x` subnet. Treating the lab as the target, the tester uses a standard unprivileged user account in the `sevenkingdoms.local` domain to query BloodHound, mapping the path to the `WINTERFELL` DC. They then successfully execute the RBCD exploit in the isolated GOAD environment, proving the concept and refining their toolset without risking disruption to any real-world production networks.

## Chaining Opportunities

*   **BloodHound Mapping**: The absolute first step in the GOAD lab is running BloodHound (via SharpHound or Python-BloodHound) to visualize the massive, deliberately tangled web of ACLs, group delegations, and local admin rights. See [[18 - Active Directory Enumeration with BloodHound]].
*   **Practicing Attack Paths**: Use GOAD to sequentially practice attacks. Start with LLMNR Poisoning -> Capture Hash -> Crack Hash -> Kerberoast -> DC Sync. See [[22 - Pass the Hash and Credential Dumping]] and [[16 - Kerberos Authentication and AS-REP Roasting]].

## Related Notes
*   [[11 - Security Identifiers SIDs and Relative IDs RIDs]]
*   [[12 - Active Directory Schema and Attributes]]
*   [[16 - Kerberos Authentication and AS-REP Roasting]]
*   [[18 - Active Directory Enumeration with BloodHound]]
