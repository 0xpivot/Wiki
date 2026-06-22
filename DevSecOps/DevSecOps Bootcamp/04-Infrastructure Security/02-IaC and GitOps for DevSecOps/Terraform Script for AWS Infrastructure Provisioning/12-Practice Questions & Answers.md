---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between `resource` and `data` blocks in Terraform.**

In Terraform, `resource` blocks are used to define and create new resources, such as EC2 instances, roles, or security groups. These resources are created or modified during the execution of the Terraform plan and apply process. 

On the other hand, `data` blocks are used to fetch existing resources or information from the cloud provider. For example, you might use a `data` block to retrieve the ARN of an existing IAM policy or the ID of an existing VPC. This information can then be used in the configuration of other resources.

For instance, in the given script, `data` blocks are used to fetch existing IAM policies, which are then attached to roles created by `resource` blocks.

**Q2. How would you exploit the `user_data` feature in Terraform to automate the setup of an EC2 instance?**

The `user_data` feature in Terraform can be used to pass initialization scripts to an EC2 instance upon launch. This allows for automating the setup of the instance, such as installing necessary software, setting up configurations, and performing other initializations.

Here’s an example of how you might use `user_data` to automate the installation of Docker and AWS CLI on an EC2 instance:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y docker.io
              curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
              unzip awscliv2.zip
              sudo ./aws/install
              EOF
}
```

In this example, the `user_data` script updates the package list, installs Docker, and then installs the AWS CLI. This ensures that the EC2 instance is configured correctly upon launch.

**Q3. Why is it important to create a new VPC instead of using the default VPC in Terraform scripts?**

Creating a new VPC instead of using the default VPC in Terraform scripts is important for several reasons:

1. **Isolation**: Using a custom VPC allows you to isolate your resources from other services that might be running in the default VPC. This enhances security by reducing the attack surface.

2. **Control**: You have complete control over the configuration of the VPC, including subnets, route tables, and security groups. This allows you to tailor the network architecture to your specific requirements.

3. **Cleanup**: When you create a custom VPC, it is easier to clean up and destroy all resources associated with it. This is particularly useful in development and testing environments where you frequently create and destroy resources.

4. **Best Practices**: Creating a new VPC aligns with best practices in cloud infrastructure management. It ensures that your infrastructure is self-contained and does not rely on default settings that could change over time.

**Q4. How would you modify the Terraform script to increase the volume size of the EC2 instances?**

To increase the volume size of the EC2 instances in the Terraform script, you would need to adjust the `volume_size` attribute in the EC2 instance resource definition. Here’s an example of how you might do this:

```hcl
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  root_block_device {
    volume_size = 24
  }

  # Other configurations...
}

resource "aws_instance" "gitlab_runner" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  root_block_device {
    volume_size = 24
  }

  # Other configurations...
}
```

In this example, the `root_block_device` block is used to specify the `volume_size` for the root volume of the EC2 instances. By setting `volume_size` to 24, you ensure that the instances have a larger root volume.

**Q5. What are the benefits of using Terraform modules in your infrastructure as code (IaC) projects?**

Using Terraform modules in your IaC projects provides several benefits:

1. **Reusability**: Modules allow you to encapsulate common infrastructure components, making them reusable across multiple projects. This reduces duplication and improves consistency.

2. **Modularity**: By breaking down your infrastructure into smaller, manageable pieces, modules make it easier to understand and maintain your Terraform configurations.

3. **Abstraction**: Modules provide a layer of abstraction, hiding the complexity of individual resources and presenting a higher-level interface. This simplifies the configuration process and makes it easier to manage large-scale infrastructures.

4. **Collaboration**: Modules can be shared among team members, improving collaboration and enabling better teamwork. They can also be published to public registries, allowing others to reuse and contribute to them.

5. **Versioning**: Modules can be versioned, allowing you to track changes and roll back to previous versions if necessary. This helps in managing dependencies and ensuring stability in your infrastructure.

**Q6. How would you handle the manual acquisition of the GitLab runner registration token in a Terraform script?**

Handling the manual acquisition of the GitLab runner registration token in a Terraform script involves using Terraform variables to store the token value. Here’s how you can do it:

1. Define a variable for the token in your `variables.tf` file:

```hcl
variable "gitlab_runner_token" {
  description = "The registration token for the GitLab runner."
  type        = string
}
```

2. Set the token value in your `terraform.tfvars` file:

```hcl
gitlab_runner_token = "your_registration_token_here"
```

3. Use the token in your Terraform script:

```hcl
resource "aws_instance" "gitlab_runner" {
  # ... other configurations ...

  user_data = <<-EOF
              #!/bin/bash
              # ... other initialization commands ...
              gitlab-runner register --non-interactive \
                --url "${var.gitlab_url}" \
                --registration-token "${var.gitlab_runner_token}" \
                --executor "docker" \
                --description "My GitLab Runner" \
                --docker-image "alpine:latest"
              EOF
}
```

In this example, the `gitlab_runner_token` variable is used in the `user_data` script to register the GitLab runner. This approach ensures that the token is securely managed outside of the Terraform script and can be updated as needed.

**Q7. What are the recent real-world examples of misconfigurations in AWS infrastructure that could have been prevented by using Terraform?**

Recent real-world examples of misconfigurations in AWS infrastructure that could have been prevented by using Terraform include:

1. **AWS S3 Bucket Misconfiguration (CVE-2021-20225)**: In 2021, several high-profile breaches occurred due to misconfigured S3 buckets that were publicly accessible. Using Terraform, you can enforce strict access controls and ensure that buckets are not publicly exposed by default.

2. **EC2 Instance Security Group Misconfiguration**: In another incident, EC2 instances were found to have overly permissive security group rules, allowing unrestricted access to sensitive ports. With Terraform, you can define and enforce strict security group rules, ensuring that only necessary ports are exposed.

3. **IAM Role Misconfiguration**: IAM roles with excessive permissions were exploited in various breaches. Terraform allows you to define least privilege IAM roles and policies, reducing the risk of unauthorized access.

By using Terraform, you can enforce consistent and secure configurations across your infrastructure, reducing the likelihood of such misconfigurations occurring.

---
<!-- nav -->
[[11-Infrastructure as Code (IaC) and GitOps for DevSecOps|Infrastructure as Code (IaC) and GitOps for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]]
