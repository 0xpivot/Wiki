---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Ansible (Ansible) Server Management

Ansible (correctly spelled Ansible) is an open-source automation tool used for configuration management, application deployment, and task automation. It simplifies the process of managing infrastructure and applications across multiple servers by providing a simple yet powerful framework. This chapter will delve into setting up Ansible server management using inventory files, explaining the concepts, commands, and practical applications in detail.

### What is Ansible?

Ansible is a configuration management tool that automates IT tasks such as provisioning, configuring, and deploying applications. It uses a simple language called YAML to define tasks and plays, making it easy to understand and maintain. Ansible operates agentless, meaning it does not require any additional software to be installed on the managed nodes; it relies on SSH for communication.

#### Why Use Ansible?

1. **Agentless**: No need to install agents on managed nodes.
2. **Simple Language**: Uses YAML, which is human-readable and easy to learn.
3. **Idempotent**: Ensures that configurations are applied consistently and repeatedly without causing errors.
4. **Role-Based Configuration**: Allows for modular and reusable configurations.
5. **Inventory Management**: Supports complex inventory management through dynamic and static inventories.

### Setting Up Ansible Inventory Files

An Ansible inventory file is a list of hosts and groups that Ansible manages. It defines the target systems and their attributes. The inventory file is crucial for specifying which hosts to manage and how to group them.

#### Structure of an Inventory File

The basic structure of an inventory file includes:

```yaml
[all]
host1 ansible_host=192.168.1.1
host2 ansible_host=192.168.1.2

[web_servers]
host1
host2

[databases]
host3 ansible_host=192.168.1.3
```

Here, `all` is a default group containing all hosts, and `web_servers` and `databases` are custom groups.

### Specifying the Host File

When running Ansible commands, you need to specify which inventory file to use. This is done using the `-i` flag followed by the path to the inventory file.

#### Example Command

```bash
ansible -i /path/to/inventory all -m ping
```

This command tells Ansible to use the specified inventory file and ping all hosts listed in it.

### Executing Commands with Modules

Ansible uses modules to perform specific tasks. A module is a container for one specific command or set of commands. The `ping` module is used to check if the remote host is reachable.

#### Ping Module

The `ping` module sends a simple ICMP echo request to the remote host to verify connectivity.

```bash
ansible -i /path/to/inventory all -m ping
```

This command will ping all hosts listed in the inventory file.

### Handling SSH Key Authenticity Prompts

When connecting to a new host via SSH, you might encounter a host key authenticity prompt. This is a security measure to ensure that the host you are connecting to is indeed the one you expect.

#### Example Output

```plaintext
SSH host key for 192.168.1.1 has changed:
old key type ssh-rsa, fingerprint SHA256:abc123...
new key type ssh-rsa, fingerprint SHA256:def456...
It is recommended that you update your known_hosts file.
Failed to verify the SSH host key for 192.168.1.1: Host key verification failed.
```

To handle this, you can either manually confirm the host key or configure Ansible to automatically accept new keys.

### Managing Multiple Platforms

Imagine you have servers on multiple different platforms, such as DigitalOcean, AWS, and another cloud provider. You can manage these servers using a single Ansible inventory file.

#### Example Inventory File

```yaml
[DigitalOcean]
host1 ansible_host=192.168.1.1
host2 ansible_host=192.168.1.2

[AWS]
host3 ansible_host=10.0.0.1
host4 ansible_host=10.0.0.2

[OtherPlatform]
host5 ansible_host=172.16.0.1
```

### Detailed Example: Pinging Servers

Let's walk through a detailed example of pinging servers using Ansible.

#### Step 1: Create the Inventory File

Create a file named `inventory.ini` with the following content:

```ini
[all]
host1 ansible_host=192.168.1.1
host2 ansible_host=192.168.1.2

[web_servers]
host1
host2

[databases]
host3 ansible_host=192.168.1.3
```

#### Step 2: Run the Ping Command

Run the following command to ping all hosts:

```bash
ansible -i inventory.ini all -m ping
```

#### Expected Output

```plaintext
host1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
host2 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
host3 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Handling SSH Key Authenticity Prompts

If you encounter an SSH key authenticity prompt, you can manually confirm the host key or configure Ansible to automatically accept new keys.

#### Manually Confirming Host Keys

Manually confirm the host key by typing `yes` when prompted.

#### Automatically Accepting New Keys

Configure Ansible to automatically accept new keys by adding the following to your `ansible.cfg` file:

```ini
[defaults]
host_key_checking = False
```

### How to Prevent / Defend

#### Detecting SSH Key Changes

Monitor SSH key changes by regularly checking the `known_hosts` file.

#### Preventing Unauthorized Access

1. **Use Strong Authentication**: Ensure strong SSH authentication methods like public key authentication.
2. **Limit SSH Access**: Restrict SSH access to trusted IP addresses.
3. **Regular Audits**: Regularly audit SSH configurations and logs.

#### Secure Coding Fixes

Compare the insecure and secure versions of the `known_hosts` handling:

**Insecure Version**

```bash
ssh-keyscan -H 192.168.1.1 >> ~/.ssh/known_hosts
```

**Secure Version**

```bash
ssh-keyscan -H 192.168.1.1 | ssh-keygen -lf -
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-44228 (Log4Shell)**: Demonstrates the importance of regular audits and updates.
- **SolarWinds Supply Chain Attack**: Highlights the need for strong authentication and monitoring.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**
- **OWASP Juice Shop**
- **DVWA (Damn Vulnerable Web Application)**
- **WebGoat**

These labs provide practical experience in managing and securing servers using Ansible.

### Conclusion

This chapter covered the setup and usage of Ansible for server management, including inventory files, modules, and handling SSH key prompts. By following these steps and best practices, you can effectively manage and secure your infrastructure using Ansible.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/09-Ansible Server Management Setup Using Inventory Files/00-Overview|Overview]] | [[02-Introduction to Ansible Inventory Files|Introduction to Ansible Inventory Files]]
