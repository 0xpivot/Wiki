---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how to register variables as results of module execution in Ansible Playbooks.**

To register variables as results of module execution in Ansible Playbooks, you use the `register` attribute within a task. This allows you to capture the output of a module and store it in a variable. The syntax looks like this:

```yaml
- name: Create a Linux user
  user:
    name: "{{ username }}"
    state: present
  register: user_creation_result
```

Here, the output of the `user` module is stored in the `user_creation_result` variable. To access the contents of this variable, you can use the `debug` module:

```yaml
- name: Display user creation result
  debug:
    var: user_creation_result
```

The output will be a dictionary containing various key-value pairs, such as the UID of the newly created user, which can be accessed as `user_creation_result.uid`.

**Q2. How do you parameterize values in an Ansible Playbook, and what are the considerations for syntax?**

To parameterize values in an Ansible Playbook, you replace hardcoded values with variables enclosed in double curly braces (`{{ }}`). Considerations for syntax include:

- When the double curly braces follow a colon (`:`), you need to enclose them in quotes to avoid confusion with YAML dictionary syntax.
  
For example:

```yaml
- name: Copy Node.js app
  copy:
    src: "{{ node_app_location }}/nodejs-app-v{{ node_version }}.tar.gz"
    dest: "/home/{{ user_home_directory }}"
```

If `node_app_location` follows a colon, it should be quoted:

```yaml
src: "{{ 'node_app_location' }}/nodejs-app-v{{ node_version }}.tar.gz"
```

However, if the variable is part of a larger string, you don’t need to quote it:

```yaml
dest: "/home/{{ user_home_directory }}"
```

**Q3. How can you set variable values from outside the playbook during runtime?**

Variable values can be set from outside the playbook during runtime using the `--extra-vars` (or `-e`) flag when executing the playbook. This allows you to pass variables dynamically without modifying the playbook itself.

Example:

```bash
ansible-playbook my_playbook.yml --extra-vars "node_version=1.0.0 node_app_location=/path/to/app"
```

This approach is particularly useful for making the playbook more flexible and configurable across different environments or users.

**Q4. What is the benefit of using a separate variables file in Ansible Playbooks?**

Using a separate variables file in Ansible Playbooks offers several benefits:

- **Convenience**: Managing a large number of variables becomes easier when they are stored in a dedicated file rather than passed via command-line arguments.
- **Reusability**: Variables can be reused across multiple playbooks, reducing redundancy and maintaining consistency.
- **Team Collaboration**: Each team member can maintain their own local version of the variables file, adapting it to their specific needs without altering the main playbook.

To use a variables file, you specify its location using the `vars_files` attribute:

```yaml
vars_files:
  - ./project_vars
```

Where `project_vars` contains the variable definitions in YAML format:

```yaml
node_version: 1.0.0
node_app_location: /path/to/app
user_home_directory: /home/user
```

**Q5. What are the naming conventions for variables in Ansible Playbooks, and why are they important?**

Naming conventions for variables in Ansible Playbooks are important to avoid conflicts with reserved words and ensure readability. Key points include:

- Avoid using reserved words like `name`, `state`, etc., as variable names to prevent warnings or errors.
- Use underscores (`_`) or camelCase for multi-word variable names to ensure valid syntax. For example, `linux_user_name` or `linuxUserName`.
- Choose descriptive names to enhance readability and maintainability.

Example of proper naming:

```yaml
linux_user_name: nana
node_version: 1.0.0
user_home_directory: /home/user
```

By adhering to these conventions, you can avoid syntax errors and make your playbooks more understandable and maintainable.

---
<!-- nav -->
[[03-Variable Registration and Usage in Ansible Playbooks|Variable Registration and Usage in Ansible Playbooks]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/20-Variable Registration And Usage In Ansible Playbooks/00-Overview|Overview]]
