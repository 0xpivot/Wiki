---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Configuration Management with Ansible Playbooks

Configuration management is a critical aspect of modern DevOps practices, ensuring consistency and reliability across environments. Ansible is a popular open-source tool used for configuration management, deployment, and orchestration. This chapter focuses on using Ansible playbooks to manage the installation and versioning of software packages, specifically using the `apt` module for Debian-based systems like Ubuntu.

### What is Ansible?

Ansible is an automation tool that simplifies IT tasks such as configuration management, application deployment, and intra-service orchestration. It uses a simple language called YAML to define tasks and plays, which are executed on remote hosts. Ansible operates agentless, meaning it does not require any additional software to be installed on the managed nodes; it relies on SSH for communication.

### Why Use Ansible for Configuration Management?

Configuration management ensures that your infrastructure is consistent and predictable. By using Ansible, you can:

- **Automate repetitive tasks**: Reduce manual errors and save time.
- **Ensure consistency**: Apply the same configurations across multiple servers.
- **Version control**: Keep track of changes and roll back if necessary.
- **Idempotency**: Ensure that the desired state is achieved without unnecessary changes.

### Basic Concepts in Ansible

Before diving into the specifics of managing software versions, let's review some fundamental concepts in Ansible:

- **Playbook**: A playbook is a collection of plays that define the desired state of the system. Each play consists of tasks that are executed on the target hosts.
- **Task**: A task is a single action performed by Ansible, such as installing a package or modifying a file.
- **Module**: Modules are the building blocks of tasks. They perform specific actions, such as installing software or managing files.
- **Inventory**: An inventory is a list of hosts that Ansible manages. It defines the target environment for the playbook.

### Managing Software Versions with Ansible

In the context of the provided transcript, we are focusing on managing the version of the `EngineX` package on an Ubuntu server. This involves specifying the exact version or a range of versions to ensure consistency across environments.

#### Specifying Exact Version

To install a specific version of a package, you can use the `version` parameter in the `apt` module. Here’s how you can do it:

```yaml
---
- name: Install EngineX version 1.16.1
  hosts: all
  become: yes
  tasks:
    - name: Install EngineX version 1.16.1
      apt:
        name: engine-x=1.16.1
        state: present
```

In this playbook:

- `name: engine-x=1.16.1`: Specifies the exact version of the package to install.
- `state: present`: Ensures that the specified version is installed.

#### Using Regular Expressions

If you want to install any version that matches a certain pattern, you can use a regular expression. For example, to install any version starting with `1.18`, you can use:

```yaml
---
- name: Install EngineX version starting with 1.18
  hosts: all
  become: yes
  tasks:
    - name: Install EngineX version starting with 1.18
      apt:
        name: engine-x
        version: '^1\.18'
        state: present
```

In this playbook:

- `version: '^1\.18'`: Uses a regular expression to match any version starting with `1.18`.

### Checking Installed Version

To verify the installed version of a package, you can use the `command` module to run a shell command:

```yaml
---
- name: Check installed version of EngineX
  hosts: all
  tasks:
    - name: Get installed version of EngineX
      command: dpkg -l | grep engine-x
      register: engine_x_version
    - debug:
        var: engine_x_version.stdout_lines
```

This playbook:

- `command: dpkg -l | grep engine-x`: Runs the `dpkg -l` command to list installed packages and filters the output to show only lines containing `engine-x`.
- `register: engine_x_version`: Stores the output of the command in a variable.
- `debug`: Displays the output of the command.

### Real-World Example: CVE-2021-3156

A real-world example of the importance of managing software versions is the Log4j vulnerability (CVE-2021-44228). This vulnerability affected many applications and required immediate updates to mitigate the risk. By using Ansible to manage software versions, you can ensure that all instances of a package are updated to a secure version.

For instance, if you were managing the Log4j package, you could use a playbook to update all instances to a version that includes the security patch:

```yaml
---
- name: Update Log4j to a secure version
  hosts: all
  become: yes
  tasks:
    - name: Update Log4j to version 2.15.0
      apt:
        name: log4j
        version: 2.15.0
        state: present
```

### Pitfalls and Best Practices

When managing software versions with Ansible, there are several pitfalls to avoid:

- **Inconsistent versions**: Ensure that all instances of a package are updated to the same version to maintain consistency.
- **Dependency issues**: Some packages may have dependencies that need to be updated as well. Use the `update_cache: yes` option to refresh the package cache before installing.
- **Security vulnerabilities**: Always check for known vulnerabilities in the versions you are installing. Use tools like `trivy` or `clair` to scan for vulnerabilities.

### How to Prevent / Defend

To prevent issues related to software version management, follow these best practices:

- **Use version pinning**: Specify exact versions to avoid unintended upgrades.
- **Regularly update**: Keep your software up-to-date with the latest security patches.
- **Automate testing**: Use continuous integration (CI) pipelines to test changes before deploying them.
- **Monitor changes**: Use monitoring tools to detect unexpected changes in software versions.

### Secure Coding Fix

Here’s an example of how to securely manage software versions in Ansible:

**Vulnerable Code:**

```yaml
---
- name: Install EngineX without version pinning
  hosts: all
  become: yes
  tasks:
    - name: Install EngineX
      apt:
        name: engine-x
        state: present
```

**Secure Code:**

```yaml
---
- name: Install EngineX with version pinning
  hosts: all
  become: yes
  tasks:
    - name: Install EngineX version 1.16.1
      apt:
        name: engine-x=1.16.1
        state: present
```

### Conclusion

Managing software versions with Ansible is crucial for maintaining consistency and security in your infrastructure. By specifying exact versions or using regular expressions, you can ensure that all instances of a package are updated to the desired version. Regularly updating and testing your configurations helps prevent security vulnerabilities and ensures a reliable environment.

### Practice Labs

For hands-on practice with Ansible and configuration management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including configuration management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including configuration management.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning security concepts.

These labs provide practical experience in applying the concepts learned in this chapter.

---
<!-- nav -->
[[02-Introduction to Ansible Playbooks for Configuration Management|Introduction to Ansible Playbooks for Configuration Management]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/06-Ansible Playbooks Configuration Management/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/06-Ansible Playbooks Configuration Management/04-Practice Questions & Answers|Practice Questions & Answers]]
