---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the advantages of automating Nexus installation using Ansible over manual installation.**

Ansible provides a way to automate the installation and configuration of software like Nexus, ensuring consistency across multiple servers. By scripting the installation process, you can easily replicate the setup on any number of servers and quickly recover from failures. Additionally, Ansible allows you to manage the entire lifecycle of the installation, including updates and maintenance, in a repeatable and reliable manner. This automation reduces human error and saves time, making it ideal for DevOps practices.

**Q2. How would you write an Ansible playbook to install Java and NetTools on a remote server?**

To install Java and NetTools on a remote server using Ansible, you can create a playbook with the following structure:

```yaml
---
- name: Install Java and NetTools
  hosts: your_server
  become: yes
  tasks:
    - name: Update package lists
      apt:
        update_cache: yes

    - name: Install Java version 8
      apt:
        name: openjdk-8-jdk
        state: present

    - name: Install NetTools
      apt:
        name: net-tools
        state: present
```

This playbook ensures that the package lists are updated before installing the required packages. The `become: yes` directive allows the tasks to be executed with elevated privileges.

**Q3. How would you use Ansible to download and unpack the latest Nexus tarball from a specified URL?**

To download and unpack the latest Nexus tarball using Ansible, you can use the `get_url` and `unarchive` modules. Here’s an example playbook:

```yaml
---
- name: Download and unpack Nexus
  hosts: your_server
  become: yes
  tasks:
    - name: Download Nexus tarball
      get_url:
        url: http://download.sonatype.com/nexus/3/latest-unix.tar.gz
        dest: /opt/nexus.tar.gz
        force_basic_auth: yes
      register: download_result

    - name: Unpack Nexus tarball
      unarchive:
        src: "{{ download_result.dest }}"
        dest: /opt/
        remote_src: yes
```

The `get_url` module downloads the tarball, and the `unarchive` module unpacks it. The `register` keyword captures the result of the `get_url` task, allowing you to dynamically reference the downloaded file.

**Q4. Explain how to use the `stat` module to check if a directory exists and conditionally skip tasks in Ansible.**

To check if a directory exists and conditionally skip tasks in Ansible, you can use the `stat` module along with the `when` conditional. Here’s an example:

```yaml
---
- name: Check and rename Nexus folder
  hosts: your_server
  become: yes
  tasks:
    - name: Check if Nexus folder exists
      stat:
        path: /opt/nexus
      register: nexus_folder_stat

    - name: Rename Nexus folder
      shell: mv /opt/nexus-* /opt/nexus
      when: not nexus_folder_stat.stat.exists
```

The `stat` module checks if the `/opt/nexus` directory exists. The `when` conditional skips the `Rename Nexus folder` task if the directory already exists.

**Q5. How would you use the `find` module in Ansible to locate a directory with a specific pattern?**

To locate a directory with a specific pattern using the `find` module in Ansible, you can use the following playbook:

```yaml
---
- name: Find Nexus folder
  hosts: your_server
  become: yes
  tasks:
    - name: Find Nexus folder name
      find:
        paths: /opt
        patterns: 'nexus-*'
        file_type: directory
      register: nexus_folder_find

    - name: Print found directory
      debug:
        var: nexus_folder_find.files[0].path
```

The `find` module searches the `/opt` directory for any subdirectory matching the pattern `nexus-*`. The `patterns` attribute uses a regular expression to match the directory names. The `file_type` attribute ensures that only directories are matched.

**Q6. Why is it important to use conditionals (`when`) with shell commands in Ansible?**

Using conditionals (`when`) with shell commands in Ansible is crucial because Ansible does not inherently track the state of shell commands. Without conditionals, shell commands might be executed repeatedly, leading to errors or unnecessary operations. For example, attempting to move a directory that already exists will result in an error. Conditionals allow you to control the execution based on certain conditions, such as checking if a directory exists before performing operations on it. This ensures that tasks are idempotent and avoids potential issues during repeated playbook runs.

---
<!-- nav -->
[[06-Droplet Management and Preparation|Droplet Management and Preparation]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/12-Automating Nexus Installation with Ansible/00-Overview|Overview]]
