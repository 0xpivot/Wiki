---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using modules in Terraform configurations.**

Modules in Terraform serve to break down large, monolithic configurations into smaller, reusable pieces. This modular approach helps manage complexity, making it easier to maintain and scale infrastructure as it grows. By encapsulating related resources into logical groups, modules promote reusability and modularity, similar to how functions are used in programming. This allows teams to avoid duplicating code and to easily manage changes by updating a single module rather than scattered code across a large configuration.

**Q2. How would you create a module for an EC2 instance in Terraform? What resources might you include in this module?**

To create a module for an EC2 instance, you would first define a directory structure for the module. Within this directory, you would include a `main.tf` file to define the resources. A typical EC2 instance module might include:

- An AWS EC2 instance resource.
- An AWS key pair resource for SSH access.
- An AWS security group resource to control inbound traffic.
- Any necessary IAM roles or policies.

Here’s an example of what the `main.tf` might look like:

```hcl
resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = var.instance_type

  key_name = aws_key_pair.key.id
  vpc_security_group_ids = [aws_security_group.web.id]
}

resource "aws_key_pair" "key" {
  key_name   = var.key_name
  public_key = var.public_key
}

resource "aws_security_group" "web" {
  name        = var.security_group_name
  description = "Allow HTTP access"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

The module would also include a `variables.tf` file to define input variables and an `outputs.tf` file to expose relevant outputs such as the instance ID or public IP address.

**Q3. Why is it important to properly abstract resources within a module? Provide an example.**

Properly abstracting resources within a module ensures that the module is both reusable and maintainable. Abstracting resources means grouping them into logical units that perform specific tasks, rather than creating modules for single resources, which can lead to unnecessary overhead and complexity.

For example, instead of creating a module for just an EC2 instance, it is better to create a module that includes the EC2 instance along with its associated key pair, security group, and possibly additional resources like volumes or IAM roles. This way, the module represents a complete, functional unit (like a web server), which can be reused across different environments or projects without needing to redefine the same set of resources repeatedly.

**Q4. How do you use pre-existing modules from the Terraform Registry in your project?**

Using pre-existing modules from the Terraform Registry involves a few steps:

1. **Identify the Module**: Browse the Terraform Registry to find a module that suits your needs. For example, you might choose the `terraform-aws-modules/vpc/aws` module for creating a VPC.

2. **Include the Module in Your Project**: Add the module to your Terraform configuration using the `module` block. Specify the source of the module and any required input variables.

3. **Define Input Variables**: Set the input variables required by the module. These variables are typically documented in the module’s README file.

4. **Initialize Providers**: Ensure that the necessary providers are initialized. When you run `terraform init`, Terraform will automatically install any providers required by the module.

Here’s an example of how to include the `terraform-aws-modules/vpc/aws` module:

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
}
```

5. **Use Outputs from the Module**: Access the outputs of the module to use the created resources in other parts of your configuration. For example, you might use the VPC ID and subnet IDs to create other resources like EC2 instances.

By following these steps, you can leverage existing modules to streamline your Terraform configurations and reduce development time.

**Q5. What are the benefits of using Terraform modules compared to writing everything in a single configuration file?**

Using Terraform modules offers several benefits over writing everything in a single configuration file:

1. **Reusability**: Modules can be reused across different projects or environments, reducing duplication and maintenance effort.

2. **Modularity**: Breaking down configurations into smaller, manageable pieces improves readability and maintainability.

3. **Encapsulation**: Modules encapsulate logic and resources, making it easier to understand and modify specific parts of the infrastructure without affecting others.

4. **Abstraction**: Modules can abstract away complex configurations, providing simpler interfaces through input variables and outputs.

5. **Collaboration**: Pre-built modules from the Terraform Registry can be shared and used by different teams, promoting collaboration and standardization.

6. **Scalability**: As infrastructure grows, using modules helps manage complexity and scale more effectively.

For example, consider a scenario where you need to deploy multiple VPCs across different regions. Instead of writing separate configurations for each region, you can use a VPC module and simply pass in different input variables for each deployment. This approach simplifies management and reduces the risk of errors.

**Q6. How do you handle dependencies between modules in Terraform?**

Handling dependencies between modules in Terraform involves ensuring that the outputs of one module are correctly referenced as inputs in another module. This can be achieved by using Terraform’s built-in mechanisms for managing dependencies.

For example, suppose you have a module for creating a VPC and another module for creating an EC2 instance. The EC2 module might require the VPC ID and subnet IDs, which are outputs of the VPC module.

Here’s how you can handle this:

1. **Define Outputs in the VPC Module**: Ensure that the VPC module defines outputs for the VPC ID and subnet IDs.

2. **Reference Outputs in the EC2 Module**: Use the outputs from the VPC module as inputs in the EC2 module.

Here’s an example:

VPC Module (`modules/vpc/main.tf`):

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_ids" {
  value = aws_subnet.main.*.id
}
```

EC2 Module (`modules/ec2/main.tf`):

```hcl
variable "vpc_id" {}
variable "subnet_ids" {}

resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.web.id]
  subnet_id              = var.subnet_ids[0]
}
```

Main Configuration (`main.tf`):

```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "ec2" {
  source = "./modules/ec2"

  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.subnet_ids
  ami         = "ami-0c94855ba95c71c99"
  instance_type = "t2.micro"
}
```

By structuring your modules and referencing outputs appropriately, you ensure that dependencies are managed correctly, allowing Terraform to apply the configuration in the right order.

**Q7. Can you give an example of a real-world scenario where using Terraform modules significantly improved infrastructure management?**

A real-world example where Terraform modules significantly improved infrastructure management is the adoption of Terraform modules at Netflix. Netflix manages a vast and complex infrastructure, including multiple AWS accounts, VPCs, and various services.

By adopting Terraform modules, Netflix was able to:

1. **Standardize Infrastructure**: Create standardized modules for common infrastructure components like VPCs, security groups, and IAM roles, ensuring consistency across different teams and projects.

2. **Improve Reusability**: Leverage pre-built modules from the Terraform Registry and internal modules, reducing the need to reinvent the wheel and speeding up development cycles.

3. **Enhance Maintainability**: Break down large configurations into smaller, manageable modules, making it easier to understand and modify specific parts of the infrastructure.

4. **Promote Collaboration**: Share and reuse modules across different teams, fostering collaboration and standardization.

For instance, Netflix uses a module for creating VPCs, which encapsulates the creation of VPCs, subnets, route tables, and internet gateways. This module is reused across different environments, ensuring consistency and reducing the risk of errors.

By leveraging Terraform modules, Netflix has been able to manage its complex infrastructure more efficiently, improving both the speed and reliability of deployments.

---
<!-- nav -->
[[02-Modularizing Terraform Configuration with Modules|Modularizing Terraform Configuration with Modules]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/12-Modularizing Terraform Configuration With Modules/00-Overview|Overview]]
