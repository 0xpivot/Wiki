---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Infrastructure as Code (IaC) and GitOps for DevSecOps

### Introduction to Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a practice in which infrastructure is managed and provisioned through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for automation, consistency, and version control of infrastructure configurations. In the context of DevSecOps, IaC plays a crucial role in ensuring that infrastructure is deployed securely and consistently across different environments.

#### Why Use IaC?

- **Consistency**: Ensures that the same configuration is applied across multiple environments, reducing human error.
- **Automation**: Automates the deployment and management of infrastructure, saving time and effort.
- **Version Control**: Allows tracking changes to infrastructure configurations, making it easier to roll back to previous states if needed.
- **Reproducibility**: Makes it easy to replicate environments, which is particularly useful for testing and development purposes.

### User Data in IaC

User data is a feature provided by cloud providers like AWS that allows you to pass data or commands to an instance during its creation. This data is typically executed as a script on the instance immediately after it boots up. This is particularly useful for automating initial configuration tasks such as installing software, setting up services, or configuring environment variables.

#### How User Data Works

When an instance is launched, the cloud provider passes the user data to the instance. The instance then executes the user data as a script. This script can perform various tasks, such as:

- Installing software packages.
- Configuring system settings.
- Setting up services.
- Running custom initialization scripts.

#### Example: Using User Data with Terraform

Let's consider an example where we use Terraform to launch an AWS EC2 instance and pass user data to it. The user data will be used to install Docker and configure the necessary permissions.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo usermod -aG docker ubuntu
              EOF
}
```

In this example, the `user_data` field contains a shell script that updates the package list, installs Docker, and adds the `ubuntu` user to the `docker` group.

### Base64 Encoding User Data

Since user data is passed as a string, it often needs to be encoded in a format that is safe for transmission. Base64 encoding is commonly used for this purpose. Base64 encoding converts binary data into ASCII characters, making it suitable for transmission over protocols that expect textual data.

#### Example: Base64 Encoding User Data

Let's encode the user data script using Base64 encoding.

```bash
echo -n '#!/bin/bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu' | base64
```

The output of this command can be used as the value for the `user_data` field in Terraform.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<BASE64
              IyEvc2g/YmFzaAo=
              BASE64
}
```

### Script Templates in IaC

In complex IaC setups, it is common to use script templates that can be parameterized with variables. This allows for more flexibility and reusability of scripts across different environments.

#### Example: Using Script Templates

Consider a scenario where we have two types of servers: an application server and a GitLab server. Each server requires different initial configurations.

```hcl
locals {
  script_application = base64encode(file("${path.module}/scripts/application.sh"))
  script_gitlab      = base64encode(file("${path.module}/scripts/gitlab.sh"))
}

resource "aws_instance" "application" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = local.script_application
}

resource "aws_instance" "gitlab" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = local.script_gitlab
}
```

In this example, the `local` block defines two script templates, one for the application server and one for the GitLab server. These templates are then referenced in the `user_data` fields of the respective instances.

### Script Templates Defined in Files

The script templates are defined in separate files within the `scripts` directory. Here is an example of what the `application.sh` and `gitlab.sh` files might look like.

#### `application.sh`

```sh
#!/bin/bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
```

#### `gitlab.sh`

```sh
#!/bin/bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker gitlab-runner
```

These scripts are then base64 encoded and passed as user data to the respective instances.

### Real-World Examples and Security Considerations

#### Recent Breaches and CVEs

One notable breach involving IaC misconfigurations is the Capital One breach in 2019. The attacker exploited a misconfigured AWS S3 bucket, which was due to a mistake in the IaC configuration. This highlights the importance of properly securing and validating IaC configurations.

#### Secure Coding Practices

To prevent such vulnerabilities, it is essential to follow secure coding practices when writing IaC scripts. This includes:

- **Least Privilege Principle**: Ensure that scripts run with the minimum necessary privileges.
- **Input Validation**: Validate all inputs to scripts to prevent injection attacks.
- **Secure Configuration Management**: Use tools like Terraform to manage and validate configurations.

#### Example: Secure IaC Configuration

Here is an example of a secure IaC configuration using Terraform.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo usermod -aG docker ubuntu
              EOF
}

resource "aws_security_group" "example" {
  name        = "example-sg"
  description = "Allow SSH and HTTP access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, the `aws_security_group` resource is used to define a security group that restricts access to the instance. This helps prevent unauthorized access to the instance.

### How to Prevent / Defend

#### Detection

To detect misconfigurations in IaC, use tools like `Terraform Validate` and `TFLint`. These tools can help identify potential issues in your IaC configurations.

#### Prevention

To prevent misconfigurations, follow these best practices:

- **Use Version Control**: Store IaC configurations in version control systems like Git.
- **Automated Testing**: Implement automated testing to validate IaC configurations.
- **Code Reviews**: Conduct regular code reviews to catch potential issues.

#### Secure-Coding Fixes

Here is an example of a vulnerable IaC configuration and its secure counterpart.

**Vulnerable Configuration**

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo usermod -aG docker ubuntu
              EOF
}
```

**Secure Configuration**

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo usermod -aG docker ubuntu
              EOF

  security_groups = [aws_security_group.example.id]
}

resource "aws_security_group" "example" {
  name        = "example-sg"
  description = "Allow SSH and HTTP access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In the secure configuration, a security group is defined to restrict access to the instance.

### Conclusion

In conclusion, Infrastructure as Code (IaC) and GitOps are essential practices in DevSecOps. By automating infrastructure provisioning and managing configurations through code, organizations can ensure consistency, reproducibility, and security. Proper use of user data, script templates, and secure coding practices can help prevent misconfigurations and vulnerabilities. Regular validation and testing of IaC configurations can further enhance security and reliability.

### Practice Labs

For hands-on experience with IaC and GitOps, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications and infrastructure.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in applying IaC and GitOps principles in a secure manner.

---
<!-- nav -->
[[08-Introduction to Infrastructure as Code (IaC) and GitOps|Introduction to Infrastructure as Code (IaC) and GitOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]] | [[10-Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2|Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2]]
