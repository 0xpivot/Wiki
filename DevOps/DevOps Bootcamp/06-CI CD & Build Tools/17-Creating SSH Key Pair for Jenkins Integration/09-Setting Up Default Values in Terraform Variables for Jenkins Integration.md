---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up Default Values in Terraform Variables for Jenkins Integration

### Background Theory

Terraform is an infrastructure as code (IaC) tool that allows you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). These configuration files can be managed through Continuous Integration and Continuous Deployment (CI/CD) pipelines, such as those orchestrated by Jenkins.

When working with Terraform, you often need to pass variables to your configuration files. These variables can represent various aspects of your infrastructure, such as network configurations, environment settings, and more. Managing these variables effectively is crucial for maintaining consistency and flexibility in your CI/CD pipeline.

### Default Values in Terraform Variables

One of the most efficient ways to manage variables in Terraform is by setting default values. This approach ensures that you don't have to specify every variable manually each time you run your Terraform configuration. Instead, you can rely on predefined defaults and only override them when necessary.

#### Why Use Default Values?

Using default values in Terraform variables offers several benefits:

1. **Consistency**: Default values ensure that certain variables are consistently set across different environments unless explicitly overridden.
2. **Efficiency**: You don't need to specify every variable manually, reducing the chance of human error.
3. **Flexibility**: You can still override default values when needed, providing the flexibility to adapt to different scenarios.

#### How to Set Default Values

To set default values in Terraform, you define them within your `.tf` files. Here’s an example of how to define default values for variables:

```hcl
variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  default     = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
  description = "The CIDR block for the subnet."
  default     = "10.0.1.0/24"
}

variable "environment" {
  description = "The environment name (e.g., dev, staging, prod)."
  default     = "dev"
}
```

In this example, `vpc_cidr_block`, `subnet_cidr_block`, and `environment` are defined with default values. These defaults can be overridden when running Terraform commands.

### Overriding Default Values in Jenkins

In a Jenkins CI/CD pipeline, you can override these default values by passing them as parameters. This allows you to dynamically configure your infrastructure based on the specific environment or requirements of the deployment.

Here’s an example of how you might set up a Jenkins pipeline to override these default values:

```groovy
pipeline {
    agent any

    environment {
        TF_VAR_vpc_cidr_block = "${params.VPC_CIDR_BLOCK}"
        TF_VAR_subnet_cidr_block = "${params.SUBNET_CIDR_BLOCK}"
        TF_VAR_environment = "${params.ENVIRONMENT}"
    }

    stages {
        stage('Initialize') {
            steps {
                script {
                    sh 'terraform init'
                }
            }
        }
        stage('Plan') {
            steps {
                script {
                    sh 'terraform plan'
                }
            }
        }
        stage('Apply') {
            steps {
                script {
                    sh 'terraform apply -auto-approve'
                }
            }
        }
    }
}
```

In this Jenkins pipeline, the `environment` block sets the Terraform variables using the `TF_VAR_` prefix followed by the variable name. These values are passed as parameters (`params.VPC_CIDR_BLOCK`, `params.SUBNET_CIDR_BLOCK`, `params.ENVIRONMENT`) to the pipeline.

### Real-World Example: Recent Breaches and CVEs

Consider a recent breach where an attacker exploited misconfigured network settings in a cloud environment. In this case, the attacker was able to access sensitive resources due to incorrect subnet configurations. By using default values and overriding them only when necessary, you can reduce the risk of such misconfigurations.

For instance, a CVE (Common Vulnerabilities and Exposures) might highlight a situation where default network settings were not properly secured, leading to unauthorized access. By ensuring that your default values are secure and only overridden when necessary, you can mitigate such risks.

### Pitfalls and Common Mistakes

While using default values can be highly beneficial, there are some common pitfalls to watch out for:

1. **Over-reliance on Defaults**: Relying too heavily on default values can lead to inflexibility and potential security issues if the defaults are not secure.
2. **Incorrect Override Logic**: Incorrectly overriding default values in your CI/CD pipeline can lead to unexpected behavior and misconfigurations.
3. **Security Risks**: Using default values that are not secure can expose your infrastructure to vulnerabilities.

### How to Prevent / Defend

To prevent and defend against the risks associated with managing Terraform variables, follow these best practices:

#### Secure Default Values

Ensure that your default values are secure and appropriate for your environment. For example, use secure default values for network settings and environment configurations.

#### Secure-Coding Fixes

Show the vulnerable pattern and the corrected secure version side by side:

**Vulnerable Pattern:**
```hcl
variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  default     = "0.0.0.0/0"  # Insecure default value
}
```

**Secure Pattern:**
```hcl
variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  default     = "10.0.0.0/16"  # Secure default value
}
```

#### Configuration Hardening

Use tools like `tfsec` to scan your Terraform configurations for security issues. Ensure that your default values are reviewed and validated regularly.

#### Detection and Mitigation

Implement monitoring and logging to detect any unauthorized changes to your infrastructure. Use tools like `terraform state` to track changes and validate configurations.

### Complete Example: Full HTTP Request and Response

Here’s a complete example of a full HTTP request and response for a Jenkins API call to set Terraform variables:

**HTTP Request:**
```http
POST /job/my-job/buildWithParameters HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

VPC_CIDR_BLOCK=10.0.0.0%2F16&SUBNET_CIDR_BLOCK=10.0.1.0%2F24&ENVIRONMENT=prod
```

**HTTP Response:**
```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Jenkins
Location: http://jenkins.example.com/job/my-job/1/

{"status":"success","message":"Build triggered successfully"}
```

### Mermaid Diagrams

#### Network Topology

```mermaid
graph TB
  A[VPC] -- "CIDR Block: 10.0.0.0/16" --> B[Subnet]
  B -- "CIDR Block: 10.0.1.0/24" --> C[Instance]
```

#### Request/Response Flow

```mermaid
sequenceDiagram
  participant Jenkins
  participant Terraform
  participant User

  User->>Jenkins: Trigger Build with Parameters
  Jenkins->>Terraform: Initialize with Default Values
  Terraform-->>Jenkins: Plan and Apply
  Jenkins-->>User: Build Success
```

### Practice Labs

For hands-on practice with Terraform and Jenkins integration, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on CI/CD pipeline security.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Useful for learning about web application security.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in managing Terraform variables and integrating them with Jenkins pipelines.

By following these detailed explanations and best practices, you can effectively manage Terraform variables in your CI/CD pipeline, ensuring both efficiency and security.

---
<!-- nav -->
[[08-Setting Up Credentials for Jenkins Integration with Terraform|Setting Up Credentials for Jenkins Integration with Terraform]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/17-Creating SSH Key Pair for Jenkins Integration/00-Overview|Overview]] | [[10-Timing Issues in CICD Pipelines|Timing Issues in CICD Pipelines]]
