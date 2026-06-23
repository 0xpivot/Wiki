---
course: DevSecOps
topic: Understanding the Need for Security Compliance
tags: [devsecops]
---

## Traditional Approach to Security Compliance

### Background Theory

The traditional approach to security compliance can be likened to a linear process, similar to the waterfall methodology used in software development. In this model, security compliance is treated as a series of sequential steps, each of which must be completed successfully before moving on to the next. This approach is heavily influenced by the idea of quality assurance checks, where security measures are inspected at various points during the product delivery cycle.

#### Linear Sequence of Steps

The traditional approach involves a linear sequence of steps, each serving as a gate that must be passed before proceeding to the next stage. These steps typically include:

1. **Risk Assessment**: Identifying potential risks and vulnerabilities.
2. **Security Testing**: Conducting various types of security tests (e.g., penetration testing, vulnerability scanning).
3. **Remediation**: Addressing identified issues.
4. **Final Audit**: A comprehensive review to ensure compliance with security standards.

This linear approach is designed to ensure that all necessary security measures are in place before the final product is delivered. However, this method has several drawbacks, particularly in the context of modern, agile development environments.

### Information Security Friction

One of the primary issues with the traditional approach is the concept of "information security friction." This refers to the resistance or delay encountered when implementing security measures within a project. The traditional approach often leads to delays because security is treated as an afterthought, rather than an integral part of the development process.

#### Delayed Project Deliveries

In the traditional model, security is often seen as a separate phase that occurs after the main development work is completed. This can result in significant delays, as issues discovered during the final audit may require extensive rework. For example, consider a scenario where a company is developing a new web application. After months of development, a final security audit reveals critical vulnerabilities. The team must then spend additional time remediating these issues, potentially delaying the release date.

#### Late Discovery of Issues

Another issue with the traditional approach is that problems are often discovered too late in the project lifecycle. By the time the final audit is conducted, it may be difficult or costly to address the identified issues. This can lead to a situation where security is compromised, as the team may be forced to release the product with known vulnerabilities.

### Real-World Examples

To illustrate the impact of the traditional approach, let's look at some recent real-world examples:

#### Example 1: Equifax Data Breach (CVE-2017-5638)

In 2017, Equifax suffered a massive data breach that exposed sensitive personal information of millions of customers. The breach was caused by a vulnerability in Apache Struts, a popular web application framework. The company had failed to apply a critical security patch, which allowed attackers to gain unauthorized access to the system.

**Traditional Approach Analysis**:
- **Risk Assessment**: Equifax likely performed a risk assessment, but it did not identify the specific vulnerability in Apache Struts.
- **Security Testing**: Regular security testing might have been conducted, but it did not catch the unpatched vulnerability.
- **Remediation**: The company did not apply the available security patch, leading to the breach.
- **Final Audit**: The final audit did not reveal the unpatched vulnerability, resulting in a significant security failure.

#### Example 2: Capital One Data Breach (CVE-2019-11510)

In 2019, Capital One experienced a data breach that exposed the personal information of over 100 million customers. The breach was caused by a misconfiguration in a web application firewall (WAF) that allowed an attacker to access sensitive data.

**Traditional Approach Analysis**:
- **Risk Assessment**: Capital One likely performed a risk assessment, but it did not identify the misconfiguration in the WAF.
- **Security Testing**: Regular security testing might have been conducted, but it did not catch the misconfiguration.
- **Remediation**: The company did not correct the misconfiguration, leading to the breach.
- **Final Audit**: The final audit did not reveal the misconfiguration, resulting in a significant security failure.

### How to Prevent / Defend

To mitigate the issues associated with the traditional approach, organizations should adopt a more integrated and continuous security strategy. This involves treating security as an ongoing process, rather than a one-time event.

#### Secure Coding Practices

Secure coding practices are essential for preventing security vulnerabilities. Developers should follow best practices such as input validation, output encoding, and least privilege principles. Here’s an example of a vulnerable code snippet and its secure counterpart:

```python
# Vulnerable Code
def display_user_info(user_id):
    user = get_user_from_db(user_id)
    print(f"User Info: {user['name']}")

# Secure Code
def display_user_info(user_id):
    user = get_user_from_db(user_id)
    print(f"User Info: {html.escape(user['name'])}")
```

In the secure version, `html.escape` is used to encode the user name, preventing potential cross-site scripting (XSS) attacks.

#### Continuous Integration and Continuous Deployment (CI/CD)

Implementing CI/CD pipelines can help integrate security into the development process. Automated security testing tools can be integrated into the pipeline to detect vulnerabilities early in the development cycle. Here’s an example of a CI/CD pipeline using Jenkins:

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Security Test') {
            steps {
                sh 'dependency-check --project MyProject --scan target/'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/path/to/app'
            }
        }
    }
}
```

In this pipeline, the `Security Test` stage runs a dependency check to identify any known vulnerabilities in the project dependencies.

#### Configuration Management

Proper configuration management is crucial for maintaining security. Tools like Ansible, Puppet, or Chef can be used to manage configurations across systems. Here’s an example of an Ansible playbook for securing a web server:

```yaml
---
- hosts: webservers
  become: yes
  tasks:
    - name: Ensure mod_security is installed
      apt:
        name: libapache-mod-security
        state: present

    - name: Configure mod_security rules
      template:
        src: modsecurity.conf.j2
        dest: /etc/modsecurity/modsecurity.conf
```

In this playbook, `mod_security` is installed and configured to enhance the security of the web server.

### Conclusion

The traditional approach to security compliance, characterized by a linear sequence of steps and delayed security testing, has significant drawbacks. It often leads to information security friction, delayed project deliveries, and late discovery of issues. To mitigate these issues, organizations should adopt a more integrated and continuous security strategy, incorporating secure coding practices, CI/CD pipelines, and proper configuration management.

### Practice Labs

For hands-on practice in DevSecOps, consider the following real-world labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application to teach web application security lessons.

These labs provide practical experience in identifying and mitigating security vulnerabilities, reinforcing the concepts learned in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/11-Understanding the Need for Security Compliance/05-Traditional Approach to Security Compliance/00-Overview|Overview]] | [[02-Understanding the Need for Security Compliance|Understanding the Need for Security Compliance]]
