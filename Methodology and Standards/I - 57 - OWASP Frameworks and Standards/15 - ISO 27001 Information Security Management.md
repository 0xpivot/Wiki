---
tags: [owasp, compliance, standards, vapt]
difficulty: advanced
module: "57 - OWASP Frameworks and Standards"
topic: "57.15 ISO 27001 Information Security Management"
---

# ISO 27001 Information Security Management System

## Introduction to ISO/IEC 27001

ISO/IEC 27001 is the premier internationally recognized standard for creating, implementing, maintaining, and continually improving an Information Security Management System (ISMS). 

Unlike PCI DSS, which prescribes exact technical requirements (e.g., "you must use TLS 1.2 or higher"), ISO 27001 is fundamentally risk-based and framework-oriented. It does not dictate specific technologies or configurations. Instead, it mandates a management structure designed to systematically identify risks and apply appropriate controls to mitigate those risks to a level acceptable to the business. 

For a VAPT (Vulnerability Assessment and Penetration Testing) professional, encountering an organization holding an ISO 27001 certification indicates mature management processes and a structured approach to security, though it does not guarantee absolute technical security. VAPT activities act as a critical verification mechanism within the broader ISMS.

## The ISMS and PDCA Cycle Architecture

```text
       ISO 27001 Continuous Improvement Cycle (PDCA)
+-------------------------------------------------------------+
|                                                             |
|           [ P L A N ]                             [ A C T ] |
|  Establish ISMS policy, objectives,      Take corrective and|
|  processes, and risk assessments.      preventative actions.|
|           |                                       ^         |
|           v                                       |         |
|                                                             |
|  [ D O ]                                      [ C H E C K ] |
|  Implement and operate the ISMS      Assess and measure ISMS|
|  policies, controls, processes.      performance vs policy. |
|           |                                       ^         |
|           +---------------------------------------+         |
|                                                             |
+-------------------------------------------------------------+
                            |
         +------------------v------------------+
         |     ISO 27001 Annex A Controls      |
         | (Technical and Operational mapping) |
         +-------------------------------------+
```

## Information Security Management System (ISMS)

The core concept of ISO 27001 is the ISMS. An ISMS is a systematic, comprehensive approach to managing sensitive company information so that it remains secure. It includes people, processes, and IT systems by applying a risk management process. 

The primary goal of the ISMS is to preserve the confidentiality, integrity, and availability (CIA triad) of information.

### The Plan-Do-Check-Act (PDCA) Cycle
While explicitly removed as a strict requirement in recent iterations in favor of a more general "continuous improvement" model, PDCA remains the underlying philosophy of an effective ISMS.
1. **Plan**: Establish the context of the organization, identify risks to information security, evaluate those risks, and select appropriate treatments.
2. **Do**: Implement the risk treatment plan and deploy the chosen controls.
3. **Check**: Monitor, measure, audit, and review ISMS performance. This is where VAPT heavily integrates, providing empirical evidence of control effectiveness.
4. **Act**: Make changes to continually improve the ISMS based on the results of the 'Check' phase.

## Risk Assessment and Risk Treatment

A formal, documented Risk Assessment is the engine that drives ISO 27001.
1. **Identify Risks**: Identify assets, threats to those assets, and vulnerabilities that could be exploited.
2. **Analyze Risks**: Determine the likelihood of a threat exploiting a vulnerability and the potential business impact.
3. **Evaluate Risks**: Compare the analyzed risks against the organization's documented risk appetite.
4. **Risk Treatment**: Once a risk is evaluated, the organization must decide how to handle it:
   - **Mitigate**: Apply technical or administrative controls (e.g., implementing a WAF, conducting regular VAPT) to reduce the risk.
   - **Transfer**: Transfer the financial impact of the risk (e.g., buying cybersecurity insurance or outsourcing a risky process to a specialized third party).
   - **Avoid**: Stop the activity that is causing the risk entirely.
   - **Accept**: Management formally accepts the risk (this must be documented and signed off by senior leadership).

## Statement of Applicability (SoA)

The SoA is arguably the most important document in an ISO 27001 audit. It lists all the reference controls from Annex A of the standard. 

For every single control, the organization must explicitly state:
1. Is this control applicable to our organization?
2. If yes, how is it implemented? (Referencing policies, procedures, or technical tools).
3. If no, what is the formal justification for excluding it?

## ISO 27001 Annex A Controls (Technical Deep Dive)

While the main body of the standard (Clauses 4-10) dictates the requirements for the management system, Annex A provides a reference list of information security controls. 

*Note: ISO 27001:2022 restructured these significantly from the older 2013 version into 4 main themes: Organizational, People, Physical, and Technological. The concepts remain the same.*

Here are critical technical domains highly relevant to VAPT:

### A.8 Asset Management
- **Inventory of Assets**: You cannot secure what you don't know exists. Pentesting often uncovers shadow IT, forgotten staging servers, or abandoned assets. Finding these during an engagement directly highlights failures in the organization's Asset Management controls.

### A.9 Access Control
- **Access Rights and Provisioning**: Implementing strict RBAC (Role-Based Access Control) and the Principle of Least Privilege. Pentests targeting privilege escalation, lateral movement, or IDOR (Insecure Direct Object Reference) vulnerabilities are directly testing the effectiveness of these controls.

### A.10 Cryptography
- **Policy on Cryptographic Controls**: Managing keys securely and defining approved cryptographic algorithms. Pentests check for weak ciphers, expired certificates, and improper key storage.

### A.12 Operations Security / Technological Controls
- **Logging and Monitoring**: Audit logs must be recorded, protected, and regularly analyzed. Red team engagements test whether the Security Operations Center (SOC) actually detects the malicious activity defined in the ISMS.
- **Protection from Malware**: EDR (Endpoint Detection and Response) and Antivirus deployment.
- **Vulnerability Management**: The organization must obtain information about technical vulnerabilities, evaluate exposure, and take measures. This directly mandates routine vulnerability scanning and patch management.

### A.14 System Acquisition, Development and Maintenance
- **Secure SDLC**: Integrating security into the software development lifecycle.
- **Security Testing**: Application security testing (SAST/DAST) and manual penetration testing must occur before major releases and periodically in production environments.

### A.16 Information Security Incident Management
- **Reporting and Responding**: VAPT (specifically purple or red teaming) tests the incident response capabilities. If an organization is breached during a pentest and the internal team fails to follow their documented IR plan, it is an audit non-conformity.

## Integrating VAPT into ISO 27001

VAPT is primarily a verification activity within the 'Check' phase and a risk identification activity within the 'Plan' phase.

1. **Risk Identification**: A pentest identifies technical vulnerabilities that must be fed back into the formal Risk Assessment registry to adjust risk scores.
2. **Control Verification**: If the SoA claims that "Web applications are protected against OWASP Top 10 via a Web Application Firewall and secure coding practices," a clean VAPT report is the empirical evidence presented to the external auditor to prove that claim is actually true.
3. **Continuous Improvement**: The remediation of vulnerabilities found during a pentest serves as concrete evidence of the 'Act' phase.

## Internal vs External Audits for Certification

To achieve and maintain ISO 27001 certification, an organization undergoes multiple types of audits:
- **Internal Audit**: Conducted by independent internal staff or consultants. It reviews the ISMS against the ISO standard to prepare for the formal audit and identify gaps.
- **External Audit (Stage 1)**: A documentation review by an accredited external certification body to ensure the ISMS is designed correctly.
- **External Audit (Stage 2)**: The main event. Evidence collection. The auditor asks for proof that controls are operating as designed (e.g., "Show me the pentest report from Q3 and the Jira tickets proving the high-risk vulnerabilities were patched within your SLA").
- **Surveillance Audits**: Annual check-ups to ensure the ISMS is maintained.
- **Recertification**: A full audit every three years to renew the certificate.

## Transitioning from ISO 27001:2013 to 2022

The 2022 update brought the standard in line with modern cloud architectures, remote work, and contemporary threats:
- Added **Threat Intelligence** controls (gathering information on threat actors and TTPs).
- Added **Information Security for Use of Cloud Services** (explicitly addressing shared responsibility models in AWS/Azure/GCP).
- Added **Data Masking** and **Data Leakage Prevention (DLP)** controls.
- Added **Secure Coding** as an explicit control, aligning closely with OWASP recommendations.

## Synergies with NIST and SOC 2

- **NIST CSF**: While NIST provides a great technical taxonomy (Identify, Protect, Detect, Respond, Recover), ISO 27001 provides the rigorous governance, auditing structure, and global certification mechanism. Organizations often use NIST frameworks to implement the specific technical controls required by ISO 27001's SoA.
- **SOC 2**: Highly popular in the US, SOC 2 focuses on Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy). SOC 2 generates an attestation report detailing how specific controls operated over a period of time, whereas ISO 27001 provides a certificate that the management system conforms to the standard. They are highly complementary and often pursued together.

## Chaining Opportunities
- **Auditor Focus**: Pentesting an organization preparing for an ISO 27001 audit should heavily focus on identifying bypasses to their documented controls. For example, if the ISMS mandates MFA for all remote access, finding a legacy VPN endpoint or an obscure admin panel lacking MFA is a critical finding that could result in a major audit non-conformity.
- **Supply Chain Attacks**: ISO 27001 heavily emphasizes supplier relationships. Compromising an organization via a poorly secured third-party integration highlights a failure in their vendor risk management controls.

## Related Notes
- [[12 - NIST Cybersecurity Framework]]
- [[14 - GDPR Security Requirements for Developers]]
- [[13 - PCI DSS Payment Card Security Requirements]]
- [[11 - Introduction to Continuous Integration Security]]
