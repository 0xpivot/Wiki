---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Handling Local Files with Terraform

Terraform provides a `local` provider for handling local files. This is useful when you need to create or modify files on your local machine as part of your Terraform workflow.

### What is the Local Provider?

The `local` provider is a built-in Terraform provider that allows you to manage local files and directories. It supports operations such as creating, modifying, and deleting files.

### Why Use the Local Provider?

Using the `local` provider instead of simple shell commands (`local-exec`) has several advantages:

1. **State Management**: The `local` provider maintains state, allowing Terraform to detect changes and apply them accordingly.
2. **Declarative Model**: It aligns with Terraform's declarative model, making it easier to manage and understand your infrastructure.

### Example: Creating a Local File

```hcl
provider "local" {}

resource "local_file" "example" {
  filename = "/tmp/example.txt"
  content  = "Hello, World!"
}
```

In this example, Terraform creates a file named `/tmp/example.txt` with the content "Hello, World!".

### How to Prevent / Defend

#### Detection

Use tools like `git` to track changes to your local files and ensure that they are properly version-controlled.

#### Prevention

1. **Version Control**: Store your Terraform configurations in a version control system.
2. **Automated Testing**: Implement automated tests to verify the correctness of your local file operations.

### Real-World Example: CVE-2-2021-20226

CVE-2021-20226 was a vulnerability in the AWS SDK for Python that allowed unauthorized access to S3 buckets. Proper use of the `local` provider could have helped mitigate this by ensuring that sensitive information was not stored in plain text files.

### Mermaid Diagram: Local File Creation

```mermaid
graph TD
  A[Terraform] --> B[Local Provider]
  B --> C[Create Local File]
  C --> D[/tmp/example.txt]
```

---
<!-- nav -->
[[06-Executing User Data Scripts with Terraform|Executing User Data Scripts with Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/09-Executing User Data Scripts with Terraform/00-Overview|Overview]] | [[08-Integrating Terraform with CICD Pipelines|Integrating Terraform with CICD Pipelines]]
