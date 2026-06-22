---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the difference between authentication, session management, and access control.**

Authentication is the process of verifying a user's identity, typically through credentials such as a username and password. Session management involves maintaining the user's identity across multiple requests after successful authentication, usually through a session token. Access control determines whether a user has permission to perform specific actions or access particular resources within the application. While authentication confirms who the user is, access control ensures that the user can only perform actions appropriate to their role and privileges.

**Q2. Describe the three types of access control vulnerabilities and provide an example for each.**

1. **Horizontal Privilege Escalation**: Occurs when a user gains access to resources belonging to another user of the same privilege level. Example: An attacker changes the `user_id` parameter in a URL to access another user’s account information.
   
2. **Vertical Privilege Escalation**: Happens when a user gains access to privileged functionality that they are not supposed to access. Example: An attacker modifies a `role=admin` parameter to access the admin panel.
   
3. **Access Control Vulnerabilities in Multi-Step Processes**: These occur when access control rules are implemented inconsistently across different steps of a process. Example: An attacker directly accesses a `/delete` endpoint without going through the confirmation step, leading to unauthorized deletion of resources.

**Q3. How can you find access control vulnerabilities from a black box perspective?**

From a black box perspective, you can find access control vulnerabilities by mapping the application and identifying all input vectors (URL parameters, hidden fields, cookies) that could influence access control decisions. Manipulate these parameters to check if they can be exploited to access unauthorized resources. Tools like Burp Suite's Autorize extension can automate parts of this process by testing access control rules for different privilege levels.

**Q4. Discuss the impact of broken access control vulnerabilities on the CIA Triad (Confidentiality, Integrity, Availability).**

Broken access control vulnerabilities can impact all aspects of the CIA Triad:
- **Confidentiality**: Users can access sensitive data that they should not have access to.
- **Integrity**: Unauthorized users can modify data, leading to incorrect or corrupted information.
- **Availability**: Attackers can delete or disrupt resources, affecting the availability of services to legitimate users.

**Q5. How can you prevent access control vulnerabilities in your application?**

To prevent access control vulnerabilities:
1. Implement a security-centric design where access is verified first and all requests go through an access control check.
2. Use a denied-by-default design that automatically denies access unless specific policies are set.
3. Apply the principle of least privilege, granting users only the necessary access and privileges.
4. Consider using attribute or feature-based access control for more granular control in complex applications.
5. Ensure that all access control checks are performed on the server side and that client-side inputs are validated.

**Q6. Provide an example of a recent real-world breach related to broken access control and explain how it occurred.**

One notable example is the Capital One breach in 2019 (CVE-2019-11510). The attacker exploited a misconfigured web application firewall (WAF) that allowed unauthorized access to sensitive customer data. The WAF was supposed to limit access to certain resources, but due to a misconfiguration, it failed to enforce these restrictions effectively. This led to the exposure of over 100 million customer records. The breach highlights the importance of proper configuration and enforcement of access control mechanisms.

---
<!-- nav -->
[[24-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]]
