---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Modularizing Terraform Configuration with Modules

### Introduction to Terraform Modules

Terraform is an infrastructure as code (IaC) tool that allows you to define and provision your infrastructure using declarative configuration files. One of the key features of Terraform is its ability to modularize configurations, which helps in managing complex infrastructures more efficiently. A **module** in Terraform is a reusable component that encapsulates a set of resources and their associated configurations. This modularity allows you to break down large configurations into smaller, manageable pieces, making it easier to maintain and scale your infrastructure.

#### Why Use Modules?

Using modules in Terraform offers several benefits:

1. **Reusability**: You can reuse modules across different environments and projects, reducing duplication of effort.
2. **Encapsulation**: Modules encapsulate the details of resource creation, allowing you to focus on higher-level abstractions.
3. **Maintainability**: Smaller, modular configurations are easier to understand and maintain than monolithic configurations.
4. **Scalability**: By breaking down configurations into modules, you can scale your infrastructure more easily as your needs grow.

### Creating a Module

To create a module in Terraform, you typically follow these steps:

1. **Create a Directory Structure**: Each module should reside in its own directory. This directory contains the Terraform configuration files for the module.
2. **Define Resources**: Inside the module directory, you define the resources that the module will manage. These resources can include AWS instances, VPCs, security groups, etc.
3. **Export Outputs**: Modules can export outputs, which are values that can be used by other parts of your Terraform configuration.

Let's walk through an example of creating a module for a simple web server setup.

#### Example: Web Server Module

Suppose you want to create a module that sets up a web server with the following components:
- An EC2 instance
- A security group with appropriate inbound rules
- A key pair for SSH access

Here’s how you might structure the module:

```markdown
web-server/
├── main.tf
├── variables.tf
└── outputs.tf
```

#### `main.tf` (Resource Definitions)

```hcl
resource "aws_instance" "web_server" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = aws_key_pair.web_server.key_name

  vpc_security_group_ids = [aws_security_group.web_server.id]

  tags = {
    Name = "WebServer"
  }
}

resource "aws_key_pair" "web_server" {
  key_name   = "web_server_key"
  public_key = file(var.public_key_path)
}

resource "aws_security_group" "web_server" {
  name        = "web_server_sg"
  description = "Security group for web server"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

#### `variables.tf` (Input Variables)

```hcl
variable "ami" {
  description = "The AMI ID to use for the web server."
  type        = string
}

variable "instance_type" {
  description = "The instance type to use for the web server."
  type        = string
}

variable "public_key_path" {
  description = "Path to the public SSH key."
  type        = string
}
```

#### `outputs.tf` (Output Values)

```hcl
output "web_server_public_ip" {
  value = aws_instance.web_server.public_ip
}

output "web_server_private_ip" {
  value = aws_instance.web_server.private_ip
}
```

### Using a Module

Once you have defined a module, you can use it in your main Terraform configuration. Here’s an example of how to use the `web-server` module:

```hcl
module "web_server" {
  source = "./web-server"

  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  public_key_path = "/path/to/public_key.pub"
}
```

### Reusing Existing Modules

For common use cases, Terraform provides a registry of pre-built modules that you can reuse. The Terraform Registry is a repository of community-contributed modules that can be used directly in your configurations.

#### Example: Reusing a VPC Module

Suppose you want to create a VPC with a set of subnets, an internet gateway, and a route table. Instead of defining these resources manually, you can use a pre-built VPC module from the Terraform Registry.

1. **Find a Suitable Module**: Navigate to the Terraform Registry and search for a VPC module.
2. **Use the Module**: Include the module in your Terraform configuration.

Here’s an example of using a VPC module from the Terraform Registry:

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}
```

### Real-World Examples and Pitfalls

#### Real-World Example: VPC Module Usage

Consider a scenario where you are setting up a multi-tier application with a VPC, subnets, and a NAT gateway. Using a pre-built VPC module can significantly simplify this process.

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}
```

#### Pitfall: Overcomplicating Modules

One common pitfall when working with Terraform modules is overcomplicating them. It’s important to keep modules focused and modular. Avoid including too many unrelated resources in a single module, as this can make the module harder to understand and maintain.

#### How to Prevent / Defend

1. **Keep Modules Simple**: Ensure each module focuses on a specific task or set of related tasks.
2. **Document Inputs and Outputs**: Clearly document the input variables and output values for each module.
3. **Test Modules Independently**: Test modules independently to ensure they work as expected before integrating them into larger configurations.
4. **Use Version Control**: Keep your modules in version control to track changes and collaborate effectively.

### Conclusion

Modularizing Terraform configurations with modules is a powerful technique for managing complex infrastructures. By breaking down configurations into smaller, reusable components, you can improve maintainability, scalability, and reusability. Whether you create your own modules or reuse existing ones from the Terraform Registry, understanding how to effectively use modules is crucial for any DevOps practitioner.

### Practice Labs

For hands-on practice with Terraform modules, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also includes modules for setting up infrastructure.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be deployed using Terraform modules.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training, deployable with Terraform.
- **Kubernetes Goat**: A Kubernetes-based lab for practicing security and deployment techniques, which can involve Terraform modules for infrastructure setup.

These labs provide practical experience in using Terraform modules to set up and manage infrastructure, reinforcing the concepts covered in this chapter.

---
<!-- nav -->
[[01-Introduction to Terraform Modules|Introduction to Terraform Modules]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/12-Modularizing Terraform Configuration With Modules/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/12-Modularizing Terraform Configuration With Modules/03-Practice Questions & Answers|Practice Questions & Answers]]
