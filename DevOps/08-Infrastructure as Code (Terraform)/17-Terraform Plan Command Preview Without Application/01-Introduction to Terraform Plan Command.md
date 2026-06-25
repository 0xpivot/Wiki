---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform Plan Command

Terraform is an infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and provision data centers and cloud services using declarative configuration files. One of the most powerful commands in Terraform is `terraform plan`, which provides a preview of the changes that will be made to your infrastructure before you apply them.

### What is Terraform Plan?

The `terraform plan` command generates an execution plan based on the differences between the current state of your infrastructure and the desired state defined in your configuration files. This plan shows you exactly what actions Terraform will take to bring your infrastructure to the desired state. It is a crucial step in the Terraform workflow because it allows you to review and understand the changes before they are applied.

### Why Use Terraform Plan?

Using `terraform plan` is essential for several reasons:

1. **Review Changes**: Before making any changes to your infrastructure, you can review the proposed changes to ensure they align with your expectations.
2. **Avoid Unexpected Outcomes**: By reviewing the plan, you can catch potential issues such as unintended deletions or modifications.
3. **Collaboration**: In environments where multiple people are working on the same project, `terraform plan` helps ensure everyone is aware of the changes being made.
4. **Testing**: You can test the plan in a staging environment before applying it to production.

### How Does Terraform Plan Work?

When you run `terraform plan`, Terraform performs the following steps:

1. **State Comparison**: Terraform compares the current state of your infrastructure (stored in the `.tfstate` file) with the desired state defined in your configuration files.
2. **Change Detection**: Terraform identifies any differences between the two states and determines the necessary actions to reconcile them.
3. **Plan Generation**: Terraform generates an execution plan that lists the actions to be taken, including creating, updating, or deleting resources.

### Example Configuration

Let's consider a simple example where we have a configuration file (`main.tf`) that defines a subnet in AWS:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_subnet" "subnet1" {
  vpc_id     = "vpc-12345678"
  cidr_block = "10.0.1.0/24"
}
```

### Running Terraform Plan

To run `terraform plan`, you first initialize Terraform:

```bash
terraform init
```

Then, you generate the plan:

```bash
terraform plan
```

This command will output a detailed plan showing the actions Terraform will take. Here’s an example of what the output might look like:

```plaintext
Terraform will perform the following actions:

  # aws_subnet.subnet1 will be created
  + resource "aws_subnet" "subnet1" {
      + arn              = (known after apply)
      + availability_zone = (known after apply)
      + cidr_block       = "10.0.1.0/24"
      + id               = (known after apply)
      + ipv6_cidr_block  = (known after apply)
      + map_public_ip_on_launch = (known after apply)
      + owner_id         = (known after apply)
      + tags             = (known after apply)
      + vpc_id           = "vpc-12345678"
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

### Dealing with Deleted Resources

In the scenario described in the transcript, a subnet was deleted using `terraform destroy`, but it still exists in the configuration file. When you run `terraform plan`, Terraform will identify this discrepancy and propose to recreate the subnet:

```bash
terraform plan
```

Output:

```plaintext
Terraform will perform the following actions:

  # aws_subnet.subnet1 will be created
  + resource "aws_subnet" "subnet1" {
      + arn              = (known after apply)
      + availability_zone = (known after apply)
      + cidr_block       = "10.0.1.0/24"
      + id               = (known after apply)
      + ipv6_cidr_block  = (known after apply)
      + map_public_ip_on_launch = (known after apply)
      + owner_id         = (known after apply)
      + tags             = (known after apply)
      + vpc_id           = "vpc-12345678"
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

### Auto-Approval Flag

If you want to automatically apply the changes without manual confirmation, you can use the `-auto-approve` flag:

```bash
terraform apply -auto-approve
```

This command will immediately apply the changes without prompting for confirmation.

### Real-World Examples

#### Example 1: Accidental Resource Deletion

Consider a scenario where a developer accidentally deletes a critical resource from the configuration file. Running `terraform plan` would reveal this deletion, allowing you to correct it before applying the changes.

#### Example 2: Unexpected State Differences

In a multi-developer environment, one developer might make changes to the infrastructure directly through the cloud provider's console, bypassing Terraform. Running `terraform plan` would highlight these discrepancies, ensuring that the configuration files reflect the actual state of the infrastructure.

### Pitfalls and Common Mistakes

1. **Ignoring the Plan**: Always review the plan before applying changes. Ignoring the plan can lead to unexpected outcomes.
2. **Manual Changes**: Avoid making manual changes to the infrastructure outside of Terraform. This can cause the state to diverge from the configuration.
3. **Configuration Drift**: Regularly run `terraform plan` to detect and address any drift between the configuration and the actual state.

### How to Prevent / Defend

#### Detection

Regularly run `terraform plan` to detect any discrepancies between the current state and the desired state. This can be automated using CI/CD pipelines.

#### Prevention

1. **Version Control**: Store your Terraform configuration files in version control systems like Git. This ensures that all changes are tracked and reviewed.
2. **Code Reviews**: Implement code reviews for Terraform configuration changes to catch potential issues before they are applied.
3. **Automated Testing**: Use automated testing frameworks to validate the correctness of your Terraform configurations.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }
}
```

**Secure Configuration:**

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
```

In the secure configuration, the `lifecycle` block is used to ignore changes to the `tags` attribute, preventing accidental modifications.

### Conclusion

The `terraform plan` command is a critical tool in managing your infrastructure as code. By providing a preview of the changes, it helps you avoid unexpected outcomes and ensures that your infrastructure remains in sync with your configuration files. Regularly running `terraform plan` and reviewing the results is a best practice that should be followed in any Terraform-based infrastructure management process.

### Practice Labs

For hands-on experience with Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of web application security, including some that involve Terraform.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. While it doesn’t focus on Terraform specifically, it can be used to practice securing infrastructure.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training. Similar to OWASP Juice Shop, it can be used to practice securing infrastructure.
- **Kubernetes Goat**: Focuses on Kubernetes security and can be used to practice securing Kubernetes clusters using Terraform.
- **CloudGoat**: Provides a series of labs focused on cloud security, including Terraform-based infrastructure management.

By practicing with these labs, you can gain a deeper understanding of how to effectively use Terraform and manage your infrastructure securely.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/17-Terraform Plan Command Preview Without Application/00-Overview|Overview]] | [[02-Introduction to Terraform and Infrastructure Management|Introduction to Terraform and Infrastructure Management]]
