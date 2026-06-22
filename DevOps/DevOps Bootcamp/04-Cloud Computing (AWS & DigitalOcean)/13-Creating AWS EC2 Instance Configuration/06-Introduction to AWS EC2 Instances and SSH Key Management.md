---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS EC2 Instances and SSH Key Management

In the realm of DevOps, managing infrastructure as code (IaC) is crucial for maintaining consistency, reliability, and security. One of the primary services used for deploying and managing compute resources in the cloud is Amazon Web Services (AWS) Elastic Compute Cloud (EC2). This chapter delves into the process of creating an EC2 instance using Terraform, focusing on SSH key management and configuration.

### Background Theory

#### What is AWS EC2?

Amazon EC2 is a web service that provides resizable compute capacity in the cloud. It allows you to launch virtual servers, known as instances, with various configurations and operating systems. These instances can be managed through the AWS Management Console, command-line tools, or programmatically via APIs.

#### What is Terraform?

Terraform is an open-source infrastructure as code (IaC) tool created by HashiCorp. It enables you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud, and more.

### SSH Key Management

SSH (Secure Shell) keys are used to authenticate users to remote servers securely. They consist of a public key and a private key pair. The public key is stored on the server, while the private key is kept securely on the client machine.

#### Why Use SSH Keys?

Using SSH keys enhances security compared to traditional password-based authentication. Here’s why:

1. **Stronger Authentication**: SSH keys provide stronger cryptographic authentication than passwords.
2. **Automated Login**: SSH keys allow automated login, which is essential for scripts and continuous integration/continuous deployment (CI/CD) pipelines.
3. **Key Rotation**: SSH keys can be rotated periodically, enhancing security.

#### How SSH Keys Work

When you attempt to SSH into a server, the following steps occur:

1. **Client Request**: The client sends a request to the server to establish an SSH connection.
2. **Server Response**: The server responds with its public key.
3. **Client Verification**: The client verifies the server’s public key.
4. **Authentication**: The client uses its private key to generate a signature, which is sent to the server.
5. **Server Validation**: The server validates the signature using the corresponding public key.

### SSH Key Management in AWS EC2

#### Creating an SSH Key Pair

To create an SSH key pair in AWS, follow these steps:

1. **Generate Key Pair**: Use the `ssh-keygen` command to generate a new key pair.
    ```bash
    ssh-keygen -t rsa -b 2048 -f mykeypair
    ```
    This command generates a new RSA key pair with a 2048-bit length and saves it to `mykeypair`.

2. **Upload Public Key to AWS**: Upload the public key (`mykeypair.pub`) to AWS using the AWS Management Console or the AWS CLI.
    ```bash
    aws ec2 import-key-pair --key-name mykeypair --public-key-material file://mykeypair.pub
    ```

3. **Store Private Key Securely**: Store the private key (`mykeypair`) securely in a directory such as `~/.ssh`.
    ```bash
    chmod 400 ~/.ssh/mykeypair
    ```

### Associating SSH Key with EC2 Instance Using Terraform

#### Terraform Configuration

To create an EC2 instance and associate an SSH key using Terraform, you need to define the necessary resources in a `.tf` file.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_key_pair" "example" {
  key_name   = "server_key"
  public_key = file("~/.ssh/mykeypair.pub")
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  key_name = aws_key_pair.example.key_name

  tags = {
    Name = "dev_server"
  }
}
```

#### Explanation of the Configuration

1. **Provider Block**: Specifies the AWS provider and the region.
2. **aws_key_pair Resource**: Defines the SSH key pair to be used.
    - `key_name`: The name of the key pair.
    - `public_key`: The path to the public key file.
3. **aws_instance Resource**: Defines the EC2 instance.
    - `ami`: The Amazon Machine Image (AMI) ID.
    - `instance_type`: The type of instance.
    - `key_name`: References the key pair defined earlier.
    - `tags`: Tags to be applied to the instance.

### Running Terraform Commands

#### Terraform Plan

Before applying the configuration, run `terraform plan` to see the changes that will be made.

```bash
terraform plan
```

This command outputs a detailed plan of the actions Terraform will take. If there are any issues, they will be highlighted here.

#### Terraform Apply

Once you are satisfied with the plan, apply the configuration using `terraform apply`.

```bash
terraform apply
```

This command creates the EC2 instance with the specified configuration.

### Common Pitfalls and How to Prevent Them

#### Missing Equal Sign in Configuration

One common pitfall is missing an equal sign in the configuration file. For example, in the provided transcript, the lecturer mentioned forgetting to put an equal sign on line 105.

**Vulnerable Code:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type t2.micro
  key_name      = aws_key_pair.example.key_name
  tags          = {
    Name = "dev_server"
  }
}
```

**Fixed Code:**
```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  key_name      = aws_key_pair.example.key_name
  tags          = {
    Name = "dev_server"
  }
}
```

#### How to Prevent

1. **Code Review**: Always review your code for syntax errors before running `terraform plan`.
2. **Linting Tools**: Use linting tools like `terraform fmt` to automatically format and check your code.

### Real-World Examples and Breaches

#### CVE-2021-20225: AWS EC2 Metadata Service Vulnerability

CVE-2021-20225 was a critical vulnerability in the AWS EC2 metadata service. This vulnerability allowed unauthorized access to sensitive metadata, including SSH keys, if the metadata service was improperly configured.

**Impact**: Unauthorized access to SSH keys could lead to unauthorized access to EC2 instances.

**Mitigation**: Ensure that the metadata service is properly configured and that access to it is restricted.

### Secure Coding Practices

#### Secure SSH Key Management

1. **Use Strong Key Lengths**: Use RSA keys with at least 2048 bits.
2. **Store Keys Securely**: Store private keys in a secure location with restricted permissions.
3. **Rotate Keys Periodically**: Rotate SSH keys periodically to enhance security.

#### Example of Secure SSH Key Management

**Vulnerable Code:**
```bash
chmod 644 ~/.ssh/mykeypair
```

**Fixed Code:**
```bash
chmod 400 ~/.ssh/mykeypair
```

### Detection and Prevention

#### Detection

1. **Audit Logs**: Regularly audit logs to detect unauthorized access attempts.
2. **Security Groups**: Use security groups to restrict access to the metadata service.

#### Prevention

1. **IAM Policies**: Use IAM policies to restrict access to sensitive resources.
2. **Network ACLs**: Use Network Access Control Lists (NACLs) to control traffic to and from the metadata service.

### Conclusion

Creating and managing AWS EC2 instances using Terraform requires careful attention to SSH key management and configuration. By following best practices and securing your infrastructure, you can ensure the reliability and security of your cloud environment.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers cloud security concepts.
- **CloudGoat**: Provides a series of labs to learn about AWS security best practices.
- **flaws.cloud**: Offers a variety of labs to explore and mitigate common cloud security vulnerabilities.

These labs will help you gain practical experience in managing AWS EC2 instances and securing your infrastructure.

---
<!-- nav -->
[[05-Introduction to AWS EC2 Instances and SSH Access|Introduction to AWS EC2 Instances and SSH Access]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[07-Introduction to AWS EC2 Instances and Terraform Configuration|Introduction to AWS EC2 Instances and Terraform Configuration]]
