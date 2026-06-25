---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating SSH Host Key Checks With Ansible

When working with Ansible to automate tasks across multiple servers, one critical aspect is ensuring the integrity and security of SSH connections. This involves verifying the host keys of remote servers to prevent man-in-the-middle attacks. Depending on your use case, you have two primary options for handling SSH host key checks:

1. **Strict Host Key Checking**: Ensures that the host key of the remote server is verified against a known list of keys. This is the default behavior and provides strong security but can be cumbersome in dynamic environments.
2. **Dynamic Host Key Acceptance**: Automatically accepts new host keys, which is more flexible but less secure.

### Strict Host Key Checking

#### What is Strict Host Key Checking?

Strict host key checking ensures that the SSH client verifies the host key of the remote server against a known list of keys stored in the `~/.ssh/known_hosts` file. If the host key does not match, the connection is refused. This prevents man-in-the-middle attacks where an attacker could intercept and modify the SSH traffic.

#### Why Use Strict Host Key Checking?

Using strict host key checking is crucial for maintaining the security of your SSH connections. It ensures that you are connecting to the correct server and not to an impersonator. This is particularly important in environments where security is paramount, such as financial institutions or government agencies.

#### How Does Strict Host Key Checking Work?

When you initiate an SSH connection, the SSH client retrieves the host key from the remote server and compares it against the known hosts file. If the key matches, the connection proceeds. If the key does not match, the connection is terminated, and an error message is displayed.

#### Example Configuration

To enforce strict host key checking in Ansible, you can set the `ansible_ssh_common_args` variable in your inventory file or playbook:

```yaml
---
- name: Example Playbook with Strict Host Key Checking
  hosts: all
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=yes'
  tasks:
    - name: Ensure strict host key checking is enforced
      debug:
        msg: "Strict host key checking is enabled"
```

#### Pitfalls and Common Mistakes

One common pitfall with strict host key checking is that it can break automation in dynamic environments where server IP addresses or hostnames change frequently. In such cases, you may need to manually update the `known_hosts` file or use a script to manage the host keys.

### Dynamic Host Key Acceptance

#### What is Dynamic Host Key Acceptance?

Dynamic host key acceptance automatically accepts new host keys without prompting the user. This is useful in environments where servers are frequently added or removed, and the overhead of managing host keys manually is too high.

#### Why Use Dynamic Host Key Acceptance?

Dynamic host key acceptance is often used in development and testing environments where flexibility is more important than strict security. It allows for seamless integration with CI/CD pipelines and automated deployment scripts.

#### How Does Dynamic Host Key Acceptance Work?

When you initiate an SSH connection with dynamic host key acceptance, the SSH client automatically adds the new host key to the `known_hosts` file without prompting the user. This allows the connection to proceed even if the host key has changed.

#### Example Configuration

To enable dynamic host key acceptance in Ansible, you can set the `ansible_ssh_common_args` variable in your inventory file or playbook:

```yaml
---
- name: Example Playbook with Dynamic Host Key Acceptance
  hosts: all
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
  tasks:
    - name: Ensure dynamic host key acceptance is enabled
      debug:
        msg: "Dynamic host key acceptance is enabled"
```

#### Pitfalls and Common Mistakes

The main pitfall with dynamic host key acceptance is that it reduces the security of your SSH connections. Without strict host key checking, you are more susceptible to man-in-the-middle attacks. Therefore, it should only be used in environments where the risk is acceptable.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-20225

In 2021, a vulnerability was discovered in the SSH protocol that allowed attackers to bypass host key verification. This vulnerability, CVE-2021-20225, affected several SSH clients and servers. By exploiting this vulnerability, an attacker could perform a man-in-the-middle attack even when strict host key checking was enabled.

#### How to Prevent / Defend

To defend against such vulnerabilities, ensure that your SSH clients and servers are up-to-date with the latest security patches. Additionally, use strict host key checking whenever possible and monitor your `known_hosts` file for unexpected changes.

#### Secure Coding Fixes

Here is an example of how to configure strict host key checking in Ansible:

**Vulnerable Code:**
```yaml
---
- name: Vulnerable Playbook
  hosts: all
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
  tasks:
    - name: Perform insecure SSH operations
      shell: echo "This is an insecure operation"
```

**Secure Code:**
```yaml
---
- name: Secure Playbook
  hosts: all
  vars:
    ansible_ssh_common_args: '-o StrictHostKeyChecking=yes'
  tasks:
    - name: Perform secure SSH operations
      shell: echo "This is a secure operation"
```

### Practice Labs

For hands-on practice with automating SSH host key checks using Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on SSH security that covers host key verification and man-in-the-middle attacks.
- **OWASP Juice Shop**: Provides a vulnerable application environment where you can practice securing SSH connections.
- **DVWA (Damn Vulnerable Web Application)**: Another platform for practicing web security, including SSH configurations.

By understanding and implementing the appropriate SSH host key checking strategy, you can significantly enhance the security of your automated tasks in a DevOps environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/14-Automating SSH Host Key Checks With Ansible/03-Introduction to SSH Key Authentication|Introduction to SSH Key Authentication]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/14-Automating SSH Host Key Checks With Ansible/00-Overview|Overview]] | [[05-Automating SSH Host Key Checks with Ansible|Automating SSH Host Key Checks with Ansible]]
