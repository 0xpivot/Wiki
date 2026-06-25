---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Web Server Configuration in DevOps

In the realm of DevOps, configuring web servers is a critical task that requires a deep understanding of infrastructure-as-code (IAC) principles and tools such as Terraform. This chapter will delve into the intricacies of configuring a web server using Terraform, focusing on parameterizing various components and ensuring the configuration is flexible and secure.

### Parameterization in Terraform

Parameterization is a fundamental concept in Terraform that allows you to make your infrastructure definitions more dynamic and reusable. By parameterizing your configurations, you can easily adapt your infrastructure to different environments and scenarios without having to modify the core code.

#### Key Concepts

- **Variables**: These are placeholders that can be assigned values at runtime. They allow you to customize your infrastructure without changing the underlying code.
- **Inputs**: Inputs are the actual values provided to the variables. These can be hardcoded within the configuration or passed dynamically when the module is declared.
- **Outputs**: Outputs are the results of the Terraform execution that can be used in other parts of the configuration or exported for further processing.

### Example: Parameterizing a Web Server Configuration

Let's consider a scenario where we are configuring a web server using Terraform. We will parameterize several components such as the server key, public key location, instance type, AMI, subnet ID, security group ID, availability zone, and entry script.

```hcl
variable "server_key" {
  description = "The SSH key to use for the server."
  type        = string
}

variable "public_key_location" {
  description = "The location of the public key."
  type        = string
}

variable "instance_type" {
  description = "The type of EC2 instance to launch."
  type        = string
  default     = "t2.micro"
}

variable "ami" {
  description = "The Amazon Machine Image (AMI) to use."
  type        = string
}

variable "subnet_id" {
  description = "The subnet ID for the EC2 instance."
  type        = string
}

variable "security_group_id" {
  description = "The security group ID for the EC2 instance."
  type        = string
}

variable "availability_zone" {
  description = "The availability zone for the EC2 instance."
  type        = string
}

variable "entry_script_path" {
  description = "The path to the entry script to execute on the server."
  type        = string
}
```

### Using Variables in the Configuration

Once the variables are defined, we can use them in our Terraform configuration to create the web server. Here’s an example of how these variables might be used:

```hcl
resource "aws_instance" "web_server" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = var.server_key
  subnet_id     = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  availability_zone = var.availability_zone

  user_data = file(var.entry_script_path)
}
```

### Parameterizing External Modules

If you are using external modules, you need to ensure that the parameters are correctly passed to the module. For example, if you have a module defined elsewhere, you would pass the variables as inputs when declaring the module.

```hcl
module "web_server_module" {
  source = "./modules/web_server"

  server_key            = var.server_key
  public_key_location   = var.public_key_location
  instance_type         = var.instance_type
  ami                   = var.ami
  subnet_id             = var.subnet_id
  security_group_id     = var.security_group_id
  availability_zone     = var.availability_zone
  entry_script_path     = var.entry_script_path
}
```

### Hardcoding vs. Parameterizing Values

Deciding whether to hardcode or parameterize values depends on the context and requirements of your project. Here are some considerations:

- **Hardcoding**: Useful for values that are unlikely to change across different environments. However, this approach reduces flexibility and reusability.
- **Parameterizing**: Ideal for values that may vary between environments or require dynamic assignment. This approach enhances flexibility and maintainability.

### Real-World Examples and Best Practices

#### Recent CVEs and Breaches

One notable example is the CVE-2021-3560, which affected the Amazon Elastic Compute Cloud (EC2) service. This vulnerability allowed unauthorized access to EC2 instances due to misconfigured security groups. Proper parameterization and validation of security group IDs can help mitigate such risks.

#### Secure Coding Practices

To ensure your web server configuration is secure, follow these best practices:

- **Validate Inputs**: Ensure that all input values are validated before being used in the configuration.
- **Use Strong Authentication Mechanisms**: Utilize strong SSH keys and secure key management practices.
- **Limit Access**: Restrict access to the web server using appropriate security group rules and IAM policies.

### How to Prevent / Defend

#### Detection

Regularly audit your Terraform configurations and infrastructure to identify potential vulnerabilities. Tools like `tfsec` and `trivy` can help detect insecure configurations and dependencies.

#### Prevention

- **Secure Key Management**: Use a secure key management system to store and manage SSH keys.
- **Least Privilege Principle**: Assign the minimum necessary permissions to users and services.
- **Automated Testing**: Implement automated testing and validation processes to catch configuration errors early.

#### Secure-Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**

```hcl
resource "aws_instance" "web_server" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"
  key_name      = "my-key-pair"
  subnet_id     = "subnet-12345678"
  vpc_security_group_ids = ["sg-12345678"]
  availability_zone = "us-west-2a"

  user_data = file("path/to/entry-script.sh")
}
```

**Secure Configuration**

```hcl
variable "server_key" {
  description = "The SSH key to use for the server."
  type        = string
}

variable "public_key_location" {
  description = "The location of the public key."
  type        = string
}

variable "instance_type" {
  description = "The type of EC2 instance to launch."
  type        = string
  default     = "t2.micro"
}

variable "ami" {
  description = "The Amazon Machine Image (AMI) to use."
  type        = string
}

variable "subnet_id" {
  description = "The subnet ID for the EC2 instance."
  type        = string
}

variable "security_group_id" {
  description = "The security group ID for the EC2 instance."
  type        = string
}

variable "availability_zone" {
  description =  "The availability zone for the EC2 instance."
  type        = string
}

variable "entry_script_path" {
  description = "The path to the entry script to execute on the server."
  type        = string
}

resource "aws_instance" "web_server" {
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = var.server_key
  subnet_id     = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  availability_zone = var.availability_zone

  user_data = file(var.entry_script_path)
}
```

### Conclusion

Parameterizing your web server configuration in Terraform is crucial for maintaining flexibility, security, and reusability. By following best practices and using secure coding techniques, you can ensure that your infrastructure remains robust and resilient against potential threats.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.
- **WebGoat**: An interactive web application designed to teach web application security lessons.

These labs provide practical experience in configuring and securing web servers, making them invaluable resources for mastering DevOps practices.

---
<!-- nav -->
[[04-Introduction to Web Server Configuration Using Terraform|Introduction to Web Server Configuration Using Terraform]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/22-Web Server Configuration Module Extraction/00-Overview|Overview]] | [[06-Introduction to Web Server Configuration with Terraform|Introduction to Web Server Configuration with Terraform]]
