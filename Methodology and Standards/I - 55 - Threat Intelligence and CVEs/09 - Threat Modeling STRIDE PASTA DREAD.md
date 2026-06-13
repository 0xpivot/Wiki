---
tags: [threat-intel, cve, research, vapt]
difficulty: intermediate
module: "55 - Threat Intelligence and CVEs"
topic: "55.09 Threat Modeling STRIDE PASTA DREAD"
---

# Threat Modeling: STRIDE, PASTA, and DREAD

## 1. The Imperative of Threat Modeling

Threat modeling is a structured procedure used to identify potential security threats and vulnerabilities, quantify the seriousness of each, and prioritize mitigation techniques. Crucially, threat modeling is typically performed *before* a single line of code is written. It is the cornerstone of the "Shift-Left" security paradigm.

While VAPT (Vulnerability Assessment and Penetration Testing) evaluates a built, running system, Threat Modeling evaluates the *design* and *architecture*. Fixing an architectural flaw during the design phase costs a fraction of what it costs to fix after deployment.

A successful threat model answers four core questions:
1. What are we building? (Architecture/Data Flow Diagrams)
2. What can go wrong? (Threat identification)
3. What are we going to do about it? (Mitigation)
4. Did we do a good enough job? (Validation)

## 2. Data Flow Diagrams (DFDs)

Before applying any framework, the system must be mapped. The standard tool for this is the Data Flow Diagram.

**Key Elements of a DFD:**
- **External Entities (Rectangles):** Users, browsers, external APIs.
- **Processes (Circles):** Web servers, authentication modules.
- **Data Stores (Parallel Lines):** Databases, file systems, S3 buckets.
- **Data Flows (Arrows):** The movement of data between components.
- **Trust Boundaries (Dotted Lines):** The boundary where data changes its level of trust (e.g., from the Internet to the DMZ, or from a user to the database).

### ASCII DFD Example: Simple Web App
```text
               [ Trust Boundary: Internet vs Internal ]
                              . . . . . . . . . . . . . . . . . . . . .
 [ User ]                     .                                       .
    |                         .                                       .
    | (1. HTTP POST Creds)    .        (2. Query User Hash)           .
    V                         .                 |                     .
 ( Web Server / Login ) <-----------------------+                     .
                              .                 V                     .
                              .         [ User Database ]             .
                              .                                       .
                              . . . . . . . . . . . . . . . . . . . . .
```
*Threats almost always manifest across Trust Boundaries.*

## 3. The STRIDE Framework

Developed by Microsoft, STRIDE is a mnemonic for the six most common categories of security threats. It is used to answer the question: "What can go wrong?"

### 3.1 Spoofing (S)
- **Definition:** Impersonating something or someone else. Violates **Authentication**.
- **Examples:** MAC spoofing, session hijacking, forged emails, stealing credentials.
- **Mitigation:** Strong authentication, MFA, digital signatures, PKI.

### 3.2 Tampering (T)
- **Definition:** Modifying data in transit or at rest. Violates **Integrity**.
- **Examples:** Altering a database record, modifying an API request via Burp Suite, changing log files.
- **Mitigation:** TLS/SSL, digital signatures, file integrity monitoring (FIM), parameterized queries.

### 3.3 Repudiation (R)
- **Definition:** Claiming you didn't perform an action, and the system cannot prove otherwise. Violates **Non-repudiation**.
- **Examples:** A user deleting a file and claiming they didn't; an attacker covering their tracks because logs were disabled.
- **Mitigation:** Centralized, immutable audit logging, digital signatures, blockchain ledgers.

### 3.4 Information Disclosure (I)
- **Definition:** Exposing information to individuals who are not supposed to see it. Violates **Confidentiality**.
- **Examples:** SQL Injection extracting databases, misconfigured S3 buckets, verbose error messages.
- **Mitigation:** Encryption at rest and in transit, strict access controls (RBAC), masking data.

### 3.5 Denial of Service (D)
- **Definition:** Denying or degrading service to valid users. Violates **Availability**.
- **Examples:** Volumetric DDoS attacks, algorithmic complexity attacks (ReDoS), account lockout abuse.
- **Mitigation:** Rate limiting, WAFs, CAPTCHA, auto-scaling, robust input validation.

### 3.6 Elevation of Privilege (E)
- **Definition:** Gaining capabilities without proper authorization. Violates **Authorization**.
- **Examples:** Vertical privilege escalation (User -> Admin) via unpatched exploit, Insecure Direct Object Reference (IDOR).
- **Mitigation:** Principle of Least Privilege, strict authorization checks on every request, sandboxing.

## 4. The DREAD Risk Assessment Model

While STRIDE identifies *what* the threat is, DREAD helps assess *how bad* it is. DREAD is a scoring system (typically 1-10 for each category) to prioritize mitigation efforts.

- **Damage Potential:** If the exploit occurs, how much damage will be caused? (1 = None, 10 = Total system destruction/data loss).
- **Reproducibility:** How easy is it to reproduce the attack? (1 = Nearly impossible/timing dependent, 10 = Consistently works every time).
- **Exploitability:** How much effort and expertise is required? (1 = Nation-state APT, 10 = Script kiddie with a web browser).
- **Affected Users:** If successful, how many users are impacted? (1 = One user, 10 = All users/System-wide).
- **Discoverability:** How easy is it to find the vulnerability? (1 = Requires deep source code access, 10 = Visible in URL or public HTTP headers).

*Note: Microsoft officially abandoned DREAD due to the subjective nature of the scoring (one engineer's 5 is another's 8). It has largely been replaced by CVSS, but remains conceptually useful for internal threat prioritization.*

## 5. The PASTA Framework

PASTA (Process for Attack Simulation and Threat Analysis) is a risk-centric threat modeling framework developed by VerSprite. Unlike STRIDE, which is highly technical, PASTA bridges the gap between technical threats and business impact. It is an attacker-centric, seven-step process.

### The 7 Steps of PASTA:
1. **Define Business Objectives:** Understand the business context. What are we protecting? (e.g., PCI compliance, PII protection, brand reputation).
2. **Define Technical Scope:** What are the boundaries of the application? (Hardware, software, network dependencies).
3. **Application Decomposition:** Create DFDs. Map out trust boundaries, use cases, and entry points.
4. **Threat Analysis:** Gather threat intelligence. What are the active threats targeting this type of technology or industry?
5. **Vulnerability and Flaws Analysis:** Identify weaknesses in the design. (This is where STRIDE could be integrated).
6. **Attack Modeling:** Build attack trees to simulate how an adversary would chain vulnerabilities to achieve their goal.
7. **Risk and Impact Analysis:** Calculate the real risk to the business based on the likelihood and impact, and provide tactical mitigations.

## 6. Threat Modeling in Agile and DevSecOps

Traditional threat modeling was a massive bottleneck, sometimes taking weeks of meetings. Modern methodologies focus on agile threat modeling:
- **Abuser Stories:** Adding "As an attacker, I want to [action] so that I can [impact]" alongside normal user stories in Jira.
- **Threat Modeling as Code:** Using tools like Python-based `pytm` or AWS Threat Composer to generate threat models automatically from code or architecture-as-code files.
- **Iterative Updates:** Only modeling the delta (the changes) in the new sprint, rather than the entire application.

## 7. Deep Dive: STRIDE in Code and Architecture

To truly understand how threat modeling works in practice, VAPT professionals must translate the abstract STRIDE concepts into concrete architectural vulnerabilities.

### 7.1 Spoofing at the Protocol Level
A classic architectural flaw is relying on client-side IP addresses for authentication.
- **The Design:** An internal HR API allows any request originating from the `10.0.0.0/8` subnet to bypass authentication.
- **The Threat (Spoofing):** An external attacker performs IP spoofing, or more practically, finds an SSRF (Server-Side Request Forgery) vulnerability in a public-facing web app to bounce their request internally, spoofing the source IP.
- **The Fix:** Implement Zero Trust architecture. The API must validate a cryptographic token (e.g., JWT or mutual TLS) regardless of the source IP.

### 7.2 Tampering with In-Transit Data
- **The Design:** A mobile application sends a user's high score to a gaming server via HTTP.
- **The Threat (Tampering):** An attacker uses a proxy (like Burp Suite) to intercept the plaintext traffic and modifies the `score=100` parameter to `score=9999999` before forwarding it to the server.
- **The Fix:** Implement TLS pinning on the mobile application to prevent proxy interception, and sign the payload cryptographically on the client device so the server can verify integrity.

### 7.3 Information Disclosure via Side Channels
Information disclosure isn't always a direct database dump. Often, it's an architectural side-channel.
- **The Design:** A password reset function tells the user "Password reset link sent to email" if the account exists, but says "Account not found" if it doesn't.
- **The Threat (Information Disclosure):** An attacker automates a script to test millions of email addresses, discovering exactly which users are registered on the platform. This is critical reconnaissance.
- **The Fix:** Standardize the response. Regardless of whether the account exists or not, the system should respond with: "If that account exists, a reset link has been sent."

## 8. Alternative Frameworks: OCTAVE, VAST, and LINDDUN

While STRIDE and PASTA are dominant, the VAPT expert should be aware of other specialized frameworks.

### 8.1 OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation)
Developed by CERT at Carnegie Mellon University, OCTAVE is heavily focused on organizational risk and strategic assessment rather than technical application-level flaws. It is often used by enterprise compliance and audit teams. It focuses heavily on defining critical assets, the infrastructure that houses them, and the organizational vulnerabilities that could expose them (e.g., poor employee training).

### 8.2 VAST (Visual, Agile, and Simple Threat)
The VAST methodology is designed specifically for integration into Agile software development workflows. It relies heavily on automated threat modeling tools (like ThreatModeler) and creates two distinct types of models:
1. **Application Threat Models:** Built using process flow diagrams, designed for developers.
2. **Operational Threat Models:** Built using Data Flow Diagrams (DFDs), designed for the infrastructure and cloud teams.

### 8.3 LINDDUN (Privacy-Focused)
With the rise of GDPR and CCPA, threat modeling for privacy is critical. LINDDUN is the privacy equivalent of STRIDE. It stands for:
- **L**inkability (Can two datasets be linked to identify a user?)
- **I**dentifiability (Can an individual be isolated?)
- **N**on-repudiation (In a privacy context, forcing a user to own an action they might want kept private).
- **D**etectability (Can an observer know if an individual is participating in a system?)
- **D**isclosure of information.
- **U**nawareness (Users not knowing how their data is used).
- **N**on-compliance (Failing regulatory requirements).

By integrating LINDDUN alongside STRIDE, organizations can ensure they are designing systems that are both secure against attackers and compliant with international privacy laws.

---
## Chaining Opportunities
- **[[06 - MITRE ATT&CK Framework]]:** ATT&CK is heavily used during the "Threat Analysis" and "Attack Modeling" phases of PASTA to simulate realistic adversary behaviors.
- **[[24 - Secure SDLC Basics]]:** Threat modeling is a fundamental requirement in the early design phases of a Secure Software Development Life Cycle.

## Related Notes
- [[25 - Web Application Architecture Analysis]]
- [[40 - Exploit Development Basics]]
- [[48 - Risk Assessment and Management]]
