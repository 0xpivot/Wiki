---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Ansible and Docker Modules

Ansible is a powerful automation tool used in DevOps environments to manage infrastructure and applications. One of its key features is the ability to handle Docker images and containers through specific modules. This chapter will delve into the intricacies of using Docker modules in Ansible, focusing on state management and the importance of fully qualified names.

### Background Theory

Ansible uses modules to perform specific tasks, such as deploying Docker images. These modules can be part of built-in collections or custom collections. The naming convention for these modules has evolved over time, with Ansible version 2.10 introducing fully qualified names to enhance clarity and avoid conflicts.

#### Naming Constructs

In Ansible, a module can be referenced in two ways:

1. **Fully Qualified Name**: This includes the namespace and collection name, e.g., `docker_container`.
2. **Module Name Only**: This omits the namespace and collection name, e.g., `container`.

The transition to fully qualified names was necessary to maintain backward compatibility while introducing new features and avoiding naming conflicts.

### Backward Compatibility in Ansible

Ansible version 2.10 introduced fully qualified names to improve modularity and avoid conflicts. However, to ensure backward compatibility, Ansible allows the use of module names without the namespace and collection names. This means that you can still use the module name alone, but it is recommended to use fully qualified names in future versions.

#### Example: Using Module Names Without Namespace

```yaml
---
- name: Deploy Docker Image
  hosts: localhost
  tasks:
    - name: Pull Docker image
      docker_image:
        name: nginx
```

This playbook uses the `docker_image` module without specifying the namespace and collection name. While this works, it may lead to confusion and potential conflicts in larger projects.

#### Example: Using Fully Qualified Names

```yaml
---
- name: Deploy Docker Image
  hosts: localhost
  tasks:
    - name: Pull Docker image
      community.docker.docker_image:
        name: nginx
```

Here, the fully qualified name `community.docker.docker_image` is used, which is more explicit and less prone to errors.

### How Ansible Resolves Module Names

When you run an Ansible playbook, Ansible resolves the module names based on the configuration and available collections. To understand this process, you can use the `-vvv` flag, which provides verbose output.

#### Example: Running Playbook with Verbose Output

```sh
ansible-playbook deploy_docker.yml -vvv
```

This command will display detailed information about how Ansible resolves the modules defined in the playbook.

#### Detailed Output Explanation

```plaintext
...
<...>
enziplaybook 2.10.0
config file = /etc/ansible/ansible.cfg
configured module search path = ['/usr/share/ansible/plugins/modules', '/home/user/.ansible/plugins/modules']
ansible python module location = /usr/lib/python3/dist-packages/ansible
executable location = /usr/bin/ansible
python version = 3.8.10 (default, Nov 26 2021, 20:14:08) [GCC 9.3.0]
...
```

This output shows the version of Ansible, the configuration file location, the module search path, and other relevant details. The module search path indicates where Ansible looks for modules, ensuring that the correct module is used.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities often involve misconfigurations or improper use of automation tools like Ansible. For instance, a breach might occur due to a misconfigured Docker container that exposes sensitive data.

#### Example: CVE-2021-44228 (Log4Shell)

CVE-2021-44228, also known as Log4Shell, affected many systems, including those managed by Ansible. A misconfigured Docker container could expose a vulnerable application, leading to a breach.

#### Secure Configuration Example

To prevent such issues, ensure that Docker containers are properly configured and that sensitive data is protected. Here’s an example of a secure configuration:

```yaml
---
- name: Deploy Secure Docker Image
  hosts: localhost
  tasks:
    - name: Pull Docker image
      community.docker.docker_image:
        name: nginx
        pull: yes
        force_pull: yes
    - name: Run Docker container
      community.docker.docker_container:
        name: secure_nginx
        image: nginx
        ports:
          - "80:80"
        volumes:
          - "/data/nginx:/var/www/html"
```

This playbook ensures that the Docker image is pulled securely and that the container is configured to protect sensitive data.

### Common Pitfalls and How to Avoid Them

#### Pitfall: Using Insecure Docker Images

Using insecure Docker images can lead to vulnerabilities. Always ensure that the images are from trusted sources and are up-to-date.

#### Secure Coding Practices

Use fully qualified names to avoid conflicts and ensure clarity. Here’s a comparison of insecure and secure configurations:

**Insecure Configuration**

```yaml
---
- name: Deploy Docker Image
  hosts: localhost
  tasks:
    - name: Pull Docker image
      docker_image:
        name: nginx
```

**Secure Configuration**

```yaml
---
- name: Deploy Docker Image
  hosts: localhost
  tasks:
    - name: Pull Docker image
      community.docker.docker_image:
        name: nginx
```

### Detection and Prevention

#### Detection

Regularly audit your Ansible playbooks and configurations to ensure they are secure. Use tools like `ansible-lint` to check for common issues.

#### Prevention

1. **Use Fully Qualified Names**: Ensure that all module names are fully qualified to avoid conflicts.
2. **Regular Updates**: Keep Ansible and Docker images up-to-date to mitigate vulnerabilities.
3. **Secure Configurations**: Follow best practices for configuring Docker containers and Ansible playbooks.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security, including Docker configurations.
- **OWASP Juice Shop**: Provides a vulnerable web application for practice.
- **DVWA (Damn Vulnerable Web Application)**: Another resource for practicing web application security.

These labs provide real-world scenarios to apply the concepts learned in this chapter.

### Conclusion

Understanding how to use Docker modules in Ansible for state management is crucial for effective DevOps practices. By following best practices and using fully qualified names, you can ensure that your configurations are secure and efficient. Regular audits and updates are essential to maintaining a robust and secure environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/16-Docker Modules in Ansible for State Management/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/16-Docker Modules in Ansible for State Management/02-Introduction to Docker Compose|Introduction to Docker Compose]]
