---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how Terraform output values work and why they are useful.**

Terraform output values allow you to specify particular attributes of resources that should be displayed after the Terraform configuration is applied. This is useful because it provides a clear and concise way to view important details about the resources created, such as IDs or IP addresses, without having to manually inspect the state file or use commands like `terraform state show`. By defining output values, you can ensure that critical information is easily accessible and can be used in subsequent steps of your infrastructure deployment process.

**Q2. How would you configure Terraform to output the ID of a VPC and a subnet created in AWS? Provide an example configuration.**

To output the ID of a VPC and a subnet in AWS, you need to define output blocks in your Terraform configuration file. Here’s an example:

```hcl
resource "aws_vpc" "devvpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "devsubnet1" {
  vpc_id     = aws_vpc.devvpc.id
  cidr_block = "10.0.1.0/24"
}

output "devvpc_id" {
  value = aws_vpc.devvpc.id
}

output "devsubnet1_id" {
  value = aws_subnet.devsubnet1.id
}
```

In this example, `aws_vpc.devvpc.id` and `aws_subnet.devsubnet1.id` are the attributes being outputted. After running `terraform apply`, the IDs of the VPC and subnet will be displayed in the output section.

**Q3. Why can't you have multiple values in a single output block in Terraform?**

In Terraform, each output block is designed to return a single value. This design ensures clarity and simplicity in the output structure. If you were allowed to return multiple values in a single output block, it would complicate the output handling and make it harder to manage and reference individual values programmatically. By requiring separate output blocks for each value, Terraform maintains a clean and organized approach to output management.

**Q4. How can you verify which attributes are available for outputting from a resource in Terraform?**

To verify which attributes are available for outputting from a resource in Terraform, you can use the `terraform plan` command. This command provides a preview of the actions Terraform plans to take, including the attributes that are set or generated for each resource. The output of `terraform plan` will list all the attributes associated with the resources, allowing you to choose which ones to output. Additionally, you can refer to the Terraform documentation for the specific resource type to see a comprehensive list of available attributes.

**Q5. What is the advantage of using Terraform output values over manually checking the state file or using `terraform state show`?**

The primary advantage of using Terraform output values over manually checking the state file or using `terraform state show` is convenience and ease of access. Output values provide a direct and immediate way to display important resource attributes, such as IDs or IP addresses, without needing to navigate through the state file or run additional commands. This makes it easier to integrate the output values into scripts or other automation processes, ensuring that critical information is readily available and can be used efficiently in your workflow.

---
<!-- nav -->
[[02-Terraform Output Values for Resource Attributes|Terraform Output Values for Resource Attributes]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/16-Terraform Output Values For Resource Attributes/00-Overview|Overview]]
