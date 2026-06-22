---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Securing Node.js Deployments with Non-Root Users

In the realm of DevOps, securing applications and infrastructure is paramount. One critical aspect of this is ensuring that applications run with the least privilege necessary. This means avoiding the use of root or superuser accounts for application processes. In this section, we will delve into the process of securing Node.js deployments by running them as non-root users. Specifically, we will focus on the use of Ansible to manage these configurations.

### Why Run Applications as Non-Root Users?

Running applications as non-root users is a fundamental principle of the Principle of Least Privilege (PoLP). This principle states that a process should only have access to the resources it needs to perform its function. By running an application as a non-root user, you limit the potential damage that can be caused by a security breach. If an attacker gains control of a non-root user, they will have limited permissions and will not be able to escalate their privileges easily.

#### Real-World Example: CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) is a prime example of why running applications with minimal privileges is crucial. This vulnerability allowed attackers to execute arbitrary code on affected systems. If the application was running as a non-root user, the attacker would have been limited in what they could do, even if they exploited the vulnerability. However, if the application was running as root, the attacker could potentially gain full control of the system.

### Setting Up a Non-Root User for Node.js Deployment

To secure a Node.js deployment, we will create a non-root user and configure our deployment to use this user. Let's walk through the steps involved in this process.

#### Step 1: Create a Non-Root User

First, we need to create a non-root user. This can be done using the `adduser` command on most Linux distributions. Here’s an example:

```bash
sudo adduser nana
```

This command creates a new user named `nana`. You will be prompted to set a password and provide additional information about the user.

#### Step 2: Adjust Directory Ownership

Next, we need to ensure that the files and directories used by our Node.js application are owned by the `nana` user. This involves changing the ownership of the relevant directories and files.

For example, if your Node.js application is located in `/var/www/nodejs`, you would change the ownership as follows:

```bash
sudo chown -R nana:nana /var/www/nodejs
```

This command changes the ownership of the `/var/www/nodejs` directory and all its contents to the `nana` user.

### Using Ansible to Manage Non-Root User Deployment

Ansible is a powerful automation tool that can help us manage the deployment of our Node.js application as a non-root user. We will use Ansible to ensure that our deployment scripts and configurations are executed with the appropriate user permissions.

#### Step 3: Configure Ansible Playbook

We need to configure our Ansible playbook to use the `nana` user for executing tasks. This involves specifying the `become_user` and `become` attributes in our playbook.

Here is an example of an Ansible playbook that sets up a Node.js application to run as the `nana` user:

```yaml
---
- name: Deploy Node.js Application
  hosts: all
  become: yes
  become_user: nana

  tasks:
    - name: Ensure Node.js application directory exists
      file:
        path: /home/nana/nodejs
        state: directory
        owner: nana
        group: nana
        mode: '0755'

    - name: Copy Node.js application files
      copy:
        src: /path/to/local/nodejs/files
        dest: /home/nana/nodejs
        owner: nana
        group: nana
        mode: '0644'

    - name: Install Node.js dependencies
      npm:
        path: /home/nana/nodejs
        state: present

    - name: Start Node.js application
      systemd:
        name: nodejs-app
        enabled: yes
        state: started
```

In this playbook, we use the `become` and `become_user` attributes to ensure that all tasks are executed as the `nana` user. The `file` module ensures that the Node.js application directory exists and is owned by the `nana` user. The `copy` module copies the application files to the correct location and sets the appropriate ownership and permissions. Finally, the `npm` module installs the Node.js dependencies, and the `systemd` module starts the Node.js application as a service.

### Understanding the `become` and `become_user` Attributes

The `become` and `become_user` attributes in Ansible are crucial for managing user permissions during task execution. Let's break down these attributes:

- **`become`:** This attribute enables privilege escalation. By default, Ansible runs tasks as the user specified in the `remote_user` attribute (which is typically the `root` user). Setting `become: yes` allows Ansible to switch to another user for executing tasks.

- **`become_user`:** This attribute specifies the user to which Ansible should switch when executing tasks. In our example, we set `become_user: nana` to ensure that all tasks are executed as the `nana` user.

By combining these attributes, we can ensure that our Node.js deployment is executed with the least privilege necessary.

### How to Prevent / Defend Against Privilege Escalation

While running applications as non-root users significantly reduces the risk of privilege escalation, it is essential to implement additional security measures to further protect your system. Here are some best practices:

#### Secure SSH Configuration

Ensure that SSH access is restricted to only the necessary users and that strong authentication methods are used. For example, disable password-based authentication and require public key authentication.

```yaml
---
- name: Secure SSH Configuration
  hosts: all
  become: yes

  tasks:
    - name: Disable password authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PasswordAuthentication'
        line: 'PasswordAuthentication no'
        state: present

    - name: Restart SSH service
      systemd:
        name: ssh
        state: restarted
```

#### Use SELinux or AppArmor

Implementing SELinux or AppArmor can provide an additional layer of security by enforcing strict access controls on processes and files.

```yaml
---
- name: Enable SELinux
  hosts: all
  become: yes

  tasks:
    - name: Set SELinux policy to enforcing
      selinux:
        policy: targeted
        state: enforcing

    - name: Apply SELinux policy
      shell: semanage permissive -a httpd_t
```

#### Regularly Update and Patch Systems

Keep your operating system and applications up to date with the latest security patches. This helps mitigate known vulnerabilities.

```yaml
---
- name: Update System Packages
  hosts: all
  become: yes

  tasks:
    - name: Update package lists
      apt:
        update_cache: yes

    - name: Upgrade installed packages
      apt:
        upgrade: dist
```

### Conclusion

Securing Node.js deployments by running them as non-root users is a critical step in maintaining the security of your applications and infrastructure. By following the steps outlined in this chapter, you can ensure that your Node.js applications are deployed with the least privilege necessary, reducing the risk of privilege escalation and other security threats.

### Practice Labs

To reinforce your understanding of securing Node.js deployments with non-root users, consider working through the following practice labs:

- **PortSwigger Web Security Academy:** This platform offers a variety of labs that cover different aspects of web application security, including securing deployments.
- **OWASP Juice Shop:** This interactive learning environment simulates a vulnerable web application, allowing you to practice securing various components, including Node.js deployments.

By completing these labs, you will gain hands-on experience in implementing the concepts discussed in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/01-Linux & OS Basics/18-Securing Node.js Deployments with Non-Root Users/00-Overview|Overview]] | [[02-Securing Node.js Deployments with Non-Root Users|Securing Node.js Deployments with Non-Root Users]]
