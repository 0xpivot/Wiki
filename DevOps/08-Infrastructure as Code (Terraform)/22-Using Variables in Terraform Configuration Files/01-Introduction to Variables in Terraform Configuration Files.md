---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Variables in Terraform Configuration Files

Variables in Terraform configuration files are a fundamental concept that allows for dynamic and reusable infrastructure definitions. By using variables, you can avoid hardcoding values within your Terraform scripts, making them more flexible and adaptable to different environments and use cases. This chapter will delve deeply into the concept of variables in Terraform, explaining their purpose, usage, and benefits, along with practical examples and best practices.

### What Are Variables in Terraform?

In Terraform, variables are placeholders for values that can be set externally. They allow you to abstract specific details of your infrastructure, such as IP addresses, environment-specific settings, or resource names, into configurable parameters. This abstraction makes your Terraform configurations more modular and easier to manage across different environments.

#### Why Use Variables?

Using variables in Terraform offers several key advantages:

1. **Reusability**: You can reuse the same Terraform configuration for different environments (development, staging, production) by passing different values to the variables.
2. **Maintainability**: Hardcoded values can become difficult to manage and update. Variables make it easier to modify values without changing the core configuration.
3. **Security**: Sensitive information can be passed securely through variables, reducing the risk of exposing secrets in your configuration files.

### Defining Variables in Terraform

To define a variable in Terraform, you use the `variable` keyword followed by the variable name and an optional block containing attributes. Here’s a basic example:

```hcl
variable "subnet_cidr_block" {
  description = "The CIDR block for the subnet."
}
```

This defines a variable named `subnet_cidr_block` with a description that explains its purpose.

#### Attributes of Variables

When defining a variable, you can specify several attributes:

- **description**: A human-readable description of the variable.
- **default**: A default value for the variable if none is provided.
- **type**: The data type of the variable (e.g., string, number, list).
- **validation**: A validation rule to ensure the variable meets certain criteria.

Here’s an example with more attributes:

```hcl
variable "subnet_cidr_block" {
  description = "The CIDR block for the subnet."
  default     = "10.0.1.0/24"
  type        = string
  validation {
    condition     = length(regexall("[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}/[0-9]{1,2}", var.subnet_cidr_block)) == 1
    error_message = "Invalid CIDR block format."
  }
}
```

### Using Variables in Terraform

Once a variable is defined, you can reference it in your Terraform configuration using the `var` prefix. For example:

```hcl
resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = var.subnet_cidr_block
}
```

In this example, the `cidr_block` attribute of the `aws_subnet` resource is set to the value of the `subnet_cidr_block` variable.

### Passing Values to Variables

Values can be passed to variables in several ways:

1. **Command Line**: Using the `-var` flag when running `terraform apply`.
    ```sh
    terraform apply -var "subnet_cidr_block=10.0.2.0/24"
    ```

2. **Variable File**: Creating a `.tfvars` file and specifying it with the `-var-file` flag.
    ```hcl
    # variables.tfvars
    subnet_cidr_block = "10. 0.3.0/24"
    ```
    ```sh
    terraform apply -var-file="variables.tfvars"
    ```

3. **Environment Variables**: Setting environment variables prefixed with `TF_VAR_`.
    ```sh
    export TF_VAR_subnet_cidr_block="10.0.4.0/24"
    terraform apply
    ```

### Real-World Example: Reusing Configurations Across Environments

Consider a scenario where you have a Terraform configuration for creating a VPC and subnets. You want to reuse this configuration for both development and production environments, but with different CIDR blocks and other settings.

#### Development Environment

```hcl
# dev.tfvars
subnet_cidr_block = "10.0.1.0/24"
```

#### Production Environment

```hcl
# prod.tfvars
subnet_cidr_block = "10.0.2.0/24"
```

#### Terraform Configuration

```hcl
variable "subnet_cidr_block" {
  description = "The CIDR block for the subnet."
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = var.subnet_cidr_block
}
```

### How to Prevent / Defend Against Misuse of Variables

While variables provide flexibility, they also introduce potential risks if not managed properly. Here are some best practices to ensure secure and effective use of variables:

1. **Validation Rules**: Always validate the input values to ensure they meet the required format and constraints.
2. **Default Values**: Provide sensible default values to avoid errors due to missing inputs.
3. **Sensitive Data Handling**: Use Terraform's built-in mechanisms for handling sensitive data, such as `terraform state rm` for removing sensitive state data.
4. **Access Control**: Restrict access to `.tfvars` files and ensure they are stored securely, especially if they contain sensitive information.

### Pitfalls and Common Mistakes

- **Hardcoding Values**: Avoid hardcoding values that should be dynamic. This reduces the reusability and maintainability of your Terraform configurations.
- **Ignoring Validation**: Failing to validate input values can lead to unexpected behavior and errors.
- **Exposing Sensitive Data**: Ensure that sensitive data is handled securely and not exposed in plain text.

### Conclusion

Variables in Terraform are a powerful feature that enhances the flexibility and reusability of your infrastructure configurations. By understanding how to define, use, and manage variables effectively, you can create robust and secure Terraform configurations that adapt to various environments and use cases.

### Practice Labs

For hands-on practice with Terraform variables, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on using Terraform for infrastructure as code.
- **OWASP Juice Shop**: Provides a comprehensive environment for learning and practicing DevOps security concepts, including Terraform.
- **DVWA (Damn Vulnerable Web Application)**: Useful for understanding the practical application of Terraform in a real-world context.

By engaging with these labs, you can gain deeper insights into the practical aspects of using variables in Terraform and reinforce your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/22-Using Variables in Terraform Configuration Files/00-Overview|Overview]] | [[02-Using Variables in Terraform Configuration Files|Using Variables in Terraform Configuration Files]]
