---
tags: [apt, attribution, ttp, vapt]
difficulty: advanced
module: "86 - Advanced Threat Actor Attribution and TTPs"
topic: "86.07 Financial Crime Syndicates FIN7 FIN11"
---

# 86.07 Financial Crime Syndicates: FIN7 & FIN11

## 1. Overview of Financially Motivated APTs

Financially motivated threat groups, often referred to as FIN groups (a designation popularized by Mandiant), represent a distinct class of Advanced Persistent Threats. Unlike state-sponsored espionage actors whose goals are intelligence gathering or geopolitical disruption, financial crime syndicates are driven purely by monetary gain. Over the years, these groups have evolved from conducting simple banking trojan campaigns and point-of-sale (POS) malware deployments to orchestrating complex, multi-million dollar ransomware and extortion operations.

Key characteristics of Financially Motivated APTs include:
- **Professionalization:** Operating like legitimate software companies with distinct departments for development, HR, initial access, and negotiations.
- **Affiliate Models:** Heavy reliance on Ransomware-as-a-Service (RaaS) models and Initial Access Brokers (IABs).
- **Rapid Exploitation:** Swiftly weaponizing 1-day vulnerabilities in enterprise software to gain widespread access.
- **Double/Triple Extortion:** Stealing data before encryption to leverage against the victim (and their clients) to force payment.
- **Fluid Affiliations:** Developers and operators frequently move between groups or rebrand to evade law enforcement (e.g., Conti to BlackBasta/Zeon).

Two of the most prolific and sophisticated financial syndicates are FIN7 and FIN11.

## 2. FIN7 (Carbanak Group, Navigator Group, Sangria Tornado)

FIN7 is a highly sophisticated, financially motivated threat group that has been active since at least 2015. Historically, they were notorious for targeting the retail, restaurant, and hospitality sectors to steal payment card data using POS malware. In recent years, they have shifted tactics significantly toward ransomware deployment and data extortion.

### 2.1 Strategic Objectives
- **Monetization:** Maximizing financial return through whatever means are currently most profitable (historically POS theft, currently ransomware).
- **Scale:** Compromising large numbers of organizations simultaneously to increase the likelihood of successful extortion.

### 2.2 Initial Access and Delivery
FIN7's initial access techniques are highly refined and socially engineered.
- **Weaponized Documents:** Sending highly tailored spear-phishing emails with malicious Word or Excel documents. These documents often require the user to enable macros or interact with embedded OLE objects.
- **Fake Front Companies:** FIN7 is known for creating fake cybersecurity companies (e.g., Combi Security, Bastion Secure) to recruit unwary freelance penetration testers and developers to write their tooling and conduct intrusions.
- **USB Drops:** In some targeted campaigns (e.g., targeting hospitality), they have mailed physical USB drives (often disguised as BadUSBs like the LilyGO) containing malicious payloads directly to victims, accompanied by fake gift cards or letters.

### 2.3 Tooling and Malware Arsenal
FIN7 develops and maintains a vast, proprietary arsenal of malware.
1. **Carbanak Backdoor:** A highly capable backdoor used for deep reconnaissance and lateral movement.
2. **GRIFFON (and HALFBAKED):** JavaScript-based reconnaissance and downloader scripts.
3. **DICELOADER (Lizar/Tirion):** A stealthy backdoor and loader designed to evade EDR solutions, often loaded reflectively into memory.
4. **JSSLoader:** A .NET remote access trojan used to download secondary payloads.
5. **Ransomware Affiliations:** FIN7 has been associated with deploying REvil, DarkSide, BlackMatter, and ALPHV/BlackCat ransomware.

### 2.4 Infrastructure and C2 Characteristics
- **Dynamic Infrastructure:** Rapidly cycling domains and IPs to hinder tracking.
- **Front Domains:** Using domains that mimic legitimate services or are parked under seemingly benign registrant information.

## 3. FIN11 (TA505 subset, Clop Ransomware Affiliate)

FIN11 is a financially motivated group that shares significant overlap with the broader TA505 umbrella. FIN11 is particularly known for high-volume malicious email campaigns and their central role in distributing and operating the Clop (Cl0p) ransomware, as well as orchestrating massive zero-day exploitation campaigns against managed file transfer appliances.

### 3.1 Strategic Objectives
- **Mass Infection:** Casting a wide net through massive spam campaigns to compromise as many endpoints as possible.
- **High-Value Extortion:** Targeting large enterprises capable of paying massive ransoms.
- **Data Theft:** Prioritizing the theft of highly sensitive data to fuel their extortion sites (e.g., the Clop leak site).

### 3.2 Initial Access and Delivery
- **High-Volume Phishing:** Sending millions of emails containing malicious attachments (e.g., HTML, Excel, Word) or links to malicious domains.
- **Appliance Exploitation:** FIN11/Clop is infamous for discovering and exploiting zero-day vulnerabilities in enterprise file transfer appliances, including:
  - Accellion FTA (2020/2021)
  - Fortra GoAnywhere MFT (2023)
  - Progress MOVEit Transfer (2023)

### 3.3 Tooling and Malware Arsenal
1. **FlawedAmmyy:** A remote access trojan based on the leaked source code of the legitimate Ammyy Admin software.
2. **GET2:** A downloader used in early stages of the attack chain to fetch subsequent payloads.
3. **SDBbot:** A robust remote access trojan written in C++, used for persistence and lateral movement.
4. **MINIKATZ:** A stripped-down version of Mimikatz used for credential dumping.
5. **DEWMODE:** A web shell specifically developed and deployed during the Accellion FTA exploitation campaigns to exfiltrate data.
6. **Clop Ransomware:** Their primary payload for the final stage of the attack.

### 3.4 Infrastructure and C2 Characteristics
- **Fast Flux:** Utilizing fast flux DNS networks to obscure the true location of their C2 servers.
- **Bulletproof Hosting:** Relying heavily on bulletproof hosting providers in jurisdictions uncooperative with Western law enforcement.

## 4. Visualizing the Attack Flow

```ascii
+-----------------------------------------------------------------------------------+
|                     FIN11 / CLOP TYPICAL ATTACK FLOW                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  PHASE 1: INITIAL ACCESS (Two distinct paths)                                     |
|                                                                                   |
|  [Path A: Phishing]                      [Path B: Zero-Day Exploitation]          |
|  Mass Email Campaign                     Targeting Edge Appliances (e.g., MOVEit) |
|         |                                              |                          |
|         v                                              v                          |
|  User opens malicious .XLS               SQLi/RCE exploit executed                |
|  Executes macro / GET2 downloader        Webshell dropped (e.g., DEWMODE/LEMUR)   |
|         |                                              |                          |
|         v                                              v                          |
|                                                                                   |
|  PHASE 2: FOOTHOLD & ESCALATION                                                   |
|                                                                                   |
|  [Payload Delivery] <-------------------- [Direct Access to Data]                 |
|  SDBbot / FlawedAmmyy installed           Data exfiltrated directly via webshell  |
|         |                                              |                          |
|         v                                              v                          |
|  [Lateral Movement]                       [Extortion Phase]                       |
|  Cobalt Strike deployed                   Victim listed on Clop Leak Site         |
|  Domain Admin compromised                                                         |
|         |                                                                         |
|         v                                                                         |
|  PHASE 3: IMPACT (Ransomware)                                                     |
|                                                                                   |
|  [Data Exfiltration] --> Large archives sent via Rclone/Megasync                  |
|         |                                                                         |
|         v                                                                         |
|  [Deployment] --> Clop Ransomware executed via GPO or PsExec                      |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## 5. Advanced Attribution Techniques

Attributing activities to these financial syndicates requires a deep understanding of the cybercriminal ecosystem:
- **Code Overlap:** Identifying shared codebases or encryption routines in malware (e.g., linking DICELOADER to older FIN7 tooling).
- **Cryptocurrency Tracking:** Analyzing blockchain transactions to trace ransom payments and identify shared wallets among affiliates, linking different ransomware strains to the same underlying operators.
- **TTP Profiling:** FIN7's specific use of heavily obfuscated JavaScript loaders (GRIFFON) or their unique spear-phishing lures (e.g., restaurant complaints) are strong behavioral markers.
- **Affiliate Overlap:** Recognizing that an attack deploying BlackCat ransomware might actually be orchestrated by FIN7 operators acting as affiliates.

## 6. Real-World Attack Scenario

### Scenario: FIN11 Exploitation of Progress MOVEit Transfer

**Initial Access:** In May 2023, FIN11 (operating as the Clop group) began exploiting a zero-day SQL injection vulnerability (CVE-2023-34362) in Progress Software's MOVEit Transfer application. They systematically scanned the internet for vulnerable instances.

**Exploitation & Webshell Deployment:** Upon identifying a vulnerable server, they executed an exploit that bypassed authentication and deployed a custom ASP.NET web shell named LEMURLOOT. This web shell was specifically designed to interact with the MOVEit underlying database.

**Data Exfiltration:** Unlike traditional ransomware attacks requiring lateral movement, the MOVEit servers already contained highly sensitive enterprise data. The attackers used the LEMURLOOT web shell to enumerate files, download configurations (including Azure Blob Storage keys if configured), and exfiltrate massive volumes of data directly from the server.

**Extortion:** No ransomware was deployed on the endpoints. Instead, FIN11 relied entirely on data extortion. They posted the names of hundreds of compromised organizations on the Clop leak site on the dark web, demanding multi-million dollar ransoms to prevent the public release of the stolen data.

## 7. YARA Rule Example: Detecting LEMURLOOT Webshell

```yara
rule FIN11_Clop_LEMURLOOT_Webshell {
    meta:
        author = "CTI Team"
        description = "Detects LEMURLOOT ASP.NET webshell used by FIN11 in MOVEit campaigns"
        date = "2026-06-10"
        reference = "CVE-2023-34362 Analysis"
        tags = "apt, fin11, clop, webshell, moveit"
    strings:
        // Unique headers and parameters expected by the webshell
        $header1 = "X-siLock-Comment" ascii wide
        $header2 = "X-siLock-Step1" ascii wide
        // Specific SQL queries hardcoded in the webshell
        $sql1 = "SELECT * FROM users WHERE" ascii wide
        // Session and password variables used in the webshell logic
        $var1 = "Session[\"siLockPassword\"]" ascii wide
        $var2 = "X-siLock-Set" ascii wide
    condition:
        filesize < 50KB and
        any of ($header*) and any of ($sql*) and any of ($var*)
}
```

## 8. Analyzing FIN7's Shift to Extortion

Initially, FIN7 was exclusively focused on point-of-sale systems. They would compromise a restaurant chain, wait for POS transactions, and steal magstripe data (Track 1 and Track 2 data) to sell on dark web carding forums like Joker's Stash. The decline in the value of stolen credit card data, combined with the rise of EMV chips, forced a pivot.

FIN7 realized that the access they had to corporate networks was inherently more valuable than the credit card data they were extracting. This led to their evolution into ransomware deployment. Instead of stealing a few thousand credit cards, they could hold the entire corporation hostage.

They formed a group known as the "Navigator Group" internally and began deploying the REvil and DarkSide ransomware strains. They operated as highly skilled affiliates, utilizing their proprietary access and lateral movement tools (like DICELOADER) to deploy the ransomware quickly. Their sophisticated initial access techniques, often involving elaborate fake front companies to hire unaware pentesters, allowed them to scale their operations massively. This shift represents a broader trend in cybercrime where the initial access itself is the most valuable commodity.

## 9. Clop's Mass Zero-Day Exploitation Strategy

FIN11, acting as the core operator behind Clop, pioneered a new and devastating approach to ransomware. Rather than the traditional model of spear-phishing an employee, moving laterally, and eventually encrypting domain controllers, Clop focused on identifying and exploiting zero-day vulnerabilities in massive file transfer appliances (Accellion, GoAnywhere, MOVEit).

These appliances are uniquely attractive targets:
1. **Internet Facing:** They are designed to be accessible from the internet, meaning no initial phishing or complex network pivoting is required.
2. **High-Value Data:** They are explicitly used by enterprises to transfer their most sensitive files (financial records, health data, proprietary source code).
3. **Wide Impact:** A single zero-day vulnerability in a popular appliance can instantly grant access to hundreds of Fortune 500 companies simultaneously.

The Clop strategy is entirely data-extortion focused. They do not deploy encryption on these servers; they simply exfiltrate the data via specialized webshells like LEMURLOOT and threaten to leak it. This mass-exploitation model allows for an unprecedented scale of attack and revenue generation.

## 10. Chaining Opportunities
- **Ransomware Forensics:** Link this intelligence with [[14 - Advanced Ransomware Reverse Engineering]] to understand the inner workings of Clop or BlackCat.
- **Webshell Detection:** Connect the LEMURLOOT analysis to [[16 - Hunting and Analyzing Advanced Webshells]].
- **Threat Hunting:** Apply FIN7/FIN11 TTPs to proactive hunting strategies in [[12 - Threat Hunting and Incident Response Playbooks]].

## 11. Related Notes
- [[06 - Iranian State-Sponsored APTs MuddyWater Charming Kitten]]
- [[08 - Analyzing Malware Compilations Timestamps and Toolmarks]]
- [[09 - Code Overlap and String Similarity Analysis]]
- [[10 - Tracking Threat Actors via PDB Paths]]
- [[01 - Introduction to Threat Actor Attribution]]
