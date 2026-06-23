---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Ansible Modules: Command vs. Shell

In the context of DevOps automation using Ansible, two commonly used modules are `command` and `shell`. These modules are essential for executing commands on remote hosts. While both modules serve similar purposes, they have distinct differences that make them suitable for different scenarios. Understanding these differences is crucial for effective and secure automation.

### What Are Command and Shell Modules?

The `command` and `shell` modules in Ansible are used to run commands on remote hosts. They are part of the core set of modules provided by Ansible and are widely used in playbooks for various tasks such as installing software, managing services, and performing system administration tasks.

#### Command Module

The `command` module executes a command on the remote host. It does not use the shell to execute the command, which means it does not support shell features such as pipes (`|`), redirects (`>`), and environment variables. This makes the `command` module more secure because it reduces the risk of shell injection attacks.

```yaml
- name: Run a simple command
  command: echo "Hello, World!"
```

#### Shell Module

The `shell` module, on the other hand, executes a command through the shell. This means it supports shell features such as pipes, redirects, and environment variables. However, this also means it is more susceptible to shell injection attacks.

```yaml
- name: Run a complex command with shell features
  shell: echo "Hello, World!" | tr '[:lower:]' '[:upper:]'
```

### Why Use Command Over Shell?

The primary reason to use the `command` module over the `shell` module is security. By not using the shell, the `command` module reduces the risk of shell injection attacks. Shell injection occurs when an attacker injects malicious commands into a shell command, potentially leading to unauthorized access or data breaches.

#### Real-World Example: CVE-2021-21366

A notable example of a shell injection vulnerability is CVE-2021-21366, which affected the Jenkins CI/CD platform. In this case, an attacker could inject arbitrary shell commands into the Jenkins pipeline, leading to remote code execution. This vulnerability highlights the importance of using the `command` module when possible to mitigate such risks.

### Why Use Shell Over Command?

While the `command` module is more secure, there are scenarios where the `shell` module is necessary. The `shell` module provides additional flexibility by supporting shell features such as pipes, redirects, and environment variables. These features are often required for more complex command sequences.

#### Example: Using Environment Variables

Consider a scenario where you need to use environment variables in your command. The `command` module does not support this, but the `shell` module does.

```yaml
- name: Use environment variable in command
  shell: echo $PATH
```

### How to Choose Between Command and Shell

When deciding whether to use the `command` or `shell` module, consider the following:

1. **Security**: If the command does not require shell features, use the `command` module to reduce the risk of shell injection.
2. **Complexity**: If the command requires shell features such as pipes, redirects, or environment variables, use the `shell` module.

### Practical Example: Deploying a Node.js Application

Let's consider a practical example of deploying a Node.js application using Ansible. We will use both the `command` and `shell` modules to demonstrate their usage.

#### Step 1: Install Node.js

First, we install Node.js using the `command` module since it does not require shell features.

```yaml
- name: Install Node.js
  command: apt-get update && apt-get install -y nodejs
```

#### Step 2: Install npm Packages

Next, we install npm packages using the `shell` module because we need to use the `&&` operator to chain commands.

```yaml
- name: Install npm packages
  shell: cd /path/to/app && npm install
```

### How to Prevent / Defend Against Shell Injection

To prevent shell injection attacks, follow these best practices:

1. **Use the Command Module When Possible**: Always prefer the `command` module over the `shell` module unless you need shell features.
2. **Validate Input**: Ensure that any user input used in commands is properly validated and sanitized.
3. **Use Secure Coding Practices**: Follow secure coding practices to minimize the risk of vulnerabilities.

#### Vulnerable Code Example

Consider the following vulnerable code where user input is directly included in a shell command:

```yaml
- name: Vulnerable code example
  shell: echo {{ user_input }}
```

#### Secure Code Example

To secure this, validate and sanitize the user input before including it in the command:

```yaml
- name: Secure code example
  shell: echo "{{ user_input | regex_replace('[^a-zA-Z0-9]', '') }}"
```

### Conclusion

Understanding the differences between the `command` and `shell` modules in Ansible is crucial for effective and secure automation. By choosing the appropriate module based on the requirements and following best practices, you can ensure that your automation scripts are both functional and secure.

### Practice Labs

For hands-on practice with Ansible modules, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve Ansible.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be deployed and managed using Ansible.

These labs provide practical experience in using Ansible modules effectively and securely.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/39-Nodejs Application Deployment With Npm Install/00-Overview|Overview]] | [[02-Introduction to Asynchronous Task Execution in Node.js Deployment|Introduction to Asynchronous Task Execution in Node.js Deployment]]
