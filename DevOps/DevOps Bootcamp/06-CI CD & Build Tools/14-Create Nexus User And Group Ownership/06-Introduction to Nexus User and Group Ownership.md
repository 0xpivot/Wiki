---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus User and Group Ownership

In this section, we will delve into the process of creating a Nexus user and assigning ownership of specific directories to this user. This is a critical step in setting up a Nexus repository manager, ensuring that the user has the necessary permissions to execute Nexus commands and manage the repository effectively.

### Background Theory

Nexus Repository Manager is a powerful artifact management solution used in many organizations to store and manage binary artifacts such as JAR files, WAR files, Docker images, and more. To function correctly, Nexus requires specific directory structures and permissions. By default, these directories might be owned by the `root` user, which can lead to permission issues when trying to run Nexus commands or manage the repository.

### Creating a Nexus User and Group

The primary goal is to create a dedicated user and group for Nexus, and then change the ownership of the relevant directories to this new user. This ensures that the Nexus service runs with the least privilege necessary, enhancing security and preventing potential misconfigurations.

#### Step-by-Step Process

1. **Identify the Directories**: The directories that need to be owned by the Nexus user are typically `/opt/sonatype-work` and `/opt/nexus`. These directories contain the data and configurations for the Nexus repository.

2. **Create the Nexus User and Group**:
    - **Group Creation**: First, we create a group named `nexus`.
    - **User Creation**: Then, we create a user named `nexus` and assign it to the `nexus` group.

3. **Change Directory Ownership**: Finally, we change the ownership of the directories to the `nexus` user and group.

### Using Ansible Playbook for Automation

Ansible is an open-source automation tool that simplifies the process of managing infrastructure and applications. We will use an Ansible playbook to automate the creation of the Nexus user and group and to change the directory ownership.

#### Ansible Playbook Structure

An Ansible playbook consists of a series of tasks that are executed on specified hosts. Each task can involve different modules, such as `user`, `group`, and `file`.

```yaml
---
- name: Create Nexus user and group
  hosts: localhost
  become: yes
  tasks:
    - name: Ensure Nexus group exists
      group:
        name: nexus
        state: present

    - name: Create Nexus user
      user:
        name: nexus
        group: nexus
        shell: /bin/bash
        system: no

    - name: Change ownership of Nexus directories
      file:
        path: "{{ item }}"
        owner: nexus
        group: nexus
        recurse: yes
      with_items:
        - /opt/nexus
        - /opt/sonatype-work
```

### Detailed Explanation of Each Task

#### Task 1: Ensure Nexus Group Exists

This task uses the `group` module to ensure that the `nexus` group exists. If the group does not exist, Ansible will create it.

```yaml
- name: Ensure Nexus group exists
  group:
    name: nexus
    state: present
```

- **Explanation**: The `group` module is used to manage groups on the target system. The `name` parameter specifies the name of the group (`n.exus` in this case), and the `state` parameter is set to `present`, indicating that the group should be created if it does not already exist.

#### Task 2: Create Nexus User

This task uses the `user` module to create the `nexus` user and assign it to the `nexus` group.

```yaml
- name: Create Nexus user
  user:
    name: nexus
    group: nexus
    shell: /bin/bash
    system: no
```

- **Explanation**: The `user` module is used to manage users on the target system. The `name` parameter specifies the username (`nexus`), the `group` parameter assigns the user to the `nexus` group, the `shell` parameter sets the login shell to `/bin/bash`, and the `system` parameter is set to `no`, indicating that this is a regular user account rather than a system account.

#### Task 3: Change Ownership of Nexus Directories

This task uses the `file` module to change the ownership of the specified directories to the `nexus` user and group.

```yaml
- name: Change ownership of Nexus directories
  file:
    path: "{{ item }}"
    owner: nexus
    group: nexus
    recurse: yes
  with_items:
    - /opt/nexus
    - /opt/sonatype-work
```

- **Explanation**: The `file` module is used to manage file attributes on the target system. The `path` parameter specifies the directory to modify, the `owner` and `group` parameters set the ownership to `nexus`, and the `recurse` parameter is set to `yes`, indicating that the ownership should be changed recursively for all subdirectories and files within the specified directories.

### Full Example of HTTP Request and Response

While this task primarily involves file system operations, let's consider a scenario where we might interact with the Nexus server via HTTP to verify the changes.

#### HTTP Request to Verify Changes

```http
GET /service/rest/v1/status HTTP/1.1
Host: localhost:8081
Authorization: Basic YWRtaW46YWRtaW4=
Accept: application/json
```

- **Explanation**: This HTTP request is sent to the Nexus REST API endpoint to check the status of the Nexus server. The `Authorization` header contains basic authentication credentials (`admin:admin`).

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Date: Tue, 14 Mar 2023 12:00:00 GMT
Transfer-Encoding: chunked

{
  "version": "3.35.1",
  "status": "UP"
}
```

- **Explanation**: The response indicates that the Nexus server is up and running. The `Content-Type` header specifies that the response body is in JSON format.

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Incorrect Ownership

If the ownership of the directories is not correctly set, Nexus may fail to start or may encounter permission errors when trying to access the directories.

- **How to Avoid**: Always verify the ownership of the directories after making changes. You can use the `ls -l` command to check the ownership.

```bash
ls -l /opt/nexus
ls -l /opt/sonatype-work
```

#### Pitfall 2: Missing Group Creation

If the group is not created before the user is created, the user creation task will fail.

- **How to Avoid**: Ensure that the group creation task is executed before the user creation task.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21277

CVE-2021-21277 is a vulnerability in Sonatype Nexus Repository Manager 3.x that allows unauthorized access to sensitive information due to improper validation of user input. This vulnerability highlights the importance of proper user and group management to prevent unauthorized access.

- **Impact**: An attacker could exploit this vulnerability to gain unauthorized access to sensitive information stored in the Nexus repository.
- **Mitigation**: Ensure that the Nexus user and group are properly configured and that the directories are owned by the correct user and group.

### How to Prevent / Defend

#### Detection

To detect potential issues with user and group ownership, you can use tools like `auditd` to monitor file system changes and `ps` to check running processes.

```bash
# Monitor file system changes
sudo auditctl -w /opt/nexus -p wa -k nexus_changes
sudo auditctl -w /opt/sonatype-work -p wa -k sonatype_changes

# Check running processes
ps aux | grep nexus
```

#### Prevention

- **Secure Configuration**: Ensure that the Nexus user and group are properly configured and that the directories are owned by the correct user and group.
- **Least Privilege Principle**: Run the Nexus service with the least privilege necessary to perform its functions.
- **Regular Audits**: Regularly audit the configuration and permissions to ensure that they remain secure.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and the corresponding secure configuration:

**Vulnerable Configuration**

```yaml
- name: Create Nexus user
  user:
    name: nexus
    group: root
    shell: /bin/bash
    system: no
```

**Secure Configuration**

```yaml
- name: Create Nexus user
  user:
    name: nexus
    group: nexus
    shell: /bin/bash
    system: no
```

### Conclusion

Creating a Nexus user and assigning ownership of specific directories is a crucial step in setting up a Nexus repository manager. By following the steps outlined in this chapter, you can ensure that the Nexus service runs securely and efficiently. Additionally, by using Ansible to automate the process, you can streamline the setup and reduce the risk of human error.

### Practice Labs

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that touch on user and group management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes. While it focuses on web application security, it can help you understand the broader context of securing applications and services.

By completing these labs, you can gain practical experience in managing user and group ownership in a controlled environment.

---
<!-- nav -->
[[05-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/14-Create Nexus User And Group Ownership/00-Overview|Overview]] | [[07-Introduction to Pausing Tasks in Ansible Playbooks|Introduction to Pausing Tasks in Ansible Playbooks]]
