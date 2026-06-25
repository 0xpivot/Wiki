---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform and AWS Integration

Terraform is an open-source Infrastructure as Code (IaC) tool developed by HashiCorp. It allows users to define and provision infrastructure resources in a declarative manner using a high-level configuration language. Terraform supports a wide range of cloud providers, including Amazon Web Services (AWS), Google Cloud Platform (GCP), Microsoft Azure, and many others. In this chapter, we will focus on setting up and using Terraform to manage AWS infrastructure.

### Why Use Terraform?

Terraform provides several key benefits:

1. **Declarative Configuration**: Users describe their desired infrastructure state in a declarative manner, making it easier to understand and maintain.
2. **Consistency and Reproducibility**: Terraform ensures that the same configuration can be applied consistently across different environments, reducing human error.
3. **Version Control**: Since Terraform configurations are plain text files, they can be stored in version control systems like Git, enabling collaboration and tracking changes.
4. **Multi-Cloud Support**: Terraform supports multiple cloud providers, allowing users to manage hybrid cloud environments seamlessly.

### Setting Up Terraform

Before diving into the specifics of setting up Terraform for AWS, let's go through the installation process across different operating systems.

#### Installation on Linux

To install Terraform on a Linux system, follow these steps:

1. Download the latest version of Terraform from the official HashiCorp website.
2. Extract the downloaded package.
3. Move the `terraform` binary to a directory included in your `PATH`.

```bash
# Download the latest version of Terraform
wget https://releases.hashicorp.com/terraform/1.0.0/terraform_1.0.0_linux_amd64.zip

# Extract the zip file
unzip terraform_1.0.0_linux_amd64.zip

# Move the binary to /usr/local/bin
sudo mv terraform /usr/local/bin/
```

#### Installation on macOS

On macOS, you can use Homebrew to install Terraform:

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Terraform using Homebrew
brew install terraform
```

#### Installation on Windows

For Windows, download the Terraform installer from the official HashiCorp website and run it. Ensure that the installation directory is added to your system's `PATH`.

### Creating a Project Folder

Once Terraform is installed, the next step is to create a project folder where all your Terraform configuration files will reside. Let's create a folder named `Terraform`:

```bash
mkdir Terraform
cd Terraform
```

### Initializing Terraform

Before creating any resources, you need to initialize Terraform. This step downloads the necessary provider plugins and sets up the backend configuration.

```bash
terraform init
```

### Writing Your First Terraform File

Now, let's create a Terraform configuration file that connects to your AWS account and creates a VPC and subnet. We'll start by creating a file named `main.tf` in the `Terraform` folder.

```bash
touch main.tf
```

Open `main.tf` in your preferred text editor. For this example, we'll use Visual Studio Code (VSCode).

### Installing VSCode Plugins

To enhance your development experience, you can install a Terraform plugin for VSCode. There are several options available, but we'll use the official `HashiCorp Terraform Language Support` extension.

1. Open VSCode.
2. Click on the Extensions icon in the left sidebar.
3. Search for `HashiCorp Terraform Language Support`.
4. Click on `Install`.

Alternatively, you can use other plugins like `Terraform` by `Shital Shah`, which also provides syntax highlighting and other features.

### Writing the Terraform Configuration

Let's write the basic Terraform configuration to create a VPC and subnet in your AWS account.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "example-vpc"
  }
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "example-subnet"
  }
}
```

### Explanation of the Configuration

- **Provider Block**: The `provider` block specifies the cloud provider and its configuration. Here, we are using AWS with the `region` set to `us-west-2`.
- **Resource Block**: The `resource` block defines the infrastructure resources to be created. In this case, we are creating an AWS VPC and a subnet within that VPC.
  - `aws_vpc`: Defines a VPC resource with a CIDR block of `10.0.0.0/16`.
  - `aws_subnet`: Defines a subnet resource within the previously created VPC with a CIDR block of `1.0.1.0/24`.

### Applying the Configuration

After writing the configuration, you can apply it using the following command:

```bash
terraform apply
```

This command will prompt you to confirm the changes. Type `yes` to proceed.

### Understanding the Apply Process

The `terraform apply` command performs the following steps:

1. **Plan**: Terraform generates a plan of the actions it will take to achieve the desired state.
2. **Apply**: Terraform applies the plan, creating or updating the specified resources.

### Viewing the Plan

Before applying the changes, you can view the plan using the `terraform plan` command:

```bash
terraform plan
```

This command shows the proposed changes without actually applying them.

### Cleaning Up

To destroy the resources created by Terraform, use the `terraform destroy` command:

```bash
terraform destroy
```

This command will prompt you to confirm the destruction of the resources. Type `yes` to proceed.

### Security Considerations

When working with Terraform and AWS, it's crucial to consider security best practices. Here are some key points:

1. **IAM Roles and Policies**: Ensure that the IAM roles and policies used by Terraform have the minimum necessary permissions.
2. **Environment Variables**: Store sensitive information like access keys and secret keys in environment variables or use AWS credentials profiles.
3. **State Management**: Securely store and manage the Terraform state file to prevent unauthorized access.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable AWS CloudTrail to log API calls made to your AWS account.
- **Monitoring**: Use AWS CloudWatch to monitor the state of your resources and detect any unauthorized changes.

#### Prevention

- **Least Privilege**: Assign IAM roles and policies with the least privilege necessary to perform required tasks.
- **Secure State Storage**: Use AWS S3 with encryption and proper access controls to store the Terraform state file.

#### Secure Coding Fixes

**Vulnerable Code Example**:

```hcl
provider "aws" {
  region = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

**Fixed Code Example**:

```hcl
provider "aws" {
  region = "us-west-2"
  profile = "default"
}
```

In the fixed example, we use an AWS credentials profile instead of hardcoding access keys and secret keys.

### Conclusion

In this chapter, we covered the basics of setting up and using Terraform to manage AWS infrastructure. We discussed the installation process, creating a project folder, initializing Terraform, writing a basic configuration file, and applying the configuration. We also touched on security considerations and provided a clear guide on how to prevent and defend against potential issues.

### Practice Labs

To further solidify your understanding, consider practicing with the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for learning web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training.
- **WebGoat**: An interactive, gamified web application security training tool.

These labs provide practical experience in managing and securing cloud infrastructure using Terraform and other tools.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/15-Terraform Installation And Setup Across Operating Systems/00-Overview|Overview]] | [[02-Introduction to Terraform|Introduction to Terraform]]
