---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Post-Deployment Tasks with Shell Scripts

### Executing Commands After Infrastructure Setup

Once the infrastructure is ready, you often need to perform additional tasks such as installing software, configuring services, or running initialization scripts. Terraform itself does not support these tasks directly, so you need to use other methods to achieve them.

One common approach is to use user data scripts, which are executed during the boot process of an EC2 instance. User data scripts are typically written in shell script and can be specified in the Terraform configuration.

Here’s an example of how to specify user data in a Terraform configuration for an AWS EC2 instance:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              systemctl enable docker
              systemctl start docker
              EOF

  tags = {
    Name = "example-instance"
  }
}
```

In this example, the `user_data` block contains a shell script that updates the package list, installs Docker, and starts the Docker service.

### Debugging User Data Scripts

One of the challenges with user data scripts is debugging. If something goes wrong during the execution of the script, you may not receive immediate feedback. To diagnose issues, you need to SSH into the instance and check the logs or manually run the commands to see what went wrong.

For example, if the Docker installation fails, you might need to SSH into the instance and run the following commands to check the status:

```sh
sudo journalctl -u docker.service
```

This command shows the log output of the Docker service, which can help you identify any errors.

### Shell Scripting Requirements

To effectively use user data scripts, you need to be proficient in shell scripting. This includes understanding how to write shell scripts, execute commands, and handle errors. While Terraform provides the infrastructure setup, you still need to know how to write and execute shell scripts to configure the servers.

### Example: Installing Docker and Configuring the Server

Let’s walk through a more detailed example of installing Docker and configuring the server using a user data script.

#### Step 1: Define the Terraform Configuration

First, define the Terraform configuration to create an EC2 instance and specify the user data script:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              echo "Starting user data script..."
              
              # Update package list
              echo "Updating package list..."
              sudo apt-get update

              # Install Docker
              echo "Installing Docker..."
              sudo apt-get install -y docker.io

              # Enable and start Docker service
              echo "Enabling and starting Docker service..."
              systemctl enable docker
              systemctl start docker

              # Verify Docker installation
              echo "Verifying Docker installation..."
              docker --version
              EOF

  tags = {
    Name = "example-instance"
  }
}
```

#### Step 2: Apply the Terraform Configuration

Apply the Terraform configuration to create the EC2 instance and execute the user data script:

```sh
terraform init
terraform apply
```

#### Step 3: Verify the Installation

After the instance is created, you can SSH into the instance to verify that Docker was installed correctly:

```sh
ssh -i <path-to-key-pair> ec2-user@<instance-public-ip>
docker --version
```

### Common Pitfalls and How to Avoid Them

#### 1. Incorrect Shell Syntax

Ensure that your shell script syntax is correct. A small typo can cause the script to fail silently. Always test your scripts locally before deploying them.

#### 2. Missing Dependencies

Make sure that all dependencies required by your script are available. For example, if you are installing Docker, ensure that the package repository is up to date.

#### 3. Insufficient Permissions

Some commands require elevated permissions. Ensure that your script runs with the necessary privileges. Using `sudo` is a common way to elevate permissions, but be cautious about overusing it.

### How to Prevent / Defend

#### Detection

To detect issues with user data scripts, you can:

1. **Check Logs**: Review the system logs to identify any errors or warnings.
2. **SSH Access**: SSH into the instance and manually run the commands to see if they succeed.

#### Prevention

To prevent issues with user data scripts, you can:

1. **Test Locally**: Test your scripts locally before deploying them.
2. **Use Version Control**: Store your scripts in version control to track changes and collaborate with team members.
3. **Automate Testing**: Use automated testing tools to validate your scripts.

#### Secure Coding Fixes

Here’s an example of a vulnerable user data script and its secure counterpart:

**Vulnerable Script:**

```sh
#!/bin/bash
echo "Starting user data script..."

# Update package list
echo "Updating package list..."
apt-get update

# Install Docker
echo "Installing Docker..."
apt-get install -y docker.io

# Enable and start Docker service
echo "Enabling and starting Docker service..."
systemctl enable docker
systemctl start docker

# Verify Docker installation
echo "Verifying Docker installation..."
docker --version
```

**Secure Script:**

```sh
#!/bin/bash
echo "Starting user data script..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker.io

# Enable and start Docker service
echo "Enabling and starting Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Verify Docker installation
echo "Verifying Docker installation..."
docker --version
```

### Real-World Examples

#### Recent Breaches and CVEs

While Terraform itself is not directly involved in most breaches, misconfigurations in user data scripts can lead to vulnerabilities. For example, if a user data script inadvertently exposes sensitive information or installs insecure software, it can be exploited.

#### Example: CVE-2021-21277

CVE-2021-21277 is a vulnerability in Docker that could allow an attacker to escalate privileges and gain root access to the host system. This vulnerability highlights the importance of keeping Docker and other software up to date and securely configured.

### Conclusion

Terraform is a powerful tool for managing infrastructure, but it has limitations when it comes to post-deployment tasks. By using user data scripts, you can extend Terraform’s capabilities to configure and initialize your servers. However, you need to be proficient in shell scripting and understand the challenges and pitfalls associated with user data scripts.

### Practice Labs

For hands-on practice with Terraform and user data scripts, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can be useful for understanding the broader context of DevOps security.
- **OWASP Juice Shop**: A deliberately vulnerable web application for learning about web security.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **WebGoat**: An interactive web security training application.

These labs provide practical experience with various aspects of DevOps and web security, helping you to better understand and apply the concepts discussed in this chapter.

---
<!-- nav -->
[[04-Automating Server Setup with Terraform User Data|Automating Server Setup with Terraform User Data]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/02-Automating Server Setup with Terraform User Data/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/02-Automating Server Setup with Terraform User Data/06-Practice Questions & Answers|Practice Questions & Answers]]
