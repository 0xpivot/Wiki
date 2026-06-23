---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Key Concepts and Background Theory

### Private Key and Public Key

In the context of connecting to an EC2 instance, the private key and public key are crucial components of the SSH (Secure Shell) protocol. These keys form a cryptographic pair used for authentication and encryption.

#### What Are Private and Public Keys?

- **Private Key**: This is a secret key that should be kept confidential. It is used to decrypt messages sent to you and to sign messages you send.
- **Public Key**: This key is shared publicly. It is used to encrypt messages sent to you and to verify signatures made by your private key.

#### Why Are They Important?

- **Authentication**: The private key is used to prove your identity to the server. The server verifies this using the corresponding public key.
- **Encryption**: The public key can be used to encrypt data that only the holder of the private key can decrypt.

#### How Do They Work?

When you connect to an EC2 instance using SSH, the following steps occur:

1. **Key Exchange**: Your client sends the public key to the server.
2. **Verification**: The server uses the public key to verify the signature created by your private key.
3. **Session Establishment**: If the verification is successful, the session is established, and you can interact with the server.

#### Example of Key Usage

```bash
ssh -i ~/.ssh/id_rsa ec2-user@ec2-instance-public-dns
```

Here, `~/.ssh/id_rsa` is the path to your private key file, and `ec2-user` is the username on the EC2 instance.

### EC2 User

The `ec2-user` is a default administrative user provided by Amazon EC2 for Linux instances. This user has elevated privileges and can perform administrative tasks.

#### Why Is It Important?

- **Access Control**: By using `ec2-user`, you ensure that you have the necessary permissions to configure and manage the instance.
- **Security**: Using a dedicated administrative user helps in maintaining a separation of duties and reduces the risk of unauthorized access.

### Playbook Creation with Ansible

Ansible is an open-source automation tool used to automate IT infrastructure, including provisioning, configuration management, application deployment, and orchestration.

#### What Is a Playbook?

A playbook is a YAML file that contains a series of tasks to be executed on one or more remote servers. It defines the desired state of the system and how to achieve it.

#### Why Use Playbooks?

- **Repeatability**: Playbooks can be run multiple times to ensure the system remains in the desired state.
- **Idempotency**: Ansible ensures that tasks are only executed if necessary, avoiding unnecessary changes.
- **Documentation**: Playbooks serve as documentation for the configuration of the system.

#### Example Playbook Structure

```yaml
---
- name: Install Docker on EC2 Instance
  hosts: docker_server
  become: yes
  tasks:
    - name: Install Docker
      yum:
        name: docker
        state: present
```

### Package Manager Differences

Different Linux distributions use different package managers. For example, Ubuntu uses `apt`, CentOS uses `yum`, and Fedora uses `dnf`.

#### Why Does It Matter?

- **Compatibility**: Understanding the package manager used by your distribution ensures that you can correctly install and manage software.
- **Automation**: In Ansible playbooks, you need to specify the correct module (`apt`, `yum`, etc.) to ensure compatibility with the target system.

#### Example of Package Installation

```bash
# On Ubuntu
sudo apt update
sudo apt install docker.io

# On CentOS
sudo yum update
sudo yum install docker
```

### Ansible Modules

Ansible modules are reusable components that perform specific tasks. The `yum` module is used to manage packages on systems that use the `yum` package manager.

#### Example of Using the `yum` Module

```yaml
---
- name: Install Docker on EC2 Instance
  hosts: docker_server
  become: yes
  tasks:
    - name: Install Docker
      yum:
        name: docker
        state: present
```

### Common Pitfalls and How to Prevent Them

#### Incorrect Key Usage

**Vulnerable Pattern:**

```bash
ssh -i ~/.ssh/id_rsa wrong_user@ec2-instance-public-dns
```

**Secure Fix:**

```bash
ssh -i ~/.ssh/id_rsa ec2-user@ec2-instance-public-dns
```

#### Incorrect Package Manager

**Vulnerable Pattern:**

```yaml
---
- name: Install Docker on EC2 Instance
  hosts: docker_server
  become: yes
  tasks:
    - name: Install Docker
      apt:
        name: docker
        state: present
```

**Secure Fix:**

```yaml
---
- name: Install Docker on EC2 Instance
  hosts: docker_server
  become: yes
  tasks:
    - name: Install Docker
      yum:
        name: docker
        state: present
```

### Detection and Prevention

#### Detection

- **Logging**: Ensure that SSH and package installation logs are enabled and monitored.
- **Audit Tools**: Use tools like `auditd` to track changes made to the system.

#### Prevention

- **Key Management**: Store private keys securely and limit access to them.
- **User Permissions**: Use the `ec2-user` for administrative tasks and restrict access to other users.
- **Playbook Validation**: Regularly review and test Ansible playbooks to ensure they work as intended.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21330**: A vulnerability in Docker that allowed unauthorized access to the Docker daemon.
- **Breaches**: Many breaches have occurred due to misconfigured SSH keys and unauthorized access to servers.

### Hands-On Labs

For practical experience with automated Docker setup on AWS EC2 with Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide a controlled environment to practice and understand the concepts discussed.

### Conclusion

Understanding the key concepts of SSH keys, EC2 users, and Ansible playbooks is crucial for automating Docker setup on AWS EC2 instances. By following best practices and using secure configurations, you can ensure that your infrastructure remains robust and secure.

---
<!-- nav -->
[[04-Introduction to Docker Setup on AWS EC2 with Ansible|Introduction to Docker Setup on AWS EC2 with Ansible]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/11-Automated Docker Setup on AWS EC2 with Ansible/00-Overview|Overview]] | [[06-Automated Docker Setup on AWS EC2 with Ansible|Automated Docker Setup on AWS EC2 with Ansible]]
