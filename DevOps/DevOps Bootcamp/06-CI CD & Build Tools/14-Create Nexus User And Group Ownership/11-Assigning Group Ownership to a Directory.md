---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Assigning Group Ownership to a Directory

### Understanding the `file` Module

The `file` module in Ansible is used to manage files and directories. It allows you to set ownership, permissions, and other attributes. Here are some key attributes of the `file` module:

- **path**: Specifies the path to the file or directory.
- **owner**: Specifies the owner of the file or directory.
- **group**: Specifies the group of the file or directory.
- **recurse**: Determines whether the changes should be applied recursively.

### Example Playbook to Set Ownership

Let's create a playbook to set ownership of a directory named `Nexus`.

```yaml
---
- name: Set ownership of Nexus directory
  hosts: localhost
  become: yes
  tasks:
    - name: Ensure Nexus directory exists
      file:
        path: /path/to/Nexus
        state: directory

    - name: Set ownership of Nexus directory
      file:
        path: /path/to/Nexus
        owner: Nexus
        group: Nexus
        recurse: yes
```

### Explanation of the Playbook

- **hosts: localhost**: Specifies that the playbook should run on the local machine.
- **become: yes**: Enables privilege escalation, allowing the playbook to run with elevated privileges.
- **tasks**: Defines the tasks to be executed.
- **Ensure Nexus directory exists**: Uses the `file` module to ensure the directory exists.
  - **path: /path/to/Nexus**: Specifies the path to the directory.
  - **state: directory**: Ensures that the directory exists.
- **Set ownership of Nexus directory**: Uses the `file` module to set ownership.
  - **path: /path/to/Nexus**: Specifies the path to the directory.
  - **owner: Nexus**: Specifies the owner of the directory.
  - **group: Nexus**: Specifies the group of the directory.
  - **recurse: yes**: Applies the changes recursively to all subdirectories and files.

### Running the Playbook

To run the playbook, use the following command:

```bash
ansible-playbook set_nexus_ownership.yml
```

### Verifying the Ownership

After running the playbook, you can verify that the ownership was set correctly by checking the directory's attributes:

```bash
ls -ld /path/to/Nexus
```

You should see output similar to:

```
drwxr-xr-x 2 Nexus Nexus 4096 Jan 1 12:00 /path/to/Nexus
```

This indicates that the directory `Nexus` is owned by the user `Nexus` and the group `Nexus`.

---
<!-- nav -->
[[10-Introduction to User and Group Management in DevOps|Introduction to User and Group Management in DevOps]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/14-Create Nexus User And Group Ownership/00-Overview|Overview]] | [[12-Creating a User with Ansible|Creating a User with Ansible]]
