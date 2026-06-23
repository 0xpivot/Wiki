---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS CLI Installation and Usage

The Amazon Web Services Command Line Interface (AWS CLI) is a powerful tool that allows you to interact with AWS services through the command line. This tool provides a flexible and efficient way to manage your AWS resources, automate tasks, and integrate with other tools and scripts. In this chapter, we will cover the installation process of AWS CLI, its usage, and various practical examples to help you understand how to effectively manage your AWS resources.

### Background Theory

Before diving into the installation and usage of AWS CLI, let's understand the underlying concepts and why they matter.

#### What is AWS CLI?

AWS CLI is a unified tool to control multiple AWS services from the command line. It allows you to perform actions such as creating and managing EC2 instances, S3 buckets, RDS databases, and more. The CLI is built on top of the AWS SDK, which provides a set of libraries and APIs to interact with AWS services programmatically.

#### Why Use AWS CLI?

Using AWS CLI offers several advantages:

1. **Automation**: Automate repetitive tasks and integrate with CI/CD pipelines.
2. **Efficiency**: Perform operations quickly and efficiently without navigating through the AWS Management Console.
3. **Scripting**: Write scripts to manage AWS resources, making it easier to handle complex workflows.
4. **Consistency**: Ensure consistency across environments by using the same commands and configurations.

### Installing AWS CLI

The installation process varies depending on your operating system. Let's go through the steps for macOS, Windows, and Linux.

#### macOS Installation

On macOS, you can use Homebrew to install AWS CLI. Homebrew is a package manager for macOS that simplifies the installation of software packages.

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update

# Install AWS CLI
brew install awscli
```

Alternatively, you can directly install the latest version of AWS CLI:

```bash
brew install awscli
```

#### Windows Installation

For Windows, you can download the installer from the AWS CLI GitHub releases page. Follow these steps:

1. Visit the [AWS CLI GitHub Releases](https://github.com/aws/aws-cli/releases) page.
2. Download the latest `.msi` installer.
3. Run the installer and follow the prompts to complete the installation.

#### Linux Installation

On Linux, you can use the package manager specific to your distribution to install AWS CLI. Here are the steps for Ubuntu and CentOS/RHEL:

**Ubuntu:**

```bash
# Update the package list
sudo apt-get update

# Install AWS CLI
sudo apt-get install awscli
```

**CentOS/RHEL:**

```bash
# Install the EPEL repository
sudo yum install epel-release

# Install AWS CLI
sudo yum install awscli
```

### Verifying the Installation

Once you have installed AWS CLI, you can verify the installation by checking the version:

```bash
aws --version
```

This command should output the version number of the installed AWS CLI, such as `aws-cli/2.1.1`.

### Configuring AWS CLI

After installing AWS CLI, the next step is to configure it to connect to your AWS account. This involves setting up your AWS credentials and default region.

#### Setting Up Credentials

To configure AWS CLI, you need to provide your AWS Access Key ID and Secret Access Key. These credentials can be obtained from the AWS Management Console.

```bash
aws configure
```

When prompted, enter your Access Key ID, Secret Access Key, and default region (e.g., `us-west-2`). Optionally, you can specify a default output format (e.g., `json`).

### Creating an EC2 Instance Using AWS CLI

Now that AWS CLI is installed and configured, let's create an EC2 instance using the command line.

#### Step 1: Create a Security Group

A security group acts as a virtual firewall for your EC2 instance. It controls inbound and outbound traffic based on defined rules.

```bash
aws ec2 create-security-group --group-name my-security-group --description "Security group for my EC2 instance"
```

This command creates a new security group named `my-security-group`. The output will include the security group ID.

#### Step 2: Add Inbound Rules to the Security Group

Next, we need to add inbound rules to allow SSH access.

```bash
aws ec2 authorize-security-group-ingress --group-id sg-xxxxxxxx --protocol tcp --port 22 --cidr 0.0.0.0/0
```

Replace `sg-xxxxxxxx` with the actual security group ID obtained in the previous step. This command allows inbound traffic on port 22 (SSH) from any IP address (`0.0.0.0/0`).

#### Step 3: Create a Key Pair

A key pair is used to securely connect to your EC2 instance via SSH.

```bash
aws ec2 create-key-pair --key-name my-key-pair --query 'KeyMaterial' --output text > my-key-pair.pem
chmod 400 my-key-pair.pem
```

This command creates a new key pair named `my-key-pair` and saves the private key to `my-key-pair.pem`. The `chmod 400` command sets the correct permissions for the private key file.

#### Step 4: Launch an EC2 Instance

Finally, we can launch an EC2 instance using the created security group and key pair.

```bash
aws ec2 run-instances --image-id ami-xxxxxxxx --count 1 --instance-type t2.micro --key-name my-key-pair --security-group-ids sg-xxxxxxxx --subnet-id subnet-xxxxxxxx
```

Replace `ami-xxxxxxxx`, `sg-xxxxxxxx`, and `subnet-xxxxxxxx` with the appropriate values for your environment. This command launches a new EC2 instance with the specified image ID, instance type, key pair, security group, and subnet.

### Managing EC2 Instances

Once your EC2 instance is launched, you can manage it using various AWS CLI commands.

#### Listing EC2 Instances

To list all EC2 instances in your account:

```bash
aws ec2 describe-instances
```

This command returns detailed information about all EC2 instances, including their IDs, states, and associated security groups.

#### Stopping and Starting an EC2 Instance

To stop an EC2 instance:

```bash
aws ec2 stop-instances --instance-ids i-xxxxxxxx
```

To start an EC2 instance:

```bash

```

---
<!-- nav -->
[[01-Introduction to AWS CLI Installation and Usage for Efficient Management|Introduction to AWS CLI Installation and Usage for Efficient Management]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/03-AWS CLI Installation and Usage for Efficient Management/00-Overview|Overview]] | [[03-Introduction to AWS CLI|Introduction to AWS CLI]]
