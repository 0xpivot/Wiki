---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## What is Ansible?

Ansible is an open-source automation tool designed to simplify the management and deployment of IT infrastructure. It allows you to automate various tasks such as provisioning, configuring, deploying, and managing systems and applications. Ansible operates using a simple language called YAML (YAML Ain't Markup Language) and does not require agents to be installed on managed nodes, making it agentless and easy to deploy.

### Why Automate IT Tasks?

Automating IT tasks is crucial for several reasons:

1. **Efficiency**: Manual tasks can be time-consuming and error-prone. Automation ensures consistency and reduces the likelihood of human errors.
2. **Scalability**: As the number of servers and applications grows, manual management becomes impractical. Automation allows you to manage large-scale infrastructures efficiently.
3. **Consistency**: Automated scripts ensure that configurations and deployments are consistent across all systems, reducing discrepancies and potential vulnerabilities.
4. **Speed**: Automation significantly speeds up the deployment process, allowing for faster iterations and quicker responses to changes.

### Example Scenarios

Let's explore some real-life scenarios where Ansible can be used to streamline IT processes.

#### Scenario 1: Deploying a New Application Version

Imagine you have a distributed application running on 10 servers. You need to deploy a new version of the application on all these servers. Manually logging into each server and performing the deployment would be time-consuming and prone to errors. With Ansible, you can create a playbook that automates this process.

```yaml
---
- name: Deploy new application version
  hosts: all
  become: yes
  tasks:
    - name: Stop the application service
      systemd:
        name: myapp.service
        state: stopped

    - name: Copy new application files
      copy:
        src: /path/to/new/app/files
        dest: /opt/myapp/

    - name: Start the application service
      systemd:
        name: myapp.service
        state: started
```

This playbook stops the application service, copies the new application files, and then starts the service again. This ensures that the deployment is consistent and error-free.

#### Scenario 2: Updating Docker Version

Another common task is updating the Docker version on multiple servers. This might involve multiple steps such as stopping services, updating packages, and restarting services. An Ansible playbook can handle this seamlessly.

```yaml
---
- name: Update Docker version
  hosts: all
  become: yes
  tasks:
    - name: Stop Docker service
      systemd:
        name: docker
        state: stopped

    - name: Update Docker package
      apt:
        name: docker-ce
        state: latest

    - name: Start Docker service
      systemd:
        name: docker
        state: started
```

This playbook stops the Docker service, updates the Docker package, and then restarts the service.

#### Scenario 3: System Maintenance Tasks

System maintenance tasks such as updates, backups, and system reboots are repetitive and time-consuming. Ansible can automate these tasks to save time and reduce errors.

```yaml
---
- name: Perform system maintenance tasks
  hosts: all
  become: yes
  tasks:
    - name: Update system packages
      apt:
        upgrade: yes
        update_cache: yes

    - name: Create system backup
      shell: tar czvf /backup/system_backup_{{ ansible_date_time.iso8601 }}.tar.gz /etc /var/log

    - name: Reboot system
      reboot:
```

This playbook updates system packages, creates a system backup, and then reboots the system.

### Components of Ansible

Ansible consists of several key components that work together to automate IT tasks:

1. **Playbooks**: These are the main configuration files written in YAML. They define the tasks to be executed and the order in which they should be performed.
2. **Inventory**: This is a list of hosts that Ansible manages. It can be defined in a simple text file or dynamically generated.
3. **Modules**: These are reusable components that perform specific tasks. Ansible has a vast library of modules for various tasks.
4. **Facts**: These are pieces of information gathered about the managed nodes. Facts can be used to make decisions within playbooks.
5. **Roles**: These are reusable units of configuration that encapsulate tasks, variables, and other components. Roles help in organizing and reusing configurations.

### Using Ansible with Docker

Docker is a popular containerization platform that simplifies the deployment and management of applications. Ansible can be used to automate Docker-related tasks such as building images, running containers, and managing Docker services.

#### Example: Building and Running a Docker Container

```yaml
---
- name: Build and run Docker container
  hosts: all
  become: yes
  tasks:
    - name: Build Docker image
      docker_image:
        name: myapp
        build:
          path: /path/to/dockerfile

    - name: Run Docker container
      docker_container:
        name: myapp-container
        image: myapp
        state: started
```

This playbook builds a Docker image and runs a container based on that image.

### Comparing Ansible with Other Tools

Ansible is one of several automation tools available. Some alternatives include Puppet and Chef. Here’s a comparison:

- **Ansible**: Agentless, simple YAML-based configuration, easy to learn and use.
- **Puppet**: Agent-based, uses a declarative language called Puppet DSL, more complex but powerful for large-scale environments.
- **Chef**: Agent-based, uses a Ruby-based DSL, flexible and powerful but has a steeper learning curve.

### How to Prevent / Defend

While Ansible simplifies automation, it is essential to follow best practices to ensure security and reliability.

#### Secure Configuration Management

1. **Use Version Control**: Store your Ansible playbooks and configurations in a version control system like Git. This allows you to track changes and collaborate effectively.
2. **Limit Permissions**: Ensure that only authorized users have access to modify playbooks and configurations. Use role-based access control (RBAC) to manage permissions.
3. **Validate Inputs**: Validate inputs to prevent injection attacks. Use Ansible's built-in validation mechanisms to ensure that inputs are safe.

#### Example: Secure Configuration Management

```yaml
---
- name: Secure configuration management
  hosts: all
  become: yes
  vars:
    app_user: myappuser
    app_group: myappgroup
  tasks:
    - name: Create application user
      user:
        name: "{{ app_user }}"
        groups: "{{ app_group }}"
        state: present

    - name: Set permissions for application directory
      file:
        path: /opt/myapp/
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        mode: '0755'
```

This playbook creates an application user and sets appropriate permissions for the application directory.

### Real-World Examples

#### CVE-2021-44228: Log4Shell

The Log4Shell vulnerability (CVE-2021-44228) affected many applications using Apache Log4j. Ansible can be used to patch and mitigate this vulnerability.

```yaml
---
- name: Patch Log4j vulnerability
  hosts: all
  become: yes
  tasks:
    - name: Update Log4j package
      apt:
        name: log4j
        state: latest

    - name: Restart affected services
      systemd:
        name: myapp.service
        state: restarted
```

This playbook updates the Log4j package and restarts affected services.

### Conclusion

Ansible is a powerful tool for automating IT tasks, providing efficiency, scalability, and consistency. By understanding its components and best practices, you can effectively manage and deploy your IT infrastructure. Whether you are deploying new application versions, updating Docker, or performing system maintenance tasks, Ansible can streamline these processes and reduce the likelihood of errors.

### Practice Labs

For hands-on experience with Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including automation with Ansible.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. You can use Ansible to automate the deployment and management of this application.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training. Ansible can be used to automate the setup and management of DVWA.

By practicing with these labs, you can gain practical experience in using Ansible for automation in IT infrastructure management.

---
<!-- nav -->
[[01-Introduction to Ansible Automation in IT Infrastructure Management|Introduction to Ansible Automation in IT Infrastructure Management]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/03-Ansible Automation in IT Infrastructure Management/00-Overview|Overview]] | [[03-Environmental Variables and Start Scripts in Application Deployment|Environmental Variables and Start Scripts in Application Deployment]]
