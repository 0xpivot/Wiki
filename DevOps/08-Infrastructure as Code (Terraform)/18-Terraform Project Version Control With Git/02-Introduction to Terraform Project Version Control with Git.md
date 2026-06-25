---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform Project Version Control with Git

In this section, we will delve into the process of managing Terraform projects using Git for version control. This is a crucial aspect of DevOps practices, ensuring that infrastructure as code (IaC) is properly tracked, versioned, and collaboratively managed. We'll cover the steps involved in setting up a Git repository for a Terraform project, committing changes, and pushing them to a remote repository. Additionally, we'll explore the importance of maintaining a list of providers and their versions within the repository, along with best practices for working with branches and making changes.

### What is Terraform?

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud, and many others. By using Terraform, you can manage your infrastructure in a consistent and repeatable manner, reducing the risk of human error and ensuring that your infrastructure is always in the desired state.

### What is Git?

Git is a distributed version control system that tracks changes in files and directories. It was created by Linus Torvalds in 2005 and has since become the most widely used version control system in the world. Git allows developers to collaborate on projects, track changes, and maintain a history of modifications. It is particularly useful for managing codebases, but it can also be used for other types of files, such as configuration files, documentation, and more.

### Why Use Git with Terraform?

Using Git with Terraform provides several benefits:

1. **Version Control**: Git allows you to track changes to your Terraform configuration files, ensuring that you can revert to previous versions if needed.
2. **Collaboration**: Multiple team members can work on the same Terraform project simultaneously, with Git helping to manage conflicts and merge changes.
3. **History Tracking**: Git maintains a complete history of changes, allowing you to understand how your infrastructure has evolved over time.
4. **Branch Management**: You can create branches to experiment with new features or configurations without affecting the main codebase.

### Setting Up a Git Repository for a Terraform Project

To set up a Git repository for a Terraform project, follow these steps:

1. **Initialize a Git Repository**:
   ```bash
   git init
   ```

2. **Create a `.gitignore` File**:
   Create a `.gitignore` file to exclude unnecessary files and directories from being tracked by Git. For Terraform, you might want to exclude the `.terraform` directory and any `.tfstate` files.
   ```plaintext
   .terraform/
   *.tfstate
   *.tfstate.*
   ```

3. **Add Terraform Configuration Files**:
   Add your Terraform configuration files to the repository.
   ```bash
   git add .
   ```

4. **Initial Commit**:
   Commit the initial set of files to the repository.
   ```bash
   git commit -m "Initial commit of Terraform configuration"
   ```

5. **Push to Remote Repository**:
   Push the changes to a remote repository, such as GitHub, GitLab, or Bitbucket.
   ```bash
   git remote add origin <remote-repository-url>
   git push -u origin master
   ```

### Adding Providers to the Repository

One important aspect of managing Terraform projects with Git is to include a list of providers and their versions within the repository. This ensures that everyone working on the project uses the same versions of the providers, reducing the risk of compatibility issues.

#### What are Terraform Providers?

Terraform providers are plugins that allow Terraform to interact with various cloud providers and services. Each provider is responsible for creating, updating, and destroying resources within its respective cloud environment. Providers are specified in the Terraform configuration files using the `provider` block.

#### Why Include Providers in the Repository?

Including a list of providers and their versions in the repository ensures that everyone working on the project uses the same versions of the providers. This helps to avoid compatibility issues and ensures that the infrastructure is consistently managed across different environments.

#### How to List Providers

You can list the providers and their versions using the `terraform providers` command. This command outputs a list of providers and their versions that are currently installed locally.

```bash
terraform providers
```

The output might look something like this:

```plaintext
Providers required by configuration:
.
├── provider[registry.terraform.io/hashicorp/aws]
│   └── 3.72.0
└── provider[registry.terraform.io/hashicorp/null]
    └── 3.1.0
```

#### Adding Providers to the Repository

To add the list of providers to the repository, you can create a file named `providers.txt` and populate it with the output of the `terraform providers` command.

```bash
terraform providers > providers.txt
```

Then, add the `providers.txt` file to the repository and commit the changes.

```bash
git add providers.txt
git commit -m "Add list of providers and their versions"
```

### Initial Commit and First Push

After setting up the Git repository and adding the Terraform configuration files and the list of providers, you can perform the initial commit and push the changes to the remote repository.

#### Initial Commit

```bash
git commit -m "Initial commit of Terraform configuration and providers"
```

#### First Push

When pushing the changes to the remote repository for the first time, you need to specify the remote repository and the branch you are pushing to.

```bash
git push -u origin master
```

This command does the following:

- `-u`: Sets up tracking information for the current branch and its remote counterpart.
- `origin`: The name of the remote repository.
- `master`: The name of the branch you are pushing to.

### Working with Branches

Once the initial commit and push are complete, you can start working with branches to experiment with different use cases or configurations.

#### Creating a New Branch

To create a new branch, use the `git checkout` command with the `-b` option.

```bash
git checkout -b feature/new-feature
```

This creates a new branch named `feature/new-feature` and switches to it.

#### Making Changes and Committing

Make changes to the Terraform configuration files as needed, then commit the changes to the branch.

```bash
git add .
git commit -m "Add new feature to Terraform configuration"
```

#### Pushing Changes to the Remote Repository

To push the changes to the remote repository, use the `git push` command.

```bash
git push origin feature/new-feature
```

This pushes the changes to the `feature/new-feature` branch on the remote repository.

### History and Collaboration

By using Git with Terraform, you can maintain a complete history of changes to your infrastructure as code. This allows you to understand how your infrastructure has evolved over time and collaborate effectively with other team members.

#### Viewing History

To view the history of commits, use the `git log` command.

```bash
git log
```

This command displays a list of commits, including the author, date, and commit message.

#### Collaborating with Others

When collaborating with others, you can use Git to manage conflicts and merge changes. For example, if someone else makes changes to the same file, you can use the `git pull` command to fetch the latest changes and resolve any conflicts.

```bash
git pull origin master
```

If there are conflicts, Git will prompt you to resolve them manually. Once resolved, you can commit the changes and push them to the remote repository.

### Real-World Examples and Best Practices

#### Recent CVEs and Breaches

While there haven't been specific CVEs targeting Terraform itself, there have been instances where misconfigured Terraform scripts led to security vulnerabilities. For example, a misconfigured AWS S3 bucket could expose sensitive data if the Terraform script did not properly restrict access.

#### Best Practices

1. **Use `.gitignore`**: Ensure that sensitive files, such as `.tfstate`, are excluded from version control.
2. **Maintain Provider Versions**: Keep a list of providers and their versions in the repository to ensure consistency.
3. **Use Branches**: Use branches to experiment with new features or configurations without affecting the main codebase.
4. **Regularly Review Commits**: Regularly review commits to ensure that changes are properly documented and reviewed.

### How to Prevent / Defend

#### Detection

To detect potential issues with Terraform configurations, you can use tools like `tflint` and `tfsec`. These tools help identify common security and compliance issues in Terraform scripts.

```bash
# Install tflint
brew install tflint

# Run tflint
tflint

# Install tfsec
brew install tfsec

# Run tfsec
tfsec
```

#### Prevention

To prevent security vulnerabilities, follow these best practices:

1. **Use Secure Defaults**: Configure resources with secure defaults, such as restricting access to specific IP addresses or using encryption.
2. **Review Changes**: Regularly review changes to Terraform scripts to ensure that they are properly documented and reviewed.
3. **Use Automated Tools**: Use automated tools like `tflint` and `tfsec` to identify and fix common security issues.

#### Secure Coding Fixes

Here is an example of a vulnerable Terraform script and its secure version:

**Vulnerable Script**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
}
```

**Secure Script**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"

  acl = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
```

### Conclusion

Managing Terraform projects with Git is a critical aspect of DevOps practices. By using Git, you can track changes, collaborate with others, and maintain a complete history of your infrastructure as code. This ensures that your infrastructure is consistently managed and reduces the risk of human error. By following best practices and using automated tools, you can further enhance the security and reliability of your Terraform projects.

### Practice Labs

For hands-on practice with Terraform and Git, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, which can be integrated with Terraform for infrastructure management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be deployed using Terraform.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training, which can be deployed using Terraform.
- **WebGoat**: An interactive web application security training tool, which can be deployed using Terraform.

These labs provide practical experience in deploying and managing infrastructure using Terraform and Git, helping you to gain a deeper understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[01-Introduction to Git and Version Control in DevOps|Introduction to Git and Version Control in DevOps]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/18-Terraform Project Version Control With Git/00-Overview|Overview]] | [[03-Introduction to Terraform and Version Control with Git|Introduction to Terraform and Version Control with Git]]
