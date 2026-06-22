---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the inconsistent security controls in the lab allow unauthorized users to access the admin panel.**

The inconsistent security controls in the lab allow unauthorized users to access the admin panel due to a lack of proper validation and verification mechanisms. Specifically, the application allows users to update their email addresses to any value within the "don't want to cry" domain without verifying ownership of the new email address. Since the admin panel is accessible only to users with email addresses in the "don't want to cry" domain, an attacker can simply change their email address to one in this domain to gain access to the admin panel. This flaw bypasses the intended restriction and exposes sensitive functionalities to unauthorized users.

**Q2. How would you exploit the vulnerability described in the lab to access the admin panel?**

To exploit the vulnerability described in the lab and access the admin panel, follow these steps:

1. Register a new user account with a valid email address provided by the Web Security Academy.
2. Confirm the registration by following the link sent to the email address.
3. Log in to the application using the registered credentials.
4. Navigate to the profile settings or email update functionality.
5. Update the email address to a value within the "don't want to cry" domain, such as `test@don'twanttocry.com`.
6. Attempt to access the admin panel, which should now be accessible since the email address is in the required domain.

By changing the email address to one in the "don't want to cry" domain, the application incorrectly grants access to the admin panel, allowing unauthorized users to perform administrative actions.

**Q3. Why is it important to verify email address ownership before granting access to sensitive functionalities?**

Verifying email address ownership before granting access to sensitive functionalities is crucial for several reasons:

1. **Prevent Unauthorized Access**: Without verifying ownership, attackers can easily impersonate legitimate users by changing their email address to one associated with sensitive roles or permissions. This can lead to unauthorized access to critical systems and data.

2. **Maintain Security Posture**: Proper email verification ensures that only authenticated and authorized users can access sensitive functionalities. This helps maintain the overall security posture of the application by preventing unauthorized access and potential exploitation of vulnerabilities.

3. **Compliance Requirements**: Many regulatory frameworks require organizations to implement robust authentication and verification mechanisms. Verifying email address ownership is a fundamental step in ensuring compliance with such regulations.

For example, in the context of the recent CVE-2021-44228 (Log4j vulnerability), many attacks exploited weak authentication mechanisms to gain unauthorized access to systems. Ensuring that email address ownership is verified can help mitigate such risks and protect against similar vulnerabilities.

**Q4. How would you configure the application to prevent unauthorized access to the admin panel due to inconsistent security controls?**

To prevent unauthorized access to the admin panel due to inconsistent security controls, the application should implement the following measures:

1. **Email Address Verification**: Ensure that any changes to the email address are verified through a confirmation link sent to the new email address. This prevents attackers from simply changing their email address to one in the required domain.

2. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that only users with the appropriate role can access the admin panel. This can be achieved by associating roles with specific email domains and verifying that the user's role matches the required role for accessing the admin panel.

3. **Audit Logs**: Maintain audit logs of all user actions, including email address changes and attempts to access the admin panel. This can help in detecting and responding to unauthorized access attempts.

Here is an example of how you might implement email address verification in Python:

```python
import smtplib
from email.mime.text import MIMEText

def send_verification_email(email):
    # Create the email message
    msg = MIMEText('Please click on the following link to verify your email address.')
    msg['Subject'] = 'Verify Your Email Address'
    msg['From'] = 'noreply@example.com'
    msg['To'] = email
    
    # Send the email
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login('username', 'password')
    server.sendmail('noreply@example.com', [email], msg.as_string())
    server.quit()

# Example usage
send_verification_email('test@dontwanttocry.com')
```

By implementing these measures, the application can prevent unauthorized access to the admin panel and maintain a secure environment.

**Q5. What recent real-world examples highlight the importance of consistent security controls in web applications?**

Recent real-world examples highlight the importance of consistent security controls in web applications. One notable example is the SolarWinds supply chain attack (CVE-2020-1014) in December 2020. In this attack, hackers compromised the SolarWinds software update mechanism and injected malicious code into the updates. This allowed the attackers to gain unauthorized access to numerous high-profile organizations, including government agencies and private companies.

Another example is the Capital One breach in 2019 (CVE-2019-11157). The breach occurred due to a misconfiguration in a web application firewall rule, which exposed sensitive customer data. The incident highlighted the importance of consistent security controls and proper configuration management to prevent unauthorized access to sensitive data.

These incidents underscore the critical importance of consistent security controls in web applications to prevent unauthorized access and protect sensitive data.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/04-Lab 3 Inconsistent security controls/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/04-Lab 3 Inconsistent security controls/00-Overview|Overview]]
