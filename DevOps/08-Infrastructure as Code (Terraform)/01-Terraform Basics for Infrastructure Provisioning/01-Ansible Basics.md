---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Ansible Basics

### What is Ansible?

Ansible is an open-source IT automation tool that enables configuration management, application deployment, task automation, and multi-node orchestration. Ansible is agentless, meaning it does not require any additional software to be installed on the managed nodes.

### Why Use Ansible?

Ansible is particularly strong in the following areas:

1. **Agentless**: Ansible does not require any additional software to be installed on the managed nodes, making it easy to use.
2. **Playbooks**: Ansible uses playbooks, which are written in YAML, to define the desired state of your infrastructure.
3. **Idempotence**: Ansible is idempotent, meaning that running the same playbook multiple times will not change the outcome.
4. **Multi-platform Support**: Ansible supports a wide range of operating systems, including Linux, Windows, and macOS.

### How Does Ansible Work?

Ansible works by defining your infrastructure in playbooks. These playbooks describe the desired state of your infrastructure, including the tasks you want to perform, the hosts you want to target, and the order in which tasks should be executed.

#### Example Ansible Playbook

Here is a simple example of an Ansible playbook (`playbook.yml`):

```yaml
---
- name: Install and configure Nginx
  hosts: webservers
  become: yes
  tasks:
    - name: Ensure Nginx is installed
      apt:
        name: nginx
        state: present

    - name: Ensure Nginx is started
      service:
        name: nginx
        state: started
        enabled: yes
```

This playbook installs and starts the Nginx service on the specified hosts.

### Ansible Commands

Ansible provides several commands to manage your infrastructure:

- `ansible-playbook`: Executes the tasks defined in a playbook.
- `ansible-inventory`: Manages inventory files, which define the hosts and groups of hosts.
- `ansible-galaxy`: Manages roles, which are reusable collections of playbooks and tasks.

### Ansible Inventory

Ansible uses inventory files to define the hosts and groups of hosts that you want to manage. Inventory files can be written in various formats, including INI, YAML, and script-based.

#### Example Inventory File

Here is an example of an Ansible inventory file (`inventory.ini`):

```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
db2.example.com
```

### Ansible Roles

Ansible roles allow you to encapsulate and reuse playbooks and tasks. Roles can be nested within each other, making it easy to build complex infrastructure configurations.

#### Example Role

Here is an example of an Ansible role (`roles/nginx/tasks/main.yml`):

```yaml
---
- name: Ensure Nginx is installed
  apt:
    name: nginx
    state: present

- name: Ensure Nginx is started
  service:
    name: nginx
    state: started
    enabled: yes
```

You can use this role in your main playbook (`playbook.yml`):

```yaml
---
- name: Install and configure Nginx
  hosts: webservers
  become: yes
  roles:
    - nginx
```

### Ansible Best Practices

To get the most out of Ansible, follow these best practices:

1. **Use Version Control**: Store your Ansible playbooks and roles in a version control system like Git.
2. **Use Roles**: Encapsulate and reuse playbooks and tasks using roles.
3. **Use Idempotence**: Write playbooks that are idempotent, meaning they can be run multiple times without changing the outcome.
4. **Use Variables**: Use variables to abstract away hardcoded values.

### Real-World Examples

#### Example: Install and Configure Nginx

Here is a more complex example of an Ansible playbook that installs and configures Nginx:

```yaml
---
- name: Install and configure Nginx
  hosts: webservers
  become: yes
  vars:
    nginx_conf: |
      server {
        listen 80;
        server_name {{ ansible_hostname }};
        root /var/www/html;

        location / {
          index index.html index.htm;
        }
      }
  tasks:
    - name: Ensure Nginx is installed
      apt:
        name: nginx
        state: present

    - name: Ensure Nginx is started
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Create Nginx configuration file
      copy:
        content: "{{ nginx_conf }}"
        dest: /etc/nginx/sites-available/default
```

### Common Pitfalls and How to Avoid Them

#### Pitfall: Missing Dependencies

**Problem**: If you forget to define dependencies between tasks, Ansible may execute tasks in the wrong order.

**Solution**: Use the `depends_on` attribute to explicitly define dependencies between tasks.

#### Pitfall: Hardcoding Values

**Problem**: Hardcoding values in your playbooks makes it difficult to reuse and modify your infrastructure.

**Solution**: Use variables and roles to abstract away hardcoded values.

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Perform regular audits of your Ansible playbooks and roles to ensure they are up-to-date and consistent.
- **Automated Testing**: Use automated testing tools to validate your Ans

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/02-Introduction to Infrastructure as Code (IaC)|Introduction to Infrastructure as Code (IaC)]]
