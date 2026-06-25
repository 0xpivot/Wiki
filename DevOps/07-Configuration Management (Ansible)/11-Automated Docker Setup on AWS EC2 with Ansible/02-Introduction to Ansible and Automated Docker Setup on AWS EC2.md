---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Ansible and Automated Docker Setup on AWS EC2

In this section, we will delve into the automation of Docker setup on AWS EC2 using Ansible, a powerful configuration management tool. Ansible allows us to manage infrastructure as code, ensuring consistency and reliability across different environments. We will cover the necessary steps to automate the setup of Docker on an EC2 instance, including handling permission issues and ensuring services are running correctly.

### What is Ansible?

Ansible is a configuration management tool similar to Ansible but designed specifically for managing cloud infrastructure. It provides a simple yet powerful way to define and apply configurations to servers and other resources. Ansible uses playbooks written in YAML to describe the desired state of the system, making it easy to maintain and scale.

#### Why Use Ansible?

Using Ansible offers several benefits:

1. **Consistency**: Ensures that all servers are configured identically.
2. **Automation**: Reduces manual errors and speeds up deployment processes.
3. **Idempotence**: Configurations can be applied repeatedly without changing the result.
4. **Version Control**: Playbooks can be stored in version control systems, allowing for easy tracking of changes.

### Setting Up Docker on AWS EC2

To set up Docker on an AWS EC2 instance, we will use Ansible to automate the process. This includes installing Docker, copying Docker Compose files, and starting Docker services.

#### Prerequisites

Before we begin, ensure you have the following:

1. **AWS Account**: An active AWS account with access to EC2 instances.
2. **Ansible Installed**: Ensure Ansible is installed on your local machine.
3. **EC2 Instance**: An EC2 instance running Linux (e.g., Ubuntu).

### Ansible Playbook Structure

An Ansible playbook consists of a series of tasks organized into plays. Each task defines a specific action to be performed on the target hosts. Here’s a basic structure of an Ansible playbook:

```yaml
---
- name: Setup Docker on EC2
  hosts: ec2_instances
  become: yes
  tasks:
    - name: Install Docker
      apt:
        name: docker.io
        state: present

    - name: Copy Docker Compose file
      copy:
        src: ./docker-compose.yml
        dest: /opt/docker-compose.yml

    - name: Start Docker service
      systemd:
        name: docker
        state: started
```

### Handling Permission Issues

During the setup process, you might encounter permission issues, such as `permission denied` errors. To resolve these, we can use Ansible’s `matter` module to reset the connection immediately after adding a user to a group.

#### Example Playbook with Permission Handling

Here’s an example playbook that includes handling permission issues:

```yaml
---
- name: Setup Docker on EC2
  hosts: ec2_instances
  become: yes
  tasks:
    - name: Add user to sudo group
      user:
        name: ubuntu
        groups: sudo
        append: yes

    - name: Reset connection
      matter:
        value: reset_connection

    - name: Install Docker
      apt:
        name: docker.io
        state: present

    - name: Copy Docker Compose file
      copy:
        src: ./docker-compose.yml
        dest: /opt/docker-compose.yml

    - name: Start Docker service
      systemd:
        name: docker
        state: started
```

### Testing the Playbook

To test the playbook, run the following command:

```bash
ansible-playbook setup_docker.yml
```

If everything is set up correctly, you should see output indicating successful execution without any errors.

### Naming Conventions in Ansible Tasks

In Ansible, it’s important to name tasks descriptively to understand their purpose. This helps in maintaining and debugging playbooks. Here are some examples of good task names:

- `ensure Docker is running`
- `make sure Docker is not running`
- `make sure Python 3 and Docker are installed`

These names clearly indicate the desired outcome of the task.

### Real-World Examples and Recent CVEs

#### Example: Docker Security Vulnerability (CVE-2021-29923)

In 2021, a critical vulnerability was discovered in Docker (CVE-2021-29923). This vulnerability allowed attackers to escalate privileges and execute arbitrary code on the host system. To mitigate this, it’s crucial to keep Docker and its dependencies up to date.

#### Secure Configuration Example

Here’s an example of how to securely configure Docker using Ansible:

```yaml
---
- name: Secure Docker Configuration
  hosts: ec2_instances
  become: yes
  tasks:
    - name: Update Docker to latest version
      apt:
        name: docker.io
        state: latest

    - name: Disable Docker API
      lineinfile:
        path: /etc/docker/daemon.json
        regexp: '^ *"$'
        line: '{"api-enable": false}'
        create: yes

    - name: Restart Docker service
      systemd:
        name: docker
        state: restarted
```

### How to Prevent / Defend

#### Detection

To detect potential issues, regularly monitor logs and use security tools like Docker Security Scanning. For example, you can use the following command to scan images:

```bash
docker scan <image-name>
```

#### Prevention

1. **Keep Software Updated**: Regularly update Docker and its dependencies.
2. **Use Secure Configurations**: Follow best practices for securing Docker configurations.
3. **Limit Privileges**: Run Docker with minimal privileges and avoid running as root.

#### Secure Coding Fixes

Here’s an example of a vulnerable vs. secure Docker configuration:

**Vulnerable Configuration:**

```yaml
version: '3'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      - DB_HOST=db
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

**Secure Configuration:**

```yaml
version: '3'
services:
  web:
    image: myapp:latest
    ports:
      - "80:80"
    environment:
      - DB_HOST=db
    volumes:
      - /var/lib/myapp:/var/lib/myapp
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises for web application security.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security skills.
- **CloudGoat**: Provides scenarios for practicing cloud security on AWS.

### Conclusion

Automating Docker setup on AWS EC2 using Ansible ensures consistent and reliable configurations. By following best practices and using secure configurations, you can mitigate potential vulnerabilities and ensure the security of your Docker environment.

### Further Reading

- **Ansible Documentation**: Official documentation for Ansible.
- **Docker Security Best Practices**: Guidelines for securing Docker installations.
- **AWS Security Best Practices**: Recommendations for securing AWS environments.

By mastering these concepts, you will be well-equipped to handle complex DevOps tasks and ensure the security of your infrastructure.

---
<!-- nav -->
[[01-Introduction to Ansible Playbooks and Python Interpreters|Introduction to Ansible Playbooks and Python Interpreters]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/11-Automated Docker Setup on AWS EC2 with Ansible/00-Overview|Overview]] | [[03-Introduction to Automated Docker Setup on AWS EC2 with Ansible|Introduction to Automated Docker Setup on AWS EC2 with Ansible]]
