---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it beneficial to separate `outputs`, `variables`, and `providers` into their own `.tf` files in a Terraform project?**

Separating `outputs`, `variables`, and `providers` into their own `.tf` files helps improve the organization and readability of the Terraform configuration. By isolating these components, you can easily locate and manage specific aspects of your infrastructure:

- **Outputs**: Placing outputs in a dedicated `outputs.tf` file allows you to quickly find and modify output definitions without sifting through resource configurations.
- **Variables**: Storing variables in a `variables.tf` file makes it easier to manage input parameters and ensures consistency across your Terraform modules.
- **Providers**: Although less common due to the simplicity of most provider configurations, separating providers into a `providers.tf` file can help maintain clarity, especially in projects with multiple providers.

This separation aligns with best practices in Terraform, promoting modularity and maintainability.

**Q2. How do you create and use a module in Terraform? Provide an example.**

To create and use a module in Terraform, follow these steps:

1. **Create the Module Folder**: Create a folder for the module, e.g., `modules/subnet`.
2. **Define the Module Files**: Inside the module folder, create `main.tf`, `outputs.tf`, and `variables.tf` files.
3. **Define Resources in `main.tf`:** Define the resources that the module will manage. For example, a subnet module might include resources like subnets, internet gateways, and route tables.
4. **Define Outputs in `outputs.tf`:** Define outputs that the module will expose, such as the subnet ID.
5. **Define Variables in `variables.tf`:** Define variables that the module will accept, such as VPC ID and CIDR block.
6. **Reference the Module in the Root Module:** In the root module’s `main.tf`, reference the module using the `module` keyword and provide required variables.

Example:

```hcl
# modules/subnet/main.tf
resource "aws_subnet" "example" {
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block
}

# modules/subnet/outputs.tf
output "subnet_id" {
  value = aws_subnet.example.id
}

# modules/subnet/variables.tf
variable "vpc_id" {}
variable "cidr_block" {}

# root/main.tf
module "subnet_module" {
  source = "./modules/subnet"
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block
}
```

**Q3. Explain why creating a module for just one or two resources is generally not recommended.**

Creating a module for just one or two resources is generally not recommended because it does not provide significant benefits and can introduce unnecessary complexity. Here are the reasons:

- **Overhead**: Managing a module introduces overhead, such as defining variables, outputs, and potentially managing additional files. For a small number of resources, this overhead outweighs the benefits.
- **Modularity**: The primary benefit of modules is to encapsulate related resources and promote reuse. A module with just one or two resources does not achieve this goal effectively.
- **Readability**: Keeping a small number of resources in a single file can often be more readable and maintainable than splitting them into a separate module.

Instead, modules should be designed to group logically related resources together, providing a clear abstraction and promoting reuse across different parts of your infrastructure.

**Q4. How do you reference a resource created by a module in another module? Provide an example.**

To reference a resource created by a module in another module, you need to use the `module` keyword followed by the module name and the output name. Here’s an example:

1. **Define the Module**: Create a module that defines a subnet and exposes the subnet ID as an output.

```hcl
# modules/subnet/main.tf
resource "aws_subnet" "example" {
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block
}

# modules/subnet/outputs.tf
output "subnet_id" {
  value = aws_subnet.example.id
}

# modules/subnet/variables.tf
variable "vpc_id" {}
variable "cidr_block" {}
```

2. **Reference the Module**: In the root module, reference the subnet module and use the output in another resource.

```hcl
# root/main.tf
module "subnet_module" {
  source = "./modules/subnet"
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block
}

resource "aws_instance" "example" {
  ami           = var.ami
  instance_type = var.instance_type
  subnet_id     = module.subnet_module.subnet_id
}
```

In this example, the `aws_instance` resource references the `subnet_id` output from the `subnet_module`.

**Q5. What is the purpose of the `terraform init` command when working with modules?**

The `terraform init` command initializes the Terraform working directory and sets up any necessary modules and providers. When working with modules, `terraform init` performs the following tasks:

- **Initialize Modules**: It initializes any modules referenced in the configuration, ensuring that the module sources are properly resolved and downloaded.
- **Configure Providers**: It configures any providers specified in the Terraform configuration, ensuring that the necessary plugins are installed.
- **Backend Configuration**: If a backend is configured, `terraform init` initializes the backend, preparing it for state management.

Running `terraform init` is crucial when you add, remove, or update modules in your Terraform configuration. It ensures that Terraform has the latest information about the modules and providers it needs to manage your infrastructure.

**Q6. How do you handle variables in a module and pass them from the root module? Provide an example.**

Handling variables in a module involves defining them in the module’s `variables.tf` file and passing them from the root module. Here’s an example:

1. **Define Variables in the Module**: Define the variables in the module’s `variables.tf` file.

```hcl
# modules/subnet/variables.tf
variable "vpc_id" {}
variable "cidr_block" {}
```

2. **Use Variables in the Module**: Use the variables in the module’s `main.tf` file.

```hcl
# modules/subnet/main.tf
resource "aws_subnet" "example" {
  vpc_id     = var.v_`vpc_id`
  cidr_block = var.cidr_block
}
```

3. **Pass Variables from the Root Module**: Pass the variables from the root module to the module.

```hcl
# root/main.tf
module "subnet_module" {
  source = "./modules/subnet"
  vpc_id     = var.vpc_id
  cidr_block = var.cidr_block
}
```

In this example, the root module passes the `vpc_id` and `cidr_block` variables to the `subnet_module`. The module uses these variables to configure the subnet resource.

**Q7. What is the significance of the `outputs.tf` file in a module? Provide an example.**

The `outputs.tf` file in a module is significant because it defines the outputs that the module exposes to the rest of the Terraform configuration. Outputs allow you to return values from the module, such as resource IDs or other computed values, which can be used in other parts of your configuration.

Here’s an example:

```hcl
# modules/subnet/outputs.tf
output "subnet_id" {
  value = aws_subnet.example.id
}
```

In this example, the `subnet_id` output returns the ID of the subnet resource created by the module. This output can be referenced in other parts of the Terraform configuration, such as in the root module or other modules.

**Q8. How do you ensure that a module is properly initialized and ready for use in a Terraform project?**

To ensure that a module is properly initialized and ready for use in a Terraform project, follow these steps:

1. **Run `terraform init`:** Run the `terraform init` command to initialize the Terraform working directory and set up any necessary modules and providers.
2. **Check Module Sources:** Ensure that the module sources are correctly specified and accessible. This includes checking that the paths to local modules are correct and that remote modules are properly referenced.
3. **Verify Variables:** Ensure that all required variables for the module are defined and properly passed from the root module.
4. **Run `terraform validate`:** Optionally, run the `terraform validate` command to check for any syntax errors or issues in the Terraform configuration.
5. **Plan and Apply:** Run `terraform plan` to preview the changes that Terraform will make, and then run `terraform apply` to apply the changes.

By following these steps, you can ensure that the module is properly initialized and ready for use in your Terraform project.

---
<!-- nav -->
[[03-Creating Reusable Modules in Terraform Projects|Creating Reusable Modules in Terraform Projects]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/07-Creating Reusable Modules in Terraform Projects/00-Overview|Overview]]
