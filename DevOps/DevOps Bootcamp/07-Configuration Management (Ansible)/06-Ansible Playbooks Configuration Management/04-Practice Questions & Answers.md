---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of Ansible Playbooks and how they fit into the infrastructure as code paradigm.**

Ansible Playbooks are used to automate the configuration management of servers. They allow users to define a series of tasks that should be performed on specific hosts, such as installing software, updating configurations, or managing services. By treating these configuration files as code, Ansible aligns with the infrastructure as code (IaC) paradigm, enabling version control, collaboration, and consistent deployment across environments. This approach ensures that the infrastructure is reproducible and maintainable over time.

**Q2. How do you structure an Ansible Playbook, and what are the key components involved?**

An Ansible Playbook is structured in YAML format and consists of multiple plays. Each play contains:

- **Hosts**: Specifies which servers the play should run on.
- **Tasks**: A list of actions to perform on the specified hosts, such as installing software or managing services.
- **Modules**: Specific commands or operations that are executed, like `apt` for package installation or `service` for managing services.

A typical playbook structure looks like this:

```yaml
---
- name: Configure EngineX Web Server
  hosts: webserver
  tasks:
    - name: Install EngineX server
      apt:
        name: engine-x
        state: latest
    - name: Start EngineX server
      service:
        name: engine-x
        state: started
```

**Q3. How would you exploit the item potency feature of Ansible to ensure consistent server states without unnecessary changes?**

Item potency ensures that repeated executions of the same playbook produce the same results without making unnecessary changes. To exploit this feature, you can:

- Use the `state` parameter in modules to specify desired states (e.g., `latest`, `present`, `started`).
- Leverage the `changed_when` directive to control when a task is marked as changed.
- Utilize conditional statements (`when`) to skip tasks if certain conditions are met.

For example, to ensure EngineX is installed and running without reinstalling if already present:

```yaml
- name: Install EngineX server
  apt:
    name: engine-x
    state: latest
  register: engine_x_install
- name: Start EngineX server
  service:
    name: engine-x
    state: started
  when: engine_x_install.changed
```

This ensures that the service is started only if the installation was a new change.

**Q4. What is the significance of the `hosts` file in an Ansible project, and how does it integrate with playbooks?**

The `hosts` file is crucial in an Ansible project as it lists the servers (or groups of servers) that the playbooks will interact with. It serves as the inventory of managed systems. When a playbook is executed, Ansible references the `hosts` file to determine which servers to target based on the `hosts` attribute defined in each play.

Example `hosts` file:

```ini
[webserver]
192.168.1.10
192.168.1.11
```

In the playbook, you refer to these groups:

```yaml
hosts: webserver
```

This integration ensures that the playbook tasks are applied to the correct set of servers.

**Q5. How do you handle specific package versions in Ansible playbooks, and what are the implications of specifying exact versions versus using the latest version?**

To handle specific package versions in Ansible, you can use the `version` parameter within the `apt` module. For example:

```yaml
- name: Install specific version of EngineX
  apt:
    name: engine-x
    version: 1.16.1
    state: present
```

Specifying exact versions ensures that the exact version is installed, which can be important for compatibility or security reasons. Using the latest version (`state: latest`) ensures that the most recent version is installed, which might include bug fixes and security patches but could introduce breaking changes or incompatibilities.

**Q6. Describe how you would use Ansible to uninstall a package and stop a service, ensuring idempotency.**

To uninstall a package and stop a service while maintaining idempotency, you can use the following playbook:

```yaml
- name: Uninstall EngineX and stop service
  hosts: webserver
  tasks:
    - name: Stop EngineX server
      service:
        name: engine-x
        state: stopped
    - name: Uninstall EngineX server
      apt:
        name: engine-x
        state: absent
```

By setting the `state` to `stopped` and `absent`, Ansible ensures that the service is stopped and the package is uninstalled only if necessary, maintaining idempotency. Repeated execution will show no changes if the desired state is already achieved.

**Q7. How does Ansible's `gather facts` module contribute to the execution of playbooks, and why is it important?**

The `gather facts` module automatically runs at the beginning of each play to collect information about the remote servers, such as their operating system, network configuration, and hardware details. This information can be used in conditional statements (`when`) and variable interpolation within the playbook, allowing for more dynamic and context-aware automation.

For example:

```yaml
- name: Gather facts
  setup:

- name: Install EngineX only on Ubuntu
  apt:
    name: engine-x
    state: latest
  when: ansible_os_family == 'Debian'
```

Here, the `setup` module gathers facts, and the subsequent task checks the OS family before proceeding with the installation. This ensures that the playbook behaves correctly across different environments.

---
<!-- nav -->
[[03-Introduction to Configuration Management with Ansible Playbooks|Introduction to Configuration Management with Ansible Playbooks]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/06-Ansible Playbooks Configuration Management/00-Overview|Overview]]
