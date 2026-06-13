---
tags: [defense, hardening, security, vapt, incident-response]
difficulty: advanced
module: "56 - Defensive Security and Hardening"
topic: "56.13 Incident Response PICERL"
---

# Incident Response: The PICERL Framework

## Overview
Incident Response (IR) is the structured, methodological approach an organization takes to manage the aftermath of a security breach or cyberattack. The primary objective is to handle the situation in a manner that limits immediate damage, reduces recovery time and financial costs, and meticulously preserves forensic evidence for legal, regulatory, or root-cause analysis purposes. 

The industry standard for IR methodologies is derived from frameworks provided by NIST (Special Publication 800-61r2) and the SANS Institute. SANS popularized the widely adopted six-step framework known by the acronym **PICERL**: Preparation, Identification, Containment, Eradication, Recovery, and Lessons Learned. Understanding and rigorously applying these phases is critical for modern SOC operations, defensive security, and minimizing business disruption during a crisis.

## Architecture and ASCII Diagram

Below is a visualization of the PICERL lifecycle. It highlights the critical, iterative feedback loop between the Containment, Eradication, and Recovery phases—as responders often discover new compromised assets during cleanup, forcing them back into containment.

```text
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                                THE PICERL LIFECYCLE                               |
|                                                                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +-----------------+                                                              |
|  | 1. Preparation  | <-------------------------------------------------------+    |
|  |   (People,      |                                                         |    |
|  |    Process,     |                                                         |    |
|  |    Technology)  |                                                         |    |
|  +--------+--------+                                                         |    |
|           |                                                                  |    |
|           v                                                                  |    |
|  +-----------------+                                                         |    |
|  | 2. Identification|                                                         |    |
|  |   (Detection,   |                                                         |    |
|  |    Triage,      |                                                         |    |
|  |    Declaration) |                                                         |    |
|  +--------+--------+                                                         |    |
|           |                                                                  |    |
|           v                                                                  |    |
|  +-----------------+       +-----------------+       +-----------------+     |    |
|  | 3. Containment  | ----> | 4. Eradication  | ----> | 5. Recovery     |     |    |
|  |   (Short-term,  | <---- |   (Root Cause,  | <---- |   (Restore,     |     |    |
|  |    Long-term)   | (Iter)|    Removal)     | (Iter)|    Monitor)     |     |    |
|  +--------+--------+       +--------+--------+       +--------+--------+     |    |
|           |                         |                         |              |    |
|           |                         |                         |              |    |
|           +-------------------------+-------------------------+              |    |
|                                     |                                        |    |
|                                     v                                        |    |
|                            +-----------------+                               |    |
|                            | 6. Lessons      |                               |    |
|                            |    Learned      | ------------------------------+    |
|                            |   (Post-Mortem, |                                    |
|                            |    Improvement) |                                    |
|                            +-----------------+                                    |
+-----------------------------------------------------------------------------------+
```

## 1. Preparation (The Most Critical Phase)

Preparation is the foundation of incident response. You cannot effectively respond to a sophisticated attack if you do not have the necessary tools, processes, and personnel in place beforehand. A poorly prepared organization will resort to panic-driven decisions, often leading to exacerbated damage, destruction of forensic evidence, and PR disasters.

**Key Components:**
-   **Policies and Governance:** Developing a comprehensive Incident Response Plan (IRP) authorized by executive leadership. This defines roles (Incident Commander, Lead Investigator), legal/PR escalation paths, and thresholds for declaring an incident.
-   **Playbooks (Runbooks):** Creating specific, step-by-step technical guides for handling common incident types (e.g., Ransomware, Business Email Compromise, Insider Threat, DDoS). 
-   **Tools and Technology:** Deploying required defensive tooling (SIEM, EDR, Network Forensics), ensuring adequate log retention policies are enforced, and pre-deploying forensic collection agents (e.g., KAPE, GRR, Velociraptor) across the fleet.
-   **Team Readiness:** Conducting regular training, tabletop exercises (simulated text-based scenarios), and purple team simulations to build "muscle memory" for the IR team and executives.
-   **Out-of-Band Communication:** Establishing secure, alternative communication channels (e.g., Signal groups, a separate cloud tenant for Slack/Teams, physical burner phones) in case the primary corporate network is compromised by the attacker.

## 2. Identification (Detection and Analysis)

This phase involves detecting anomalous activity, verifying that an actual security incident has occurred (as opposed to an IT outage or a false positive), and determining the initial scope.

**Key Components:**
-   **Detection & Triage:** Monitoring alerts from SIEMs, IDSs, and EDRs, or receiving external reports. Tier 1 analysts perform the initial triage to confirm malicious intent.
-   **Scoping (Blast Radius):** Determining the extent of the compromise. Which systems are affected? Have domain admin credentials been compromised? What type of data (PII, PHI, Source Code) is involved?
-   **Categorization and Prioritization:** Assigning a severity level based on the potential impact on business operations and data confidentiality (e.g., Severity 1: Enterprise-wide ransomware vs. Severity 4: Single user phishing click).
-   **Declaration:** The formal act of declaring an incident. This triggers the activation of the IR Team (IRT), changes operational priorities, and may require notifying legal counsel or cyber insurance providers.

## 3. Containment

Containment is about stopping the bleeding. The immediate goal is to limit the spread of the attack, prevent data exfiltration, and protect critical assets. Containment strategies must be carefully balanced against business continuity requirements.

**Key Components:**
-   **Short-Term Containment:** Immediate, tactical actions to halt the attack's progression. Examples:
    -   Isolating a compromised host from the network using an EDR platform (network lock).
    -   Disabling compromised user accounts in Active Directory.
    -   Null-routing malicious C2 IP addresses at the perimeter firewall.
    -   *Crucially: Avoid immediately powering off systems, as this destroys highly valuable volatile memory evidence. Disconnect from the network, but leave powered on if possible.*
-   **Long-Term Containment:** More robust measures designed to keep the environment temporarily secure while the root cause is fully investigated and eradicated. This could involve segmenting entire network enclaves, applying emergency block rules via Group Policy, or rebuilding critical services from known-good offline backups.
-   **Evidence Preservation:** Before taking destructive containment actions, forensic images of disks and memory MUST be acquired according to strict chain-of-custody procedures.

## 4. Eradication

Once the threat is effectively contained and evidence is preserved, the focus shifts to completely removing the adversary, their tools, and their artifacts from the environment.

**Key Components:**
-   **Root Cause Analysis:** Determining exactly *how* the attacker gained entry (e.g., exploiting an unpatched VPN appliance vulnerability, spear-phishing, stolen credentials). You cannot truly eradicate the threat if the initial entry vector remains open.
-   **Artifact Removal:** Deleting malicious files, backdoors, webshells, and destroying persistence mechanisms (e.g., malicious scheduled tasks, registry Run keys, hijacked DLLs, compromised services).
-   **Remediation:** Patching the exploited vulnerabilities across the entire enterprise, resetting passwords for all compromised accounts (and potentially all accounts if AD is fully compromised), and tightening configuration baselines to prevent reinfection.
-   **Active Directory Sanitation:** If AD is deeply compromised (e.g., Golden Ticket attack), this phase is extremely complex, requiring a double password reset of the `KRBTGT` account and a comprehensive review of all group policies, ACLs, and domain trusts.

## 5. Recovery

Recovery involves restoring systems and operations to normal functionality while strictly ensuring they are no longer vulnerable to the specific attack that caused the incident.

**Key Components:**
-   **Restoration:** Rebuilding systems from clean, offline backups, reinstalling operating systems and applications from trusted media, and restoring validated data.
-   **Validation:** Rigorously testing the restored systems to ensure they are fully functional, patched, and secure before reintroducing them to the production network.
-   **Continuous Monitoring:** Placing the recovered systems under heightened scrutiny. Attackers frequently attempt to return to known targets; the SOC must maintain vigilant monitoring for any resurgence of the original TTPs or related IoCs.
-   **Communication:** Notifying stakeholders, customers, and regulatory bodies that operations have returned to normal and transitioning out of crisis management mode.

## 6. Lessons Learned (Post-Incident Activity)

Often neglected in the rush to return to normal, this is arguably the most vital phase for long-term security maturity. It involves a critical, blameless review of the incident and the team's response.

**Key Components:**
-   **Post-Mortem Meeting:** Gathering all involved parties (SOC, IT Ops, Legal, Management) within a week of the incident resolution to discuss the events.
-   **Documentation:** Creating a comprehensive final incident report detailing the precise timeline, impact, root cause, forensic findings, and response actions taken.
-   **Improvement Identification:** Asking critical questions: What went well? What failed? Were the playbooks accurate? Did our tools provide adequate visibility? Was communication effective?
-   **Action Items:** Creating concrete, assigned tasks to remediate systemic vulnerabilities, improve detection rules, update IR playbooks, and acquire necessary tools or training. This output feeds directly back into the **Preparation** phase, closing the loop.

## The Iterative Reality
It is vital to note that Containment, Eradication, and Recovery are rarely linear. During eradication, you will likely discover a new compromised server or a previously unseen backdoor, forcing you to step back into the Containment phase for that specific asset before proceeding. This iterative cycle continues until the environment is clean.

## Chaining Opportunities
-   The Identification phase relies heavily on the alerts, analytics, and telemetry generated by a well-configured [[11 - SIEM Concepts Log Aggregation Alerting]].
-   The execution of the PICERL framework is the primary responsibility of the Tier 2 and Tier 3 analysts operating within the structure defined in [[12 - SOC Operations Tier 1 2 3 Overview]].
-   During Containment and Eradication, responders will extensively utilize methodologies from [[14 - Digital Forensics Evidence Collection]] to preserve data, and [[15 - Memory Forensics Volatility]] to identify advanced, fileless malware.

## Related Notes
-   [[11 - SIEM Concepts Log Aggregation Alerting]]
-   [[12 - SOC Operations Tier 1 2 3 Overview]]
-   [[14 - Digital Forensics Evidence Collection]]
-   [[15 - Memory Forensics Volatility]]
