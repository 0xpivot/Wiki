---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Keeping Software and Plugins Updated

Maintaining the security of a CI/CD pipeline also involves keeping the software and plugins up to date. This is particularly important to mitigate known vulnerabilities and ensure that the pipeline remains secure.

### Differences Between On-Premise and SaaS

When using on-premise software, you have more control over updates and system hardening. You need to implement processes to regularly update the software and plugins. In contrast, with software as a service (SaaS), the software is often automatically updated, but you may still need to manually update plugins.

### Why Keep Software and Plugins Updated?

Keeping software and plugins updated is crucial because it ensures that you have the latest security patches and bug fixes. Outdated software can be exploited by attackers to gain unauthorized access or cause disruptions.

### How to Update Software and Plugins

For on-premise software, you should:

1. **Implement Update Processes:** Establish regular update schedules and automate the process where possible.
2. **Monitor for Vulnerabilities:** Use tools like vulnerability scanners to identify outdated software and plugins.

For SaaS, you should:

1. **Check Plugin Updates:** Regularly check for updates to plugins and apply them as needed.
2. **Monitor for Security Advisories:** Stay informed about security advisories related to the software and plugins you use.

### Real-World Example

In 2021, a major vulnerability was discovered in a widely used CI/CD tool. Organizations that had not kept their software and plugins updated were exposed to this vulnerability. Regular updates and monitoring could have prevented this exposure.

### How to Prevent / Defend

**Detection:**
- Use vulnerability scanners to identify outdated software and plugins.
- Monitor for security advisories and updates.

**Prevention:**
- Implement regular update processes for on-premise software.
- Manually check and update plugins for SaaS solutions.

**Secure Configuration:**
```bash
# Secure configuration example
# Automate updates for on-premise software
sudo apt-get update && sudo apt-get upgrade -y

# Check for plugin updates
npm outdated
npm update
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/06-Keeping Software and Plugins Up to Date|Keeping Software and Plugins Up to Date]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/08-Restricting Access to Information About Jobs|Restricting Access to Information About Jobs]]
