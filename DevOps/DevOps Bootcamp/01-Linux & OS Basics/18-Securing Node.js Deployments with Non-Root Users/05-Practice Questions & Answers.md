---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it important to run Node.js applications with a non-root user?**

Running Node.js applications with a non-root user is crucial for security reasons. If an application runs with root privileges and is compromised, an attacker could gain full control over the system, leading to severe consequences such as data theft, system corruption, or unauthorized access to other systems. By using a non-root user, the potential damage is limited to the permissions granted to that user, reducing the risk of a full system compromise.

**Q2. How would you create a new user for a Node.js application in Ansible?**

To create a new user for a Node.js application in Ansible, you can use the `user` module. Here’s an example playbook snippet:

```yaml
- name: Create new Linux user for Node app
  hosts: all
  tasks:
    - name: Create Linux user
      user:
        name: nana
        state: present
        groups: admin
```

This playbook creates a user named `nana` and adds it to the `admin` group. Adjust the group and user name as needed.

**Q3. Explain how to configure Ansible to run tasks as a non-root user.**

To configure Ansible to run tasks as a non-root user, you need to use the `become_user` and `become` attributes in your playbook. Here’s an example:

```yaml
- name: Run tasks as a non-root user
  hosts: all
  become: yes
  become_user: nana
  tasks:
    - name: Ensure Node.js app is deployed
      copy:
        src: /path/to/node/app
        dest: /home/nana/
```

In this example, the `become` attribute is set to `yes`, and `become_user` specifies the user (`nana`) under which the tasks should be executed. This ensures that the tasks are performed with the permissions of the `nana` user rather than the root user.

**Q4. What are the benefits of running each application with its own user?**

Running each application with its own user provides several benefits:

1. **Isolation**: Each application runs with its own set of permissions, limiting the impact if one application is compromised.
2. **Security**: Reduces the risk of an attacker gaining elevated privileges by compromising an application.
3. **Auditing**: Easier to track and audit actions performed by specific applications through their respective user accounts.
4. **Resource Management**: Allows better control over resource allocation and usage by restricting access to only necessary files and directories.

**Q5. How can you ensure that a newly created user has minimal permissions necessary to run a Node.js application?**

To ensure that a newly created user has minimal permissions necessary to run a Node.js application, follow these steps:

1. **Create a dedicated group**: Create a group with minimal permissions and add the user to this group.
2. **Set ownership and permissions**: Set the ownership of the application files and directories to the new user and restrict permissions accordingly.
3. **Limit sudo privileges**: If the user needs to perform administrative tasks, limit sudo privileges to only the necessary commands.

Here’s an example playbook snippet:

```yaml
- name: Create a user with minimal permissions
  hosts: all
  tasks:
    - name: Create a group with minimal permissions
      group:
        name: nodeappgroup
        state: present

    - name: Create a user for the Node.js application
      user:
        name: nana
        state: present
        groups: nodeappgroup

    - name: Set ownership and permissions
      file:
        path: /path/to/node/app
        owner: nana
        group: nodeappgroup
        mode: '0755'
```

This playbook creates a group with minimal permissions, adds the user `nana` to this group, and sets the ownership and permissions of the application directory appropriately.

---
<!-- nav -->
[[04-Understanding User Management in Node.js Deployments|Understanding User Management in Node.js Deployments]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/18-Securing Node.js Deployments with Non-Root Users/00-Overview|Overview]]
