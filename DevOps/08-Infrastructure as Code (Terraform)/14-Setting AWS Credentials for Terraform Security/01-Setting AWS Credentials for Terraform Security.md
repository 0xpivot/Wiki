---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting AWS Credentials for Terraform Security

### Introduction

In the realm of DevOps, managing infrastructure as code (IaC) is a critical aspect of modern software development. Tools like Terraform enable developers to define and provision infrastructure resources declaratively. However, securing these configurations is paramount, especially when dealing with sensitive information such as AWS credentials.

### Why Hardcoding Credentials is Insecure

Hardcoding AWS credentials directly into a Terraform configuration file is a significant security risk. This practice exposes sensitive data to unauthorized access, particularly when the configuration files are stored in a version control system like Git. If the repository is public or compromised, the credentials could be easily extracted and misused.

#### Real-World Example: Data Breach Due to Exposed Credentials

A notable example of this vulnerability occurred in 2021 when a major corporation exposed AWS credentials in a public GitHub repository. This breach led to unauthorized access to their cloud infrastructure, resulting in significant financial and reputational damage. The incident underscores the importance of securely managing credentials.

### Best Practices for Managing AWS Credentials

To mitigate these risks, it is essential to follow best practices for managing AWS credentials in Terraform configurations. Two primary methods are commonly used:

1. **Environmental Variables**
2. **AWS Configuration Files**

#### Environmental Variables

Using environmental variables is a recommended approach for managing AWS credentials in Terraform. This method ensures that sensitive information is not hardcoded into the configuration files, thereby reducing the risk of exposure.

##### Setting Environmental Variables

To set AWS credentials using environmental variables, you need to define two environment variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

These variables should be set in the environment where Terraform is executed. Here’s how you can set these variables in a Unix-based system:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
```

For Windows systems, you can use the following commands:

```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

##### Example: Setting Environmental Variables

Let’s walk through an example of setting these environmental variables and then running a Terraform command.

1. **Set the Environmental Variables:**

   ```bash
   export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
   export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
   ```

2. **Run Terraform Apply:**

   ```bash
   terraform apply
   ```

By setting these environmental variables, Terraform can authenticate with AWS without needing to store the credentials in the configuration files.

#### AWS Configuration Files

Another method for managing AWS credentials is through the use of AWS configuration files. These files are typically located in the `~/.aws` directory and include the `credentials` and `config` files.

##### Structure of AWS Configuration Files

The `credentials` file contains the AWS access key and secret key:

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

The `config` file can contain additional settings such as the default region:

```ini
[default]
region = us-west-2
output = json
```

##### Example: Using AWS Configuration Files

1. **Create the `credentials` File:**

   ```ini
   [default]
   aws_access_key_id = AKIAIOSFODNN7EXAMPLE
   aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

2. **Create the `config` File:**

   ```ini
   [default]
   region = us-west-2
   output = json
   ```

3. **Run Terraform Apply:**

   ```bash
   terraform apply
   ```

By using these configuration files, Terraform can automatically read the credentials and region settings without needing to specify them in the configuration files.

### How to Prevent / Defend

#### Detection

To detect potential credential leaks, you can use tools like `git-secrets` or `truffleHog`. These tools scan your Git repositories for sensitive information and alert you if credentials are found.

##### Example: Using `git-secrets`

1. **Install `git-secrets`:**

   ```bash
   brew install git-secrets
   ```

2. **Initialize `git-secrets` in your repository:**

   ```bash
   git secrets --register-aws
   git secrets --install .git
   ```

3. **Scan your repository:**

   ```bash
   git secrets --scan
   ```

#### Prevention

To prevent credential leaks, follow these best practices:

1. **Use Environmental Variables:** Store credentials in environmental variables rather than hardcoding them.
2. **Use AWS Configuration Files:** Utilize the `~/.aws` directory for storing credentials.
3. **Secure Access Management:** Use IAM roles and policies to restrict access to resources.
4. **Least Privilege Principle:** Ensure that credentials have the minimum necessary permissions.
5. **Regular Audits:** Conduct regular audits of your AWS accounts to identify and remediate any security issues.

##### Secure Coding Fix

Here’s an example of how to securely manage credentials in a Terraform configuration file:

**Vulnerable Code:**

```hcl
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  region     = "us-west-2"
}
```

**Secure Code:**

```hcl
provider "aws" {
  region = "us-west-2"
}
```

By removing the hard-coded credentials, you ensure that sensitive information is not stored in the configuration files.

### Conclusion

Managing AWS credentials securely is crucial for maintaining the integrity and confidentiality of your cloud infrastructure. By using environmental variables or AWS configuration files, you can significantly reduce the risk of credential exposure. Additionally, implementing detection and prevention measures can further enhance your security posture.

### Practice Labs

To gain hands-on experience with these concepts, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on secure coding practices.
- **OWASP Juice Shop:** Provides a vulnerable application for practicing security assessments.
- **CloudGoat:** A cloud security training platform that includes scenarios for managing AWS credentials securely.

By following these best practices and engaging in practical exercises, you can ensure that your Terraform configurations remain secure and robust.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/14-Setting AWS Credentials for Terraform Security/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/14-Setting AWS Credentials for Terraform Security/02-Practice Questions & Answers|Practice Questions & Answers]]
