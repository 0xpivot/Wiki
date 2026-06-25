---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it not recommended to hard-code AWS credentials directly into a Terraform configuration file?**

Hard-coding AWS credentials directly into a Terraform configuration file is not recommended because it poses significant security risks. If the configuration file is checked into a version control system like Git, the credentials could be exposed to unauthorized individuals. This could lead to unauthorized access to AWS resources and potential data breaches. Instead, it is best practice to store credentials securely using environment variables or a dedicated credentials file.

**Q2. How can you set AWS credentials for Terraform using environment variables?**

To set AWS credentials for Terraform using environment variables, you need to set two specific environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
```

Once these environment variables are set, Terraform can use them to authenticate with AWS. You can verify that the environment variables are correctly set by running `echo $AWS_ACCESS_KEY_ID` and `echo $AWS_SECRET_ACCESS_KEY`.

**Q3. What is the purpose of the `.aws` directory and how can you configure AWS credentials globally using it?**

The `.aws` directory is used to store AWS credentials and configuration settings globally on the local machine. To configure AWS credentials globally, you can use the `aws configure` command:

```bash
aws configure
```

This command prompts you to enter your AWS Access Key ID, Secret Access Key, and default region. After entering these details, the `.aws` directory is created (if it doesn’t exist) and populated with a `credentials` file and a `config` file. Terraform can then read these credentials from the `.aws` directory.

**Q4. How can you define and use custom environment variables in Terraform?**

To define custom environment variables in Terraform, you can use the `TF_VAR_` prefix followed by the variable name. For example, to set a custom variable for an availability zone:

```bash
export TF_VAR_availability_zone="us-west-2b"
```

In your Terraform configuration file, you can then reference this variable as follows:

```hcl
variable "availability_zone" {}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
  availability_zone = var.availability_zone
}
```

When you run `terraform apply`, Terraform will use the value of the `TF_VAR_availability_zone` environment variable.

**Q5. Explain how Terraform uses environment variables to authenticate with different cloud providers, such as Google Cloud or Jenkins.**

Terraform supports authentication with various cloud providers through environment variables. For example, to authenticate with Google Cloud, you might set the following environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

For Jenkins, you might set:

```bash
export JENKINS_URL="http://jenkins.example.com"
export JENKINS_USERNAME="admin"
export JENKINS_PASSWORD="password"
```

These environment variables allow Terraform to authenticate with the respective services without hard-coding sensitive information into the configuration files. Each provider’s documentation specifies the required environment variables.

**Q6. How does Terraform handle the region setting when using environment variables?**

Terraform can handle the region setting using environment variables. You can set the `AWS_DEFAULT_REGION` environment variable to specify the default region:

```bash
export AWS_DEFAULT_REGION="us-east-1"
```

If this environment variable is set, Terraform will use the specified region for AWS operations. This allows users to configure the region dynamically without modifying the Terraform configuration files.

**Q7. Describe a recent real-world example where improper handling of credentials led to a security breach.**

One notable example is the Capital One data breach in 2019 (CVE-2019-11156). The breach occurred due to misconfigured web application firewall rules, allowing unauthorized access to sensitive data. While the primary issue was the misconfiguration, the incident highlighted the importance of secure credential management. If proper security practices, including the use of environment variables and secure storage mechanisms, had been followed, the risk of exposure might have been reduced.

---
<!-- nav -->
[[01-Setting AWS Credentials for Terraform Security|Setting AWS Credentials for Terraform Security]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/14-Setting AWS Credentials for Terraform Security/00-Overview|Overview]]
