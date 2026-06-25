---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS EC2 Instances and Key Pairs

In the realm of cloud computing, Amazon Web Services (AWS) stands as one of the most prominent platforms, offering a wide array of services to manage and deploy applications at scale. One of the foundational services provided by AWS is the Elastic Compute Cloud (EC2), which allows users to launch virtual servers in the cloud. These virtual servers, known as instances, can run various operating systems and perform tasks ranging from simple web hosting to complex data processing.

### What is an EC2 Instance?

An EC2 instance is essentially a virtual machine that runs within the AWS infrastructure. Each instance is defined by a specific combination of hardware and software configurations, including the type of CPU, amount of memory, storage capacity, and the operating system. Users can choose from a variety of pre-configured instance types, each optimized for different use cases such as general-purpose computing, compute-intensive tasks, memory-intensive tasks, and more.

### Key Pairs for SSH Access

One of the critical aspects of managing EC2 instances is ensuring secure access to them. Secure Shell (SSH) is a cryptographic network protocol used for secure communication between a client and a server. To enable SSH access to an EC2 instance, AWS uses key pairs. A key pair consists of a public key and a private key. The public key is stored on the EC2 instance, while the private key is kept securely by the user.

#### Public Key vs. Private Key

- **Public Key**: This key is used to encrypt data that can only be decrypted by the corresponding private key. In the context of EC2, the public key is uploaded to the instance and used to authenticate incoming SSH connections.
  
- **Private Key**: This key is used to decrypt data encrypted with the corresponding public key. The private key is kept secret and used by the user to establish an SSH connection to the EC2 instance.

### Why Use Key Pairs?

Using key pairs for SSH access provides several advantages:

1. **Security**: Key-based authentication is more secure than password-based authentication. Passwords can be guessed or brute-forced, whereas key pairs provide strong encryption.
2. **Automation**: Key pairs can be easily integrated into automated deployment scripts and tools, making it easier to manage large numbers of instances.
3. **Flexibility**: Key pairs can be reused across multiple instances, simplifying management and reducing the overhead of generating new keys for each instance.

### Manual Creation of Key Pairs

Manually creating key pairs involves several steps:

1. **Generate Key Pair**: Use a tool like `ssh-keygen` to generate a public-private key pair.
2. **Upload Public Key**: Upload the public key to the EC2 instance through the AWS Management Console or via the AWS CLI.
3. **Download Private Key**: Download the private key and store it securely on your local machine.
4. **Configure SSH Client**: Copy the private key to the `.ssh` directory on your local machine and configure the SSH client to use it.

Here is an example of generating a key pair using `ssh-keygen`:

```bash
ssh-keygen -t rsa -b 4096 -f my_key_pair
```

This command generates a 4096-bit RSA key pair named `my_key_pair`. The public key will be stored in `my_key_pair.pub`, and the private key will be stored in `my_key_pair`.

### Challenges with Manual Key Pair Management

While manual key pair management is straightforward, it becomes cumbersome when dealing with large-scale deployments. Manually creating and managing key pairs for each instance can lead to:

- **Human Error**: Mistakes in copying or configuring keys can result in failed SSH connections.
- **Scalability Issues**: Managing key pairs for hundreds or thousands of instances can become impractical.
- **Security Risks**: Storing private keys in plain text or insecure locations can expose them to unauthorized access.

### Automating Key Pair Management with Terraform

To address these challenges, automation tools like Terraform can be used to manage key pairs programmatically. Terraform is an infrastructure as code (IaC) tool that allows users to define and provision infrastructure resources using declarative configuration files.

#### Creating Key Pairs Using Terraform

Terraform provides a resource called `aws_key_pair` that can be used to create and manage key pairs for EC2 instances. Here is an example of how to create a key pair using Terraform:

```hcl
resource "aws_key_pair" "example" {
  key_name   = "server_key"
  public_key = file("~/.ssh/id_rsa.pub")
}
```

In this example, the `aws_key_pair` resource is defined with the `key_name` attribute set to `"server_key"` and the `public_key` attribute set to the contents of the public key file located at `~/.ssh/id_rsa.pub`.

### How to Prevent / Defend Against Key Pair Mismanagement

#### Detection

To detect mismanagement of key pairs, consider the following practices:

1. **Audit Logs**: Regularly review audit logs to identify unauthorized access attempts or changes to key pairs.
2. **Monitoring Tools**: Use monitoring tools like AWS CloudTrail to track API calls related to key pair management.
3. **Key Rotation**: Implement a key rotation policy to periodically replace old key pairs with new ones.

#### Prevention

To prevent mismanagement of key pairs, follow these best practices:

1. **Secure Storage**: Store private keys in a secure location, such as a hardware security module (HSM) or a secure key management service.
2. **Access Control**: Limit access to key pairs to authorized personnel only. Use IAM roles and policies to control who can create or modify key pairs.
3. **Automated Management**: Use automation tools like Terraform to manage key pairs programmatically, reducing the risk of human error.

### Real-World Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in the AWS SDK for Java that allowed attackers to bypass key pair validation, potentially leading to unauthorized access to EC2 instances. This vulnerability highlights the importance of secure key pair management and the need to stay up-to-date with security patches and best practices.

### Conclusion

Managing key pairs for EC2 instances is a crucial aspect of securing access to cloud resources. While manual key pair management is possible, it becomes impractical for large-scale deployments. Automation tools like Terraform provide a robust solution for managing key pairs programmatically, reducing the risk of human error and improving overall security.

### Practice Labs

For hands-on practice with AWS EC2 and key pair management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on cloud security, including EC2 instance management.
- **CloudGoat**: Provides a series of labs focused on AWS security, including key pair management and other IaC practices.

By mastering the concepts and techniques covered in this chapter, you will be well-equipped to manage EC2 instances securely and efficiently in a cloud environment.

---
<!-- nav -->
[[03-Introduction to AWS EC2 Instances and AMIs|Introduction to AWS EC2 Instances and AMIs]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[05-Introduction to AWS EC2 Instances and SSH Access|Introduction to AWS EC2 Instances and SSH Access]]
