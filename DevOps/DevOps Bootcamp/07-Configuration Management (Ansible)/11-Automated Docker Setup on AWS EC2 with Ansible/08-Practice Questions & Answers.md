---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain why the package manager `YUM` is used instead of `APT` on an Amazon Linux EC2 instance.**

The Amazon Linux operating system uses `YUM` (Yellowdog Updater Modified) as its package manager, whereas Ubuntu uses `APT` (Advanced Package Tool). `YUM` is designed to work with RPM-based systems, which is the package format used by Amazon Linux. When configuring an Ansible playbook for an EC2 instance running Amazon Linux, `YUM` must be used to manage software packages because it is the appropriate package manager for the underlying OS.

**Q2. How would you configure an Ansible playbook to install Docker and Docker Compose on an EC2 instance running Amazon Linux?**

To install Docker and Docker Compose on an EC2 instance running Amazon Linux using Ansible, follow these steps:

1. **Install Python 3**: Ensure Python 3 is installed since Ansible prefers Python 3 for its operations.
   
   ```yaml
   - name: Install Python 3
     yum:
       name: python3
       state: present
     become: yes
   ```

2. **Install Docker**: Use the `YUM` module to install Docker.

   ```yaml
   - name: Install Docker
     yum:
       name: docker
       state: present
     become: yes
   ```

3. **Start Docker Service**: Use the `systemd` module to start the Docker service.

   ```yaml
   - name: Start Docker Service
     systemd:
       name: docker
       state: started
     become: yes
   ```

4. **Install Docker Compose**: Download Docker Compose using the `get_url` module and make it executable.

   ```yaml
   - name: Download Docker Compose
     get_url:
       url: https://github.com/docker/compose/releases/download/{{ docker_compose_version }}/docker-compose-{{ ansible_facts['os_family'].lower() }}-{{ ansible_facts['architecture'] }}
       dest: /usr/local/bin/docker-compose
     become: yes
   
   - name: Make Docker Compose Executable
     file:
       path: /usr/local/bin/docker-compose
       mode: 'a+x'
     become: yes
   ```

5. **Add User to Docker Group**: Add the EC2 user to the Docker group to avoid needing `sudo` for Docker commands.

   ```yaml
   - name: Add EC2 User to Docker Group
     user:
       name: ec2-user
       groups: docker
       append: yes
     become: yes
   ```

6. **Reconnect Session**: Reset the SSH session to apply group changes.

   ```yaml
   - name: Reconnect to Server
     meta: reset_connection
   ```

**Q3. Why is it necessary to use Python 2 for certain tasks such as the `YUM` module in Ansible playbooks on Amazon Linux?**

Certain modules in Ansible, such as the `YUM` module, are not compatible with Python 3. They require Python 2 bindings for RPM to function correctly. Therefore, even if Python 3 is installed and configured as the default interpreter for Ansible, tasks involving the `YUM` module must be executed using Python 2. This ensures compatibility and avoids errors related to missing Python 2 bindings.

**Q4. How would you troubleshoot and resolve the issue of Docker not running on an EC2 instance after installation via an Ansible playbook?**

To troubleshoot and resolve the issue of Docker not running on an EC2 instance after installation via an Ansible playbook, follow these steps:

1. **Check Docker Service Status**: Verify if the Docker service is running.

   ```yaml
   - name: Check Docker Service Status
     command: systemctl status docker
   ```

2. **Start Docker Service**: If the Docker service is not running, start it using the `systemd` module.

   ```yaml
   - name: Start Docker Service
     systemd:
       name: docker
       state: started
     become: yes
   ```

3. **Check Docker Daemon Connection**: Test the connection to the Docker daemon.

   ```yaml
   - name: Test Docker Daemon Connection
     command: docker info
   ```

4. **Verify User Permissions**: Ensure the user has the necessary permissions to interact with Docker.

   ```yaml
   - name: Add User to Docker Group
     user:
       name: ec2-user
       groups: docker
       append: yes
     become: yes
   ```

5. **Reconnect SSH Session**: Reset the SSH session to apply group changes.

   ```yaml
   - name: Reconnect to Server
     meta: reset_connection
   ```

By following these steps, you can diagnose and resolve issues related to Docker not running on an EC2 instance after installation via an Ansible playbook.

**Q5. What is the significance of the `become` directive in Ansible playbooks, especially when dealing with package installations and service management on an EC2 instance?**

The `become` directive in Ansible playbooks is used to elevate privileges to perform tasks that require administrative rights, such as installing packages or managing services. By setting `become: yes`, Ansible switches to the root user (or another specified user) to execute the task. This is crucial for actions like installing Docker or starting the Docker service, which typically require elevated permissions. Without the `become` directive, such tasks would fail due to insufficient privileges.

**Q6. How would you modify the Ansible playbook to handle the installation of Docker and Docker Compose on a fresh EC2 instance, ensuring compatibility with Python 2 and Python 3?**

To handle the installation of Docker and Docker Compose on a fresh EC2 instance while ensuring compatibility with both Python 2 and Python 3, follow these steps:

1. **Install Python 3**: Ensure Python 3 is installed and configured as the default interpreter.

   ```yaml
   - name: Install Python 3
     yum:
       name: python3
       state: present
     become: yes
   ```

2. **Configure Python Interpreter**: Set the Python interpreter to Python 3 in the Ansible configuration file.

   ```yaml
   interpreter_python: python3
   ```

3. **Install Docker Using Python 2**: Execute the `YUM` module tasks using Python 2.

   ```yaml
   - name: Install Docker
     yum:
       name: docker
       state: present
     become: yes
     vars:
       ansible_python_interpreter: /usr/bin/python
   ```

4. **Install Docker Compose**: Download Docker Compose using the `get_url` module and make it executable.

   ```yaml
   - name: Download Docker Compose
     get_url:
       url: https://github.com/docker/compose/releases/download/{{ docker_compose_version }}/docker-compose-{{ ansible_facts['os_family'].lower() }}-{{ ansible_facts['architecture'] }}
       dest: /usr/local/bin/docker-compose
     become: yes
   
   - name: Make Docker Compose Executable
     file:
       path: /usr/local/bin/docker-compose
       mode: 'a+x'
     become: yes
   ```

5. **Start Docker Service**: Use the `systemd` module to start the Docker service.

   ```yaml
   - name: Start Docker Service
     systemd:
       name: docker
       state: started
     become: yes
   ```

6. **Add User to Docker Group**: Add the EC2 user to the Docker group to avoid needing `sudo` for Docker commands.

   ```yaml
   - name: Add EC2 User to Docker Group
     user:
       name: ec2-user
       groups: docker
       append: yes
     become: yes
   ```

7. **Reconnect SSH Session**: Reset the SSH session to apply group changes.

   ```yaml
   - name: Reconnect to Server
     meta: reset_connection
   ```

By following these steps, you can ensure that the Ansible playbook handles the installation of Docker and Docker Compose on a fresh EC2 instance while maintaining compatibility with both Python 2 and Python 3.

---
<!-- nav -->
[[07-User Group Management and Docker Permissions on AWS EC2|User Group Management and Docker Permissions on AWS EC2]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/11-Automated Docker Setup on AWS EC2 with Ansible/00-Overview|Overview]]
