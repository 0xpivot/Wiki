---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps

Infrastructure as Code (IaC) is a practice where infrastructure is defined and managed through code rather than manual processes. This approach allows for automation, consistency, and version control of infrastructure configurations. GitOps extends this concept by using Git as the single source of truth for infrastructure state and using pull requests to manage changes.

### Background Theory

#### What is Infrastructure as Code?

Infrastructure as Code (IaC) involves defining infrastructure configurations in code, typically using declarative languages like YAML or JSON. This code can then be checked into a version control system (VCS) such as Git, allowing for collaboration, review, and tracking of changes. Tools like Terraform, Ansible, and CloudFormation are commonly used to implement IaC.

#### Why Use Infrastructure as Code?

- **Consistency**: Ensures that environments are consistently provisioned and configured.
- **Automation**: Reduces manual errors and speeds up deployment processes.
- **Version Control**: Allows tracking of changes and rollbacks to previous states.
- **Collaboration**: Facilitates team collaboration and code reviews.

#### How Does Infrastructure as Code Work?

1. **Define Infrastructure**: Write code that defines the desired state of your infrastructure.
2. **Check-in Code**: Commit the code to a VCS like Git.
3. **Apply Changes**: Use tools to apply the code to your infrastructure.
4. **Monitor and Update**: Continuously monitor the infrastructure and update the code as needed.

### Example: AWS Infrastructure as Code

Let’s consider an example where we define AWS infrastructure using Terraform. Here’s a simple Terraform configuration for creating an EC2 instance:

```hcl
provider "aws" {
  region = "eu-west-3"
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t3.small"

  tags = {
    Name = "AppServer"
  }
}
```

This configuration defines an EC2 instance in the `eu-west-3` region with the specified AMI and instance type. The `tags` block adds a name tag to the instance.

### GitOps Overview

GitOps is a set of practices that uses Git as the single source of truth for all infrastructure and application configurations. It leverages Git’s features for collaboration, version control, and continuous integration/continuous delivery (CI/CD).

#### Key Concepts of GitOps

- **Single Source of Truth**: All infrastructure and application configurations are stored in a Git repository.
- **Pull Requests**: Changes are proposed via pull requests, which can be reviewed and merged.
- **Automated Deployment**: Automated tools sync the live environment with the Git repository.

### Example: GitOps with FluxCD

FluxCD is a popular tool for implementing GitOps. Let’s see how we can use FluxCD to manage our AWS infrastructure.

1. **Install FluxCD**: Deploy FluxCD to your Kubernetes cluster.
2. **Define Configurations**: Store your infrastructure and application configurations in a Git repository.
3. **Sync with Git**: Configure FluxCD to sync the live environment with the Git repository.

Here’s a basic example of a FluxCD configuration:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta1
kind: GitRepository
metadata:
  name: infra-repo
spec:
  url: https://github.com/myorg/infra-configs.git
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta1
kind: Kustomization
metadata:
  name: infra-kustomization
spec:
  sourceRef:
    kind: GitRepository
    name: infra-repo
  path: ./kustomize
  interval: 10m
  prune: true
```

This configuration tells FluxCD to watch the `infra-repo` Git repository and apply any changes found in the `./kustomize` directory.

### Automating Infrastructure Provisioning

In the given transcript, we see the process of automatically provisioning resources and registering them with GitLab. Let’s break down the steps involved:

1. **Provision Resources**: Use IaC tools to create and configure resources.
2. **Register Resources**: Automatically register the newly created resources with GitLab.
3. **Verify Configuration**: Ensure that the resources are correctly configured and registered.

### Example: Automating Resource Registration with GitLab

Let’s assume we have an EC2 instance that needs to be registered with GitLab as a runner. Here’s how we can achieve this:

1. **Provision EC2 Instance**: Use Terraform to create the EC2 instance.
2. **Register with GitLab**: Use a script to register the instance as a GitLab runner.

Here’s a sample Terraform configuration for creating an EC2 instance:

```hcl
provider "aws" {
  region = "eu-west-3"
}

resource "aws_instance" "gitlab_runner" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t3.small"

  tags = {
    Name = "GitLabRunner"
  }
}
```

Next, we can use a script to register the instance as a GitLab runner:

```bash
#!/bin/bash

# Get the instance IP address
INSTANCE_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=GitLabRunner" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

# Register the runner with GitLab
curl --request POST --url "https://gitlab.example.com/api/v4/runners" \
     --header "PRIVATE-TOKEN: <your_private_token>" \
     --data "token=<runner_token>&description=$INSTANCE_IP&tag_list=aws"
```

### Security Considerations

When automating infrastructure provisioning, security is paramount. Here are some key considerations:

1. **IAM Roles and Permissions**: Ensure that the roles and permissions assigned to the instances are minimal and necessary.
2. **Secure Communication**: Use secure communication protocols (HTTPS, SSH) for all interactions.
3. **Monitoring and Logging**: Implement monitoring and logging to detect and respond to security incidents.

### Example: Securing IAM Roles

Let’s ensure that the IAM roles assigned to our EC2 instances are secure. Here’s a sample IAM policy for the `AppServer` role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

And here’s the corresponding policy for the `GitRunner` role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Use tools like AWS CloudTrail and CloudWatch to monitor and log all activities.
- **Security Groups**: Configure security groups to restrict access to only necessary ports and IPs.

#### Prevention

- **Least Privilege Principle**: Assign minimal permissions to IAM roles.
- **Regular Audits**: Conduct regular audits of IAM roles and permissions.

#### Secure Coding Fixes

Compare the insecure and secure versions of the IAM policies:

**Insecure Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

**Secure Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-20225**: A vulnerability in AWS CloudFormation templates allowed unauthorized access to sensitive data.
- **Breaches**: Several companies have experienced breaches due to misconfigured IAM roles and permissions.

### Conclusion

By leveraging Infrastructure as Code and GitOps, organizations can automate infrastructure provisioning and management, ensuring consistency, security, and efficiency. Proper implementation and adherence to best practices are crucial to avoid common pitfalls and security risks.

### Practice Labs

For hands-on experience with IaC and GitOps, consider the following labs:

- **Terraform Workshop**: Official Terraform tutorials and workshops.
- **FluxCD Documentation**: Official FluxCD documentation and examples.
- **AWS Well-Architected Labs**: Official AWS labs for practicing IaC and GitOps.

These labs provide practical experience and reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/05-Replace Manually Created Infrastructure with Automatically Provisioned Resources/01-Introduction to IaC and GitOps for DevSecOps|Introduction to IaC and GitOps for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/05-Replace Manually Created Infrastructure with Automatically Provisioned Resources/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/05-Replace Manually Created Infrastructure with Automatically Provisioned Resources/03-Practice Questions & Answers|Practice Questions & Answers]]
