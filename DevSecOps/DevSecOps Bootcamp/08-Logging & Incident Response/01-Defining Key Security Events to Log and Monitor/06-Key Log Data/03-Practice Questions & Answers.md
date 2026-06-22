---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What are some key regulatory standards that dictate specific logging requirements for organizations?**

Logging requirements are often dictated by regulatory standards such as PCI DSS (Payment Card Industry Data Security Standard) and ISO 27001 (Information Security Management System). PCI DSS requires logging of all individual user access to card data and stopping or pausing audit logs. ISO 27001 mandates recording user activity, exceptions, false positives, and information security events, including administrative actions by system administrators and operators.

**Q2. Why is it crucial to synchronize timestamps across all systems in a logging solution?**

Synchronizing timestamps across all systems ensures that logs are consistent and can be correlated effectively during investigations. This synchronization helps in pinpointing the exact sequence of events and provides a clear timeline of activities, which is essential for forensic analysis and incident response. Tools like NTP (Network Time Protocol) can be used to ensure all systems are using a common time source.

**Q3. How does capturing both the 'before' and 'after' states of data transactions help in security auditing?**

Capturing both the 'before' and 'after' states of data transactions provides a comprehensive audit trail that can reveal unauthorized modifications or deletions. This practice helps in identifying and tracing malicious activities, as criminals often attempt to cover their tracks by removing evidence. By maintaining a permanent, read-only copy of the original data, organizations can detect and respond to security breaches more effectively.

**Q4. Explain how user identification can be achieved in a logging solution when direct user accounts are not available.**

User identification in a logging solution can be achieved through various means even when direct user accounts are not available. Techniques include capturing unique identifiers such as browser fingerprints, IP addresses, device IDs, or session tokens. These identifiers can help trace back actions to specific users or devices, providing valuable context during security investigations.

**Q5. What types of activities should be logged according to best practices in a robust logging solution?**

Best practices in a robust logging solution recommend logging activities such as user access, changes made to critical data, system administration tasks, and security events. Specific activities include file deletions, file copies, website visits, and any administrative actions. Additionally, logging should capture details about the source of the activity, such as IP addresses, and maintain a timestamped record of all actions for accurate event correlation and forensic analysis.

**Q6. How can recent real-world examples, such as the Capital One breach, highlight the importance of proper logging practices?**

In the Capital One breach, attackers gained unauthorized access to customer data by exploiting a misconfigured web application firewall. Proper logging practices could have helped in early detection and mitigation of the breach. By maintaining detailed logs of user activities, especially administrative actions, and ensuring timely alerts for suspicious behavior, organizations can reduce the window of opportunity for attackers and enhance their incident response capabilities.

---
<!-- nav -->
[[02-Timestamping and Synchronization|Timestamping and Synchronization]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/06-Key Log Data/00-Overview|Overview]]
