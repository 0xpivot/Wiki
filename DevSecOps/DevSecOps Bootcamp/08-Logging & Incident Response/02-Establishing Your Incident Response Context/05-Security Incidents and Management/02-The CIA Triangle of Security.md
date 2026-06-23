---
course: DevSecOps
topic: Establishing Your Incident Response Context
tags: [devsecops]
---

## The CIA Triangle of Security

The CIA triangle stands for Confidentiality, Integrity, and Availability. These three pillars form the foundation of information security and are critical in understanding how to manage and respond to security incidents. Let's break down each component:

### Confidentiality

**Definition**: Confidentiality ensures that sensitive information is accessible only to those authorized to have access. This means that data should remain private and protected from unauthorized disclosure.

**Why It Matters**: Without confidentiality, sensitive data can fall into the wrong hands, leading to significant financial losses, reputational damage, and legal consequences. For example, the Equifax breach in 2017 exposed personal data of over 143 million people, resulting in substantial financial penalties and loss of customer trust.

**How It Works Under the Hood**: Confidentiality is typically achieved through encryption, access controls, and secure authentication mechanisms. Encryption transforms data into a format that is unreadable without a decryption key. Access controls ensure that only authorized users can view or modify data. Secure authentication mechanisms verify the identity of users before granting access.

**Real-World Example**: In the Equifax breach, attackers exploited a vulnerability in Apache Struts (CVE-2017-5638) to gain unauthorized access to sensitive data. This breach highlights the importance of maintaining confidentiality by keeping software up-to-date and implementing robust access controls.

### Integrity

**Definition**: Integrity ensures that data remains accurate and unaltered during storage or transmission. This means that data should not be tampered with or modified without authorization.

**Why It Matters**: Without integrity, data can be manipulated, leading to incorrect decisions, financial losses, and legal issues. For example, the Target breach in 2013 resulted in the theft of credit card data, which could have been used to make fraudulent transactions.

**How It Works Under the Hood**: Integrity is maintained through cryptographic hashes, digital signatures, and checksums. Cryptographic hashes generate a unique value based on the data, ensuring that any modification will change the hash value. Digital signatures provide a way to verify the authenticity and integrity of data using public-key cryptography. Checksums are used to detect errors in data transmission.

**Real-World Example**: In the Target breach, attackers installed malware on point-of-sale systems to capture credit card data. This breach underscores the importance of maintaining data integrity by implementing strong security measures such as intrusion detection systems and regular audits.

### Availability

**Definition**: Availability ensures that authorized users can access data and resources whenever needed. This means that systems should be operational and accessible at all times.

**Why It Matters**: Without availability, users may be unable to access critical resources, leading to downtime, financial losses, and reputational damage. For example, the WannaCry ransomware attack in 2017 affected hundreds of thousands of computers worldwide, causing significant disruptions.

**How It Works Under the Hood**: Availability is maintained through redundancy, failover mechanisms, and disaster recovery plans. Redundancy involves having backup systems and components to ensure continuous operation. Failover mechanisms automatically switch to backup systems in case of a failure. Disaster recovery plans outline steps to restore systems and data in case of a major outage.

**Real-World Example**: In the WannaCry attack, attackers exploited a vulnerability in Microsoft Windows (EternalBlue) to spread ransomware, causing widespread disruption. This attack highlights the importance of maintaining system availability by keeping software up-to-date and implementing robust disaster recovery plans.

---
<!-- nav -->
[[01-Security Incident Management|Security Incident Management]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/02-Establishing Your Incident Response Context/05-Security Incidents and Management/00-Overview|Overview]] | [[03-Understanding Security Incidents in DevSecOps|Understanding Security Incidents in DevSecOps]]
