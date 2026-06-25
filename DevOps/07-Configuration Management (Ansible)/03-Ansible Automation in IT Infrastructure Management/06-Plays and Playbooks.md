---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Plays and Playbooks

In Ansible, a play is a collection of tasks that are executed on a set of hosts. A playbook is a file that contains one or more plays. This section will cover the structure and usage of plays and playbooks, along with practical examples and best practices.

### Structure of a Play

A play consists of the following components:

- **Name**: A descriptive name for the play.
- **Hosts**: The hosts on which the play will be executed.
- **Tasks**: The tasks that will be executed as part of the play.
- **Vars**: Variables that can be defined at the play level.
- **Pre-Tasks**: Tasks that are executed before the main tasks.
- **Post-Tasks**: Tasks that are executed after the main tasks.
- **Handlers**: Tasks that are executed conditionally based on events.

#### Example: Basic Play Structure

```yaml
---
- name: Example Play
  hosts: all
  tasks:
    - name: Print hello
      debug:
        msg: "Hello, world!"
```

In this example, we define a simple play that prints "Hello, world!" to the console.

### Multiple Plays in a Playbook

A playbook can contain multiple plays, each targeting different sets of hosts. This allows you to orchestrate complex workflows across multiple hosts.

#### Example: Multiple Plays in a Playbook

```yaml
---
- name: Web Server Play
  hosts: web_servers
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present

- name: Database Play
  hosts: db_servers
  tasks:
    - name: Install MySQL
      apt:
        name: mysql-server
        state: present
```

In this example, we define two plays: one for web servers and one for database servers. Each play installs the appropriate software on the specified hosts.

### Benefits of Using Multiple Plays

- **Modularity**: Each play can be focused on a specific task or set of tasks.
- **Reusability**: Plays can be reused across multiple playbooks.
- **Maintainability**: Complex workflows can be broken down into smaller, more manageable pieces.

### Best Practices for Play Usage

- **Descriptive Names**: Use descriptive names for plays to make their purpose clear.
- **Documentation**: Include comments or documentation explaining the purpose and usage of each play.
- **Logical Grouping**: Group related tasks together in a single play.

### Common Pitfalls

- **Overlapping Hosts**: Ensure that plays do not overlap in terms of the hosts they target.
- **Complex Dependencies**: Be mindful of dependencies between plays and ensure they are executed in the correct order.

### How to Prevent / Defend

- **Validation**: Use validation techniques to ensure plays are correctly defined and do not overlap.
- **Error Handling**: Implement error handling to catch and handle issues gracefully.

### Real-World Example: Complex Workflow with Multiple Plays

Consider a scenario where you want to deploy a web application across multiple servers. This can be achieved using multiple plays in a single playbook.

```yaml
---
- name: Web Server Play
  hosts: web_servers
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
    - name: Copy index.html
      copy:
        src: /path/to/index.html
        dest: /var/www/html/index.html

- name: Database Play
  hosts: db_servers
  tasks:
    - name: Install MySQL
      apt:
        name: mysql-server
        state: present
    - name: Create database
      mysql_db:
        name: mydatabase
        state: present
        login_user: root
        login_password: password

- name: Application Play
  hosts: app_servers
  tasks:
    - name: Install Node.js
      apt:
        name: nodejs
        state: present
    - name: Deploy application
      shell: npm install && npm start
```

In this example, we define three plays: one for web servers, one for database servers, and one for application servers. Each play installs the necessary software and performs the required tasks.

### Conclusion

Plays and playbooks are essential components of Ansible that enable you to orchestrate complex workflows across multiple hosts. By structuring your playbooks effectively, you can improve the modularity, reusability, and maintainability of your Ansible scripts.

---
<!-- nav -->
[[05-Playbook Execution and Orchestration|Playbook Execution and Orchestration]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/03-Ansible Automation in IT Infrastructure Management/00-Overview|Overview]] | [[07-Variables in Ansible Playbooks|Variables in Ansible Playbooks]]
