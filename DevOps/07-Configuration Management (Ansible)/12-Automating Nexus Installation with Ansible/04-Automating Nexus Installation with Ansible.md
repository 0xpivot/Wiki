---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating Nexus Installation with Ansible

In this section, we will delve into automating the installation of Nexus using Ansible. This process involves downloading and unpacking a tar file containing the Nexus binaries, and ensuring that the automation is robust and adaptable to changes in the version of Nexus being installed.

### Background Theory

Nexus Repository Manager is a powerful artifact management solution that allows teams to store and manage artifacts such as Maven, npm, NuGet, Docker, and more. It provides a centralized repository for storing and distributing these artifacts, making it easier to manage dependencies across development environments.

Ansible is an open-source IT automation tool that enables configuration management, application deployment, and task automation. It uses a simple language called YAML to define tasks and plays, which are then executed on target systems.

### Downloading and Unpacking the Tar File

To automate the installation of Nexus, we first need to download the tar file containing the Nexus binaries. This tar file is typically hosted on a remote server and can be downloaded using Ansible's `get_url` module.

#### Example Playbook

Here is an example playbook that downloads the tar file:

```yaml
---
- name: Download Nexus tar file
  hosts: localhost
  tasks:
    - name: Download Nexus tar file
      ansible.builtin.get_url:
        url: "https://download.sonatype.com/nexus/3/latest-unix.tar.gz"
        dest: "/opt/nexus-latest-unix.tar.gz"
```

This playbook uses the `get_url` module to download the tar file from the specified URL and save it to `/opt/nexus-latest-unix.tar.gz`.

### Unpacking the Tar File

Once the tar file is downloaded, we need to unpack it using Ansible's `unarchive` module. The `unarchive` module can handle various archive formats, including tar files.

#### Example Playbook

Here is an example playbook that unpacks the tar file:

```yaml
---
- name: Unpack Nexus tar file
  hosts: localhost
  tasks:
    - name: Unpack Nexus tar file
      ansible.builtin.unarchive:
        src: "/opt/nexus-latest-unix.tar.gz"
        dest: "/opt"
        remote_src: yes
```

This playbook uses the `unarchive` module to unpack the tar file located at `/opt/nexus-latest-unix.tar.gz` into the `/opt` directory. The `remote_src` parameter is set to `yes` to indicate that the source file is located on the remote machine.

### Handling Version Changes

One challenge with automating the installation of Nexus is handling version changes. When downloading the tar file, the URL typically points to the latest version of Nexus. This means that if the playbook is run at a later date, it may download a different version of Nexus.

To address this issue, we need to dynamically determine the version of Nexus that was downloaded and use it in subsequent steps of the playbook.

#### Example Playbook

Here is an example playbook that dynamically determines the version of Nexus:

```yaml
---
- name: Install Nexus
  hosts: localhost
  vars:
    nexus_tar_file: "/opt/nexus-latest-unix.tar.gz"
    nexus_install_dir: "/opt/nexus"
  tasks:
    - name: Download Nexus tar file
      ansible.builtin.get_url:
        url: "https://download.sonatype.com/nexus/3/latest-unix.tar.gz"
        dest: "{{ nexus_tar_file }}"
      register: download_result

    - name: Extract Nexus version from tar file
      ansible.builtin.shell: |
        tar -tf {{ nexus_tar_file }} | head -n 1 | cut -d '/' -f 1
      register: extract_version_result

    - name: Set Nexus version fact
      ansible.builtin.set_fact:
        nexus_version: "{{ extract_version_result.stdout }}"

    - name: Unpack Nexus tar file
      ansible.builtin.unarchive:
        src: "{{ nexus_tar_file }}"
        dest: "{{ nexus_install_dir }}"
        remote_src: yes
```

This playbook first downloads the tar file and registers the result. It then extracts the version of Nexus from the tar file using a shell command and sets it as a fact. Finally, it unpacks the tar file into the specified directory.

### Handling Pitfalls

There are several potential pitfalls to consider when automating the installation of Nexus using Ansible:

1. **Network Issues**: Ensure that the network connection is stable and that the URL for downloading the tar file is correct.
2. **File Permissions**: Ensure that the user running the playbook has the necessary permissions to download and unpack the tar file.
3. **Version Inconsistency**: Ensure that the version of Nexus being installed is consistent across all environments.

### How to Prevent / Defend

To prevent issues related to version inconsistency, you can implement the following measures:

1. **Use Version-Specific URLs**: Instead of using a URL that points to the latest version of Nexus, use a version-specific URL. This ensures that the same version of Nexus is installed across all environments.
2. **Automate Version Checking**: Implement a script that checks the version of Nexus being installed and compares it with the expected version. If the versions do not match, the script should fail and notify the administrator.

#### Secure Code Fix

Here is an example of a secure code fix that checks the version of Nexus being installed:

```yaml
---
- name: Install Nexus
  hosts: localhost
  vars:
    nexus_tar_file: "/opt/nexus-latest-unix.tar.gz"
    nexus_install_dir: "/opt/nexus"
    expected_nexus_version: "3.38.1"
  tasks:
    - name: Download Nexus tar file
      ansible.builtin.get_url:
        url: "https://download.sonatype.com/nexus/3/{{ expected_nexus_version }}/nexus-{{ expected_nexus_version }}-unix.tar.gz"
        dest: "{{ nexus_tar_file }}"
      register: download_result

    - name: Extract Nexus version from tar file
      ansible.builtin.shell: |
        tar -tf {{ nexus_tar_file }} | head -n 1 | cut -d '/' -f 1
      register: extract_version_result

    - name: Set Nexus version fact
      ansible.builtin.set_fact:
        nexus_version: "{{ extract_version_result.stdout }}"

    - name: Check Nexus version
      ansible.builtin.assert:
        that:
          - nexus_version == expected_nexus_version
        msg: "Expected Nexus version {{ expected_nexus_version }} but found {{ nexus_version }}"

    - name: Unpack Nexus tar file
      ansible.builtin.unarchive:
        src: "{{ nexus_tar_file }}"
        dest: "{{ nexus_install_dir }}"
        remote_src: yes
```

This playbook uses a version-specific URL to download the tar file and checks the version of Nexus being installed against the expected version. If the versions do not match, the playbook fails and notifies the administrator.

### Conclusion

Automating the installation of Nexus using Ansible can greatly improve the efficiency and consistency of your deployment process. By dynamically determining the version of Nexus being installed and implementing measures to prevent version inconsistencies, you can ensure that your Nexus installations are robust and reliable.

### Practice Labs

For hands-on practice with automating Nexus installation using Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover web application security, including some that involve automating the setup of web servers and services.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security concepts, including automation and configuration management.

These labs provide a practical environment to apply the concepts learned in this chapter and gain hands-on experience with automating Nexus installation using Ansible.

---
<!-- nav -->
[[03-Introduction to Automating Nexus Installation with Ansible|Introduction to Automating Nexus Installation with Ansible]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/12-Automating Nexus Installation with Ansible/00-Overview|Overview]] | [[05-Creating the Ansible Playbook|Creating the Ansible Playbook]]
