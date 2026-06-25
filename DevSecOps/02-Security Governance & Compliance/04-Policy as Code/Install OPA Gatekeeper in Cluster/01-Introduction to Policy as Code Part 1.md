---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is a practice that involves defining, deploying, and managing infrastructure policies using code. This approach allows organizations to enforce consistent policies across their infrastructure, ensuring compliance and security. One of the key tools used for implementing Policy as Code is Open Policy Agent (OPA), specifically through its Gatekeeper component. In this section, we will delve into the installation and configuration of OPA Gatekeeper within a Kubernetes cluster.

### What is Open Policy Agent (OPA)?

Open Policy Agent (OPA) is an open-source, general-purpose policy engine that enables organizations to define, enforce, and manage policies across various systems and services. OPA provides a declarative language called Rego, which allows you to express complex policies in a simple and readable manner. OPA can be integrated with different systems, including Kubernetes, to enforce policies at runtime.

### What is Gatekeeper?

Gatekeeper is a Kubernetes-native policy controller built on top of OPA. It allows you to define and enforce policies as Custom Resource Definitions (CRDs) within your Kubernetes cluster. By leveraging Gatekeeper, you can ensure that your cluster adheres to specific policies, such as resource limits, security configurations, and compliance requirements.

### Why Use Gatekeeper?

Using Gatekeeper offers several benefits:

- **Centralized Policy Management**: Gatekeeper allows you to define policies in a centralized location, making it easier to manage and enforce them across your cluster.
- **Runtime Enforcement**: Policies can be enforced at runtime, ensuring that resources are created and modified according to the defined rules.
- **Customizable Policies**: You can create custom policies using Rego, allowing you to tailor the enforcement to your specific needs.
- **Integration with CI/CD Pipelines**: Gatekeeper can be integrated with CI/CD pipelines to ensure that policies are checked during the build and deployment processes.

### Installing Gatekeeper Using Terraform

To install Gatekeeper in a Kubernetes cluster, we will use Terraform, a popular infrastructure-as-code tool. Terraform allows you to define your infrastructure in code, making it easier to manage and version control.

#### Step-by-Step Installation

1. **Create a Terraform Configuration File**

   We will start by creating a Terraform configuration file named `gatekeeper.tf`. This file will contain the necessary configuration to install Gatekeeper using a Helm chart.

   ```hcl
   # gatekeeper.tf

   provider "helm" {
     kubernetes {
       config_path = "~/.kube/config"
     }
   }

   resource "helm_release" "gatekeeper" {
     name       = "gatekeeper"
     repository = "https://open-policy-agent.github.io/gatekeeper/charts"
     chart      = "gatekeeper"
     version    = "3.10.0"

     set {
       name  = "namespace"
       value = "gatekeeper-system"
     }

     set {
       name  = "image.tag"
       value = "v3.10.0"
     }

     depends_on = [module.eks]
   }
   ```

   - **provider "helm"**: This block defines the Helm provider, which is used to interact with Helm charts.
   - **resource "helm_release" "gatekeeper"**: This block defines the Helm release for Gatekeeper.
     - **name**: The name of the Helm release.
     - **repository**: The URL of the Helm chart repository.
     - **chart**: The name of the Helm chart.
     - **version**: The version of the Helm chart to be installed.
     - **set**: Additional settings for the Helm chart, such as the namespace and image tag.
     - **depends_on**: Ensures that the EKS module is deployed before the Gatekeeper Helm chart.

2. **Define the EKS Module**

   The EKS module is responsible for setting up the Amazon Elastic Kubernetes Service (EKS) cluster. This module should be defined in a separate file, such as `eks.tf`.

   ```hcl
   # eks.tf

   module "eks" {
     source = "terraform-aws-modules/eks/aws"

     cluster_name = "my-cluster"
     version      = "1.21"

     vpc_id            = "vpc-12345678"
     subnet_ids        = ["subnet-12345678", "subnet-87654321"]
     public_subnet_ids = ["subnet-12345678", "subnet-87654321"]

     worker_groups = [
       {
         name            = "worker-group-1"
         instance_type   = "t3.micro"
         desired_capacity = 2
       }
     ]
   }
   ```

   - **module "eks"**: Defines the EKS module.
     - **source**: The source of the EKS module.
     - **cluster_name**: The name of the EKS cluster.
     - **version**: The Kubernetes version.
     - **vpc_id**: The ID of the VPC.
     - **subnet_ids**: The IDs of the private subnets.
     - **public_subnet_ids**: The IDs of the public subnets.
     - **worker_groups**: Defines the worker groups, including the instance type and desired capacity.

3. **Initialize and Apply the Terraform Configuration**

   Once the Terraform configuration files are created, you can initialize and apply the configuration using the following commands:

   ```sh
   terraform init
   terraform apply
   ```

   - **terraform init**: Initializes the Terraform working directory, downloading any required plugins and modules.
   - **terraform apply**: Applies the Terraform configuration, creating the necessary resources in the Kubernetes cluster.

### Understanding the Configuration

Let's break down the configuration in more detail:

- **Helm Chart Repository**: The repository URL (`https://open-policy-agent.github.io/gatekeeper/charts`) points to the official OPA Gatekeeper Helm chart repository.
- **Chart Version**: The version (`3.10.0`) specifies the version of the Gatekeeper Helm chart to be installed.
- **Namespace**: The `namespace` setting ensures that the Gatekeeper controller runs in its own namespace (`gatekeeper-system`). This helps isolate the Gatekeeper components from other resources in the cluster.
- **Image Tag**: The `image.tag` setting specifies the Docker image tag for the Gatekeeper controller.
- **Dependency on EKS Module**: The `depends_on` attribute ensures that the EKS module is deployed before the Gatekeeper Helm chart. This is crucial to avoid errors when the Helm chart tries to access resources that haven't been created yet.

### Full Example of Terraform Configuration

Here is the complete Terraform configuration, including both the `gatekeeper.tf` and `eks.tf` files:

```hcl
# gatekeeper.tf

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "gatekeeper" {
  name       = "gatekeeper"
  repository = "https://open-policy-agent.github.io/gatekeeper/charts"
  chart      = "gate-keeper"
  version    = "3.10.0"

  set {
    name  = "namespace"
    value = "gatekeeper-system"
  }

  set {
    name  = "image.tag"
    value = "v3.10.0"
  }

  depends_on = [module.eks]
}
```

```hcl
# eks.tf

module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = "my-cluster"
  version      = "1.21"

  vpc_id            = "vpc-12345678"
  subnet_ids        = ["subnet-12345678", "subnet-87654321"]
  public_subnet_ids = ["subnet-12345678", "subnet-87654321"]

  worker_groups = [
    {
      name            = "worker-group-1"
      instance_type   = "t3.micro"
      desired_capacity = 2
    }
  ]
}
```

### Deploying the Configuration

To deploy the configuration, follow these steps:

1. **Initialize Terraform**:
   ```sh
   terraform init
   ```

2. **Apply the Configuration**:
   ```sh
   terraform apply
   ```

### Verifying the Deployment

After applying the configuration, you can verify that Gatekeeper is deployed correctly by checking the Kubernetes cluster:

```sh
kubectl get pods -n gatekeeper-system
```

This command should list the Gatekeeper pods running in the `gatekeeper-system` namespace.

### Real-World Examples and Recent CVEs

#### Example: Misconfigured Resource Limits

In a real-world scenario, a misconfigured resource limit could lead to a denial-of-service (DoS) attack. For example, if a pod is allowed to consume unlimited CPU and memory, it could potentially exhaust the available resources in the cluster, causing other critical applications to fail.

**CVE Example**: CVE-2021-25741 - Kubernetes API Server Privilege Escalation Vulnerability

This CVE highlights the importance of enforcing strict resource limits and security policies within a Kubernetes cluster. By using Gatekeeper, you can define and enforce policies that prevent such vulnerabilities.

### How to Prevent / Defend

#### Secure Coding Practices

To prevent misconfigurations and vulnerabilities, follow these secure coding practices:

1. **Define Resource Limits**: Ensure that all pods have defined resource limits to prevent resource exhaustion.
2. **Use Gatekeeper Policies**: Define and enforce policies using Gatekeeper to ensure that resources are configured securely.
3. **Regular Audits**: Perform regular audits of your cluster to identify and remediate misconfigurations.

#### Example: Secure vs. Vulnerable Configuration

**Vulnerable Configuration**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: my-container
        image: my-image
```

**Secure Configuration**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: my-container
        image: my-image
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: "256Mi"
```

### Detection and Prevention

#### Detection

To detect misconfigurations, you can use tools like `kube-bench`, which is a security benchmarking tool for Kubernetes clusters. `kube-bench` checks your cluster against the CIS Kubernetes Benchmark and reports any issues.

```sh
curl -LO https://github.com/aquasecurity/kube-bench/releases/download/v0.6.0/kube-bench_0.6.0_linux_amd64.tar.gz
tar xvf kube-bench_0.6.0_linux_amd64.tar.gz
./kube-bench --version
./kube-bench --targets all --check all
```

#### Prevention

To prevent misconfigurations, you can use Gatekeeper to enforce policies. Here is an example of a Gatekeeper constraint template that enforces resource limits:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg, "details": {"object": obj}}] {
          provided := {k | input.review.object.metadata.labels[k] != null}
          required := {"app", "owner"}
          missing := required - provided
          msg := sprintf("missing labels: %v", [missing])
          obj := sprintf("%v/%v", [input.review.object.kind, input.review.object.metadata.name])
        }
```

### Conclusion

By using Terraform and Gatekeeper, you can effectively manage and enforce policies within your Kubernetes cluster. This approach ensures that your cluster remains secure and compliant with your organization's policies. Regular audits and the use of tools like `kube-bench` can help you detect and prevent misconfigurations.

### Practice Labs

For hands-on experience with Policy as Code and Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that touch on Kubernetes and container security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes. While it focuses on web app security, it can be deployed in a Kubernetes environment to practice securing containerized applications.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes challenges related to securing Kubernetes clusters and implementing policies.

These labs provide practical experience in deploying and managing policies within a Kubernetes environment, helping you to master the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/02-Introduction to Policy as Code Part 2|Introduction to Policy as Code Part 2]]
