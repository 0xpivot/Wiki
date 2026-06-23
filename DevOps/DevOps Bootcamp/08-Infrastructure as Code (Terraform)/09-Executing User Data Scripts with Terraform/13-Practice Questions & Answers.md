---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of user data in Terraform when provisioning EC2 instances.**

User data in Terraform is used to pass initial commands or scripts to be executed on the EC2 instance upon creation. This allows for automated setup and configuration of the instance immediately after it is launched. For example, user data can include commands to install software, set up environment variables, or run initialization scripts. This approach is particularly useful for setting up the initial state of the server without manual intervention.

**Q2. How does Terraform handle the execution of commands on remote servers using the `remote-exec` provisioner?**

The `remote-exec` provisioner in Terraform allows you to execute commands on a remote server after it has been provisioned. You define the commands to be executed using the `inline` attribute within the `remote-exec` block. Additionally, you need to specify the connection details to the remote server using the `connection` block, including the type of connection (e.g., SSH), the host address (which can be referred to using `self.public_ip` for the current resource), the username, and the private key location. Once configured, Terraform will establish an SSH connection to the remote server and execute the specified commands.

```terraform
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "echo 'Hello, World!' > /tmp/hello.txt",
      "mkdir /tmp/newdir",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("${path.module}/id_rsa")
      host        = self.public_ip
    }
  }
}
```

**Q3. Why are provisioners considered a last resort in Terraform, and what are the recommended alternatives?**

Provisioners are considered a last resort in Terraform because they break the concept of idempotency, which is a core principle of Terraform. Idempotency ensures that running `terraform apply` multiple times with the same configuration results in the same outcome. Since provisioners involve executing arbitrary scripts, Terraform cannot guarantee that these scripts will always produce the same result, leading to potential inconsistencies and errors.

Recommended alternatives include:

- **Configuration Management Tools**: Use tools like Chef, Puppet, Ansible, or SaltStack to manage the configuration of remote servers after they are provisioned. These tools provide better visibility and control over the state of the servers.
  
- **Local Provider**: For handling local files, use the `local` provider maintained by HashiCorp, which maintains a declarative model and can detect changes effectively.

- **CI/CD Integration**: Integrate script execution as part of a CI/CD pipeline using tools like Jenkins or GitLab CI, rather than executing them directly through Terraform.

**Q4. What happens if a provisioner fails during the execution of a Terraform plan?**

If a provisioner fails during the execution of a Terraform plan, Terraform marks the resource where the provisioner is applied as tainted. This means that the resource will need to be recreated in subsequent runs of `terraform apply`. Even if the underlying resource (like an EC2 instance) is created and initialized, Terraform will report an error status and mark the resource for deletion due to the failure of the provisioner.

For example, if you forget to copy a required script to the remote server and the `file` provisioner fails, Terraform will report an error and the resource will be marked for recreation.

**Q5. How can you use the `file` provisioner to copy a file from a local machine to a remote server in Terraform?**

The `file` provisioner in Terraform is used to copy files from a local machine to a remote server. You need to specify the `source` and `destination` paths for the file. The `source` is the path on the local machine, and the `destination` is the path on the remote server. You also need to define the connection details to the remote server using the `connection` block.

```terraform
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  provisioner "file" {
    source      = "${path.module}/EntryScript.sh"
    destination = "/home/ec2-user/EntryScript.sh"

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("${path.module}/id_rsa")
      host        = self.public_ip
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/ec2-user/EntryScript.sh",
      "/home/ec2-user/EntryScript.sh",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("${path.module}/id_rsa")
      host        = self.public_ip
    }
  }
}
```

In this example, the `file` provisioner copies `EntryScript.sh` from the local machine to `/home/ec2-user/EntryScript.sh` on the remote server. The `remote-exec` provisioner then sets the execute permissions and runs the script on the remote server.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/12-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/00-Overview|Overview]]
