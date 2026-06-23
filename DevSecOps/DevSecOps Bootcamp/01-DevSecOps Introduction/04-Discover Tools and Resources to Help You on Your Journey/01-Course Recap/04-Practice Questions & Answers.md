---
course: DevSecOps
topic: Discover Tools and Resources to Help You on Your Journey
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the current state of DevSecOps adoption according to Gartner's hype cycle?**

The current state of DevSecOps adoption is between 20 to 50% mainstream adoption, with full adoption expected by 2025. This places DevSecOps in a phase where it is gaining significant traction but has yet to reach widespread implementation across all industries.

**Q2. Explain the CIA triad and its relevance to incident response in DevSecOps.**

The CIA triad stands for Confidentiality, Integrity, and Availability. Confidentiality ensures that sensitive information is accessible only to those authorized to have access. Integrity ensures that data is accurate and trustworthy, preventing unauthorized alteration. Availability ensures that systems and data are accessible to authorized users whenever they are needed. In the context of incident response within DevSecOps, the focus is on protecting these three elements. Threats to any of these aspects can lead to breaches or disruptions, and incident response strategies aim to detect, mitigate, and recover from such threats.

**Q3. How does the concept of Bob, a senior developer in a small organization, illustrate the integration of DevSecOps principles?**

Bob represents a scenario where a small organization lacks the resources to maintain a dedicated security operations team. Instead, he must incorporate security practices directly into his development process. This involves automating security monitoring and incident response tasks within the codebase. By doing so, Bob minimizes the need for additional roles and maximizes efficiency, aligning with the DevSecOps principle of integrating security throughout the development lifecycle.

**Q4. Describe the automated workflow for incident response in a DevSecOps environment using the Wired Brain Coffee demo example.**

In the Wired Brain Coffee demo example, the automated workflow for incident response includes logging, monitoring, and automatic response actions. Specifically, an S3 bucket is monitored by AWS Config, which triggers events in a CloudWatch rule. These events can trigger email alerts or invoke Lambda functions to take further action, such as disabling access to the S3 bucket or initiating other security responses. This setup ensures that any suspicious activity is detected and responded to promptly without requiring human intervention.

**Q5. Why is the protection of logs crucial in a DevSecOps environment?**

Logs are critical in a DevSecOps environment because they serve as a record of system activities and can provide valuable insights during incident investigation. Logs are often referred to as the "crime scene" because they contain evidence of what happened during a breach or anomaly. Protecting logs from deletion or tampering is essential to ensure their integrity and usefulness in forensic analysis. Properly securing and backing up logs helps maintain their value as evidence and supports effective incident response and post-incident analysis.

**Q6. How can recent real-world examples like the SolarWinds breach (CVE-2020-16145) highlight the importance of DevSecOps principles?**

The SolarWinds breach, identified as CVE-2020-16145, involved a sophisticated supply chain attack where malicious code was inserted into SolarWinds' Orion software updates. This compromised numerous organizations that relied on SolarWinds products. The breach underscores the importance of integrating security throughout the development lifecycle, including continuous monitoring, automated response mechanisms, and robust logging practices. Had SolarWinds implemented stronger DevSecOps practices, such as regular security audits, automated vulnerability scanning, and comprehensive logging, the impact of the breach might have been mitigated.

---
<!-- nav -->
[[03-Storing and Protecting Evidence and Audit Trails|Storing and Protecting Evidence and Audit Trails]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/04-Discover Tools and Resources to Help You on Your Journey/01-Course Recap/00-Overview|Overview]]
