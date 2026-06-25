---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Key Pairs in AWS EC2

In the context of AWS EC2 (Elastic Compute Cloud), key pairs play a crucial role in securely accessing your EC2 instances. A key pair consists of a public key and a private key. The public key is stored in AWS, and the private key is kept securely by the user. These keys are used to authenticate and establish an encrypted connection between your local machine and the EC2 instance.

### Why Use Key Pairs?

Key pairs provide a secure method to access your EC2 instances via SSH (Secure Shell). Unlike traditional password-based authentication, which can be susceptible to brute-force attacks, key pairs offer a more robust and secure alternative. By using a private key, you ensure that only authorized users can access the instance, thereby enhancing the overall security posture of your infrastructure.

### How Key Pairs Work

When you create an EC2 instance, you specify a key pair during the launch process. The public key associated with the key pair is embedded into the instance metadata. When you attempt to SSH into the instance, the SSH client uses the private key to authenticate with the server. If the private key matches the public key stored in AWS, the connection is established.

### Creating a Key Pair Using AWS CLI

To create a key pair using the AWS CLI, you need to follow a series of steps. Let's break down the process and explore each component in detail.

#### Step 1: Install AWS CLI

Before proceeding, ensure that you have the AWS CLI installed on your system. You can install it using the following commands:

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install awscli

# For macOS
brew install awscli

# For Windows
choco install awscli
```

#### Step 2: Configure AWS CLI

After installing the AWS CLI, configure it with your AWS credentials. Run the following command:

```bash
aws configure
```

This will prompt you to enter your AWS Access Key ID, Secret Access Key, default region name, and default output format.

#### Step 3: Create a Key Pair

Now, let's create a key pair using the `aws ec2 create-key-pair` command. The command structure is as follows:

```bash
aws ec2 create-key-pair --key-name <key_name> --query 'KeyMaterial' --output text > <file_name>.pem
```

Let's break down each part of the command:

- `--key-name`: Specifies the name of the key pair.
- `--query 'KeyMaterial'`: Extracts the private key material from the response.
- `--output text`: Ensures that the output is in plain text format.
- `> <file_name>.pem`: Redirects the output to a `.pem` file, which stores the private key.

For example, to create a key pair named `my-key-pair-cli`, you would run:

```bash
aws ec2 create-key-pair --key-name my-key-pair-cli --query 'KeyMaterial' --output text > my-key-pair-cli.pem
```

### Understanding the Command Components

#### Key Name (`--key-name`)

The `--key-name` parameter specifies the name of the key pair. This name is unique within your AWS account and region. It is important to choose a meaningful name that reflects the purpose of the key pair.

#### Query (`--query 'KeyMaterial'`)

The `--query` parameter allows you to extract specific information from the JSON response. In this case, `'KeyMaterial'` extracts the private key material, which is the unencrypted private key.

#### Output Format (`--output text`)

The `--output text` parameter ensures that the output is in plain text format. This is necessary because the private key should be stored in a human-readable format.

#### Saving the Private Key (`> <file_name>.pem`)

The `>` operator redirects the output to a file. The `.pem` extension is commonly used for storing private keys in PEM (Privacy Enhanced Mail) format. This file should be kept secure and not shared with unauthorized parties.

### Example Command Execution

Let's walk through the execution of the command step-by-step:

1. **Run the Command**:
    ```bash
    aws ec2 create-key-pair --key-name my-key-pair-cli --query 'KeyMaterial' --output text > my-key-pair-cli.pem
    ```

2. **Check the File**:
    After executing the command, check if the `.pem` file was created successfully:
    ```bash
    ls -l my-key-pair-cli.pem
    ```

3. **Verify the Content**:
    Open the `.pem` file to verify its content:
    ```bash
    cat my-key-pair-cli.pem
    ```

### Using the Key Pair with EC2 Instances

Once you have created the key pair, you can use it to launch new EC2 instances. When launching an instance, specify the key pair name in the `--key-name` parameter of the `aws ec2 run-instances` command.

For example:

```bash
aws ec2 run-instances --image-id ami-0c94855ba95c71c99 --count 1 --instance-type t2.micro --key-name my-key-pair-cli --security-group-ids sg-0123456789abcdef0 --subnet-id subnet-0123456789abcdef0
```

### SSH into the Instance

To SSH into the instance, use the following command:

```bash
ssh -i my-key-pair-cli.pem ec2-user@<public_ip_address>
```

Replace `<public_ip_address>` with the actual public IP address of your EC2 instance.

### Mermaid Diagram: Key Pair Creation and Usage Flow

```mermaid
graph TD
    A[Create Key Pair] --> B[Specify Key Name]
    B --> C[Extract Key Material]
    C --> D[Save Private Key]
    D --> E[Launch EC2 Instance]
    E --> F[SSH into Instance]
```

### Common Pitfalls and Best Practices

#### Pitfall 1: Losing the Private Key

If you lose the private key, you will no longer be able to access the EC2 instance. Always keep a backup of the `.pem` file in a secure location.

#### Pitfall 2: Sharing the Private Key

Never share the private key with unauthorized parties. This can compromise the security of your EC2 instances.

#### Best Practice 1: Secure Storage

Store the `.pem` file in a secure location, such as a password manager or a secure cloud storage service.

#### Best Practice 2: Use IAM Roles

Instead of relying solely on key pairs, consider using IAM roles to manage permissions and access to your EC2 instances.

### Real-World Examples and CVEs

#### Example: CVE-2021-20225

In 2021, a vulnerability (CVE-2021-20225) was discovered in the AWS CLI, which allowed attackers to bypass authentication checks. This highlights the importance of keeping your AWS CLI and other tools up-to-date to mitigate such vulnerabilities.

### How to Prevent / Defend

#### Detection

Regularly audit your AWS environment to ensure that key pairs are being used correctly. Use AWS CloudTrail to monitor API calls related to key pair management.

#### Prevention

1. **Keep Software Updated**: Ensure that your AWS CLI and other tools are up-to-date to mitigate known vulnerabilities.
2. **Use IAM Policies**: Implement IAM policies to restrict access to key pairs and other sensitive resources.
3. **Enable Multi-Factor Authentication (MFA)**: Enable MFA for your AWS account to add an additional layer of security.

#### Secure Coding Fixes

##### Vulnerable Code

```bash
aws ec2 create-key-pair --key-name my-key-pair-cli --query 'KeyMaterial' --output text > my-key-pair-cli.pem
```

##### Secure Code

```bash
aws ec2 create-key-pair --key-name my-key-pair-cli --query 'KeyMaterial' --output text > my-key-pair-cli.pem
chmod 400 my-key-pair-cli.pem
```

By setting the file permissions to `400`, you ensure that only the owner can read the file, preventing unauthorized access.

### Complete Example: Full Command and Response

#### Command

```bash
aws ec2 create-key-pair --key-name my-key-pair-cli --query 'KeyMaterial' --output text > my-key-pair-cli.pem
```

#### Response

```plaintext
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAuXJZ...
-----END RSA PRIVATE KEY-----
```

#### Result

```plaintext
-rw------- 1 user user 1679 Jan  1 12:00 my-key-pair-cli.pem
```

### Hands-On Labs

For practical experience with AWS CLI and key pair management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide a safe environment to practice and reinforce the concepts learned in this chapter.

### Conclusion

Creating and managing key pairs in AWS EC2 is a fundamental aspect of securing your infrastructure. By following the steps outlined in this chapter, you can effectively create and use key pairs to enhance the security of your EC2 instances. Remember to follow best practices and regularly audit your environment to ensure that your key pairs are being used securely.

---
<!-- nav -->
[[03-Introduction to AWS CLI|Introduction to AWS CLI]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/03-AWS CLI Installation and Usage for Efficient Management/00-Overview|Overview]] | [[05-AWS CLI Installation and Usage for Efficient Management|AWS CLI Installation and Usage for Efficient Management]]
