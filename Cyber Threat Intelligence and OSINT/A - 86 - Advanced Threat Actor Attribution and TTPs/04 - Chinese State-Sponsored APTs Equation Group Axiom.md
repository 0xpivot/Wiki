---
tags: [apt, attribution, ttp, vapt]
difficulty: advanced
module: "86 - Advanced Threat Actor Attribution and TTPs"
topic: "86.04 Chinese State-Sponsored APTs Equation Group Axiom"
---

# Chinese State-Sponsored APTs, Axiom, and the Equation Group Intersection

## Introduction to the Chinese Cyber Threat Landscape
The People's Republic of China (PRC) commands an expansive, highly organized, and deeply resourced cyber espionage apparatus. Unlike the disruptive, chaotic, and often destructive nature of Russian cyber operations, Chinese state-sponsored APTs historically focus on massive, sustained intellectual property theft, economic espionage, and strategic intelligence gathering. This aligns precisely with national strategic goals, such as the "Made in China 2025" initiative, aiming to rapidly advance domestic technological, military, and economic capabilities by acquiring foreign proprietary data, bypassing decades of R&D costs.

Chinese cyber operations are primarily orchestrated by two massive entities:
1.  **The Ministry of State Security (MSS):** The civilian intelligence agency responsible for foreign intelligence and counterintelligence. MSS operations often utilize complex networks of private contractors, front companies, and proxy hacker groups (e.g., APT10, APT41, APT31) to maintain plausible deniability.
2.  **The People's Liberation Army (PLA):** Historically the dominant force in Chinese hacking (e.g., the infamous Unit 61398 / APT1). Following massive military reforms, cyber operations were consolidated under the Strategic Support Force (SSF), focusing on military intelligence, advanced R&D theft, and developing cyber warfare capabilities for potential conflict scenarios (e.g., targeting critical infrastructure in Taiwan or the US).

## Group Axiom (APT17, DeputyDog)
**Axiom** (also tracked under names like APT17, DeputyDog, and Group 72) represents a highly sophisticated, highly trusted subset of the Chinese cyber espionage apparatus.
**Motivation:** Corporate espionage, deep intellectual property theft, and the targeting of dissidents and NGOs.
**Target Sectors:** Defense contractors, law firms, IT service providers, mining companies, human rights organizations, and government entities in Asia.

### Axiom TTPs and Operational Style
Axiom is known for its discipline and its ability to conduct prolonged operations without detection. They are considered more advanced than many of the broader, noisier PLA-affiliated groups.
*   **Advanced Watering Hole Attacks:** Axiom pioneered and heavily utilized strategic web compromises (watering hole attacks). They compromise websites frequently visited by their highly specific targets (e.g., specific aerospace industry forums, dissident blogs) and implant exploit code. When the target visits the site, their browser is profiled, and they are silently infected.
*   **Zero-Day Usage:** Historically, Axiom has had access to a steady stream of zero-day vulnerabilities, notably exploiting multiple Internet Explorer and Adobe Flash vulnerabilities to deploy their payloads via their watering holes.
*   **Custom Malware (Derusbi):** Axiom is closely associated with the Derusbi malware family. Derusbi is a sophisticated Remote Access Trojan (RAT) that includes deep kernel-mode rootkit capabilities designed to hide its network connections, processes, and files from local security software. It was shared only among a select group of highly trusted Chinese APTs.
*   **Supply Chain Compromise:** Similar to other advanced groups, Axiom targets the IT supply chain, compromising Managed Service Providers (MSPs) and software vendors to use their trusted connections as a conduit to reach their true, heavily defended downstream targets.

## The Anomaly: The Equation Group
*Note: While often grouped in CTI discussions regarding state-sponsored capabilities, the **Equation Group** is universally attributed to the United States National Security Agency (NSA), specifically the Tailored Access Operations (TAO) unit, not China. However, the intersection between Chinese APTs and Equation Group tools is one of the most critical chapters in modern CTI.*

### What is the Equation Group?
Discovered and named by Kaspersky in 2015, the Equation Group is considered the most advanced threat actor in existence. Their capabilities redefine "Advanced."
*   **HDD Firmware Reprogramming:** They possess the capability to reprogram the firmware of hard disk drives, creating an incredibly persistent area of storage that survives operating system reinstalls, formatting, and military-grade disk wiping.
*   **Incredible Cryptographic Complexity:** Their tools use custom, highly advanced cryptographic implementations and obscure algorithms.
*   **Air-Gap Jumping:** Using complex techniques, including USB-based malware (e.g., the Fanny worm), to bridge air-gapped networks and exfiltrate data from isolated military networks.

### The Intersection: Repurposing Cyber Weapons
The boundary between Chinese cyber operations and the Equation Group blurred significantly due to the phenomenon of "tool repurposing" and cyber counter-espionage.

**The "Jian" Exploit and APT31 (Zirconium):**
Years before the infamous "Shadow Brokers" leak exposed Equation Group tools to the public, Chinese APT groups had quietly captured highly classified NSA exploits.
*   **The Capture:** Chinese threat actors (specifically APT31) captured a powerful Windows local privilege escalation (LPE) zero-day exploit (CVE-2017-0005) deployed by the Equation Group. They likely captured it during an NSA operation against Chinese targets or allied networks, analyzing the payload dropped on their own systems.
*   **The Repurposing:** APT31 reverse-engineered the Equation Group's zero-day, stripped it of its original telemetry, C2 wrappers, and specific deployment mechanisms, and repackaged the core exploit into their own tool, which researchers dubbed "Jian."
*   **The Deployment:** Chinese actors then used "Jian" (the repurposed US zero-day) against American defense contractors and international targets for years before the vulnerability was finally detected and patched by Microsoft.

This event highlights a critical paradigm shift in APT operations: the recycling of state-sponsored cyber weapons. It demonstrates the sophisticated capability of Chinese APTs to detect, analyze, and operationalize the weapons of their most advanced adversaries, turning American cyber weapons against American targets.

## Evolving TTPs: The Modern Chinese Threat Actor
Modern Chinese APTs (such as APT41, APT10, and Hafnium) have evolved significantly from the early days of noisy smash-and-grab operations.

*   **Edge Device Exploitation:** A defining characteristic of recent years is the rapid, mass-exploitation of zero-days in perimeter devices. Chinese groups aggressively target Microsoft Exchange (ProxyLogon/ProxyShell), Pulse Secure VPNs, Fortinet devices, and F5 BIG-IP load balancers. They establish web shells directly on these edge devices, bypassing internal network defenses and endpoint EDR entirely.
*   **Living off the Land (LotL):** Heavy reliance on built-in OS binaries (WMI, PowerShell, Bitsadmin) to avoid dropping custom malware that EDR solutions easily flag.
*   **The "Ransomware" Smokescreen:** Groups like APT41 (which operates with a unique dual mandate of state espionage and personal financial gain) have been observed deploying ransomware. This is often used as a smokescreen to destroy forensic evidence, complicate incident response, and hide the true objective: intellectual property theft.

## ASCII Architecture: The Watering Hole Attack Flow (Axiom TTP)

```text
                               +----------------------------------+
                               |     Targeted Industry Sector     |
                               | (e.g., Aerospace Defense Forum)  |
                               +----------------------------------+
                                                |
          +-------------------------------------+-------------------------------------+
          |                                                                           |
          v                                                                           v
+-------------------+                                                       +-------------------+
| Attacker (Axiom)  |                                                       | Target User (CEO) |
+-------------------+                                                       +-------------------+
          | 1. Identifies weakly secured site frequented by target                    |
          | 2. Exploits site vulnerability (e.g., WordPress flaw)                     |
          | 3. Injects malicious JavaScript / hidden iFrame                           |
          |                                                                           |
          v                                                                           |
+-------------------+                                                                 |
| Compromised Site  | <---------------------------------------------------------------+
| (The Watering Hole|  4. Target visits the trusted site normally
+-------------------+
          |
          | 5. Malicious JS executes in target's browser silently
          | 6. Redirects browser to Exploit Kit server
          v
+-------------------+
| Exploit Kit Server|
| (Attacker Infra)  |
+-------------------+
          | 7. Profiles browser for vulnerabilities (e.g., old Java/Flash/IE versions)
          | 8. Serves specific Zero-Day exploit tailored to the browser
          v
+-------------------+
| Target User PC    |
| (Compromised)     |
+-------------------+
          | 9. Exploit succeeds, drops "Derusbi" RAT with kernel rootkit
          | 10. Establishes persistence and C2 connection
          v
+-------------------+
| Axiom C2 Server   | <--- 11. Attacker begins lateral movement and data exfiltration
+-------------------+
```

## Real-World Attack Scenario
### Scenario: Operation "Dragon's Shadow" (Axiom & Exploit Repurposing)

**Background:**
A major US telecommunications company, crucial to national infrastructure, is the target. The goal is to gain deep access to core routing infrastructure to monitor communications and steal proprietary 5G routing algorithms.

**The Attack Execution:**
1.  **Initial Access via Edge Device:** Instead of phishing, the attackers scan the internet for a newly disclosed, unpatched vulnerability in a specific brand of enterprise VPN appliance. They automate the exploit to drop a lightweight web shell on hundreds of vulnerable devices globally, including the target telecom company.
2.  **Foothold & Reconnaissance:** Through the web shell, the attackers deploy a modified, custom-compiled version of Cobalt Strike. They use LotL techniques (`nltest`, `AdFind`) to map the Active Directory domain architecture.
3.  **Privilege Escalation via Repurposed Exploit:** The attackers encounter highly restricted jump servers requiring elevated privileges. They deploy a sophisticated Local Privilege Escalation (LPE) exploit. Forensic analysis later reveals this exploit is not custom Chinese malware, but rather a modified version of an exploit previously leaked from the Equation Group (similar to the "Jian" scenario). The attackers successfully repurposed a US cyber weapon against US infrastructure.
4.  **Targeting the Core:** With domain admin privileges acquired via the exploit, they move laterally to the jump servers that manage the core telecommunications routers.
5.  **Persistence (Firmware Level):** Demonstrating extreme sophistication, the attackers do not just install malware on the jump servers. They push modified, malicious firmware updates to several core Cisco routers. This firmware backdoor allows them to mirror traffic directly at the hardware level, rendering the compromise invisible to standard host-based network monitoring tools.

**The Investigation:**
The breach is discovered a year later when anomalous, highly encrypted traffic is detected leaving a management interface. The incident response is massive. The use of the repurposed Equation Group exploit initially causes confusion (a potential false flag), but the broader TTPs—the massive edge device exploitation, the specific command-line syntax, and the ultimate goal of strategic telecommunications monitoring—solidify the attribution to a highly advanced Chinese state-sponsored nexus.

## The Convergence of Criminal and State Actors
A unique aspect of the Chinese APT landscape is the blurred line between state-directed operations and cybercriminal enterprise. Groups like APT41 act as state-sponsored espionage units during the day, stealing corporate secrets for the MSS. However, outside of standard operating hours, the same operators use the same state-provided infrastructure and tools to conduct financially motivated attacks, such as compromising video game companies to generate virtual currency, deploying ransomware, or conducting cryptojacking. This dual-mandate complicates attribution, creates a highly volatile threat environment, and makes the actors exceptionally wealthy and resourced.

## Chaining Opportunities
*   The tactic of capturing and repurposing tools directly links to the complexities of attribution and false flags deeply covered in [[01 - The Complexity of Attribution False Flags]].
*   Compare the aggressive edge-device exploitation of Chinese APTs with the stealthy, identity-focused supply chain focus of Russian SVR operations discussed in [[03 - Russian State-Sponsored APTs Cozy Bear Fancy Bear]].

## Related Notes
*   [[01 - The Complexity of Attribution False Flags]]
*   [[02 - Advanced Persistent Threats APT Definitions]]
*   [[05 - North Korean APTs Lazarus Group HIDDEN COBRA]]
*   [[Web Shells and Edge Device Exploitation]]
*   [[Living off the Land (LotL) Techniques]]
