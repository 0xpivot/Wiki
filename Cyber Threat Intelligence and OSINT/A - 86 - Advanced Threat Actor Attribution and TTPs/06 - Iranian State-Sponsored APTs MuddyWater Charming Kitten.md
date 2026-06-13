---
tags: [apt, attribution, ttp, vapt]
difficulty: advanced
module: "86 - Advanced Threat Actor Attribution and TTPs"
topic: "86.06 Iranian State-Sponsored APTs MuddyWater Charming Kitten"
---

# 86.06 Iranian State-Sponsored APTs: MuddyWater & Charming Kitten

## 1. Overview of the Iranian Cyber Threat Landscape

The Iranian state-sponsored cyber threat landscape has matured significantly over the past decade, transitioning from simplistic website defacements and basic DDoS attacks to highly sophisticated, sustained cyber espionage and destructive operations. Iranian Advanced Persistent Threats (APTs) are heavily aligned with the strategic, geopolitical, and intelligence-gathering interests of the Islamic Republic of Iran, particularly the Islamic Revolutionary Guard Corps (IRGC) and the Ministry of Intelligence and Security (MOIS).

Key characteristics of Iranian APTs include:
- **Opportunistic Initial Access:** Frequent exploitation of newly disclosed vulnerabilities (N-days) in edge devices (e.g., VPNs, Microsoft Exchange, Fortinet).
- **Reliance on Living off the Land (LotL):** Heavy use of built-in Windows tools like PowerShell, WMI, and scheduled tasks to avoid detection.
- **Use of Legitimate RMM Tools:** Abuse of Remote Monitoring and Management software like AnyDesk, ScreenConnect, and Atera for persistent access.
- **Destructive Capabilities:** Periodic use of wipers (e.g., Shamoon, ZeroCleare) disguised as ransomware or deployed purely for disruption.
- **Social Engineering:** Elaborate, long-term credential harvesting campaigns using fake personas and sophisticated phishing infrastructure.

Two of the most prominent and active groups are MuddyWater and Charming Kitten.

## 2. MuddyWater (MERCURY, Static Kitten, Seedworm)

MuddyWater, assessed to be a subordinate element within the Iranian Ministry of Intelligence and Security (MOIS), has been active since at least 2017. They primarily target telecommunications, local government, defense, and IT services across the Middle East, Asia, and occasionally Europe and North America.

### 2.1 Strategic Objectives
- **Espionage and Intelligence Gathering:** Collecting strategic information from regional adversaries (e.g., Israel, Saudi Arabia).
- **Access Brokering:** Establishing initial access that is sometimes handed off to other state-sponsored actors for destructive attacks.
- **IT and Telecom Targeting:** Compromising telecom providers to track high-value targets, monitor communications, and intercept SMS-based MFA.

### 2.2 Initial Access and Delivery
MuddyWater heavily relies on spear-phishing campaigns containing malicious attachments.
- **Malicious Macros:** Historically, they used weaponized Word documents with VBA macros.
- **Phishing Links:** Sending links to file-hosting services (e.g., OneDrive, Dropbox) hosting archives (ZIP/RAR) containing LNK files or executable payloads.
- **Exploitation:** They rapidly adopt public exploits for unpatched edge vulnerabilities (e.g., Log4Shell, ProxyLogon).

### 2.3 Tooling and Malware Arsenal
MuddyWater is infamous for its evolving custom toolset, heavily reliant on script-based malware.

1. **MuddyC3:** A custom Python-based C2 framework used extensively in older campaigns, allowing for the generation of PowerShell payloads.
2. **PowGoop:** A DLL hijacking-based loader that decrypts and executes a PowerShell-based backdoor.
3. **Mori Backdoor:** A custom backdoor facilitating command execution and data exfiltration.
4. **PhonyC2:** A custom C2 framework developed in Python, heavily utilized since 2022.
5. **Legitimate Tools:** Extensive use of Syncro, Atera, SimpleHelp, and ScreenConnect for persistent C2.

### 2.4 Infrastructure and C2 Characteristics
- **Compromised Infrastructure:** Frequent use of compromised legitimate WordPress websites to host payloads or act as C2 proxies.
- **Cloud Services:** Abuse of AWS, Azure, and legitimate SaaS platforms for staging payloads and exfiltrating data, blending malicious traffic with legitimate TLS communications.

## 3. Charming Kitten (APT35, Phosphorus, TA453, Magic Hound)

Charming Kitten, believed to be affiliated with the IRGC, focuses heavily on espionage, targeting dissidents, journalists, human rights activists, academic researchers, and political figures globally.

### 3.1 Strategic Objectives
- **Surveillance of Dissidents:** Monitoring Iranian expatriates and political opposition.
- **Academic and Think-Tank Targeting:** Gathering intelligence from Western researchers and policy analysts focused on the Middle East.
- **Credential Harvesting:** Stealing email credentials to monitor communications and map social networks.

### 3.2 Initial Access and Delivery
Charming Kitten is highly adept at complex, long-term social engineering.
- **Persona Development:** Creating highly realistic fake personas on LinkedIn, Twitter, and via email, often masquerading as journalists, think-tank fellows, or conference organizers.
- **Interview Lures:** Inviting targets to fake webinars or interviews, leading them to phishing pages designed to steal credentials.
- **Multi-Factor Authentication (MFA) Bypass:** Utilizing sophisticated reverse-proxy phishing kits (e.g., Evilginx2) to capture session cookies and bypass MFA.

### 3.3 Tooling and Malware Arsenal
1. **Hyperscrape:** A specialized tool designed to steal user data from Gmail, Yahoo, and Microsoft Outlook by automating the extraction of emails after a successful account compromise.
2. **MacDownloader:** A macOS malware used to steal keychain data and system information.
3. **PowerLess Backdoor:** A PowerShell-based backdoor that uses a unique execution chain, often bypassing local execution policies.
4. **Sponsor:** A backdoor used to gather system information and execute arbitrary commands.

### 3.4 Infrastructure and C2 Characteristics
- **Domain Typo-squatting:** Registering domains that closely mimic legitimate news organizations, think tanks, or login portals (e.g., `mail-google.com` instead of `mail.google.com`).
- **Dynamic DNS:** Extensive use of DDNS services for C2 infrastructure.

## 4. Visualizing the Attack Flow

```ascii
+-----------------------------------------------------------------------------------+
|                         MUDDYWATER INFECTION CHAIN                                |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Attacker]                                                                       |
|      |                                                                            |
|      v                                                                            |
|  [Spear-Phishing Email] ---> Contains malicious .ZIP archive                      |
|      |                                                                            |
|      v                                                                            |
|  [Target Executes .LNK] ---> Downloads payload via Living-off-the-Land (curl)     |
|      |                                                                            |
|      v                                                                            |
|  [Initial Payload Exec] ---> PowerShell script executes, connects to C2           |
|      |                                                                            |
|      v                                                                            |
|  [C2 Server]            <--- Establishes persistence (Scheduled Task)             |
|      |                                                                            |
|      v                                                                            |
|  [Post-Exploitation]    ---> Drops RMM Tools (e.g., Atera, Syncro)                |
|      |                       Executes PowGoop DLL hijacking loader                |
|      |                                                                            |
|      v                                                                            |
|  [Lateral Movement]     ---> WMI, Pass-the-Hash, PsExec                           |
|      |                                                                            |
|      v                                                                            |
|  [Data Exfiltration]    ---> Archives data (WinRAR) & exfiltrates via custom C2   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## 5. Advanced Attribution Techniques

Attributing activities to these groups involves correlating multiple data points:
- **Infrastructure Overlap:** Identifying shared IP addresses, SSL certificates, or domain registration patterns (e.g., using specific registrars or naming conventions favored by Iranian actors).
- **Code Similarity:** Finding shared functions or encryption routines between different malware families (e.g., linking MuddyC3 code structure to newer PhonyC2 iterations).
- **Victimology:** The specific targeting of Iranian dissidents or Middle Eastern telecommunications heavily points toward Iranian state interests.
- **Language Artifacts:** Identifying Persian (Farsi) strings, PDB paths containing Iranian developer names, or timezone configurations (UTC+3:30) in malware compiles.
- **TTP Signatures:** MuddyWater's distinct sequence of dropping an LNK file that executes a heavily obfuscated PowerShell one-liner to fetch a secondary stage is a strong behavioral signature.

## 6. Real-World Attack Scenario

### Scenario: MuddyWater Targeting a Middle Eastern Telecom Provider

**Initial Access:** MuddyWater sends a spear-phishing email to a network engineer at a telecom provider. The email, disguised as an urgent HR update, contains a link to a compromised WordPress site hosting a ZIP file (`HR_Update_2026.zip`).

**Execution & Persistence:** The engineer downloads and extracts the ZIP, finding what appears to be a PDF. In reality, it's a malicious LNK file with a PDF icon. Double-clicking the LNK executes a hidden PowerShell command that downloads a VBScript payload. The VBScript creates a persistent scheduled task named `WindowsUpdateTask` that runs every 30 minutes.

**C2 & Tool Deployment:** The scheduled task connects to a MuddyWater C2 server, which instructs the infected host to download and install Atera RMM. The attackers now have GUI and command-line access to the engineer's workstation, independent of their custom malware.

**Lateral Movement & Discovery:** Using the engineer's compromised credentials and built-in Windows tools (`nltest`, `net user`), the attackers map the Active Directory environment. They use WMI to execute commands on remote servers, moving laterally to domain controllers and critical infrastructure segments.

**Objective Execution:** The attackers locate servers handling SMS routing. They deploy custom scripts to monitor and exfiltrate SMS messages, specifically looking for MFA tokens of high-value targets (e.g., political figures) to facilitate account takeovers in separate, concurrent operations. They also deploy a custom backdoor like PowGoop to maintain deep, stealthy access even if the Atera installation is detected and removed.

## 7. YARA Rule Example: Detecting MuddyWater PowGoop

```yara
rule APT_MuddyWater_PowGoop_Loader {
    meta:
        author = "CTI Team"
        description = "Detects PowGoop DLL hijacking loader used by MuddyWater"
        date = "2026-06-10"
        reference = "Internal CTI Research"
        tags = "apt, muddywater, powgoop, loader"
    strings:
        // PowGoop heavily relies on obfuscated PowerShell and specific exported functions
        $export1 = "GoogleUpdate" ascii wide
        $ps_indicator = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden" nocase ascii wide
        $obfuscation_pattern = { 4? 6? 6? 7? 6? 6? 6? 6? 6? 7? 6? 6? } // Pattern match for specific string obfuscation
        $c2_string1 = "/config/update" ascii wide
    condition:
        uint16(0) == 0x5A4D and // PE file
        2 of ($export1, $ps_indicator, $c2_string1) and
        $obfuscation_pattern
}
```

## 8. Deep Dive: PowGoop Execution Chain

The execution chain of PowGoop, heavily favored by MuddyWater, is a masterclass in DLL side-loading and fileless execution. Understanding this chain is crucial for both detection and attribution.

### Phase 1: The Lure and the Dropper
The initial entry point often involves an archive containing a legitimate, signed executable and a malicious DLL. The legitimate executable is usually an older version of a well-known software (like Google Update or a VPN client) that is vulnerable to DLL search order hijacking.

### Phase 2: DLL Hijacking (Side-Loading)
When the user or a scheduled task runs the legitimate executable, the OS attempts to load required DLLs. Because the malicious DLL is placed in the same directory as the executable, the OS loads it instead of the legitimate one found in System32. This technique provides the malicious code with the execution context of a signed, trusted process.

### Phase 3: Decrypting the Payload
The malicious DLL (PowGoop Loader) contains an embedded, encrypted payload. This payload is not another executable, but rather an obfuscated PowerShell script. The loader reads this encrypted blob, decrypts it in memory using a hardcoded key (often a simple XOR or RC4), and prepares it for execution.

### Phase 4: PowerShell Execution
Instead of calling `powershell.exe` directly (which is easily monitored), the loader often utilizes advanced execution techniques. It might inject the decrypted PowerShell script into another process or use the `System.Management.Automation` assembly directly within the context of the hijacked process to execute the script in memory (fileless execution).

### Phase 5: The PowGoop Backdoor
The final stage is the PowGoop backdoor itself, now running filelessly. This script establishes contact with the C2 server. Its primary function is to receive additional PowerShell scripts from the C2, execute them in memory, and return the results. This makes post-exploitation activities extremely difficult to detect via traditional file-based antivirus, as all subsequent tools and commands exist only in RAM.

## 9. Evolution of Charming Kitten's Social Engineering

Charming Kitten distinguishes itself not through elite zero-day development, but through unparalleled, persistent social engineering. Their campaigns are not "spray and pray" but highly targeted, multi-week or multi-month engagements.

### Persona Construction
They invest heavily in creating believable online personas. This involves:
- **LinkedIn Profiles:** Complete with realistic work histories, endorsements from other fake profiles, and connections to legitimate individuals in the target's industry.
- **Twitter Accounts:** Actively retweeting relevant industry news to build credibility.
- **Custom Domains:** Registering domains that look like legitimate personal blogs or small think-tanks (e.g., `institute-of-middle-east-studies.org`).

### The Long Con
A typical Charming Kitten engagement follows a pattern:
1. **Initial Contact:** A benign email or LinkedIn message introducing the persona and establishing common ground (e.g., "I read your recent paper on geopolitical stability in the Gulf...").
2. **Relationship Building:** Exchanging several emails over weeks to build trust. They rarely send a malicious link in the first few interactions.
3. **The Hook:** The persona invites the target to collaborate on a project, review a document, or attend an exclusive online panel/webinar.
4. **The Trap:** The target receives a link to the supposed document or webinar platform. This link leads to a highly convincing phishing page, often protected by CAPTCHAs or requiring a specific password provided by the attacker to evade automated scanners.
5. **MFA Bypass:** The phishing page is usually a reverse-proxy (like Modlishka or Evilginx2) that intercepts the target's credentials and session tokens, including the MFA code, allowing the attackers to hijack the session in real-time.

## 10. Chaining Opportunities
- **Initial Access Analysis:** Link findings here with [[02 - Initial Access Brokers and Exploit Chains]] to understand how these actors might acquire access rather than phish.
- **Obfuscation Analysis:** Connect PowerShell payloads to [[04 - Advanced PowerShell and Living off the Land (LotL) Obfuscation]] for deobfuscation techniques.
- **Incident Response:** Integrate these TTPs into playbooks discussed in [[12 - Threat Hunting and Incident Response Playbooks]].

## 11. Related Notes
- [[07 - Financial Crime Syndicates FIN7 FIN11]]
- [[08 - Analyzing Malware Compilations Timestamps and Toolmarks]]
- [[09 - Code Overlap and String Similarity Analysis]]
- [[10 - Tracking Threat Actors via PDB Paths]]
- [[01 - Introduction to Threat Actor Attribution]]
