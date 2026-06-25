---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Terraform Basics for Infrastructure Provisioning

### Introduction to Terraform

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform can manage a wide range of cloud resources, including virtual machines, storage, databases, and networking components, across multiple cloud providers and on-premises environments.

The core idea behind Terraform is to enable developers and operations teams to describe their infrastructure in code, which can then be version-controlled, tested, and deployed consistently. This approach helps in automating the provisioning process, reducing human error, and ensuring that the infrastructure is consistent across different environments.

### Desired State Configuration

One of the key concepts in Terraform is **desired state configuration**. In this model, you define the desired state of your infrastructure in a configuration file. Terraform then compares the current state of your infrastructure with the desired state and calculates the steps required to transition from the current state to the desired state.

#### How Desired State Configuration Works

When you run Terraform, it performs the following steps:

1. **Read**: Terraform reads the configuration files and the state file (if one exists).
2. **Plan**: Terraform generates a plan that outlines the actions needed to achieve the desired state.
3. **Apply**: Terraform applies the plan, making changes to the infrastructure.

This process ensures that your infrastructure is always in sync with the desired state defined in the configuration files.

```mermaid
sequenceDiagram
    participant User
    participant Terraform
    participant Provider
    participant Infrastructure

    User->>Terraform: Run terraform init
    Terraform->>Provider: Initialize providers
    Provider-->>Terraform: Providers initialized
    Terraform->>Infrastructure: Read current state
    Infrastructure-->>Terraform: Current state data
    User->>Terraform: Run terraform plan
    Terraform->>Provider: Generate plan
    Provider-->>Terraform: Plan generated
    User->>Terraform: Run terraform apply
    Terraform->>Provider: Apply plan
    Provider-->>Terraform: Changes applied
    Terraform->>Infrastructure: Update state
    Infrastructure-->>Terraform: Updated state data
```

### Providers

Providers are plugins that Terraform uses to interact with different cloud providers and services. Each provider is responsible for managing a specific set of resources. For example, the `aws` provider manages AWS resources, while the `kubernetes` provider manages Kubernetes resources.

#### Types of Providers

Terraform supports over 100 providers, covering a wide range of cloud and on-premises environments. Some common providers include:

- **AWS Provider**: Manages AWS resources such as EC2 instances, S3 buckets, RDS databases, and more.
- **Azure Provider**: Manages Azure resources such as virtual machines, storage accounts, SQL databases, and more.
- **Google Cloud Provider**: Manages Google Cloud resources such as Compute Engine instances, Cloud Storage buckets, and more.
- **Kubernetes Provider**: Manages Kubernetes resources such as deployments, services, and namespaces.
- **Software as a Service (SaaS) Providers**: Manage resources provided by SaaS platforms such as GitHub, Slack, and more.

#### Example: AWS Provider

Let's look at an example of using the AWS provider to create an EC2 instance.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

In this example, we define an AWS provider with the `region` attribute set to `us-west-2`. We then define an `aws_instance` resource with the specified AMI and instance type. The `tags` block adds a tag to the instance.

#### Example: Kubernetes Provider

Now let's look at an example of using the Kubernetes provider to create a deployment.

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_deployment" "example" {
  metadata {
    name = "example-deployment"
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "example"
      }
    }

    template {
      metadata {
        labels = {
          app = "example"
        }
      }

      spec {
        container {
          image = "nginx:latest"
          name  = "nginx"
        }
      }
    }
  }
}
```

In this example, we define a Kubernetes provider with the `config_path` attribute set to the path of the Kubernetes configuration file. We then define a `kubernetes_deployment` resource with the specified metadata and spec.

### Managing Resources Across Multiple Providers

One of the powerful features of Terraform is its ability to manage resources across multiple providers. This allows you to create complex infrastructure setups that span multiple cloud providers and on-premises environments.

For example, you might want to create an AWS infrastructure, then deploy Kubernetes on top of it, and then create services inside that Kubernetes cluster. Terraform makes this possible by allowing you to define resources across multiple providers in a single configuration file.

#### Example: Multi-Provider Setup

Let's look at an example of a multi-provider setup that creates an AWS infrastructure and deploys Kubernetes on top of it.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "example" {
  metadata {
    name = "example-namespace"
  }
}

resource "kubernetes_deployment" "example" {
  metadata {
    name = "example-deployment"
    namespace = kubernetes_namespace.example.metadata[0].name
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "example"
      }
    }

    template {
      metadata {
        labels = {
          app = "example"
        }
      }

      spec {
        container {
          image = "nginx:latest"
          name  = "nginx"
        }
      }
    }
  }
}
```

In this example, we define an AWS provider and create an AWS VPC and subnet. We then define a Kubernetes provider and create a Kubernetes namespace and deployment. The deployment is created in the namespace defined earlier.

### Common Pitfalls and Best Practices

While Terraform is a powerful tool, there are several common pitfalls and best practices to keep in mind when using it.

#### Common Pitfalls

1. **State Management**: Terraform relies on a state file to track the current state of your infrastructure. Losing or corrupting this file can lead to issues. Always back up your state file and consider using remote state storage.
2. **Resource Dependencies**: Terraform automatically detects dependencies between resources based on the configuration. However, sometimes you may need to explicitly define dependencies using the `depends_on` attribute.
3. **Configuration Drift**: Configuration drift occurs when the actual state of your infrastructure diverges from the desired state defined in the configuration files. Regularly running `terraform plan` can help identify and address configuration drift.

#### Best Practices

1. **Version Control**: Store your Terraform configuration files in a version control system like Git. This allows you to track changes, collaborate with others, and roll back to previous versions if needed.
2. **Modular Design**: Break down your configuration into smaller, reusable modules. This makes it easier to manage and maintain your infrastructure.
3. **Testing**: Regularly test your Terraform configurations using tools like `terraform validate` and `terraform plan`. Consider using automated testing frameworks like Terratest to ensure your configurations work as expected.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-39294

CVE-2021-39294 is a vulnerability in the AWS SDK for Python (Boto3) that could allow an attacker to bypass authentication and gain unauthorized access to AWS resources. This vulnerability highlights the importance of keeping your dependencies up to date and using secure coding practices.

#### Example: CVE-2021-21277

CVE-2021-21277 is a vulnerability in the Kubernetes API server that could allow an attacker to bypass authentication and gain unauthorized access to Kubernetes resources. This vulnerability underscores the importance of securing your Kubernetes clusters and using secure configuration practices.

### How to Prevent / Defend

#### Detection

To detect potential issues with your Terraform configurations, you can use tools like `terraform validate` and `terraform plan`. These tools can help you identify syntax errors, missing dependencies, and other issues before applying the configuration.

#### Prevention

To prevent issues with your Terraform configurations, follow these best practices:

1. **Keep Dependencies Up to Date**: Regularly update your dependencies to ensure you have the latest security patches and bug fixes.
2. **Use Secure Coding Practices**: Follow secure coding practices when writing your Terraform configurations. Avoid hardcoding sensitive information like passwords and API keys. Instead, use environment variables or secrets management tools.
3. **Secure Your Infrastructure**: Secure your infrastructure by using strong authentication mechanisms, enabling encryption, and limiting access to sensitive resources.

#### Secure-Coding Fixes

Here is an example of a vulnerable Terraform configuration and the corresponding secure version:

**Vulnerable Configuration**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example-bucket"
  acl    = "public-read"
}
```

In this example, the S3 bucket is configured with public read access, which could allow unauthorized access to the bucket.

**Secure Configuration**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example-bucket"
  acl    = "private"
}
```

In this example, the S3 bucket is configured with private access, which restricts access to the bucket.

### Complete Example: Full HTTP Request and Response

Here is an example of a full HTTP request and response for creating an AWS S3 bucket using the AWS SDK for Python (Boto3).

**HTTP Request**

```http
POST / HTTP/1.1
Host: s3.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=fe5f356c79c11be244a388d5b7ed0c1d75a40f7893a30de1be58e6cfb05ebc5b
X-Amz-Date: 20150101T120000Z
X-Amz-Content-Sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
Content-Length: 105

Action=CreateBucket&Bucket=example-bucket&Acl=private
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/xml
Content-Length: 283
Date: Thu, 01 Jan 2015 12:00:00 GMT
Server: AmazonS3

<?xml version="1.0" encoding="UTF-8"?>
<CreateBucketResponse xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <CreateBucketResult>
    <Location>http://example-bucket.s3.amazonaws.com/</Location>
  </CreateBucketResult>
</CreateBucketResponse>
```

### Practice Labs

To practice using Terraform, consider the following well-known labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for learning web security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web security.
- **CloudGoat**: A collection of vulnerable cloud infrastructure configurations for practicing cloud security.
- **flaws.cloud**: A cloud-native security training platform for practicing cloud security.
- **flaws2.cloud**: Another cloud-native security training platform for practicing cloud security.
- **AWS Official Workshops**: Official AWS workshops for learning about AWS services and best practices.
- **Pacu**: A penetration testing framework for AWS.
- **Kubernetes Goat**: A collection of vulnerable Kubernetes configurations for practicing Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges for learning about cryptography and secure coding.
- **kube-hunter**: A tool for hunting for misconfigurations and vulnerabilities in Kubernetes clusters.

By following these best practices and using the recommended labs, you can effectively learn and practice using Terraform for infrastructure provisioning.

---
<!-- nav -->
[[04-Introduction to Terraform|Introduction to Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/00-Overview|Overview]] | [[06-Terraform Basics|Terraform Basics]]
