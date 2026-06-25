---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating a User with Ansible

### Understanding the `user` Module

The `user` module in Ansible is used to manage user accounts on remote systems. It allows you to create, modify, and delete user accounts. Here are some key attributes of the `user` module:

- **name**: Specifies the username.
- **group**: Specifies the primary group for the user.
- **state**: Determines whether the user should be present (`present`) or absent (`absent`).

### Example Playbook to Create a User

Let's create a playbook to create a user named `Nexus`.

```yaml
---
- name: Create Nexus user
  hosts: localhost
  become: yes
  tasks:
    - name: Create Nexus user
      user:
        name: Nexus
        group: Nexus
        state: present
```

### Explanation of the Playbook

- **hosts: localhost**: Specifies that the playbook should run on the local machine.
- **become: yes**: Enables privilege escalation, allowing the playbook to run with elevated privileges.
- **tasks**: Defines the tasks to be executed.
- **user**: Uses the `user` module to create a user.
  - **name: Nexus**: Specifies the username.
  - **group: Nexus**: Specifies the primary group for the user.
  - **state: present**: Ensures that the user is created.

### Running the Playbook

To run the playbook, use the following command:

```bash
ansible-playbook create_nexus_user.yml
```

### Verifying the User Creation

After running the playbook, you can verify that the user was created successfully by checking the `/etc/passwd` file:

```bash
cat /etc/passwd | grep Nexus
```

You should see an entry similar to:

```
Nexus:x:1001:1001::/home/Nexus:/bin/bash
```

This indicates that the user `Nexus` has been created with the specified group.

---
<!-- nav -->
[[11-Assigning Group Ownership to a Directory|Assigning Group Ownership to a Directory]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/14-Create Nexus User And Group Ownership/00-Overview|Overview]] | [[13-Real-World Examples and Security Implications|Real-World Examples and Security Implications]]
