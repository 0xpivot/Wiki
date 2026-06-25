---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the purpose of the `terraform plan` command and how does it differ from `terraform apply`?**

The `terraform plan` command is used to preview the changes that would be made to the infrastructure if the `terraform apply` command were executed. It generates a plan file that outlines the actions Terraform will take to bring the current state into alignment with the desired state specified in the configuration files. The key difference is that `terraform plan` does not actually make any changes; it only shows what would happen. In contrast, `terraform apply` executes the changes outlined in the plan.

**Q2. How can you use the `auto-approve` flag with the `terraform apply` command? Provide an example.**

The `auto-approve` flag can be used with the `terraform apply` command to automatically approve the changes without requiring manual confirmation. This is useful in automated environments or scripts where user interaction is not feasible. Here’s an example:

```bash
terraform apply --auto-approve
```

This command will apply the changes described in the plan without prompting for confirmation.

**Q3. Explain the use case for the `terraform destroy` command. How does it differ from specifying a target resource to destroy?**

The `terraform destroy` command is used to remove all resources defined in the Terraform configuration files. When executed without specifying a target, it will destroy all resources in the correct order based on dependencies. This is different from destroying a specific resource because it ensures that all resources are cleaned up properly, respecting the order of dependencies. For example:

```bash
terraform destroy
```

This command will prompt for confirmation before proceeding unless the `auto-approve` flag is used. After confirming, it will remove all resources as defined in the configuration.

**Q4. Why is the `terraform destroy` command particularly useful when testing resources?**

The `terraform destroy` command is particularly useful when testing resources because it allows for easy cleanup after testing. Since it handles the destruction of all resources in the correct order, it ensures that no orphaned resources are left behind, which could cause issues in future tests. This makes it easier to start with a clean slate each time, ensuring that tests are isolated and repeatable.

**Q5. Describe a scenario where the `terraform plan` command would be especially helpful.**

A scenario where the `terraform plan` command would be especially helpful is when multiple developers are working on a project and the current state of the infrastructure is unknown. By running `terraform plan`, a developer can see the differences between the current state and the desired state specified in the configuration files. This helps in understanding what changes will be made without actually applying them, allowing for better collaboration and reducing the risk of unintended changes.

**Q6. How can you ensure that the `terraform destroy` command is executed safely and does not accidentally delete important resources outside of the defined configuration?**

To ensure that the `terraform destroy` command is executed safely and does not accidentally delete important resources outside of the defined configuration, it is crucial to:

1. **Review the Configuration**: Ensure that the Terraform configuration files accurately represent the resources you intend to manage.
2. **Use State Files**: Terraform maintains state files that track the current state of the infrastructure. These should be reviewed to ensure they match the intended resources.
3. **Test in Isolated Environments**: Before running `terraform destroy` in production, test it in isolated environments or staging areas to verify its behavior.
4. **Confirm Before Execution**: Always review the output of `terraform destroy` before confirming the action, especially if the `auto-approve` flag is not used.

By following these steps, you can minimize the risk of accidental deletions and ensure that only the intended resources are affected.

---
<!-- nav -->
[[04-Understanding Terraform `plan` Command and Resource Removal|Understanding Terraform `plan` Command and Resource Removal]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/17-Terraform Plan Command Preview Without Application/00-Overview|Overview]]
