---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Required Version in Terraform Configuration

When configuring Terraform, one of the first things to consider is the `required_version` attribute. This attribute specifies the minimum version of Terraform that your configuration requires. This ensures that your infrastructure-as-code (IaC) scripts will work correctly with the intended version of Terraform.

### What is `required_version`?

The `required_version` attribute is defined at the top level of your Terraform configuration file (`main.tf`). It takes a string value that represents a version constraint. For example:

```hcl
terraform {
  required_version = ">= 0.12"
}
```

This tells Terraform that the configuration requires version 0.12 or higher.

### Why is `required_version` important?

Using `required_version` is crucial for several reasons:

1. **Compatibility**: Different versions of Terraform may introduce breaking changes or new features. Specifying a required version ensures that your configuration remains compatible with the intended version.
2. **Consistency**: By setting a required version, you ensure that everyone working on the project uses the same version of Terraform, reducing the chances of unexpected behavior due to version differences.
3. **Security**: Newer versions of Terraform often include security patches and improvements. Specifying a required version helps ensure that you are using a secure version of Terraform.

### How does `required_version` work under the hood?

When you run `terraform init`, Terraform checks the `required_version` attribute and verifies that the installed version meets the specified requirement. If the installed version does not meet the requirement, Terraform will display an error and refuse to proceed.

### Example

Here’s an example of a Terraform configuration file with a `required_version` attribute:

```hcl
terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}
```

In this example, the configuration requires Terraform version 0.12 or higher.

### Common Mistakes

One common mistake is not specifying a `required_version`. This can lead to compatibility issues if different team members are using different versions of Terraform. Always specify a `required_version` to avoid such issues.

### How to Prevent / Defend

To ensure that your Terraform configurations are secure and consistent:

1. **Specify `required_version`**: Always include a `required_version` attribute in your Terraform configuration.
2. **Use a consistent version**: Ensure that all team members are using the same version of Terraform.
3. **Regularly update**: Keep your Terraform version up-to-date to benefit from the latest security patches and features.

---
<!-- nav -->
[[04-Configuring Remote Terraform State Storage|Configuring Remote Terraform State Storage]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/05-Configuring Remote Terraform State Storage/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/05-Configuring Remote Terraform State Storage/06-Practice Questions & Answers|Practice Questions & Answers]]
