---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Package Management in Ansible

In the realm of DevOps, automation tools like Ansible play a crucial role in streamlining the deployment and management of software across various environments. One of the key functionalities of Ansible is its ability to manage software packages on different operating systems. This chapter will delve into the intricacies of managing packages using Ansible, focusing specifically on the `apt` and `yum` modules, which are commonly used on Debian-based and Red Hat-based systems, respectively.

### Understanding Package Managers

Before diving into the specifics of Ansible modules, it's essential to understand what package managers are and their importance in system administration.

#### What is a Package Manager?

A package manager is a software tool designed to automate the process of installing, upgrading, configuring, and removing software packages on a computer. It simplifies the task of managing software dependencies, ensuring that all required libraries and components are installed correctly.

#### Common Package Managers

- **APT (Advanced Package Tool)**: Used primarily on Debian-based systems such as Ubuntu.
- **YUM (Yellowdog Updater Modified)**: Used on Red Hat-based systems such as CentOS and Fedora.

### Using Ansible Modules for Package Management

Ansible provides several modules to interact with these package managers. Let's explore the `apt` and `yum` modules in detail.

#### The `apt` Module

The `apt` module is used to manage packages on Debian-based systems. It interacts with the APT package manager to perform operations like installation, removal, and updating of packages.

##### Attributes of the `apt` Module

The `apt` module has several attributes that control its behavior. Two of the most important ones are:

- **name**: A list of package names to be managed.
- **state**: Specifies the desired state of the package. Possible values include `present`, `latest`, and `absent`.

```yaml
- name: Install Apache web server
  apt:
    name: apache2
    state: present
```

In this example, the `apt` module is used to ensure that the `apache2` package is installed (`state: present`). If the package is already installed, no action is taken.

##### Detailed Explanation of Attributes

- **name**: This attribute specifies the package(s) to be managed. It can accept a single package name or a list of package names.
  
  ```yaml
  - name: Install multiple packages
    apt:
      name:
        - nginx
        - php-fpm
      state: present
  ```

- **state**: This attribute determines the desired state of the package. The possible values are:
  - `present`: Ensures the package is installed.
  - `latest`: Ensures the package is updated to the latest version available.
  - `absent`: Ensures the package is removed.

  ```yaml
  - name: Remove Apache web server
    apt:
      name: apache2
      state: absent
  ```

##### Example: Full HTTP Request and Response

When executing an Ansible playbook that uses the `apt` module, the underlying HTTP requests and responses are handled internally by Ansible. However, for educational purposes, let's consider a hypothetical scenario where we manually trigger an HTTP request to install a package.

```http
POST /api/v2/job_templates/1/launch/ HTTP/1.1
Host: ansible.example.com
Content-Type: application/json
Authorization: Token <your_token>

{
  "extra_vars": {
    "package_name": "nginx",
    "state": "present"
  }
}
```

Response:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "status": "successful",
  "result": {
    "changed": true,
    "msg": "Package nginx installed successfully."
  }
}
```

### The `yum` Module

The `yum` module is used to manage packages on Red Hat-based systems. It interacts with the YUM package manager to perform similar operations as the `apt` module.

##### Attributes of the `yum` Module

Similar to the `apt` module, the `yum` module also has the following attributes:

- **name**: A list of package names to be managed.
- **state**: Specifies the desired state of the package. Possible values include `present`, `latest`, and `absent`.

```yaml
- name: Install MySQL server
  yum:
    name: mysql-server
    state: present
```

In this example, the `yum` module ensures that the `mysql-server` package is installed (`state: present`).

##### Detailed Explanation of Attributes

- **name**: This attribute specifies the package(s) to be managed. It can accept a single package name or a list of package names.
  
  ```yaml
  - name: Install multiple packages
    yum:
      name:
        - httpd
        - php
      state: present
  ```

- **state**: This attribute determines the desired state of the package. The possible values are:
  - `present`: Ensures the package is installed.
  1. `latest`: Ensures the package is updated to the latest version available.
  2. `absent`: Ensures the package is removed.

  ```yaml
  - name: Remove MySQL server
    yum:
      name: mysql-server
      state: absent
  ```

### Adding Repositories Before Installing Packages

Sometimes, before installing a package, you may need to add a new repository. Ansible provides modules like `apt_repository` and `yum_repository` to handle this.

#### The `apt_repository` Module

This module is used to add repositories on Debian-based systems.

```yaml
- name: Add custom repository
  apt_repository:
    repo: deb http://example.com/repo stable main
```

#### The `yum_repository` Module

This module is used to add repositories on Red Hat-based systems.

```yaml
- name: Add custom repository
  yum_repository:
    name: custom-repo
    description: Custom Repository
    baseurl: http://example.com/repo
```

### Managing Services with Ansible

Another critical aspect of system administration is managing services. Ansible provides the `service` module to start, stop, restart, and reload services.

#### Attributes of the `service` Module

- **name**: The name of the service to be managed.
- **state**: Specifies the desired state of the service. Possible values include `started`, `stopped`, `restarted`, and `reloaded`.

```yaml
- name: Start Apache service
  service:
    name: apache2
    state: started
```

In this example, the `service` module ensures that the `apache2` service is started (`state: started`).

##### Detailed Explanation of Attributes

- **name**: This attribute specifies the service to be managed.
  
  ```yaml
  - name: Stop MySQL service
    service:
      name: mysqld
      state: stopped
  ```

- **state**: This attribute determines the desired state of the service. The possible values are:
  - `started`: Ensures the service is running.
  - `stopped`: Ensures the service is stopped.
  - `restarted`: Restarts the service.
  - `reloaded`: Reloads the service configuration.

  ```yaml
  - name: Restart Apache service
    service:
      name: apache2
      state: restarted
  ```

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-44228 (Log4Shell)

One of the most significant vulnerabilities in recent years is the Log4Shell vulnerability (CVE-2021-44228). This vulnerability affected the widely-used Apache Log4j library, allowing attackers to execute arbitrary code on affected systems.

To mitigate this vulnerability, organizations had to update their Log4j installations to a patched version. Ansible can be used to automate this process.

```yaml
- name: Update Log4j to a patched version
  apt:
    name: log4j
    state: latest
```

#### Example: CVE-2022-22965 (Apache Struts)

Another notable vulnerability is CVE-2022-22965, which affects the Apache Struts framework. This vulnerability allows remote code execution, making it critical to update affected systems.

```yaml
- name: Update Apache Struts to a patched version
  yum:
    name: struts
    state: latest
```

### How to Prevent / Defend

#### Detection

To detect outdated or vulnerable packages, you can use tools like `apt list --upgradable` or `yum check-update`. Additionally, integrating continuous monitoring tools like `Clair` or `Trivy` can help identify and alert on vulnerable packages.

#### Prevention

1. **Regular Updates**: Ensure that all systems are regularly updated to the latest versions of their packages.
2. **Automated Patch Management**: Use Ansible playbooks to automate the process of applying security patches.
3. **Secure Coding Practices**: Follow secure coding practices to minimize the risk of introducing vulnerabilities.

#### Secure Code Fix

Here’s an example of how to securely manage package updates using Ansible:

**Vulnerable Code:**

```yaml
- name: Install outdated package
  apt:
    name: vulnerable-package
    state: present
```

**Fixed Code:**

```yaml
- name: Install and keep package up-to-date
  apt:
    name: vulnerable-package
    state: latest
```

### Hands-On Practice

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for learning web application security.
- **OWASP Juice Shop**: An intentionally insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide a safe environment to practice and reinforce the concepts learned in this chapter.

### Conclusion

Managing packages and services using Ansible is a powerful way to automate and streamline system administration tasks. By understanding the attributes and usage of modules like `apt`, `yum`, and `service`, you can effectively manage software installations and updates across your infrastructure. Additionally, being aware of recent vulnerabilities and implementing robust detection and prevention strategies will help ensure the security of your systems.

---
<!-- nav -->
[[02-Introduction to Ansible Modules and Documentation|Introduction to Ansible Modules and Documentation]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/19-Navigating Ansible Module Documentation/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/19-Navigating Ansible Module Documentation/04-Practice Questions & Answers|Practice Questions & Answers]]
