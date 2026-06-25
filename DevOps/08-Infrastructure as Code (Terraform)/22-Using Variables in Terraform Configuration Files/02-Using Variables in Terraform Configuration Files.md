---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Using Variables in Terraform Configuration Files

### Introduction to Variables in Terraform

Variables in Terraform are essential for creating dynamic and reusable infrastructure configurations. They allow you to parameterize your Terraform code, making it more flexible and adaptable to different environments and scenarios. In this section, we will delve into the syntax, usage, and best practices for using variables in Terraform configuration files.

### Syntax of Variables in Terraform

The syntax for defining and referencing variables in Terraform is straightforward and consistent across different types of declarations such as resources, data sources, and variables themselves. Here’s a breakdown of the syntax:

1. **Defining a Variable**:
    ```terraform
    variable "variable_name" {
      description = "A description of the variable"
      type        = string
      default     = "default_value"
    }
    ```

2. **Referencing a Variable**:
    ```terraform
    resource "aws_instance" "example" {
      ami           = "ami-0c94855ba95b798c7"
      instance_type = "t2.micro"
      subnet_id     = var.subnet_id
    }
    ```

In the above example, `var.subnet_id` references the value of the `subnet_id` variable. This consistency in syntax makes it easier to understand and maintain Terraform configurations.

### Assigning Values to Variables

There are several methods to assign values to variables in Terraform:

1. **Using Default Values**:
    ```terraform
    variable "subnet_id" {
      description = "The ID of the subnet"
      type        = string
      default     = "subnet-0123456789abcdef0"
    }
    ```
    By setting a default value, you ensure that the variable has a value even if none is explicitly provided.

2. **Using Environment Variables**:
    You can set environment variables to provide values to Terraform variables. For example:
    ```bash
    export TF_VAR_subnet_id="subnet-0123456789abcdef0"
    terraform apply
    ```

3. **Using `.tfvars` Files**:
    You can create a `.tfvars` file to specify variable values. For example, `variables.tfvars` might look like this:
    ```terraform
    subnet_id = "subnet-1234567890abcdef1"
    ```

4. **Prompting During `terraform apply`**:
    If no value is provided through any of the above methods, Terraform will prompt you to enter a value during the `terraform apply` process. For example:
    ```bash
    $ terraform apply
    var.subnet_id
      Enter a value: subnet-1234567890abcdef1
    ```

### Example: Using Variables in a Real-World Scenario

Let's consider a scenario where we are configuring a VPC and a subnet using Terraform. We will define a variable for the CIDR block and use it in our resource definitions.

#### Step 1: Define the Variable

```terraform
variable "cidr_block" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}
```

#### Step 2: Use the Variable in Resource Definitions

```terraform
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.cidr_block
  availability_zone = "us-west-2a"
}
```

#### Step 3: Apply the Configuration

When you run `terraform apply`, Terraform will either use the default value or prompt you to enter a value if no other method is used.

### Pitfalls and Best Practices

#### Common Mistakes

1. **Not Providing a Default Value**: If no default value is provided and no other method is used to assign a value, Terraform will prompt for input, which can be disruptive in automated workflows.
2. **Incorrect Data Types**: Ensure that the data type specified in the variable definition matches the type of the value being assigned.
3. **Overusing Variables**: While variables are powerful, overusing them can make your Terraform configuration harder to read and maintain.

#### Best Practices

1. **Use Descriptive Names**: Choose meaningful names for your variables to improve readability.
2. **Document Your Variables**: Provide clear descriptions for each variable to help others understand its purpose.
3. **Use Default Values Wisely**: Set default values where appropriate to avoid prompting for input during automated deployments.
4. **Validate Input**: Use validation rules to ensure that the values assigned to variables meet certain criteria.

### Real-World Examples and Security Implications

#### Example: CVE-2021-32782

CVE-2021-32782 was a critical vulnerability in Terraform that allowed an attacker to execute arbitrary code by manipulating the values of variables. This underscores the importance of validating and sanitizing input values.

#### Secure Coding Practices

To prevent such vulnerabilities, follow these secure coding practices:

1. **Input Validation**: Always validate the input values of variables to ensure they meet expected criteria.
2. **Least Privilege Principle**: Limit the permissions granted to the Terraform execution context to minimize potential damage.
3. **Regular Updates**: Keep Terraform and its plugins up to date to benefit from the latest security patches.

### How to Prevent / Defend

#### Detection

1. **Static Analysis Tools**: Use tools like `tfsec` to scan your Terraform code for security issues.
2. **Code Reviews**: Conduct regular code reviews to catch potential security vulnerabilities.

#### Prevention

1. **Validation Rules**: Implement validation rules for variables to ensure they meet specific criteria.
2. **Environment-Specific Configurations**: Use separate `.tfvars` files for different environments to avoid hardcoding sensitive information.

#### Secure-Coding Fixes

Here’s an example of how to implement secure coding practices:

##### Vulnerable Code
```terraform
variable "subnet_id" {
  description = "The ID of the subnet"
  type        = string
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"
  subnet_id     = var.subnet_id
}
```

##### Secure Code
```terraform
variable "subnet_id" {
  description = "The ID of the subnet"
  type        = string
  validation {
    condition     = length(var.subnet_id) == 20
    error_message = "Subnet ID must be exactly 20 characters long."
  }
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"
  subnet_id     = var.subnet_id
}
```

### Conclusion

Using variables in Terraform is a fundamental practice that enhances the flexibility and reusability of your infrastructure configurations. By following best practices and implementing secure coding techniques, you can ensure that your Terraform configurations are robust and secure.

### Practice Labs

For hands-on experience with using variables in Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of DevOps and infrastructure as code.
- **OWASP Juice Shop**: Provides a web application with numerous security vulnerabilities, including those related to infrastructure as code.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for security testing and training purposes.

These labs will help you gain practical experience in using variables effectively and securely in Terraform configurations.

---
<!-- nav -->
[[01-Introduction to Variables in Terraform Configuration Files|Introduction to Variables in Terraform Configuration Files]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/22-Using Variables in Terraform Configuration Files/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/22-Using Variables in Terraform Configuration Files/03-Practice Questions & Answers|Practice Questions & Answers]]
