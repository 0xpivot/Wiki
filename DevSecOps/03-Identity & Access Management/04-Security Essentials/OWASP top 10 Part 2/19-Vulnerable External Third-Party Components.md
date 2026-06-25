---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Vulnerable External Third-Party Components

One of the critical categories within the OWASP Top 10 is the use of vulnerable external third-party components. These components include libraries, frameworks, and other external dependencies that are integrated into an application. When these components are included, they become an integral part of the application itself, meaning that any security vulnerabilities present in these components can directly affect the security of the entire application.

### What Are Third-Party Components?

Third-party components are pieces of software developed by external entities that are incorporated into an application. These can include:

- **Libraries**: Pre-written code that provides specific functionality, such as encryption, database connectivity, or networking.
- **Frameworks**: Structured sets of libraries that provide a foundation for building applications, such as Spring Boot, Django, or React.
- **Services**: External services that provide specific functionalities, such as databases, messaging systems, or load balancers.

### Why Are Third-Party Components Important?

Third-party components are crucial because they allow developers to leverage existing codebases, reducing development time and effort. However, they also introduce potential security risks. When a third-party component contains a vulnerability, it can be exploited by attackers to gain unauthorized access to the system.

### How Do Vulnerabilities in Third-Party Components Impact Security?

When a third-party component is integrated into an application, it runs with the same privileges as the application itself. This means that if the component has a security vulnerability, an attacker can exploit it to gain access to the system. For example, if a database service running in the environment has a vulnerability, an attacker could potentially execute arbitrary code on the server, leading to a breach.

### Real-World Example: Apache Struts 2

A notable example of a security vulnerability in a third-party component is the remote code execution vulnerability in Apache Struts 2. This vulnerability allowed attackers to execute arbitrary code on the server, leading to significant breaches in many applications that used this framework.

#### Vulnerability Details

The vulnerability was identified as CVE-2017-5638 and affected versions of Apache Struts 2.3.x and 2.5.x. The vulnerability was due to improper input validation in the Jakarta Multipart parser, which allowed attackers to inject malicious code.

#### Exploit Example

Here is an example of how the vulnerability could be exploited:

```http
POST /struts2-showcase/index.action HTTP/1.1
Host: target.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryrRqIYzUW4JhjZKwH

------WebKitFormBoundaryrRqIYzUW4JhjZKwH
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

test
------WebKitFormBoundaryrRqIYzUW4JhjZKwH
Content-Disposition: form-data; name="Content-Type"

application/x-www-form-urlencoded
------WebKitFormBoundaryrRqIYzUW4JhjZKwH--
```

In this example, the attacker sends a POST request with a specially crafted `Content-Type` header, which triggers the vulnerability in the Jakarta Multipart parser.

#### Impact

The impact of this vulnerability was severe, leading to numerous breaches and data leaks. Many organizations were affected, including Equifax, which suffered one of the largest data breaches in history due to this vulnerability.

### How to Prevent / Defend Against Vulnerable Third-Party Components

To mitigate the risks associated with vulnerable third-party components, several steps can be taken:

#### Detection

1. **Dependency Scanning Tools**: Use tools like OWASP Dependency Check, Sonatype Nexus Lifecycle, or Snyk to scan your project dependencies for known vulnerabilities.
   
   ```bash
   # Using OWASP Dependency Check
   dependency-check --project MyProject --scan /path/to/project
   ```

2. **Regular Updates**: Keep all third-party components up to date with the latest security patches.

#### Prevention

1. **Secure Coding Practices**: Ensure that third-party components are used securely. Follow best practices for integrating external dependencies.

2. **Configuration Hardening**: Harden the configurations of third-party components to minimize the attack surface.

#### Secure Code Fix

Here is an example of how to fix a vulnerable code snippet:

**Vulnerable Code:**

```java
import org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter;

public class MyApplication {
    public void init() {
        FilterRegistration.Dynamic strutsFilter = servletContext.addFilter("struts2", StrutsPrepareAndExecuteFilter.class);
        strutsFilter.addMappingForUrlPatterns(EnumSet.of(DispatcherType.REQUEST), true, "/*");
    }
}
```

**Fixed Code:**

```java
import org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter;

public class MyApplication {
    public void init() {
        FilterRegistration.Dynamic strutsFilter = servletContext.addFilter("struts2", StrutsPrepareAndExecuteFilter.class);
        strutsFilter.addMappingForUrlPatterns(EnumSet.of(  // Limit the URL patterns to specific paths
            DispatcherType.REQUEST), true, "/secure/*");
    }
}
```

In the fixed code, the URL patterns are limited to specific paths, reducing the attack surface.

### Conclusion

Using vulnerable external third-party components can significantly impact the security of an application. By understanding the risks and implementing proper detection and prevention measures, developers can mitigate these risks and ensure the security of their applications.

### Practice Labs

For hands-on practice with securing third-party components, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on dependency scanning and secure coding practices.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes third-party components with known vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes various vulnerable components that can be exploited to understand the risks and mitigation strategies.

By engaging with these labs, you can gain practical experience in identifying and mitigating vulnerabilities in third-party components.

---
<!-- nav -->
[[18-Understanding Multi-Step Attacks|Understanding Multi-Step Attacks]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 2/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 2/20-Practice Questions & Answers|Practice Questions & Answers]]
