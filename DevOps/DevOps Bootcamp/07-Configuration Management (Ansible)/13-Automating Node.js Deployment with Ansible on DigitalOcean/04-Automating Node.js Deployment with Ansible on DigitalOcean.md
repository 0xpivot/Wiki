---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating Node.js Deployment with Ansible on DigitalOcean

### Introduction to Ansible

Ansible is an open-source automation tool used to manage infrastructure and applications. It simplifies the process of deploying, configuring, and managing systems by using playbooks written in YAML. Ansible operates through a simple agentless architecture, meaning it does not require any additional software to be installed on the managed nodes. Instead, it uses SSH to communicate and execute tasks.

### Understanding Source and Destination Paths

In the context of Ansible, the `source` and `destination` paths are crucial parameters when copying files between a local machine and a remote server. These paths define the location of the file on both ends of the transfer.

#### Source Path

The `source` path refers to the file on your local machine. This is the file you intend to copy to the remote server. For instance, if you have a Node.js application packaged in a `.tar.gz` file, the source path would be the local path to this file.

```yaml
src: /path/to/local/file.tar.gz
```

#### Destination Path

The `destination` path specifies where the file should be placed on the remote server. In the given example, the destination is set to the root user's home directory (`/root`). This means the file will be copied to `/root`.

```yaml
dest: /root/file.tar.gz
```

### Using the Root User

When working with Ansible, it is often necessary to use the root user to perform certain operations, especially those involving system-wide configurations or installations. The root user has full privileges and can access any part of the system.

#### Home Directory of the Root User

The root user's home directory is typically located at `/root`. Any files copied to the root user's home directory will be placed within this directory.

```yaml
dest: /root/new_file_name.tar.gz
```

### Copying Files with Ansible

To copy files using Ansible, you can use the `copy` module. This module allows you to copy files from your local machine to a remote server.

#### Example Playbook

Here is an example playbook that copies a `.tar.gz` file from the local machine to the remote server:

```yaml
---
- name: Copy Node.js application to remote server
  hosts: digitalocean
  become: yes
  tasks:
    - name: Copy Node.js application
      copy:
        src: /path/to/local/file.tar.gz
        dest: /root/new_file_name.tar.gz
```

### Unpacking the Tar File

After copying the `.tar.gz` file to the remote server, the next step is to unpack it. This can be done using the `unarchive` module in Ansible.

#### Example Playbook

Here is an example playbook that unpacks the `.tar.gz` file:

```yaml
---
- name: Unpack Node.js application on remote server
  hosts: digitalocean
  become: yes
  tasks:
    - name: Unpack Node.js application
      unarchive:
        src: /root/new_file_name.tar.gz
        dest: /opt/nodejs_app
        remote_src: yes
```

### Built-In Modules in Ansible

Ansible comes with a variety of built-in modules that can be used without any additional installation. The `copy` and `unarchive` modules are two such examples.

#### List of Built-In Modules

Some other commonly used built-in modules include:

- `file`: Manages files and directories.
- `shell`: Executes shell commands.
- `command`: Executes a command on a remote node.
- `apt`: Manages packages on Debian-based systems.
- `yum`: Manages packages on Red Hat-based systems.

### Real-World Examples and Security Considerations

#### Recent CVEs and Breaches

While Ansible itself is generally secure, improper usage can lead to vulnerabilities. For example, if sensitive information is included in playbooks or inventory files, it can be exposed. A recent example is the CVE-2021-44228 (Log4Shell), which affected many systems, including those managed by Ansible.

#### Secure Coding Practices

To ensure security, follow these best practices:

- **Use SSH Keys**: Always use SSH keys for authentication instead of passwords.
- **Limit Permissions**: Ensure that the user running the Ansible playbook has the minimum necessary permissions.
- **Encrypt Sensitive Data**: Use tools like Ansible Vault to encrypt sensitive data in playbooks and inventory files.

#### Example of Secure Coding

Here is an example of a secure playbook using Ansible Vault:

```yaml
---
- name: Securely deploy Node.js application
  hosts: digitalocean
  become: yes
  vars_files:
    - secrets.yml
  tasks:
    - name: Copy Node.js application
      copy:
        src: "{{ secret_path }}"
        dest: /root/new_file_name.tar.gz
    - name: Unpack Node.js application
      unarchive:
        src: /root/new_file_name.tar.gz
        dest: /opt/nodejs_app
        remote_src: yes
```

Where `secrets.yml` is encrypted using Ansible Vault:

```yaml
secret_path: /path/to/local/file.tar.gz
```

### How to Prevent / Defend

#### Detection

To detect potential issues, regularly audit your Ansible playbooks and inventory files. Tools like `ansible-lint` can help identify common issues.

#### Prevention

- **Use SSH Keys**: Always use SSH keys for authentication.
- **Limit Permissions**: Ensure users have minimal necessary permissions.
- **Encrypt Sensitive Data**: Use Ansible Vault to encrypt sensitive data.

#### Secure-Coding Fixes

Compare the insecure and secure versions of the playbook:

**Insecure Version**

```yaml
---
- name: Deploy Node.js application
  hosts: digitalocean
  become: yes
  tasks:
    - name: Copy Node.js application
      copy:
        src: /path/to/local/file.tar.gz
        dest: /root/new_file_name.tar.gz
    - name: Unpack Node.js application
      unarchive:
        src: /root/new_file_name.tar.gz
        dest: /opt/nodejs_app
        remote_src: yes
```

**Secure Version**

```yaml
---
- name: Securely deploy Node.js application
  hosts: digitalocean
  become: yes
  vars_files:
    - secrets.yml
  tasks:
    - name: Copy Node.js application
      copy:
        src: "{{ secret_path }}"
        dest: /root/new_file_name.tar.gz
    - name: Unpack Node.js application
      unarchive:
        src: /root/new_file
```

Where `secrets.yml` is encrypted using Ansible Vault:

```yaml
secret_path: /path/to/local/file.tar.gz
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for learning security.
- **WebGoat**: An interactive, gamified training application for web security.

These labs provide practical experience in securing and deploying applications using Ansible.

### Conclusion

Automating Node.js deployment with Ansible on DigitalOcean involves understanding the source and destination paths, using the root user, and leveraging built-in modules like `copy` and `unarchive`. By following secure coding practices and regularly auditing your playbooks, you can ensure a robust and secure deployment process.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/13-Automating Node.js Deployment with Ansible on DigitalOcean/03-Introduction to Node.js Application Deployment|Introduction to Node.js Application Deployment]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/13-Automating Node.js Deployment with Ansible on DigitalOcean/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/13-Automating Node.js Deployment with Ansible on DigitalOcean/05-Practice Questions & Answers|Practice Questions & Answers]]
