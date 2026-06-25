---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Web Server Configuration Using Terraform

In the realm of DevOps, automation tools like Terraform play a pivotal role in managing infrastructure as code (IaC). This chapter delves into the intricacies of configuring web servers using Terraform, focusing on the importance of variable management and referencing. By the end of this chapter, you will understand how to effectively manage and reference variables within Terraform modules, ensuring your infrastructure remains consistent and maintainable.

### Background Theory

Terraform is an open-source IaC tool developed by HashiCorp. It allows you to define and provision infrastructure resources using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform uses a provider-based architecture, where providers are plugins that interact with cloud platforms or other services to create and manage resources.

#### Variables in Terraform

Variables in Terraform are placeholders for values that can be passed into your Terraform configurations. They allow you to parameterize your configurations, making them more flexible and reusable. Variables can be defined in several ways:

1. **Variable Declaration**: Define variables in your Terraform configuration files using the `variable` keyword.
2. **Variable Assignment**: Assign values to variables either directly in the configuration or via external sources such as environment variables or `.tfvars` files.
3. **Variable References**: Reference variables within your configuration using the `${var.variable_name}` syntax.

### Variable Management in Terraform Modules

In Terraform, modules are reusable components that encapsulate complex configurations. Managing variables within modules ensures consistency and reduces redundancy. Let’s explore how to manage and reference variables within Terraform modules.

#### Example: Defining Variables in the Root Module

Consider a scenario where you are setting up a web server in an AWS environment. You might have several variables defined in your root module, such as `vpc_id`, `app_prefix`, `image_name`, `public_key_location`, and `instance_type`.

```hcl
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "app_prefix" {
  description = "Prefix for application resources"
  type        = string
}

variable "image_name" {
  description = "AMI image name"
  type        = string
}

variable "public_key_location" {
  description = "Location of the public SSH key"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}
```

### Referencing Variables in Child Modules

When defining child modules, you can reference variables from the parent module. This ensures that the same values are used consistently across different parts of your infrastructure.

```hcl
module "web_server" {
  source = "./modules/web_server"

  vpc_id           = var.vpc_id
  app_prefix       = var.app_prefix
  image_name       = var.image_name
  public_key_location = var.public_key_location
  instance_type    = var.instance_type
}
```

### Benefits of Referencing Variables

Referencing variables in Terraform provides several benefits:

1. **Consistency**: Ensures that the same values are used across different modules, reducing the risk of inconsistencies.
2. **Maintainability**: Simplifies maintenance by allowing you to update values in a single place rather than multiple locations.
3. **Reusability**: Makes your modules more reusable by abstracting away specific values.

### Real-World Example: AWS VPC Setup

Let’s consider a real-world example where you are setting up a VPC in AWS using Terraform. You might have a `variables.tf` file in your root module that defines the necessary variables.

```hcl
# variables.tf
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "app_prefix" {
  description = "Prefix for application resources"
  type        = string
}

variable "image_name" {
  description = "AMI image name"
  type        = string
}

variable "public_key_location" {
  description = "Location of the public SSH key"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}
```

In your main Terraform configuration file (`main.tf`), you can reference these variables and pass them to child modules.

```hcl
# main.tf
module "web_server" {
  source = "./modules/web_server"

  vpc_id           = var.vpc_id
  app_prefix       = var.app_prefix
  image_name       = var.image_name
  public_key_location = var.public_key_location
  instance_type    = var.instance_type
}
```

### Complete Example: Full Terraform Configuration

Here is a complete example of a Terraform configuration that sets up a web server in an AWS VPC.

```hcl
# variables.tf
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "app_prefix" {
  description = "Prefix for application resources"
  type        = string
}

variable "image_name" {
  description = "AMI image name"
  type        = string
}

variable "public_key_location" {
  description = "Location of the public SSH key"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}

# main.tf
module "web_server" {
  source = "./modules/web_server"

  vpc_id           = var.vpc_id
  app_prefix       = var.app_prefix
  image_name       = var.image_name
  public_key_location = var.public_key_location
  instance_type    = var.instance_type
}
```

### How to Prevent / Defend

#### Detection

To ensure that your Terraform configurations are correctly referencing variables, you can use Terraform’s built-in validation features. Additionally, you can run `terraform validate` to check for any syntax errors or misconfigurations.

#### Prevention

1. **Use Consistent Naming Conventions**: Ensure that variable names are consistent and descriptive.
2. **Document Your Variables**: Clearly document the purpose and usage of each variable in your `variables.tf` file.
3. **Use Default Values**: Provide default values for optional variables to avoid errors due to missing values.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of your Terraform configuration to ensure that variables are correctly referenced and managed.

**Vulnerable Version**

```hcl
# main.tf
module "web_server" {
  source = "./modules/web_server"

  vpc_id           = "vpc-12345678"
  app_prefix       = "myapp"
  image_name       = "ami-12345678"
  public_key_location = "/path/to/public/key"
  instance_type    = "t2.micro"
}
```

**Secure Version**

```hcl
# variables.tf
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "app_prefix" {
  description = "Prefix for application resources"
  type        = string
}

variable "image_name" {
  description = "AMI image name"
  type        = string
}

variable "public_key_location" {
  description = "Location of the public SSH key"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}

# main.tf
module "web_server" {
  source = "./modules/web_server"

  vpc_id           = var.vpc_id
  app_prefix       = var.app_prefix
  image_name       = var.image_name
  public_key_location = var.public_key_location
  instance_type    = var.instance_type
}
```

### Conclusion

Effective management and referencing of variables in Terraform modules are crucial for maintaining a consistent and maintainable infrastructure. By following best practices and using secure coding techniques, you can ensure that your Terraform configurations are robust and reliable.

### Practice Labs

For hands-on practice with Terraform and web server configuration, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on infrastructure setup.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in setting up and securing web servers using Terraform and other DevOps tools.

---
<!-- nav -->
[[03-Introduction to Web Server Configuration Using Terraform Modules|Introduction to Web Server Configuration Using Terraform Modules]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/22-Web Server Configuration Module Extraction/00-Overview|Overview]] | [[05-Introduction to Web Server Configuration in DevOps|Introduction to Web Server Configuration in DevOps]]
