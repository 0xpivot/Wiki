---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Ansible and Nexus Installation Automation

Ansible is an open-source automation tool used to manage infrastructure as code. It allows you to automate the deployment, configuration, and management of systems and applications. In this chapter, we will delve into automating the installation of Nexus Repository Manager using Ansible. Nexus Repository Manager is a powerful artifact management solution that helps organizations manage their software artifacts efficiently.

### Background Theory

#### What is Ansible?

Ansible is a configuration management tool that uses a simple language called YAML to define the desired state of your infrastructure. It operates agentless, meaning it does not require any additional software to be installed on the managed nodes. Instead, it uses SSH to communicate with the nodes and execute commands.

#### What is Nexus Repository Manager?

Nexus Repository Manager is a popular artifact repository manager developed by Sonatype. It provides a centralized location to store and manage various types of artifacts, such as Maven, npm, Docker, and more. This makes it easier to manage dependencies and ensure consistency across different environments.

### Automating Nexus Installation with Ansible

To automate the installation of Nexus Repository Manager using Ansible, we need to create a playbook that defines the steps required to install and configure Nexus. Let's break down the process step-by-step.

#### Step 1: Define the Playbook Structure

A playbook in Ansible is a YAML file that contains a series of tasks to be executed. Each task is defined using a specific module that performs a particular action. Here is a basic structure of a playbook:

```yaml
---
- name: Install Nexus Repository Manager
  hosts: all
  become: yes
  tasks:
    - name: Ensure Nexus is installed
      ansible.builtin.package:
        name: nexus
        state: present
    - name: Configure Nexus
      ansible.builtin.template:
        src: nexus.properties.j2
        dest: /opt/nexus/conf/nexus.properties
```

In this playbook, we first ensure that the Nexus package is installed using the `ansible.builtin.package` module. Then, we configure Nexus by copying a template file to the appropriate location.

#### Step 2: Download and Extract Nexus

To download and extract Nexus, we can use the `get_url` and `unarchive` modules. Here is an example of how to do this:

```yaml
- name: Download Nexus
  ansible.builtin.get_url:
    url: https://download.sonatype.com/nexus/3/latest-unix.tar.gz
    dest: /tmp/nexus.tar.gz

- name: Extract Nexus
  ansible.builtin.unarchive:
    src: /tmp/nexus.tar.gz
    dest: /opt/
    remote_src: yes
```

This playbook downloads the latest Nexus tarball from the Sonatype website and extracts it to the `/opt/` directory.

#### Step 3: Rename the Nexus Folder

After extracting Nexus, we need to rename the folder to remove the version number. This can be done using the `file` module:

```yaml
- name: Rename Nexus folder
  ansible.builtin.file:
    path: "{{ item.path }}"
    dest: /opt/Nexus
  loop: "{{ lookup('fileglob', '/opt/nexus-*') | map('regex_replace', '^/opt/nexus-(.*)$', '\\1') | list }}"
```

This task renames the extracted Nexus folder to `/opt/Nexus`.

### Handling Idempotency

One of the key principles of Ansible is idempotency, which means that running the same playbook multiple times should not change the system state unless necessary. However, in our case, we encountered an error when trying to rename the Nexus folder again.

#### Error Analysis

The error occurred because the `rename` task was trying to move the folder to a destination that already existed and was not empty. This is a common issue when dealing with file operations in Ansible.

#### How to Prevent / Defend

To prevent this issue, we can add a conditional check to ensure that the folder is renamed only if it does not already exist. Here is the updated task:

```yaml
- name: Rename Nexus folder
  ansible.builtin.file:
    src: "{{ item.path }}"
    dest: /opt/Nexus
    state: touch
  loop: "{{ lookup('fileglob', '/opt/nexus-*') | map('regex_replace', '^/opt/nexus-(.*)$', '\\1') | list }}"
  when: not ansible.builtin.stat(path='/opt/Nexus').exists
```

This task checks if the `/opt/Nexus` folder already exists before attempting to rename it. If the folder does not exist, it proceeds with the renaming operation.

### Full Example Playbook

Here is the complete playbook that automates the installation and configuration of Nexus Repository Manager:

```yaml
---
- name: Install Nexus Repository Manager
  hosts: all
  become: yes
  tasks:
    - name: Download Nexus
      ansible.builtin.get_url:
        url: https://download.sonatype.com/nexus/3/latest-unix.tar.gz
        dest: /tmp/nexus.tar.gz

    - name: Extract Nexus
      ansible.builtin.unarchive:
        src: /tmp/nexus.tar.gz
        dest: /opt/
        remote_src: yes

    - name: Rename Nexus folder
      ansible.builtin.file:
        src: "{{ item.path }}"
        dest: /opt/Nexus
        state: touch
      loop: "{{ lookup('fileglob', '/opt/nexus-*') | map('regex_replace', '^/opt/nexus-(.*)$', '\\1') | list }}"
      when: not ansible.builtin.stat(path='/opt/Nexus').exists

    - name: Configure Nexus
      ansible.builtin.template:
        src: nexus.properties.j2
        dest: /opt/Nexus/conf/nexus.properties
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Idempotency Issues**: As demonstrated earlier, failing to handle idempotency can lead to errors when running playbooks multiple times.
2. **File Permissions**: Ensure that the user running the playbook has the necessary permissions to perform file operations.
3. **Network Connectivity**: Ensure that the system has access to the internet to download the Nexus package.

#### Best Practices

1. **Use Conditionals**: Always use conditionals (`when`) to ensure that tasks are only executed when necessary.
2. **Error Handling**: Implement error handling mechanisms to gracefully handle failures.
3. **Testing**: Test the playbook in a controlled environment before deploying it to production.

### Real-World Examples and Recent CVEs

While there are no specific CVEs related to the automation of Nexus installation, it is important to keep the Nexus server and its dependencies up-to-date to mitigate potential vulnerabilities. Regularly review the Sonatype security advisories and apply patches as needed.

### Conclusion

Automating the installation and configuration of Nexus Repository Manager using Ansible can significantly streamline the setup process and ensure consistency across different environments. By following the steps outlined in this chapter and adhering to best practices, you can effectively manage your Nexus installations.

### Practice Labs

For hands-on practice, consider using the following labs:

- **PortSwigger Web Security Academy**: While primarily focused on web application security, this platform offers valuable experience in managing and securing repositories.
- **OWASP Juice Shop**: This interactive learning environment includes challenges related to managing and securing software artifacts.

By completing these labs, you can gain practical experience in automating Nexus installation and configuration using Ansible.

---
<!-- nav -->
[[01-Introduction to Ansible Playbooks for Nexus Installation|Introduction to Ansible Playbooks for Nexus Installation]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/12-Automating Nexus Installation with Ansible/00-Overview|Overview]] | [[03-Introduction to Automating Nexus Installation with Ansible|Introduction to Automating Nexus Installation with Ansible]]
