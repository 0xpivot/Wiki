---
course: DevSecOps
topic: Establishing Your Incident Response Context
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the definition of a security incident according to NIST?**

A security incident, as defined by the National Institute of Standards and Technology (NIST), is a violation or imminent threat of violation of computer security policies, acceptable use policies, or standard security practices. This means any event that breaches the confidentiality, integrity, or availability of a system or data.

**Q2. Explain the three main pillars of security mentioned in the lecture.**

The three main pillars of security are:

1. **Confidentiality**: Ensuring that information is accessible only to those authorized to have access. This involves protecting sensitive data from unauthorized disclosure.
   
2. **Integrity**: Ensuring that data and system resources are accurate and trustworthy. This involves preventing unauthorized modification or manipulation of data.
   
3. **Availability**: Ensuring that authorized users have timely and reliable access to information and associated assets and services. This involves maintaining system uptime and performance.

These pillars are often referred to as the CIA triangle of security.

**Q3. How does security incident management differ from general incident response in IT operations?**

Security incident management specifically focuses on the monitoring and detection of security events and the execution of proper responses to those events. While general incident response in IT operations is aimed at ensuring that computer systems and networks operate effectively and perform well, security incident management has a specific focus on security events and incidents. It aims to develop a well-understood and predictable response to damaging events and computer intrusions, ensuring that security-related alerts and events are handled properly.

**Q4. Provide a recent example of a security incident and how it affected the CIA pillars.**

One recent example is the SolarWinds breach (CVE-2020-1014), which occurred in 2020. This breach involved attackers compromising SolarWinds' software update mechanism to distribute malware. Here’s how it impacted the CIA pillars:

- **Confidentiality**: Sensitive data was exposed to unauthorized parties due to the malware installed through the compromised updates.
  
- **Integrity**: The integrity of the systems was compromised because the attackers could manipulate data and software updates without authorization.
  
- **Availability**: While availability was not directly affected in this case, the breach could have led to disruptions if the attackers chose to disable systems or services.

This breach highlights the importance of robust security incident management practices to detect and respond to such threats effectively.

**Q5. How would you implement a security incident management process in a DevSecOps environment?**

Implementing a security incident management process in a DevSecOps environment involves several steps:

1. **Define Policies and Procedures**: Establish clear policies and procedures for identifying, reporting, and responding to security incidents. Ensure these align with the organization's overall security strategy.

2. **Monitoring and Detection Tools**: Utilize tools like intrusion detection systems (IDS), security information and event management (SIEM) systems, and continuous integration/continuous deployment (CI/CD) pipelines to monitor for security events.

3. **Automated Response Mechanisms**: Implement automated response mechanisms to quickly address detected incidents. For example, setting up alerts and automated remediation scripts can help mitigate threats faster.

4. **Training and Awareness**: Regularly train staff on security best practices and incident response protocols. This ensures everyone understands their role in maintaining security.

5. **Incident Response Team**: Form an incident response team responsible for coordinating the response to security incidents. This team should include members from various departments, including IT, security, legal, and public relations.

6. **Post-Incident Review**: After an incident, conduct a review to understand what happened, how it was handled, and what can be improved. Use this feedback to refine policies and procedures.

By integrating these steps into the DevSecOps workflow, organizations can enhance their ability to manage security incidents effectively.

---
<!-- nav -->
[[03-Understanding Security Incidents in DevSecOps|Understanding Security Incidents in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/02-Establishing Your Incident Response Context/05-Security Incidents and Management/00-Overview|Overview]]
