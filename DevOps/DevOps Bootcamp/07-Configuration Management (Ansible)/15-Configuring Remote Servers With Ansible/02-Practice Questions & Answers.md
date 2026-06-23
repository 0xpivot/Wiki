---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What are the prerequisites for configuring a Linux server with Ansible?**

Ansible requires Python to be installed on the target Linux server because Ansible itself is written in Python and uses the Python interpreter to execute commands. Additionally, the server should allow SSH connections, and the user used to connect via SSH should have sufficient privileges to perform the required configurations.

**Q2. How does Ansible connect to remote servers?**

Ansible connects to remote servers using SSH. This method does not require any additional agents to be installed on the target servers. The connection is established using the SSH keys or passwords provided by the user.

**Q3. Explain why Python is necessary for Ansible to function on Linux servers.**

Python is necessary for Ansible to function on Linux servers because Ansible is built using Python. When Ansible runs tasks on a server, it relies on the Python interpreter to execute these tasks. Therefore, having Python installed ensures that Ansible can run its modules and playbooks effectively.

**Q4. What is the significance of using the root user when connecting to a server with Ansible?**

Using the root user when connecting to a server with Ansible is significant because the root user typically has full administrative privileges. This allows Ansible to perform any configuration task without encountering permission issues. However, it is generally recommended to use a non-root user with sudo privileges for security reasons.

**Q5. If you were to configure a Windows server with Ansible, what would be the key differences compared to a Linux server?**

When configuring a Windows server with Ansible, the key difference is that PowerShell must be installed on the Windows server instead of Python. Ansible uses PowerShell to execute tasks on Windows systems. Additionally, the connection method might differ slightly, often requiring the WinRM protocol for communication between Ansible and the Windows server.

**Q6. How would you verify if Python is installed on a Linux server before configuring it with Ansible?**

To verify if Python is installed on a Linux server before configuring it with Ansible, you can SSH into the server and check the presence of Python by running the following command:

```bash
python3 --version
```

This command will display the version of Python installed on the server, confirming its availability for Ansible to use.

**Q7. In the context of recent security breaches, how could misconfiguration of SSH keys lead to vulnerabilities when using Ansible?**

Misconfiguration of SSH keys can lead to vulnerabilities when using Ansible, especially if the private keys are exposed or improperly managed. For example, in the case of the 2021 SolarWinds breach (CVE-2021-44148), attackers exploited misconfigured SSH keys to gain unauthorized access to systems. To prevent such vulnerabilities, it is crucial to ensure that SSH keys are securely stored, access is restricted to authorized users, and regular audits are conducted to detect any unauthorized changes or access attempts.

---
<!-- nav -->
[[01-Introduction to Configuring Remote Servers with Ansible|Introduction to Configuring Remote Servers with Ansible]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/15-Configuring Remote Servers With Ansible/00-Overview|Overview]]
