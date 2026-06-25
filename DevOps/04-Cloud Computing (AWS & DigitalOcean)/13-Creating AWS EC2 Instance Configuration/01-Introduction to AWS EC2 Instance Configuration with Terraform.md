---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS EC2 Instance Configuration with Terraform

In this section, we delve into the process of creating an AWS EC2 instance using Terraform, focusing specifically on handling sensitive information such as SSH public keys. This is crucial for maintaining security and flexibility in your infrastructure as code (IaC) setup.

### Background Theory

Terraform is an open-source infrastructure as code (IaC) tool that allows you to safely and predictably create, change, and improve infrastructure. It enables you to define your infrastructure in declarative configuration files, which are written in the HashiCorp Configuration Language (HCL).

AWS EC2 instances are virtual servers in the cloud that allow you to run applications and services. To securely access these instances, SSH (Secure Shell) is commonly used, requiring the use of SSH keys.

### Handling Sensitive Information in Terraform

When working with Terraform, it is essential to handle sensitive information carefully. One common piece of sensitive data is the SSH public key, which is used to authenticate users to the EC2 instances.

#### Why Not Check Public Keys into the Repository?

Checking public keys into a version control system like Git is generally a bad practice due to several reasons:

1. **Security Risks**: Public keys can be used to gain unauthorized access if they fall into the wrong hands.
2. **User-Specific Data**: Each user typically has their own unique public key, making it impractical to store them centrally.
3. **Configuration Management**: Users should be able to manage their own keys independently, without needing to modify shared configuration files.

### Extracting Public Key into a Variable

To address these issues, we can extract the public key into a variable that each user can configure locally. This approach ensures that sensitive data remains out of the shared repository.

#### Step-by-Step Process

1. **Define the Variable**:
   - In your `variables.tf` file, define a variable for the public key.
   
   ```hcl
   variable "public_key" {
     description = "SSH public key for accessing the EC2 instance"
     type        = string
   }
   ```

2. **Reference the Variable**:
   - In your main Terraform configuration file, reference the variable where the public key is needed.

   ```hcl
   resource "aws_instance" "example" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.micro"

     key_name = var.public_key
   }
   ```

3. **Set the Variable Value**:
   - Each user can set the value of this variable in their local `terraform.tfvars` file.

   ```hcl
   public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@example.com"
   ```

### Using File References for Public Keys

Another approach is to reference the file location of the public key instead of embedding the key itself. This method is more flexible and secure.

#### Step-by-Step Process

1. **Define the Variable for File Location**:
   - Define a variable for the file location of the public key.

   ```hcl
   variable "public_key_location" {
     description = "File location of the SSH public key"
     type        = string
   }
   ```

2. **Read from the File**:
   - Use the `file` function to read the content of the file.

   ```hcl
   resource "aws_instance" "example" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.micro"

     key_name = file(var.public_key_location)
   }
   ```

3. **Set the Variable Value**:
   - Each user can set the value of this variable in their local `terraform.tfvars` file.

   ```hcl
   public_key_location = "/home/user/.ssh/id_rsa.pub"
   ```

### Complete Example

Here is a complete example of how to set up an AWS EC2 instance using Terraform with a public key referenced from a file.

#### `variables.tf`

```hcl
variable "public_key_location" {
  description = "File location of the SSH public key"
  type        = string
}
```

#### `main.tf`

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  key_name = file(var.public_key_location)
}
```

#### `terraform.tfvars`

```hcl
public_key_location = "/home/user/.ssh/id_rsa.pub"
```

### Pitfalls and Common Mistakes

1. **Hardcoding Public Keys**: Avoid hardcoding public keys directly in your Terraform configuration files.
2. **Incorrect File Paths**: Ensure that the file paths provided are correct and accessible.
3. **Permissions Issues**: Make sure that the file containing the public key has the appropriate permissions to be read by the Terraform process.

### How to Prevent / Defend

#### Detection

- **Code Review**: Regularly review your Terraform code to ensure that sensitive information is not hardcoded.
- **Static Analysis Tools**: Use tools like `tfsec` to scan your Terraform code for security issues.

#### Prevention

- **Environment Variables**: Use environment variables to pass sensitive information to Terraform.
- **Secrets Management**: Utilize secrets management tools like AWS Secrets Manager or HashiCorp Vault to store and manage sensitive data.

#### Secure Coding Fixes

##### Vulnerable Code

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  key_name = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@example.com"
}
```

##### Secure Code

```hcl
variable "public_key_location" {
  description = "File location of the SSH public key"
  type        = string
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  key_name = file(var.public_key_location)
}
```

### Real-World Examples

#### Recent Breaches

- **CVE-2021-44228 (Log4j)**: Although not directly related to SSH keys, this breach highlights the importance of securing sensitive data. Similar principles apply to ensuring that SSH keys are not exposed.

#### Real-World Applications

- **GitHub Actions**: Many organizations use GitHub Actions to automate their CI/CD pipelines. Ensuring that SSH keys are managed securely is critical to preventing unauthorized access.

### Hands-On Labs

For practical experience, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on managing AWS resources securely.
- **flaws.cloud**: A cloud security training platform that provides hands-on labs for various cloud security topics, including AWS EC2.

### Conclusion

Handling sensitive information like SSH public keys in Terraform requires careful consideration to maintain security and flexibility. By extracting public keys into variables and referencing file locations, you can ensure that your infrastructure as code setup remains secure and manageable.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[02-Introduction to AWS EC2 Instance Configuration|Introduction to AWS EC2 Instance Configuration]]
