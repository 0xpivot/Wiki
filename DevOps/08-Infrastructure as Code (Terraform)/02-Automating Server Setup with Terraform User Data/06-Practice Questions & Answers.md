---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using user data in Terraform when setting up an EC2 instance.**

User data in Terraform serves as an entry point script that gets executed on an EC2 instance immediately upon its creation. This allows for automating the installation and configuration of software, such as Docker, and starting services or containers without requiring manual intervention via SSH. By embedding these initialization commands within the Terraform configuration, the entire setup process becomes reproducible and part of the infrastructure as code.

**Q2. How would you exploit user data to install Docker and start a Docker container on an EC2 instance using Terraform?**

To install Docker and start a Docker container using user data in Terraform, you would include a script within the `user_data` attribute of the EC2 resource. Here’s an example:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b7981d"
  instance_type = "t2.micro"

  user_data = <<-EOF
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo usermod -a -G docker ec2-user
    sudo docker run -d -p 80:80 nginx
  EOF
}
```

This script updates the package list, installs Docker, starts the Docker service, adds the `ec2-user` to the Docker group, and runs an Nginx container.

**Q3. Why might you prefer to reference a file for user data rather than embedding the script directly in the Terraform configuration?**

Referencing a file for user data in Terraform can make the configuration cleaner and more maintainable. Embedding a long script directly in the Terraform configuration can clutter the file and make it harder to read. By referencing a file, you can keep the shell script separate, making it easier to manage and modify. Additionally, this approach allows you to version control the shell script independently of the Terraform configuration.

Here’s an example of referencing a file:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b7981d"
  instance_type = "t2.micro"

  user_data = file("${path.module}/entryscript.sh")
}
```

Where `entryscript.sh` contains the necessary commands.

**Q4. What are the limitations of using Terraform for server setup beyond infrastructure provisioning?**

Terraform is primarily designed for provisioning and managing infrastructure, such as creating EC2 instances, setting up VPCs, and configuring security groups. Once the infrastructure is in place, Terraform does not provide detailed capabilities for configuring the server itself, such as installing specific software, setting environment variables, or deploying applications. 

For these tasks, Terraform relies on user data scripts, which require knowledge of shell scripting and may lack debugging capabilities. If something goes wrong in the user data script, troubleshooting requires manually SSHing into the server. Therefore, for more complex server configurations and application deployments, additional tools like Ansible, Puppet, or Chef are often used alongside Terraform.

**Q5. How would you integrate Terraform with Ansible to manage both infrastructure and application deployment?**

Integrating Terraform with Ansible involves using Terraform to provision the infrastructure and Ansible to configure the servers and deploy applications. Here’s a high-level approach:

1. **Provision Infrastructure with Terraform**: Use Terraform to create the necessary resources, such as EC2 instances, VPCs, and security groups.

2. **Output Instance Details**: Terraform outputs the details of the created instances, such as public IP addresses, which can be used by Ansible.

3. **Configure Servers with Ansible**: Use Ansible playbooks to install software, configure services, and deploy applications on the servers provisioned by Terraform.

Example Terraform configuration:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b7981d"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }

  provisioner "local-exec" {
    command = "echo ${self.public_ip} > instance_ips.txt"
  }
}
```

Example Ansible playbook:

```yaml
---
- hosts: all
  become: yes
  tasks:
    - name: Install Docker
      yum:
        name: docker
        state: present

    - name: Start Docker service
      service:
        name: docker
        state: started

    - name: Add ec2-user to Docker group
      user:
        name: ec2-user
        groups: docker

    - name: Run Nginx container
      docker_container:
        name: nginx
        image: nginx:latest
        ports:
          - "80:80"
```

By combining these tools, you can achieve a comprehensive automation pipeline for both infrastructure and application deployment.

---
<!-- nav -->
[[05-Post-Deployment Tasks with Shell Scripts|Post-Deployment Tasks with Shell Scripts]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/02-Automating Server Setup with Terraform User Data/00-Overview|Overview]]
