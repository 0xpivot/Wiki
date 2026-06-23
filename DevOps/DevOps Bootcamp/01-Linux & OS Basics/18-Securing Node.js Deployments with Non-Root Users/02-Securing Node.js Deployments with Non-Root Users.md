---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Securing Node.js Deployments with Non-Root Users

### Introduction

In the context of deploying Node.js applications, security is paramount. One of the fundamental principles of securing a deployment is to avoid running the application with root privileges. Running applications as non-root users significantly reduces the potential damage in case of a security breach. This chapter will delve into the process of creating a new non-root user for deploying a Node.js application and configuring the environment to ensure the application runs securely.

### Background Theory

#### Why Avoid Root Privileges?

Running an application with root privileges means that the application has full control over the system. If an attacker gains access to the application, they can potentially take over the entire system. By contrast, running the application as a non-root user limits the scope of potential damage. Even if an attacker gains access to the application, they will only have the permissions of the non-root user, which should be minimal.

#### User Management in Linux

Linux systems manage users through a series of files and commands. The primary files involved are `/etc/passwd`, `/etc/shadow`, `/etc/group`, and `/etc/gshadow`. These files store information about users, passwords, and groups.

- **/etc/passwd**: Contains basic user information such as username, user ID (UID), group ID (GID), home directory, and shell.
- **/etc/shadow**: Stores encrypted password hashes and other password-related information.
- **/etc/group**: Lists groups and their members.
- **/etc/gshadow**: Stores shadowed group information, including encrypted group passwords.

### Creating a New User

To create a new user for deploying a Node.js application, we will use the `useradd` command or Ansible's `user` module. Let's walk through the process step-by-step.

#### Using the `useradd` Command

The `useradd` command is used to create a new user account. Here’s an example:

```bash
sudo useradd -m -s /bin/bash nana
```

- `-m`: Creates the user's home directory.
- `-s /bin/bash`: Specifies the user's login shell.
- `nana`: The username.

#### Using Ansible's `user` Module

Ansible provides a powerful way to automate the creation of users across multiple servers. Here’s how you can create a new user using Ansible:

```yaml
---
- name: Create new Linux user for Node.js app
  hosts: all
  become: yes
  tasks:
    - name: Create Linux user
      user:
        name: nana
        shell: /bin/bash
        state: present
```

This playbook creates a new user named `nana` with the specified shell.

### Configuring the User

Once the user is created, you need to configure the environment to ensure the Node.js application runs correctly under this user.

#### Setting Up Permissions

Ensure that the user has the necessary permissions to access the application files and directories. This typically involves setting appropriate ownership and permissions.

```bash
sudo chown -R nana:nana /path/to/nodejs/app
sudo chmod -R 755 /path/to/nodejs/app
```

- `chown`: Changes the ownership of the files and directories.
- `chmod`: Sets the permissions.

#### Running the Application as the New User

To run the Node.js application as the new user, you can use tools like `systemd` or `supervisord`.

##### Using `systemd`

Create a `systemd` service file for the Node.js application:

```ini
[Unit]
Description=Node.js Application Service
After=network.target

[Service]
User=nana
ExecStart=/usr/bin/node /path/to/nodejs/app/index.js
Restart=always

[Install]
WantedBy=multi-user.target
```

Save this file as `/etc/systemd/system/nodejs.service` and enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nodejs.service
sudo systemctl start nodejs.service
```

##### Using `supervisord`

Configure `supervisord` to run the Node.js application as the new user:

```ini
[program:nodejs]
command=/usr/bin/node /path/to/nodejs/app/index.js
user=nana
autostart=true
autorestart=true
stdout_logfile=/var/log/nodejs.stdout.log
stderr_logfile=/var/log/nodejs.stderr.log
```

Save this configuration in `/etc/supervisor/conf.d/nodejs.conf` and reload `supervisord`:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nodejs
```

### Real-World Examples and CVEs

#### CVE-2021-39128: Node.js Denial of Service Vulnerability

CVE-2021-39128 is a denial-of-service vulnerability in Node.js versions prior to 14.17.5 and 16.6.0. An attacker could exploit this vulnerability to cause a denial of service by sending specially crafted HTTP requests.

**Impact**: If the Node.js application is running with root privileges, an attacker could potentially gain full control of the system.

**Mitigation**: Running the application as a non-root user limits the potential damage. Ensure that the application is updated to the latest version to mitigate this vulnerability.

### How to Prevent / Defend

#### Detection

Regularly monitor the system for unauthorized access attempts and unusual activity. Tools like `auditd` can help track changes to critical files and directories.

```bash
sudo auditctl -w /path/to/nodejs/app -p wa -k nodejs_app
```

#### Prevention

1. **Use Non-Root Users**: Always run the Node.js application as a non-root user.
2. **Update Regularly**: Keep the Node.js application and dependencies up-to-date to mitigate known vulnerabilities.
3. **Limit Permissions**: Set appropriate file permissions and ownership to restrict access to sensitive data.
4. **Use Secure Configuration Management Tools**: Utilize tools like Ansible to automate and enforce secure configurations.

#### Secure Code Fixes

Compare the insecure and secure versions of the configuration:

**Insecure Version**:
```yaml
---
- name: Create new Linux user for Node.js app
  hosts: all
  become: yes
  tasks:
    - name: Create Linux user
      user:
        name: nana
        shell: /bin/bash
        state: present
```

**Secure Version**:
```yaml
---
- name: Create new Linux user for Node.js app
  hosts: all
  become: yes
  tasks:
    - name: Create Linux user
      user:
        name: nana
        shell: /bin/bash
        state: present
    - name: Set permissions for Node.js app directory
      file:
        path: /path/to/nodejs/app
        owner: nana
        group: nana
        mode: '0755'
    - name: Configure systemd service for Node.js app
      copy:
        src: /path/to/nodejs.service
        dest: /etc/systemd/system/nodejs.service
      notify:
        - restart nodejs service
  handlers:
    - name: restart nodejs service
      systemd:
        name: nodejs
        state: restarted
```

### Conclusion

Securing Node.js deployments by running the application as a non-root user is a crucial step in enhancing overall system security. By following the steps outlined in this chapter, you can ensure that your Node.js application is deployed securely and is less susceptible to potential security breaches.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including Node.js-specific scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which includes Node.js components.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training, which can be adapted for Node.js scenarios.

These labs provide practical experience in securing Node.js deployments and identifying potential vulnerabilities.

---
<!-- nav -->
[[01-Introduction to Securing Node.js Deployments with Non-Root Users|Introduction to Securing Node.js Deployments with Non-Root Users]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/18-Securing Node.js Deployments with Non-Root Users/00-Overview|Overview]] | [[03-Understanding Root User Privileges and Risks|Understanding Root User Privileges and Risks]]
