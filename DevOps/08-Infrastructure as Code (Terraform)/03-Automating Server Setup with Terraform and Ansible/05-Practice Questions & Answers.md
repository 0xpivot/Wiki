---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how Terraform and Ansible can be used together to automate server setup and configuration.**

Terraform is used to provision infrastructure resources such as EC2 instances, VPCs, subnets, and security groups. Once the infrastructure is set up, Ansible can be used to configure the server by executing playbooks that perform tasks such as installing software, setting up services, and managing users.

To automate the entire process, Terraform can be configured to execute an Ansible playbook after the server is provisioned. This is achieved by adding a `local-exec` provisioner to the Terraform configuration, which runs the Ansible command locally on the machine where Terraform is executed.

For example:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  provisioner "local-exec" {
    command = "ansible-playbook -i ${self.public_ip}, /path/to/playbook.yml --private-key=/path/to/private_key.pem --user=ec2-user"
  }
}
```

This ensures that the server is both provisioned and configured automatically without manual intervention.

**Q2. How can you ensure that Ansible connects to the newly created server correctly, especially when the IP address is dynamic?**

To ensure that Ansible connects to the newly created server correctly, you can pass the IP address dynamically from Terraform to Ansible using the `inventory` flag. This overrides the static host file and uses the dynamic IP address of the newly created server.

In the Terraform configuration, you can set the `inventory` flag in the `local-exec` provisioner:

```hcl
provisioner "local-exec" {
  command = "ansible-playbook -i ${self.public_ip}, /path/to/playbook.yml --private-key=/path/to/private_key.pem --user=ec2-user"
}
```

In the Ansible playbook, you can use the `hosts: all` directive to refer to the dynamic IP address passed via the `inventory` flag:

```yaml
---
- hosts: all
  gather_facts: false
  tasks:
    - name: Ensure SSH connection
      wait_for:
        port: 22
        delay: 10
        timeout: 100
        search_regex: OpenSSH
```

This ensures that Ansible connects to the correct server even when the IP address is dynamic.

**Q3. What are the potential issues with using provisioners in Terraform, and how can they be mitigated?**

One major issue with using provisioners in Terraform is the lack of control over the timing of their execution. Provisioners may run before the server is fully initialized, leading to errors or incomplete configurations.

To mitigate this, you can use Ansible to add a wait task that ensures the server is fully accessible before proceeding with further tasks. For example, you can add a `wait_for` task in your Ansible playbook:

```yaml
---
- hosts: all
  gather_facts: false
  tasks:
    - name: Ensure SSH connection
      wait_for:
        port: 22
        delay: 10
        timeout: 100
        search_regex: OpenSSH
```

This task waits until the SSH port is open and the server is ready before continuing with the rest of the playbook.

**Q4. How can you separate the Ansible playbook execution from the AWS instance resource using a `null_resource` in Terraform?**

To separate the Ansible playbook execution from the AWS instance resource, you can use a `null_resource` in Terraform. A `null_resource` allows you to define a custom task that can execute commands locally or remotely.

Here’s an example of how to use a `null_resource` to execute an Ansible playbook:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"
}

resource "null_resource" "configure_server" {
  triggers = {
    ip_address = aws_instance.example.public_ip
  }

  provisioner "local-exec" {
    command = "ansible-playbook -i ${aws_instance.example.public_ip}, /path/to/playbook.yml --private-key=/path/to/private_key.pem --user=ec2-user"
  }
}
```

In this example, the `null_resource` is triggered when the IP address of the AWS instance changes, ensuring that the Ansible playbook is executed whenever a new server is created.

**Q5. Why is it important to parameterize the SSH key location and user in the Ansible playbook command?**

Parameterizing the SSH key location and user in the Ansible playbook command is important for flexibility and maintainability. By using variables, you can easily modify the key location and user without changing the actual command in the Terraform configuration.

For example, you can define variables in the Terraform configuration:

```hcl
variable "ssh_private_key" {
  default = "/path/to/private_key.pem"
}

variable "ssh_user" {
  default = "ec2-user"
}
```

Then, in the `local-exec` provisioner, you can use these variables:

```hcl
provisioner "local-exec" {
  command = "ansible-playbook -i ${self.public_ip}, /path/to/playbook.yml --private-key=${var.ssh_private_key} --user=${var.ssh_user}"
}
```

This makes the configuration more flexible and easier to maintain, especially when dealing with multiple environments or different server configurations.

---
<!-- nav -->
[[04-Finalizing the Automation Pipeline with Terraform and Ansible|Finalizing the Automation Pipeline with Terraform and Ansible]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/00-Overview|Overview]]
