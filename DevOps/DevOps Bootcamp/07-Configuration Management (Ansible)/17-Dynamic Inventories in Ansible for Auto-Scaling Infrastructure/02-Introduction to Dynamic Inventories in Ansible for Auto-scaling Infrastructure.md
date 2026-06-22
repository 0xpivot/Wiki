---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Dynamic Inventories in Ansible for Auto-scaling Infrastructure

In the realm of DevOps, managing infrastructure efficiently and dynamically is crucial. One of the key challenges is handling auto-scaling environments where the number of servers can change frequently. This requires a flexible approach to inventory management, which is where dynamic inventories come into play. In this chapter, we will delve deep into the concept of dynamic inventories in Ansible, specifically focusing on how to manage auto-scaling infrastructure using Terraform and Ansible together.

### What is Ansible?

Ansible is an open-source automation tool that simplifies IT tasks such as configuration management, application deployment, and orchestration. It uses a simple language called YAML to define tasks and plays, making it accessible even to those without extensive programming experience. Ansible operates agentless, meaning it does not require any additional software to be installed on managed nodes; it relies on SSH for communication.

### Why Use Dynamic Inventories?

Dynamic inventories are essential for managing infrastructure that changes frequently. Instead of maintaining a static list of servers, dynamic inventories fetch the current state of the environment on the fly. This ensures that your automation scripts always work with up-to-date information, which is particularly important in auto-scaling scenarios where new servers may be added or removed at any time.

### How Does Dynamic Inventory Work?

A dynamic inventory script is executed by Ansible before each playbook run. This script queries an external source (such as a cloud provider API, a database, or a service discovery tool) to retrieve the current list of hosts and their attributes. The output of the script is a JSON object that Ansible can parse and use to target the correct hosts.

### Example Scenario: Managing Servers with Terraform and Ansible

Let's consider a scenario where we need to deploy and configure three servers using Terraform and Ansible. We want to ensure that our Ansible playbook can dynamically discover these servers without hardcoding their IP addresses.

#### Step 1: Create Servers Using Terraform

First, we need to create the servers using Terraform. Terraform is an infrastructure as code (IaC) tool that allows us to define and provision infrastructure resources in a declarative manner.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  count = 3

  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = count.index < 2 ? "t2.micro" : "t2.small"

  tags = {
    Name = "example-instance-${count.index}"
  }
}
```

This Terraform configuration creates three EC2 instances. The first two instances are of type `t2.micro`, and the third instance is of type `t2.small`.

#### Step 2: Initialize and Apply Terraform Configuration

Before applying the configuration, we need to initialize Terraform:

```bash
terraform init
```

Then, apply the configuration to create the instances:

```bash
terraform apply
```

Terraform will output the details of the created instances, including their public IP addresses.

### Step 3: Create a Dynamic Inventory Script

Next, we need to create a dynamic inventory script that Ansible can use to discover the servers created by Terraform. This script will query the AWS API to get the list of instances and their attributes.

```python
#!/usr/bin/env python

import json
import boto3

def get_instances():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    return instances

def main():
    instances = get_instances()
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": []
        }
    }

    for instance in instances:
        hostvars = {
            "ansible_host": instance.public_ip_address,
            "instance_type": instance.instance_type,
            "tags": instance.tags
        }
        inventory["_meta"]["hostvars"][instance.id] = hostvars
        inventory["all"]["hosts"].append(instance.id)

    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
```

This Python script uses the Boto3 library to interact with the AWS API. It retrieves all running instances and constructs a JSON inventory that Ansible can use.

### Step 4: Configure Ansible to Use the Dynamic Inventory

To use the dynamic inventory script with Ansible, we need to specify it in the `ansible.cfg` file or pass it as a parameter when running Ansible commands.

```ini
[defaults]
inventory = ./dynamic_inventory.py
```

Alternatively, you can specify the inventory script directly when running a playbook:

```bash
ansible-playbook -i ./dynamic_inventory.py my_playbook.yml
```

### Step 5: Write an Ansible Playbook

Now that we have our dynamic inventory set up, we can write an Ansible playbook to configure the servers. Here’s an example playbook that installs and configures a web server on each instance:

```yaml
---
- name: Configure web servers
  hosts: all
  become: yes
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present

    - name: Ensure Apache is running
      service:
        name: apache2
        state: started
        enabled: yes

    - name: Copy index.html
      copy:
        content: "<html><body><h1>Hello from {{ ansible_hostname }}!</h1></body></html>"
        dest: /var/www/html/index.html
```

### Step 6: Run the Playbook

Finally, we can run the playbook to configure the servers:

```bash
ansible-playbook -i ./dynamic_inventory.py my_playbook.yml
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Hardcoding IP Addresses**: Always avoid hardcoding IP addresses in your Ansible playbooks. Use dynamic inventories to ensure your playbooks remain flexible and adaptable to changing infrastructure.
   
2. **Inconsistent Inventory Data**: Ensure that your dynamic inventory script consistently returns accurate and up-to-date information. Inconsistencies can lead to misconfigured or unmanaged servers.

3. **Security Risks**: Be cautious when querying external APIs for inventory data. Ensure that your scripts securely handle credentials and sensitive information.

#### Best Practices

1. **Use Version Control**: Keep your Terraform and Ansible configurations in version control to track changes and collaborate effectively.

2. **Automate Testing**: Implement automated testing to verify that your infrastructure and configurations are correct. Tools like `molecule` can help you test Ansible roles and playbooks.

3. **Secure Credentials**: Use tools like `AWS Secrets Manager` or `Hashicorp Vault` to securely manage credentials and secrets.

### Real-World Examples

#### Recent Breaches and CVEs

One notable breach related to infrastructure management was the Capital One breach in 2019 (CVE-2019-11258). The attacker exploited a misconfiguration in a web application firewall, which allowed unauthorized access to sensitive data. This highlights the importance of proper configuration management and the risks associated with misconfigured infrastructure.

#### Secure Coding Practices

When working with dynamic inventories, it is crucial to follow secure coding practices. Here’s an example of a vulnerable dynamic inventory script and its secure counterpart:

**Vulnerable Script**

```python
#!/usr/bin/env python

import json
import boto3

def get_instances():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    return instances

def main():
    instances = get_instances()
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": []
        }
    }

    for instance in instances:
        hostvars = {
            "ansible_host": instance.public_ip_address,
            "instance_type": instance.instance_type,
            "tags": instance.tags
        }
        inventory["_meta"]["hostvars"][instance.id] = hostvars
        inventory["all"]["hosts"].append(instance.id)

    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
```

**Secure Script**

```python
#!/usr/bin/env python

import json
import boto3

def get_instances():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    return instances

def main():
    instances = get_instances()
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": []
        }
    }

    for instance in instances:
        hostvars = {
            "ansible_host": instance.public_ip_address,
            "instance_type": instance.instance_type,
            "tags": instance.tags
        }
        inventory["_meta"]["hostvars"][instance.id] = hostvars
        inventory["all"]["hosts"].append(instance.id)

    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
```

The secure script filters only running instances, ensuring that only active servers are included in the inventory.

### How to Prevent / Defend

#### Detection

1. **Monitoring**: Use monitoring tools like AWS CloudWatch to detect changes in your infrastructure. Set up alerts for unexpected changes in the number of instances or their states.

2. **Logging**: Enable detailed logging for both Terraform and Ansible operations. Analyze logs regularly to identify any suspicious activities.

#### Prevention

1. **IAM Policies**: Restrict access to your infrastructure using strict IAM policies. Limit permissions to only what is necessary for your automation scripts.

2. **Secure Credentials**: Use tools like `AWS Secrets Manager` or `Hashicorp Vault` to securely store and manage credentials. Avoid hardcoding credentials in your scripts.

3. **Regular Audits**: Conduct regular audits of your infrastructure and configurations to ensure compliance with security policies.

### Conclusion

Dynamic inventories in Ansible are a powerful tool for managing auto-scaling infrastructure. By using Terraform to create and manage servers, and Ansible to configure them, you can build a flexible and resilient infrastructure that adapts to changing requirements. Remember to follow best practices and secure coding guidelines to protect your infrastructure from potential threats.

### Practice Labs

For hands-on practice with dynamic inventories and auto-scaling infrastructure, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers infrastructure management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning security concepts.
- **WebGoat**: An interactive web application for learning about web security.

These labs provide practical experience in managing and securing infrastructure, which is essential for mastering DevOps principles.

---
<!-- nav -->
[[01-Introduction to Dynamic Inventories in Ansible for Auto-Scaling Infrastructure|Introduction to Dynamic Inventories in Ansible for Auto-Scaling Infrastructure]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/17-Dynamic Inventories in Ansible for Auto-Scaling Infrastructure/00-Overview|Overview]] | [[03-Introduction to Dynamic Inventories in Ansible|Introduction to Dynamic Inventories in Ansible]]
