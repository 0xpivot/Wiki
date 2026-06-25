---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Testing Phase

### Automated Penetration Testing

#### What is Automated Penetration Testing?

Automated penetration testing is a process that simulates attacks on a system or application to identify security weaknesses. Automated penetration testing tools can perform a wide range of tests, from simple vulnerability scans to complex attack scenarios.

#### Why is Automated Penetration Testing Important?

Automated penetration testing is important because it helps teams identify and remediate security issues before they can be exploited. Regular automated penetration tests can ensure that the system remains secure and compliant with industry standards.

#### How Does Automated Penetration Testing Work?

Automated penetration testing tools typically perform the following steps:

1. **Scanning**: Identify potential entry points and vulnerabilities.
2. **Exploitation**: Attempt to exploit identified vulnerabilities.
3. **Reporting**: Generate detailed reports of the findings.

#### Real-World Example: Equifax Breach (CVE-2017-5638)

The Equifax breach (CVE-2017-5638) was caused by a vulnerability in Apache Struts. An automated penetration test could have identified this vulnerability and alerted the team to update the affected component.

#### Tools for Automated Penetration Testing

Some popular automated penetration testing tools include:

- **Metasploit**
- **Burp Suite**
- **OWASP ZAP**
- **Nmap**

#### Example Configuration: Metasploit

```ruby
use auxiliary/scanner/http/apache_struts_cve2017_5638
set RHOSTS 192.168.1.1
run
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/08-Security Governance and Compliance in DevSecOps|Security Governance and Compliance in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/10-Using Compliance Code Examples from AWS|Using Compliance Code Examples from AWS]]
