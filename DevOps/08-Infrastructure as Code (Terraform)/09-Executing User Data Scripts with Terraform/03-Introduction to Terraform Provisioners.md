---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform Provisioners

In the realm of infrastructure as code (IaC), Terraform stands out as one of the most powerful tools available. It allows you to define your infrastructure in a declarative manner using HCL (HashiCorp Configuration Language). However, sometimes you need to perform additional tasks after the infrastructure is created, such as installing software, configuring services, or setting up environment variables. This is where Terraform provisioners come into play.

### What Are Terraform Provisioners?

Terraform provisioners are mechanisms that allow you to run scripts or commands on the resources that Terraform manages. They are particularly useful for performing post-deployment configurations that are not covered by the basic resource definitions. There are several types of provisioners available in Terraform, including `local-exec`, `remote-exec`, and `file`.

#### Why Use Terraform Provisioners?

Provisioners are essential for ensuring that your infrastructure is fully configured and ready to use after deployment. Without them, you would have to manually SSH into each server and run the necessary commands, which is time-consuming and error-prone. By automating these steps with provisioners, you can ensure consistency and reliability across your infrastructure.

### Remote Execution Provisioner (`remote-exec`)

The `remote-exec` provisioner is one of the most commonly used provisioners in Terraform. It allows you to execute commands on a remote machine after it has been created. This is particularly useful for tasks like installing software, configuring services, or setting up environment variables.

#### How Does `remote-exec` Work?

When you define a `remote-exec` provisioner in your Terraform configuration, Terraform will establish an SSH connection to the remote machine and execute the specified commands. The commands can be defined either inline or in a separate script file.

##### Example: Using `remote-exec` to Install Docker

Let's walk through an example where we use `remote-exec` to install Docker on a newly created EC2 instance.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y docker.io",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
    ]
  }
}
```

In this example, we first create an EC2 instance using the `aws_instance` resource. Then, we define a `remote-exec` provisioner that runs a series of commands to update the package list, install Docker, and start the Docker service.

#### Common Pitfalls and How to Avoid Them

While `remote-exec` is a powerful tool, it also comes with its share of pitfalls. Here are some common issues and how to avoid them:

1. **SSH Connection Issues**: Ensure that the SSH key pair used to connect to the remote machine is correctly configured and accessible. You can specify the SSH key explicitly using the `connection` block.

2. **Command Execution Errors**: Make sure that the commands you are running are correct and appropriate for the operating system of the remote machine. For example, the above example assumes a Debian-based system; if you are using a different OS, you may need to adjust the commands accordingly.

3. **Permissions**: Ensure that the user running the commands has the necessary permissions to execute the commands. In the example above, we use `sudo` to run commands with elevated privileges.

4. **Network Latency**: Network latency can cause issues with command execution. Ensure that the network connection between the Terraform client and the remote machine is stable.

#### How to Prevent / Defend

To prevent issues with `remote-exec`, follow these best practices:

1. **Use Explicit SSH Keys**: Specify the SSH key explicitly using the `connection` block to avoid any ambiguity.

2. **Check Command Syntax**: Verify that the commands you are running are correct and appropriate for the operating system of the remote machine.

3. **Run Commands with Elevated Privileges**: Use `sudo` or other methods to ensure that the commands are run with the necessary permissions.

4. **Test Commands Locally**: Before running the commands via `remote-exec`, test them locally on a similar machine to ensure they work as expected.

##### Example: Using `connection` Block to Specify SSH Key

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
    }

    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y docker.io",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
    ]
  }
}
```

In this example, we specify the SSH key explicitly using the `connection` block. This ensures that Terraform uses the correct key to connect to the remote machine.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21277 - Docker Daemon API Unauthorized Access

CVE-2021-21277 is a critical vulnerability in the Docker daemon API that allows unauthorized access to the Docker daemon. This vulnerability can be exploited to gain full control over the Docker daemon, leading to potential compromise of the entire system.

##### How to Prevent / Defend

To prevent this vulnerability, ensure that the Docker daemon is properly secured and that only authorized users have access to it. Here are some steps to secure the Docker daemon:

1. **Restrict Access to Docker Socket**: Ensure that only authorized users have access to the Docker socket. This can be done by setting appropriate file permissions on the Docker socket file.

2. **Enable TLS for Docker Daemon**: Enable TLS for the Docker daemon to encrypt communication and authenticate clients.

3. **Use Docker Swarm or Kubernetes**: Use orchestration tools like Docker Swarm or Kubernetes to manage Docker containers securely.

##### Example: Securing Docker Daemon with TLS

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
    }

    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y docker.io",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo mkdir -p /etc/docker",
      "sudo tee /etc/docker/daemon.json <<EOF",
      "{",
      "  \"tls\": true,",
      "  \"tlscacert\": \"/etc/docker/ca.pem\",",
      "  \"tlscert\": \"/etc/docker/server-cert.pem\",",
      "  \"tlskey\": \"/etc/docker/server-key.pem\"",
      "}",
      "EOF",
      "sudo systemctl restart docker",
    ]
  }
}
```

In this example, we configure the Docker daemon to use TLS for secure communication. We create a `daemon.json` file with the necessary TLS settings and restart the Docker daemon to apply the changes.

### Conclusion

Terraform provisioners, particularly the `remote-exec` provisioner, are powerful tools for automating post-deployment configurations. By understanding how they work and following best practices, you can ensure that your infrastructure is fully configured and secure. Always test your commands locally before running them via `remote-exec` to avoid common pitfalls. Additionally, stay informed about recent vulnerabilities and take appropriate measures to secure your infrastructure.

### Practice Labs

For hands-on practice with Terraform provisioners, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of web application security, including infrastructure as code.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security techniques, including infrastructure as code.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice security techniques.

These labs provide a safe environment to experiment with Terraform and other DevOps tools, helping you gain practical experience and deepen your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to Remote Execution Provisioners in Terraform|Introduction to Remote Execution Provisioners in Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/00-Overview|Overview]] | [[04-Introduction to Terraform and Configuration Management|Introduction to Terraform and Configuration Management]]
