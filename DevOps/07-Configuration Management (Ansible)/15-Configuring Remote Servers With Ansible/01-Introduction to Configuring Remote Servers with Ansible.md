---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Configuring Remote Servers with Ansible

In this section, we will delve into the process of configuring remote servers using Ansible, a powerful open-source automation tool. Ansible simplifies the management of infrastructure by allowing you to automate tasks such as provisioning, configuring, and deploying applications across multiple servers. This chapter will cover the setup of remote servers, connecting to them via SSH, and ensuring the necessary prerequisites are met for Ansible to function correctly.

### Creating Remote Servers on DigitalOcean

To begin, we'll create two remote servers on DigitalOcean, a popular cloud hosting provider. These servers will serve as our target machines for Ansible configurations.

#### Step-by-Step Guide to Create Droplets

1. **Log in to Your DigitalOcean Account**:
    - Navigate to the DigitalOcean website and log in to your account.

2. **Create Droplets**:
    - Click on the "Create" button and select "Droplets".
    - Choose the desired image. In this case, we'll use Ubuntu, a widely-used Linux distribution.
    - Select the size of the droplet. For simplicity, we'll choose the second smallest size available.
    - Choose the region where you want your servers to be located. This decision can affect latency and performance based on your geographical location.
    - Configure the SSH keys. Ensure that you have an SSH key configured in your DigitalOcean account. This key will allow you to securely access the servers via SSH.
    - Specify the number of droplets to create. In this scenario, we'll create two droplets.

```mermaid
graph TD
    A[Login to DigitalOcean] --> B[Create Droplets]
    B --> C[Choose Image (Ubuntu)]
    C --> D[Select Size (Second Smallest)]
    D --> E[Choose Region]
    E --> F[Configure SSH Keys]
    F --> G[Specify Number of Droplets (2)]
    G --> H[Create Droplets]
```

#### Confirming the Creation of Droplets

Once you've completed the above steps, DigitalOcean will create the droplets. You can monitor their status in the DigitalOcean dashboard. Once the droplets are active, you can proceed to the next steps.

### Connecting to Remote Servers Using SSH

Ansible uses SSH to communicate with the remote servers. This means that the servers must be accessible via SSH, and the necessary SSH keys must be set up correctly.

#### Prerequisites for SSH Access

1. **SSH Key Configuration**:
    - Ensure that the SSH key used to access the servers is properly configured in your DigitalOcean account.
    - The public key should be added to the server's `~/.ssh/authorized_keys` file.

2. **Host Key Verification**:
    - When you first connect to a new server via SSH, you will be prompted to verify the host key. This ensures that you are connecting to the correct server and not a malicious one.

#### SSH Connection Example

Let's demonstrate how to SSH into one of the created droplets:

```sh
ssh root@<server_ip>
```

Upon connecting, you might see a prompt like this:

```
The authenticity of host '<server_ip>' can't be established.
ECDSA key fingerprint is SHA256:<key_fingerprint>.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Confirm the connection by typing `yes`.

### Ensuring Python is Installed on Linux Servers

For Ansible to function correctly, the target servers must have Python installed. Ansible is written in Python and relies on the Python interpreter to execute commands and manage configurations.

#### Checking Python Installation

To check if Python is installed on your server, run the following command:

```sh
python --version
```

If Python is not installed, you can install it using the package manager specific to your Linux distribution. For Ubuntu, you can use:

```sh
sudo apt update
sudo apt install python3
```

#### Verifying Python Installation

After installation, verify the Python version again:

```sh
python3 --version
```

### Ensuring PowerShell is Installed on Windows Servers

If you were working with Windows servers instead of Linux, you would need to ensure that PowerShell is installed. PowerShell is the default shell for Windows and is required for Ansible to manage Windows servers.

#### Checking PowerShell Installation

To check if PowerShell is installed, you can run:

```sh
powershell -Command "Get-Host"
```

If PowerShell is not installed, you can install it using the Windows Package Manager (`winget`):

```sh
winget install Microsoft.PowerShell
```

### Connecting Ansible to Remote Servers

Now that the servers are set up and the necessary prerequisites are met, we can proceed to connect Ansible to the remote servers.

#### Setting Up Ansible Inventory

Ansible uses an inventory file to define the target servers. This file contains the IP addresses or hostnames of the servers along with any additional variables needed for configuration.

Here’s an example of an Ansible inventory file (`inventory.ini`):

```ini
[webservers]
server1 ansible_host=<server1_ip> ansible_user=root
server2 ansible_host=<server2_ip> ansible_user=root
```

#### Running an Ansible Playbook

An Ansible playbook is a YAML file that defines the tasks to be executed on the remote servers. Here’s a simple example of a playbook (`playbook.yml`):

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
    - name: Start Apache service
      service:
        name: apache2
        state: started
        enabled: yes
```

To run the playbook, use the following command:

```sh
ansible-playbook -i inventory.ini playbook.yml
```

### Common Pitfalls and How to Prevent Them

#### Incorrect SSH Key Configuration

**Issue**: If the SSH key is not correctly configured, you may encounter errors when trying to connect to the servers.

**Prevention**:
- Ensure that the public SSH key is added to the server's `~/.ssh/authorized_keys` file.
- Verify that the private key is correctly set up on your local machine.

#### Missing Python Installation

**Issue**: If Python is not installed on the Linux servers, Ansible will fail to execute commands.

**Prevention**:
- Always check and install Python on the target servers before running Ansible playbooks.

#### Incorrect Inventory File

**Issue**: If the inventory file is incorrectly configured, Ansible may not be able to connect to the correct servers.

**Prevention**:
- Double-check the inventory file to ensure that the IP addresses and usernames are correct.

### Real-World Examples and Recent CVEs

#### CVE-2021-21277: Ansible Vulnerability

CVE-2021-21277 is a vulnerability in Ansible that allows an attacker to execute arbitrary code on the target system. This vulnerability arises due to improper validation of user input in certain modules.

**Impact**: An attacker could exploit this vulnerability to gain unauthorized access to the target system.

**Mitigation**:
- Ensure that you are using the latest version of Ansible.
- Regularly update your Ansible modules to patch known vulnerabilities.

#### Example Exploit and Detection

Here’s an example of how an attacker might exploit this vulnerability:

```yaml
---
- name: Exploit CVE-2021-21277
  hosts: all
  tasks:
    - name: Execute arbitrary code
      shell: echo "Exploited" > /tmp/exploit.txt
```

**Detection**:
- Monitor your systems for unexpected changes or files.
- Use intrusion detection systems (IDS) to detect suspicious activities.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
---
- name: Vulnerable playbook
  hosts: all
  tasks:
    - name: Execute untrusted input
      shell: "{{ untrusted_input }}"
```

#### Secure Code Example

```yaml
---
- name: Secure playbook
  hosts: all
  tasks:
    - name: Validate input before execution
      shell: "{{ trusted_input | regex_replace('[^a-zA-Z0-9]', '') }}"
```

### Conclusion

In this chapter, we covered the process of setting up remote servers on DigitalOcean, connecting to them via SSH, and ensuring the necessary prerequisites are met for Ansible to function correctly. We also explored common pitfalls and provided real-world examples and recent CVEs to illustrate potential security issues and mitigation strategies.

By following the steps outlined in this chapter, you should be able to effectively configure and manage remote servers using Ansible. Remember to always follow secure coding practices and regularly update your tools to mitigate potential vulnerabilities.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning about web application security.
- **WebGoat**: A deliberately insecure Java application for learning about web application security.

These labs provide a comprehensive environment to practice and reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/15-Configuring Remote Servers With Ansible/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/15-Configuring Remote Servers With Ansible/02-Practice Questions & Answers|Practice Questions & Answers]]
