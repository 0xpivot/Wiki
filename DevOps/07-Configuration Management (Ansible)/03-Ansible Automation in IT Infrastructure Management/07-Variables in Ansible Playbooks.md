---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Variables in Ansible Playbooks

In Ansible, variables are a fundamental aspect of creating dynamic and reusable playbooks. Variables allow you to store values that can be reused throughout your playbook, making your scripts more flexible and easier to maintain. This section will cover how to define and use variables in Ansible, along with practical examples and best practices.

### Defining Variables

Variables in Ansible can be defined at various levels, including:

- **Playbook Level**: Defined within the `vars` section of a playbook.
- **Role Level**: Defined within the `vars` directory of a role.
- **Inventory Level**: Defined within the inventory file.
- **Host Level**: Defined within the host-specific inventory file.

For simplicity, we'll focus on defining variables at the playbook level.

#### Example: Defining Variables in a Playbook

Consider the following playbook snippet where we define two variables: `table_name` and `table_owner`.

```yaml
---
- name: Example Playbook
  vars:
    table_name: Foo
    table_owner: admin
  tasks:
    - name: Print table name
      debug:
        msg: "The table name is {{ table_name }} and the owner is {{ table_owner }}"
```

In this example, we define two variables: `table_name` and `table_owner`. These variables are then used within the `debug` task to print their values.

### Using Variables

Variables in Ansible are accessed using double curly braces (`{{ variable_name }}`). This syntax allows you to insert the value of a variable into strings, paths, or any other context where the variable's value is needed.

#### Example: Using Variables in Tasks

Let's expand on the previous example to demonstrate how variables can be used in tasks.

```yaml
---
- name: Example Playbook
  vars:
    table_name: Foo
    table_owner: admin
  tasks:
    - name: Create database table
      mysql_db:
        name: "{{ table_name }}"
        state: present
        login_user: "{{ table_owner }}"
        login_password: "password"
```

In this example, the `mysql_db` module is used to create a database table. The `name` parameter is set to the value of `table_name`, and the `login_user` parameter is set to the value of `table_owner`.

### Benefits of Using Variables

Using variables in Ansible provides several benefits:

- **Reusability**: Variables can be reused across multiple tasks and plays, reducing redundancy.
- **Flexibility**: Variables can be easily changed without modifying the underlying tasks.
- **Maintainability**: Centralizing variable definitions makes it easier to manage and update values.

### Best Practices for Variable Usage

- **Use Descriptive Names**: Choose variable names that clearly describe their purpose.
- **Document Variables**: Include comments or documentation explaining the purpose and usage of each variable.
- **Use Default Values**: Provide default values for variables to ensure they are always defined.

### Common Pitfalls

- **Undefined Variables**: Ensure that all variables are properly defined before they are used.
- **Variable Scope**: Be aware of the scope of variables and ensure they are accessible where needed.

### How to Prevent / Defend

- **Validation**: Use validation techniques to ensure variables are correctly defined before use.
- **Error Handling**: Implement error handling to catch and handle undefined variables gracefully.

### Real-World Example: Dynamic Inventory with Variables

Consider a scenario where you want to dynamically generate an inventory based on variables. This can be useful in environments where the number of hosts may change frequently.

```yaml
---
- name: Dynamic Inventory Example
  hosts: all
  vars:
    web_servers: ["web1.example.com", "web2.example.com"]
    db_servers: ["db1.example.com", "db2.example.com"]
  tasks:
    - name: Print web servers
      debug:
        msg: "Web servers: {{ web_servers }}"
    - name: Print db servers
      debug:
        msg: "DB servers: {{ db_servers }}"
```

In this example, we define two lists of servers: `web_servers` and `db_servers`. These lists can be used to dynamically target specific hosts in subsequent tasks.

### Conclusion

Variables are a powerful feature in Ansible that enable you to create dynamic and reusable playbooks. By defining and using variables effectively, you can improve the flexibility, maintainability, and reusability of your Ansible scripts.

---
<!-- nav -->
[[06-Plays and Playbooks|Plays and Playbooks]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/03-Ansible Automation in IT Infrastructure Management/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/03-Ansible Automation in IT Infrastructure Management/08-Practice Questions & Answers|Practice Questions & Answers]]
