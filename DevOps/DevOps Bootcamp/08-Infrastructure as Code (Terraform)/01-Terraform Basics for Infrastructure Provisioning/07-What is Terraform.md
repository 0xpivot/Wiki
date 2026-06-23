---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## What is Terraform?

Terraform is an open-source tool developed by HashiCorp for managing and provisioning infrastructure across various cloud providers, such as AWS, Azure, Google Cloud Platform (GCP), and others. It enables users to define their infrastructure as code using a declarative language, which simplifies the process of setting up and maintaining complex environments.

### Declarative vs. Imperative Style

The key difference between Terraform and other infrastructure management tools lies in its declarative approach. In a declarative style, you describe the desired state of your infrastructure, and Terraform figures out the steps required to achieve that state. This contrasts with imperative languages, where you explicitly define each step of the process.

#### Example: Setting Up a Server

**Declarative Style (Terraform):**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

In this example, you simply declare that you want an `aws_instance` resource with specific attributes. Terraform will handle the creation of the instance, ensuring it matches the specified state.

**Imperative Style (Bash Script):**
```bash
#!/bin/bash

# Create a new EC2 instance
INSTANCE_ID=$(aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t2.micro --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=example-instance}]' --query 'Instances[0].InstanceId' --output text)

# Wait for the instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID
```

In the imperative style, you explicitly define each step, including creating the instance and waiting for it to become available.

### Why Use Terraform?

1. **Consistency**: Terraform ensures that your infrastructure is consistent across different environments (development, staging, production).
2. **Version Control**: Since your infrastructure is defined as code, you can use version control systems like Git to track changes and collaborate with team members.
3. **Automation**: Terraform automates the provisioning and management of resources, reducing manual errors and saving time.
4. **Multi-cloud Support**: Terraform supports multiple cloud providers, allowing you to manage hybrid infrastructures seamlessly.

### Real-World Example: Infrastructure as Code (IaC)

Consider a scenario where you are deploying a web application that consists of multiple microservices and a database. You want to set up this infrastructure on AWS.

#### Step-by-Step Process

1. **Define the Infrastructure**: Write Terraform configuration files to define the resources you need.
2. **Initialize Terraform**: Initialize the Terraform environment to download necessary plugins.
3. **Plan the Changes**: Run `terraform plan` to see the proposed changes.
4. **Apply the Configuration**: Run `terraform apply` to create the resources.
5. **Destroy the Resources**: Run `terraform destroy` to clean up the resources when they are no longer needed.

#### Example Configuration

Here’s a simple example of a Terraform configuration for setting up an EC2 instance and an RDS database:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_db_instance" "db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  name                 = "mydb"
  username             = "admin"
  password             = "password"
  db_name              = "mydb"
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}
```

### How to Prevent / Defend

#### Secure Coding Practices

1. **Use Environment Variables**: Store sensitive information like API keys and passwords in environment variables instead of hardcoding them in your Terraform configuration.
2. **Encrypt Sensitive Data**: Use tools like AWS KMS to encrypt sensitive data stored in your infrastructure.
3. **Least Privilege Principle**: Ensure that your IAM roles and policies follow the least privilege principle, granting only the necessary permissions.

#### Example: Securing Sensitive Data

```hcl
variable "db_password" {
  type        = string
  description = "Password for the database"
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

resource "aws_db_instance" "db" {
  ...
  password = data.aws_secretsmanager_secret_value.db_password.secret_string
}
```

### Common Pitfalls and Best Practices

1. **State Management**: Terraform maintains state information about your infrastructure. Ensure that the state file is backed up and securely stored.
2. **Dependency Management**: Define dependencies correctly to avoid issues during the execution of Terraform commands.
3. **Testing**: Use tools like Terratest to write tests for your Terraform configurations to ensure they work as expected.

### Conclusion

Terraform is a powerful tool for managing infrastructure as code. By using a declarative approach, it simplifies the process of setting up and maintaining complex environments. Understanding the principles behind Terraform and following best practices can help you effectively manage your infrastructure while ensuring security and consistency.

### Practice Labs

For hands-on experience with Terraform, consider the following labs:

- **Terraform Documentation**: [HashiCorp Terraform Documentation](https://www.terraform.io/docs)
- **Terraform Workshop**: [HashiCorp Learn Terraform Workshop](https://learn.hashicorp.com/collections/terraform/aws-get-started)
- **Terraform Examples**: [Terraform Examples Repository](https://github.com/hashicorp/terraform-examples)

These resources provide comprehensive tutorials and examples to help you master Terraform and apply it to real-world scenarios.

---
<!-- nav -->
[[06-Terraform Basics|Terraform Basics]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/08-Practice Questions & Answers|Practice Questions & Answers]]
