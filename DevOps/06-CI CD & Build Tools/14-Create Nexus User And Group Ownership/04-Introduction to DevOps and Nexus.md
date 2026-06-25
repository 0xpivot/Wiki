---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to DevOps and Nexus

In the realm of DevOps, automation and orchestration tools play a crucial role in streamlining the development, deployment, and management of applications. One such tool is Ansible, which is widely used for automating IT infrastructure. In this chapter, we will delve into the process of creating a Nexus user and group ownership using Ansible playbooks. We will cover the necessary steps, potential pitfalls, and how to ensure the security and reliability of your setup.

### What is Nexus?

Nexus Repository Manager is an artifact repository manager developed by Sonatype. It provides a central location to store and manage artifacts (such as JAR files, WAR files, etc.) used in software development. Nexus supports various package types, including Maven, npm, Docker, and more. It is commonly used in continuous integration and delivery pipelines to manage dependencies and artifacts.

### Why Use Ansible for Nexus Management?

Ansible is a powerful automation tool that allows you to manage and configure systems using playbooks written in YAML. Using Ansible for managing Nexus offers several benefits:

1. **Consistency**: Ensures that Nexus is configured consistently across different environments.
2. **Automation**: Automates the setup and maintenance tasks, reducing manual errors.
3. **Idempotency**: Ansible playbooks are idempotent, meaning they can be run multiple times without causing unintended changes.
4. **Version Control**: Playbooks can be stored in version control systems, allowing you to track changes and collaborate with team members.

### Prerequisites

Before diving into the playbook creation, ensure you have the following prerequisites:

1. **Ansible Installed**: Install Ansible on your system. You can install it using pip:
    ```bash
    pip install ansible
    ```
2. **Nexus Installed**: Ensure Nexus is installed on the target machine. You can download and install Nexus from the [Sonatype website](https://www.sonatype.com/nexus-repository-oss).

3. **Inventory File**: Create an inventory file (`hosts`) that lists the target machines where Nexus will be managed. For example:
    ```ini
    [nexus_servers]
    nexus_server1 ansible_host=192.168.1.10
    ```

### Creating a Nexus User and Group Ownership

To create a Nexus user and group ownership, we will use Ansible playbooks. Let's break down the process step-by-step.

#### Step 1: Define the Playbook Structure

Create a new playbook file named `nexus_user_group.yml`. The playbook will consist of several tasks to create the user, group, and set ownership.

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: nexus
        state: present

    - name: Create Nexus User
      user:
        name: nexus
        group: nexus
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: nexus
        group: nexus
        recurse: yes
```

#### Step 2: Explanation of Each Task

Let's break down each task in the playbook:

1. **Create Nexus Group**:
    - The `group` module is used to create a group named `nexus`.
    - The `state: present` ensures that the group is created if it does not already exist.

2. **Create Nexus User**:
    - The `user` module is used to create a user named `nexus`.
    - The `group: nexus` assigns the user to the `nexus` group.
    - The `shell: /bin/bash` sets the default shell for the user.
    - The `state: present` ensures that the user is created if it does not already exist.

3. **Set Ownership for Nexus Directory**:
    - The `file` module is used to set the ownership of the `/opt/nexus` directory.
    - The `owner: nexus` and `group: nexus` set the ownership to the `nexus` user and group.
    - The `recurse: yes` ensures that the ownership is set recursively for all files and directories within `/opt/nexus`.

#### Step 3: Execute the Playbook

Run the playbook using the following command:

```bash
ansible-playbook -i hosts nexus_user_group.yml
```

This command will execute the playbook against the hosts listed in the `hosts` inventory file.

### Checking Nexus Status

After executing the playbook, it is essential to verify that Nexus is running correctly. We will use two methods to check the status: `ps` command and `netstat` command.

#### Using `ps` Command

The `ps` command can be used to check if the Nexus process is running.

```bash
ps aux | grep nexus
```

This command will list all processes containing the keyword `nexus`. If Nexus is running, you should see a line similar to:

```
nexus  1234  0.1  0.2  123456  7890 /opt/nexus/bin/nexus
```

#### Using `netstat` Command

The `netstat` command can be used to check if the Nexus port is listening.

```bash
netstat -tuln | grep 8081
```

This command will list all listening ports and filter for port `8081`, which is the default port for Nexus. If Nexus is running, you should see a line similar to:

```
tcp        0      0 0.0.0.0:8081            0.0.0.0:*               LISTEN
```

### Handling Timing Issues

Sometimes, the `netstat` command might not immediately show the Nexus port as listening due to timing issues. To handle this, you can configure your playbook to wait for a certain amount of time before checking the port.

#### Adding Wait Time in Playbook

Modify the playbook to include a wait time before checking the port:

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: nexus
        state: present

    - name: Create Nexus User
      user:
        name: nexus
        group: nexus
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: nexus
        group: nexus
        recurse: yes

    - name: Wait for Nexus to start
      wait_for:
        port: 8081
        host: localhost
        timeout: 60
```

In this modified playbook, the `wait_for` module is used to wait for the Nexus port to become available. The `timeout: 60` specifies that the playbook should wait up to 60 seconds for the port to become available.

### Full Example of Playbook Execution

Here is a complete example of the playbook execution, including the full HTTP request and response:

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: nexus
        state: present

    - name: Create Nexus User
      user:
        name: nexus
        group: nexus
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: nexus
        group: nexus
        recurse: yes

    - name: Wait for Nexus to start
      wait_for:
        port:  8081
        host: localhost
        timeout: 60

    - name: Check Nexus Process with ps
      shell: ps aux | grep nexus
      register: ps_output

    - debug:
        var: ps_output.stdout_lines

    - name: Check Nexus Port with netstat
      shell: netstat -tuln | grep 8081
      register: netstat_output

    - debug:
        var: netstat_output.stdout_lines
```

### Expected Output

When you run the playbook, you should see output similar to the following:

```plaintext
PLAY [Create Nexus User and Group Ownership] **************************************************************************************************************************************************************

TASK [Gathering Facts] ***************************************************************************************************************************************************************************************
ok: [nexus_server1]

TASK [Create Nexus Group] ************************************************************************************************************************************************************************************
changed: [nexus_server1]

TASK [Create Nexus User] ***************************************************************************************************************************************************************************************
changed: [nexus_server1]

TASK [Set Ownership for Nexus Directory] **********************************************************************************************************************************************************************
changed: [nexus_server1]

TASK [Wait for Nexus to start] *******************************************************************************************************************************************************************************
ok: [nexus_server1]

TASK [Check Nexus Process with ps] ***************************************************************************************************************************************************************************
changed: [nexus_server1]

TASK [debug] *************************************************************************************************************************************************************************************************
ok: [nexus_server1] => {
    "ps_output.stdout_lines": [
        "nexus  1234  0.1  0.2  123456  7890 ?        Sl   12:34   0:00 /opt/nexus/bin/nexus"
    ]
}

TASK [Check Nexus Port with netstat] ************************************************************************************************************************************************************************
changed: [nexus_server1]

TASK [debug] *************************************************************************************************************************************************************************************************
ok: [nexus_server1] => {
    "netstat_output.stdout_lines": [
        "tcp        0      0 0.0.0.0:8081            0.0.0.0:*               LISTEN"
    ]
}
```

### Potential Pitfalls and How to Prevent Them

#### Pitfall 1: Incorrect User and Group Creation

Ensure that the user and group names are correct and consistent throughout the playbook. Incorrect names can lead to permission issues and failed deployments.

**How to Prevent:**
- Double-check the user and group names before running the playbook.
- Use variables to store user and group names, making it easier to update them if needed.

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  vars:
    nexus_user: nexus
    nexus_group: nexus
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: "{{ nexus_group }}"
        state: present

    - name: Create Nexus User
      user:
        name: "{{ nexus_user }}"
        group: "{{ nexus_group }}"
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: "{{ nexus_user }}"
        group: "{{ nexus_group }}"
        recurse: yes
```

#### Pitfall 2: Incorrect Ownership Setting

Ensure that the ownership is set correctly for the Nexus directory. Incorrect ownership can lead to permission issues and failed deployments.

**How to Prevent:**
- Verify the ownership settings before running the playbook.
- Use the `file` module with the `recurse: yes` option to ensure that ownership is set recursively for all files and directories within the specified path.

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: nexus
        group: nexus
        recurse: yes
```

#### Pitfall 3: Timing Issues with `netstat` Command

Ensure that the playbook waits for the Nexus service to start before checking the port. Timing issues can cause the playbook to fail if the port is not yet listening.

**How to Prevent:**
- Use the `wait_for` module to wait for the Nexus port to become available.
- Specify a reasonable timeout value to allow enough time for the service to start.

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Wait for Nexus to start
      wait_for:
        port: 8081
        host: localhost
        timeout: 60
```

### Real-World Examples and CVEs

#### Example: CVE-2021-21285

CVE-2021-21285 is a vulnerability in Sonatype Nexus Repository Manager that allows unauthenticated attackers to perform a denial-of-service (DoS) attack by sending specially crafted requests to the server. This vulnerability highlights the importance of securing your Nexus installation and ensuring that it is properly configured and monitored.

**How to Prevent:**
- Keep your Nexus installation up-to-date with the latest security patches.
- Configure firewall rules to restrict access to the Nexus server.
- Monitor the server logs for suspicious activity and implement intrusion detection systems.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: nexus
        state: present

    - name: Create Nexus User
      user:
        name: nexus
        group: nexus
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: nexus
        group: nexus
        recurse: yes
```

#### Secure Code Example

```yaml
---
- name: Create Nexus User and Group Ownership
  hosts: nexus_servers
  vars:
    nexus_user: nexus
    nexus_group: nexus
  become: yes
  tasks:
    - name: Create Nexus Group
      group:
        name: "{{ nexus_group }}"
        state: present

    - name: Create Nexus User
      user:
        name: "{{ nexus_user }}"
        group: "{{ nexus_group }}"
        shell: /bin/bash
        state: present

    - name: Set Ownership for Nexus Directory
      file:
        path: /opt/nexus
        owner: "{{ nexus_user }}"
        group: "{{ nexus_group }}"
        recurse: yes

    - name: Wait for Nexus to start
      wait_for:
        port: 8081
        host: localhost
        timeout: 60

    - name: Check Nexus Process with ps
      shell: ps aux | grep nexus
      register: ps_output

    - debug:
        var: ps_output.stdout_lines

    - name: Check Nexus Port with netstat
      shell: netstat -tuln | grep 8081
      register: netstat_output

    - debug:
        var: netstat_output.stdout_lines
```

### Conclusion

In this chapter, we covered the process of creating a Nexus user and group ownership using Ansible playbooks. We discussed the necessary steps, potential pitfalls, and how to ensure the security and reliability of your setup. By following the best practices outlined in this chapter, you can effectively manage your Nexus installation and ensure that it is properly configured and secured.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including Nexus-related scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide practical experience in managing and securing Nexus installations in a controlled environment.

---
<!-- nav -->
[[03-Introduction to DevOps Automation with Ansible|Introduction to DevOps Automation with Ansible]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/14-Create Nexus User And Group Ownership/00-Overview|Overview]] | [[05-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]]
