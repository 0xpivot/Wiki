---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the SSH host key check and why it is important.**

The SSH host key check is a security measure designed to ensure that the client is connecting to the intended server and not a malicious impersonator. When a client connects to a server for the first time, the server's public key is stored in the client's `~/.ssh/known_hosts` file. On subsequent connections, the client verifies that the server's key matches the one stored in `known_hosts`. This helps prevent man-in-the-middle attacks by ensuring the authenticity of the server.

**Q2. How can you automate SSH host key checks with Ansible for long-running servers?**

To automate SSH host key checks for long-running servers with Ansible, you can manually add the server's public key to the `~/.ssh/known_hosts` file on the Ansible control node. This can be done using the `ssh-keyscan` command:

```bash
ssh-keyscan <server_ip_or_hostname> >> ~/.ssh/known_hosts
```

Once the server's key is added to `known_hosts`, Ansible can connect to the server without prompting for manual confirmation. Additionally, ensure that the server's authorized_keys file contains the public SSH key of the Ansible control node. This can be achieved using the `ssh-copy-id` command:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub root@<server_ip_or_hostname>
```

**Q3. How would you disable SSH host key checks in Ansible for an ephemeral infrastructure?**

For ephemeral infrastructures where servers are frequently created and destroyed, disabling SSH host key checks can simplify automation. This can be done by configuring Ansible to skip host key verification. Create an `ansible.cfg` file in the user's home directory (`~/.ansible.cfg`) or in the project directory (`./ansible.cfg`). Add the following configuration:

```ini
[defaults]
host_key_checking = False
```

This setting ensures that Ansible does not prompt for host key confirmation when connecting to new servers. For example, if you are working within a specific Ansible project directory, you can place the `ansible.cfg` file there:

```ini
# ./ansible.cfg
[defaults]
host_key_checking = False
```

**Q4. Describe a scenario where disabling SSH host key checks might pose a security risk.**

Disabling SSH host key checks can pose a significant security risk in environments where servers are static and long-lived. Without host key verification, an attacker could potentially intercept SSH connections and perform man-in-the-middle attacks. For instance, consider a scenario where an attacker gains access to a network and sets up a rogue SSH server. If SSH host key checks are disabled, clients would connect to the rogue server without any warning, allowing the attacker to intercept sensitive data and credentials.

**Q5. What recent real-world examples demonstrate the importance of SSH host key checks?**

One notable example is the compromise of GitHub in 2019, where an attacker exploited a vulnerability in the SSH protocol to bypass host key checks and gain unauthorized access to repositories. This incident highlighted the critical role of SSH host key checks in maintaining the integrity and security of network communications. Ensuring that SSH host key checks are properly configured and monitored can help prevent similar breaches.

---
<!-- nav -->
[[06-Understanding SSH Host Key Checks|Understanding SSH Host Key Checks]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/14-Automating SSH Host Key Checks With Ansible/00-Overview|Overview]]
