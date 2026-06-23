---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating SSH Host Key Checks with Ansible

### Introduction to SSH Host Key Checks

SSH (Secure Shell) is a cryptographic network protocol used for secure communication between a client and a server. One of the fundamental security features of SSH is the verification of the server's identity through its host key. When an SSH client connects to a server for the first time, it receives the server's public host key and stores it locally. This stored key is used in subsequent connections to verify that the server remains the same.

The host key check ensures that the client is connecting to the correct server and not a man-in-the-middle attacker. However, this check can become cumbersome in automated environments, especially when dealing with many servers or ephemeral instances.

### Why Automate SSH Host Key Checks?

In a DevOps environment, automation is key to maintaining efficiency and consistency. Manually confirming the host key check for each new server can significantly slow down the deployment process. Therefore, automating this process is essential for seamless integration and scaling.

### Configuring SSH Host Key Checks in Ansible

Ansible is a powerful automation tool that simplifies the management of infrastructure and application deployments. To automate SSH host key checks in Ansible, we need to configure the `ssh_known_hosts` module and set appropriate parameters in the playbook.

#### Long-Running Servers

For long-running servers, we can configure the SSH host key check once and ensure it remains valid indefinitely. This approach is suitable for servers that are created once and remain operational for extended periods.

##### Step-by-Step Configuration

1. **Create the Droplet**: First, create a new droplet using your preferred cloud provider. For this example, we'll use DigitalOcean and create a droplet in the Amsterdam region.

```bash
# Create a new droplet using DigitalOcean API
curl -X POST "https://api.digitalocean.com/v2/droplets" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{
           "name": "example-droplet",
           "region": "ams3",
           "size": "s-1vcpu-1gb",
           "image": "ubuntu-20-04-x64",
           "ssh_keys": ["YOUR_SSH_KEY_ID"],
           "tags": ["ansible"]
         }'
```

2. **Configure SSH Known Hosts**: Use the `ssh_known_hosts` module in Ansible to manage the known hosts file.

```yaml
---
- name: Configure SSH known hosts
  hosts: localhost
  tasks:
    - name: Add SSH host key to known_hosts
      ssh_known_hosts:
        path: ~/.ssh/known_hosts
        name: "{{ ansible_host }}"
        key: "{{ lookup('file', '/path/to/host/key') }}"
        state: present
```

3. **Run the Playbook**: Execute the playbook to add the host key to the known hosts file.

```bash
ansible-playbook -i inventory_file playbook.yml
```

### Handling Ephemeral Servers

Ephemeral servers are short-lived instances that are frequently created and destroyed. For such servers, managing SSH host keys becomes more complex due to their transient nature.

#### Dynamic Host Key Management

To handle ephemeral servers, we can dynamically manage SSH host keys within the Ansible playbook. This involves setting up the `ssh_known_hosts` module to automatically update the known hosts file whenever a new server is added.

##### Example Playbook

```yaml
---
- name: Manage SSH known hosts for ephemeral servers
  hosts: all
  gather_facts: no
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

  tasks:
    - name: Add SSH host key to known_hosts
      ssh_known_hosts:
        path: ~/.ssh/known_hosts
        name: "{{ ansible_host }}"
        key: "{{ lookup('file', '/path/to/host/key') }}"
        state: present
```

### Real-World Examples and CVEs

Recent breaches and vulnerabilities often involve misconfigured SSH settings, leading to unauthorized access. For instance, the CVE-2021-3560 (also known as "Log4Shell") exploited a flaw in the Apache Log4j library, which could be leveraged to gain SSH access to systems.

#### Secure Coding Practices

To prevent such vulnerabilities, it is crucial to follow secure coding practices:

1. **Use Strong Authentication Methods**: Implement multi-factor authentication (MFA) for SSH access.
2. **Regularly Update SSH Software**: Keep SSH software up-to-date to patch known vulnerabilities.
3. **Audit SSH Configurations**: Regularly audit SSH configurations to ensure compliance with security policies.

### How to Prevent / Defend

#### Detection

1. **Monitor SSH Logs**: Regularly monitor SSH logs for suspicious activities.
2. **Use Intrusion Detection Systems (IDS)**: Deploy IDS to detect and alert on potential SSH attacks.

#### Prevention

1. **Disable Root Login**: Disable root login via SSH to prevent direct access to the root account.
2. **Limit SSH Access**: Restrict SSH access to specific IP addresses or ranges.
3. **Use SSH Key-Based Authentication**: Use SSH key-based authentication instead of password-based authentication.

#### Secure Code Fix

**Vulnerable Code**

```yaml
---
- name: Vulnerable SSH configuration
  hosts: all
  gather_facts: no
  vars:
    ansible_ssh_common_args: ''

  tasks:
    - name: Add SSH host key to known_hosts
      ssh_known_hosts:
        path: ~/.ssh/known_hosts
        name: "{{ ansible_host }}"
        key: "{{ lookup('file', '/path/to/host/key') }}"
        state: present
```

**Fixed Code**

```yaml
---
- name: Secure SSH configuration
  hosts: all
  gather_facts: no
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'

  tasks:
    - name: Add SSH host key to known_hosts
      ssh_known_hosts:
        path: ~/.ssh/known_hosts
        name: "{{ ansible_host }}"
        key: "{{ lookup('file', '/path/to/host/key') }}"
        state: present
```

### Conclusion

Automating SSH host key checks with Ansible is crucial for maintaining efficient and secure DevOps practices. By configuring the `ssh_known_hosts` module and following secure coding practices, you can ensure that your infrastructure remains robust against potential threats.

### Practice Labs

For hands-on experience with automating SSH host key checks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on SSH and related security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for testing and learning security concepts.

These labs will help you apply the theoretical knowledge gained in this chapter to real-world scenarios.

---
<!-- nav -->
[[04-Automating SSH Host Key Checks With Ansible|Automating SSH Host Key Checks With Ansible]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/14-Automating SSH Host Key Checks With Ansible/00-Overview|Overview]] | [[06-Understanding SSH Host Key Checks|Understanding SSH Host Key Checks]]
