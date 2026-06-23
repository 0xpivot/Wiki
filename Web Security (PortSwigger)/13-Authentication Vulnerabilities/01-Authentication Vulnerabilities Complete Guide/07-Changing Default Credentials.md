---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Changing Default Credentials

### What Are Default Credentials?

Default credentials are pre-set usernames and passwords that come with software or devices out of the box. They are often generic and widely known, making them easy targets for attackers.

### Why Change Default Credentials?

Using default credentials poses significant security risks. Attackers can easily find and use these credentials to gain unauthorized access. Changing default credentials ensures that each deployment has unique and strong credentials, reducing the likelihood of unauthorized access.

### How to Change Default Credentials

When deploying software, always change the default credentials before going live. Ensure that the new credentials are strong and unique.

#### Real-World Example: CVE-2020-1472 (Zerologon)

The Zerologon vulnerability (CVE-2020-1472) allowed attackers to reset the password of any Active Directory domain controller to a null value. If default credentials were still in use, attackers could easily gain administrative access. Changing default credentials would have mitigated this risk.

### How to Prevent / Defend

**Detection:**
- Regularly audit systems for default credentials.
- Use automated tools to scan for known default credentials.

**Prevention:**
- Change default credentials immediately upon deployment.
- Implement a policy requiring strong, unique passwords.

**Secure Coding Fix:**
```bash
# Example of changing default credentials in a Linux system
sudo passwd root
# Enter new password
```

---
<!-- nav -->
[[06-Brute Force Protection|Brute Force Protection]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[08-Default Credentials|Default Credentials]]
