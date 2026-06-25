---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how using IAM roles instead of AWS user credentials improves security in your DevSecOps environment.**

Using IAM roles instead of AWS user credentials significantly enhances security by eliminating the need to store long-term access keys or secrets within your CI/CD pipeline or version control system. When an EC2 instance is assigned an IAM role, it automatically receives temporary security credentials that are valid only for a limited duration. These credentials are refreshed periodically, ensuring that even if they were compromised, the window for exploitation is minimal. This approach reduces the risk of unauthorized access and minimizes the attack surface, as sensitive credentials are not stored in places like GitLab or other repositories.

**Q2. How does the use of temporary tokens in AWS CLI commands contribute to the security of your infrastructure?**

Temporary tokens, often referred to as session tokens, are short-lived credentials that are issued by AWS STS (Security Token Service). These tokens are used to authenticate requests to AWS services and are designed to expire after a specified period. By using temporary tokens, you ensure that even if an attacker gains access to your system, they cannot use the credentials indefinitely. The temporary nature of these tokens means that any unauthorized activity would be limited to the duration of the token's validity, making it easier to detect and mitigate such breaches. Additionally, the requirement for re-authentication adds another layer of security, as it forces attackers to go through additional steps to maintain access.

**Q3. Describe how the removal of SSH private keys and AWS user keys from GitLab contributes to the overall security posture of your DevSecOps environment.**

Removing SSH private keys and AWS user keys from GitLab significantly improves the security posture of your DevSecOps environment. Storing such sensitive information in version control systems like GitLab poses a high risk of exposure, especially if the repository is accessible to multiple users or if there is a breach. By removing these keys, you eliminate the possibility of unauthorized access to your AWS resources through compromised credentials. Instead, you rely on IAM roles and temporary tokens, which are inherently more secure due to their short lifespan and automatic revocation upon expiration. This approach ensures that even if an attacker gains access to your GitLab instance, they will not be able to leverage stored credentials to access your AWS environment.

**Q4. What are some additional security improvements that can be implemented in the current setup described in the lecture?**

Several additional security improvements can be implemented in the current setup:

1. **Limiting IAM Policies**: Narrow down the permissions granted to IAM roles to the minimum necessary for performing specific tasks. For example, instead of granting full access to an S3 bucket, limit the permissions to only the required actions such as `s3:GetObject` and `s3:PutObject`.

2. **Blocking Port Access**: Restrict access to ports that are not necessary for the operation of your services. For instance, blocking port 22 (SSH) on your GitLab runners can prevent unauthorized SSH access.

3. **Enhancing Credential Storage**: Ensure that any credentials that must be stored are encrypted and securely managed. Use tools like AWS Secrets Manager or HashiCorp Vault to manage secrets securely.

4. **Monitoring and Logging**: Implement comprehensive monitoring and logging to detect and respond to security events promptly. Use AWS CloudTrail to log API calls and AWS Config to track changes in your AWS environment.

5. **Regular Security Audits**: Conduct regular security audits and vulnerability assessments to identify and address potential security gaps in your infrastructure.

**Q5. How does the concept of continuous security apply to the management of AWS resources in a DevSecOps context?**

Continuous security is a critical aspect of managing AWS resources in a DevSecOps context. It involves the ongoing implementation and maintenance of security measures throughout the software development lifecycle. This includes:

1. **Automated Security Testing**: Integrating automated security testing into your CI/CD pipelines to detect vulnerabilities early in the development process.

2. **Regular Updates and Patch Management**: Keeping all software components, including operating systems, libraries, and applications, up-to-date with the latest security patches.

3. **Ongoing Monitoring and Incident Response**: Continuously monitoring your AWS environment for security threats and having a robust incident response plan in place to quickly address any security issues.

4. **Security Training and Awareness**: Ensuring that all team members are trained in security best practices and are aware of the latest security threats and mitigation strategies.

By adopting a continuous security approach, you can proactively manage security risks and ensure that your AWS resources remain secure throughout their lifecycle.

**Q6. Discuss recent real-world examples (CVEs/breaches) where the lack of proper IAM role configuration led to significant security breaches.**

One notable example is the Capital One data breach in 2019 (CVE-2019-11427), where an attacker exploited misconfigured IAM roles to gain unauthorized access to sensitive customer data. The attacker was able to access the IAM role associated with the web application firewall, which had overly broad permissions. This allowed the attacker to read and download sensitive data from the company’s AWS S3 buckets.

Another example is the Twitter hack in 2020, where attackers gained access to internal tools and used them to compromise high-profile accounts. Although the root cause was multifaceted, improper IAM role configuration played a role in enabling the attackers to escalate their privileges within the organization’s AWS environment.

These incidents highlight the importance of properly configuring IAM roles with least privilege principles and regularly auditing IAM policies to ensure they align with the principle of least privilege.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/01-Overview of AWS Security Measures and Continuous Security Improvements/01-Overview of AWS Security Measures and Continuous Security Improvements|Overview of AWS Security Measures and Continuous Security Improvements]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/01-Overview of AWS Security Measures and Continuous Security Improvements/00-Overview|Overview]]
