---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a broken access control vulnerability is and provide an example from the lab.**

Broken access control vulnerabilities occur when an application fails to enforce proper restrictions on what authenticated users are allowed to do. For instance, in the lab, the application allows a regular user to modify their `roleID` parameter to `2`, which corresponds to an administrative role. This allows the user to gain unauthorized access to the admin panel and perform actions such as deleting other users, which they should not be able to do.

**Q2. How would you exploit the broken access control vulnerability described in the lab?**

To exploit the broken access control vulnerability, follow these steps:

1. Log in to the application with the provided credentials.
2. Identify the endpoint that allows changing the email address, which also contains the `roleID` parameter.
3. Modify the `roleID` parameter to `2` (admin role) in the request to the email change endpoint.
4. Send the modified request to the server. If the server accepts the change, the user will now have administrative privileges.
5. Access the admin panel and perform actions such as deleting the `Carlos` user.

Here’s a sample payload to change the `roleID`:

```python
import requests

url = 'http://example.com/my-account/change-email'
data = {
    'email': 'test@test.ca',
    'roleID': 2
}
response = requests.post(url, json=data)
print(response.text)
```

**Q3. Why is scripting the exploit important in penetration testing?**

Scripting the exploit is crucial in penetration testing for several reasons:

1. **Automation**: Automating the process allows testers to quickly repeat the exploit multiple times without manual intervention, saving time and reducing human error.
2. **Reproducibility**: A script ensures that the same steps are followed consistently, making it easier to reproduce the exploit for verification or reporting purposes.
3. **Scalability**: Scripts can be adapted to test similar vulnerabilities across different parts of an application or even across multiple applications.
4. **Documentation**: Writing scripts serves as a form of documentation, providing clear instructions on how the exploit works, which is valuable for both current and future reference.

**Q4. What recent real-world examples illustrate the impact of broken access control vulnerabilities?**

One notable example is the Capital One data breach in 2019 (CVE-2019-11271). An attacker exploited a misconfigured web application firewall (WAF) to access sensitive customer data. The WAF was supposed to restrict access to certain resources, but due to a configuration error, the attacker was able to bypass these restrictions and access millions of customer records.

Another example is the Equifax data breach in 2017, where attackers exploited a vulnerability in Apache Struts to gain unauthorized access to sensitive data. The vulnerability allowed attackers to execute arbitrary code and escalate their privileges within the system.

Both breaches highlight the severe consequences of inadequate access controls, leading to significant financial and reputational damage.

**Q5. How would you configure an application to prevent broken access control vulnerabilities?**

To prevent broken access control vulnerabilities, consider implementing the following measures:

1. **Role-Based Access Control (RBAC)**: Ensure that users are assigned roles with specific permissions, and enforce these roles strictly.
2. **Least Privilege Principle**: Grant users the minimum level of access necessary to perform their tasks.
3. **Input Validation**: Validate all input parameters to ensure they fall within expected ranges and formats.
4. **Session Management**: Use secure session management techniques to prevent session hijacking and ensure that session tokens are not easily guessable.
5. **Regular Audits**: Conduct regular security audits and penetration tests to identify and mitigate potential access control issues.

By adhering to these best practices, developers can significantly reduce the risk of broken access control vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/05-Lab 4 User role can be modified in user profile/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/05-Lab 4 User role can be modified in user profile/00-Overview|Overview]]
