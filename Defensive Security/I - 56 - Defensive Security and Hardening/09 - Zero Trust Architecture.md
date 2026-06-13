---
tags: [defense, hardening, security, vapt]
difficulty: intermediate
module: "56 - Defensive Security and Hardening"
topic: "56.09 Zero Trust Architecture"
---

# 56.09 Zero Trust Architecture

## Introduction
Zero Trust Architecture (ZTA) represents a fundamental paradigm shift in cybersecurity philosophy and design. Historically, organizations relied on a "castle-and-moat" perimeter security model: everything outside the corporate network was untrusted, and everything inside was implicitly trusted. Once an attacker (or malicious insider) breached the perimeter firewall, they had free rein to move laterally across the entire network. 

Zero Trust shatters this concept. Its core mantra is: **"Never trust, always verify."** Under ZTA, implicit trust is completely removed, regardless of whether the user or device is inside the corporate LAN, at a coffee shop, or accessing resources in the cloud. Every access request is treated as though it originates from an open, hostile network.

## Core Principles of Zero Trust
Zero Trust is not a single product or software suite you can buy; it is a strategic framework built upon several foundational principles, formalized by standards like NIST SP 800-207:

1. **Verify Explicitly:** Always authenticate and authorize based on all available data points. This includes user identity, location, device health, service or workload context, data classification, and behavioral anomalies.
2. **Use Least Privilege Access:** Limit user access with Just-In-Time (JIT) and Just-Enough-Access (JEA) concepts. If a user only needs access to a resource for one hour, grant it for one hour only.
3. **Assume Breach:** Operate under the assumption that the network is already compromised. Minimize the blast radius, prevent lateral movement via microsegmentation, and use end-to-end encryption to protect data even if the network layer is tapped.

## Architecture Diagram: Zero Trust vs Traditional

```text
===================================================================================
                       Traditional "Castle and Moat"
===================================================================================
     Untrusted                   Firewall Perimeter                 Trusted
  [ Internet ] ---------------------> [ FW ] <------------------ [ Internal Network ]
   Attacker -----------------------> Breaches FW -----------> Moves freely inside!
                                                              No further checks.

===================================================================================
                            Zero Trust Architecture
===================================================================================
                                                           
   User / Device                      Policy Engine /                   Enterprise
   Context                            Trust Broker                      Resources
                                                                     
 +---------------+                  +---------------+             +-----------------+
 | Identity (IdP)|                  |               |             |  App A (SaaS)   |
 | MFA Status    |                  |  Continuous   |  Enforces   +-----------------+
 | Device Health | =======>         |  Risk         | ========>   |  App B (On-Prem)|
 | Location      | (Request Access) |  Assessment   |  Policy     +-----------------+
 | Behavior      |                  |               |             |  Database C     |
 +---------------+                  +---------------+             +-----------------+
                                           ^
                                           | Telemetry & Logs
                                  +--------+--------+
                                  | SIEM / EDR / XDR|
                                  +-----------------+
===================================================================================
```

## The Pillars of Zero Trust

Implementing ZTA involves integrating controls across several fundamental pillars, often evaluated using maturity models (like the CISA Zero Trust Maturity Model):

### 1. Identity
Identity is the new perimeter. Organizations must ensure that the user requesting access is exactly who they claim to be.
- **Strong Authentication:** Multi-Factor Authentication (MFA) is mandatory. The industry is moving toward phishing-resistant methods like FIDO2 keys and biometrics, moving away from SMS codes.
- **Identity Provider (IdP):** Centralized identity management using modern protocols (SAML, OIDC) via platforms like Entra ID, Okta, or Ping Identity.
- **Continuous Authentication:** Authentication isn't a one-time event at login. Systems continuously monitor behavior; if an anomaly is detected (e.g., impossible travel, changing keyboard cadence), re-authentication is immediately required.

### 2. Devices / Endpoints
A verified user on a compromised device is a massive risk. ZTA requires evaluating device posture before granting access.
- **Device Registration:** Only corporate-owned or explicitly registered and managed BYOD devices are trusted.
- **Health Checks:** Before granting access, the trust broker checks if the OS is patched, the EDR agent is running, the firewall is on, and the disk is encrypted. If the device fails compliance, access is denied or restricted, regardless of user identity.

### 3. Networks
While the traditional network perimeter is deprecated, network controls remain critical for limiting the blast radius.
- **Microsegmentation:** Workloads are isolated from each other. Instead of relying on broad **[[08 - Network Segmentation and VLANs]]**, rules are applied at the application or host level using software-defined networking or host-based firewalls.
- **Encryption:** All traffic must be encrypted, both externally and internally. Mutual TLS (mTLS) is standard, ensuring both client and server cryptographically verify each other.

### 4. Applications and Workloads
Applications must be secured independently of the network they reside on.
- **Application Proxies (ZTNA):** Users never connect directly to an application server. Zero Trust Network Access (ZTNA) solutions act as proxies (e.g., Cloudflare Access, Zscaler, Tailscale) that broker the connection only after verifying identity and context.
- **API Security:** Microservices communicating with each other must continuously authenticate and authorize using modern standards (e.g., OAuth 2.0, JWTs).

### 5. Data
Protecting the data itself is the ultimate goal of the architecture.
- **Data Classification:** You cannot protect what you haven't classified. Data must be tagged based on sensitivity.
- **DLP and Encryption:** Implement Data Loss Prevention rules and ensure data is encrypted at rest and in transit.

## The Zero Trust Workflow in Action

1. **The Request:** A user attempts to access an internal application (e.g., the HR portal).
2. **Context Gathering:** The Zero Trust Policy Engine gathers context: Who is the user? Are they using MFA? Is their laptop compliant? Are they logging in from their usual location? Is the EDR reporting any suspicious local activity?
3. **Evaluation:** The Policy Engine evaluates this dynamic context against predefined risk-based rules.
4. **The Decision:**
   - **Allow:** Context is good, grant access.
   - **Block:** Context indicates high risk (e.g., malicious IP, missing critical OS patches), deny access outright.
   - **Remediate/Step-Up:** Context is questionable (e.g., new device, unknown location). Prompt for step-up MFA or grant limited, read-only access.
5. **Continuous Enforcement:** Throughout the session, the environment is continuously monitored. If the EDR detects malware on the laptop during the session, the Trust Broker dynamically revokes access mid-session, instantly severing the connection.

## SASE and SSE
Zero Trust is heavily intertwined with SASE (Secure Access Service Edge) and SSE (Security Service Edge). These cloud-native architectures deliver ZTNA, CASB (Cloud Access Security Broker), and SWG (Secure Web Gateway) functionalities directly from the cloud edge, pushing security closer to the user, regardless of their location, rather than backhauling traffic to a corporate datacenter.

## Challenges in Implementation
- **Legacy Systems:** Old applications (Mainframes, old web apps) often do not support modern authentication protocols like SAML or OIDC, making them difficult to integrate into a ZTA broker without complex gateways.
- **Cultural Shift:** ZTA fundamentally changes how employees work and how IT manages systems. It requires significant change management and executive buy-in.
- **Complexity:** Integrating IdP, EDR, MDM, and networking tools into a cohesive Policy Engine requires massive engineering effort and robust APIs.

## Chaining Opportunities
- Zero Trust fundamentally relies on a dynamic, highly intelligent **[[07 - Firewall Rules Allowlist vs Denylist]]** system to continuously open and close micro-tunnels to applications.
- The principles of ZTA are the ultimate evolution of **[[03 - Principle of Least Privilege]]**.
- **[[08 - Network Segmentation and VLANs]]** forms the physical/logical underlay upon which microsegmentation is built.

## Related Notes
- [[01 - Security Baselines]]
- [[02 - Defense in Depth]]
- [[05 - SIEM and Log Aggregation]]
- [[08 - Network Segmentation and VLANs]]
- [[10 - Intrusion Detection IDS vs IPS]]
