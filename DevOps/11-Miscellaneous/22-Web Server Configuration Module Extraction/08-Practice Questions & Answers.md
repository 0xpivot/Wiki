---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of extracting the web server configuration into a separate module in Terraform.**

The process involves isolating the resources and data sources related to the web server instance into a distinct module. This includes copying the relevant resources such as the instance itself, key pair creation, AMI query, and security group configuration into a new `main.tf` file within the web server module. After copying, the references to external values (like VPC ID, subnet ID, and security group ID) are parameterized using Terraform variables. These variables are then declared in a `variables.tf` file within the module. Finally, the module is referenced in the root `main.tf` file, passing the required variables. This modular approach helps in maintaining cleaner and more manageable code.

**Q2. How would you parameterize the operating system image (AMI) used for the web server instance?**

To parameterize the AMI used for the web server instance, you would introduce a new variable named `image_name` in the `variables.tf` file within the web server module. This variable would allow dynamic assignment of the AMI during module invocation. In the `main.tf` file, replace the hardcoded AMI reference with a reference to the `var.image_name`. When declaring the module in the root `main.tf`, pass the appropriate value for `image_name` using the `TF_VAR_image_name` environment variable or a `.tfvars` file.

**Q3. Why is it beneficial to reference values through variables in Terraform modules?**

Referencing values through variables in Terraform modules provides several benefits:
1. **Reusability**: Modules can be reused across different environments by simply changing the input variables.
2. **Maintainability**: Changes to common values (like environment prefixes or availability zones) only need to be made in one place, reducing the risk of inconsistencies.
3. **Flexibility**: Different configurations can be achieved by altering the input variables without modifying the module's core logic.
4. **Clarity**: The use of descriptive variable names improves the readability and understanding of the Terraform configuration.

**Q4. What steps would you take to resolve the error related to the missing `entry_script.sh` file in the Terraform module?**

To resolve the error related to the missing `entry_script.sh` file, follow these steps:
1. Ensure that the `entry_script.sh` file exists in the correct directory. If it was moved or deleted, restore it to its original location.
2. If the file needs to be accessible from multiple modules, consider placing it in a shared directory and updating the file paths accordingly.
3. Verify the file path specified in the Terraform configuration matches the actual location of the `entry_script.sh` file.
4. If the file is intended to be in the root module, ensure it is correctly referenced using a relative path from the root module.

**Q5. How would you output the public IP address of the EC2 instance from a Terraform module?**

To output the public IP address of the EC2 instance from a Terraform module, follow these steps:
1. In the `outputs.tf` file of the web server module, define an output for the EC2 instance's public IP address:
   ```terraform
   output "public_ip" {
     value = aws_instance.server.public_ip
   }
   ```
2. In the root `main.tf` file, reference the module output to access the public IP address:
   ```terraform
   module "my_app_server" {
     source = "./modules/web_server"
     # other variables
   }

   output "app_server_public_ip" {
     value = module.my_app_server.public_ip
   }
   ```

This setup ensures that the public IP address of the EC2 instance is accessible and can be used in further configurations or scripts.

**Q6. Discuss recent real-world examples where modularizing Terraform configurations helped in managing complex cloud infrastructures.**

Modularizing Terraform configurations has been crucial in managing complex cloud infrastructures, especially in large organizations. For instance, during the migration of systems to the cloud, companies like Netflix and Shopify have extensively used Terraform modules to manage their infrastructure. By breaking down their infrastructure into smaller, reusable modules, they can efficiently manage updates and deployments across multiple environments. Additionally, in cases like the Capital One breach (CVE-2019-11510), modularization helped in quickly identifying and isolating affected components, thereby facilitating faster recovery and mitigation efforts.

---
<!-- nav -->
[[07-Web Server Configuration Module Extraction|Web Server Configuration Module Extraction]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/22-Web Server Configuration Module Extraction/00-Overview|Overview]]
