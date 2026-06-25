---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the purpose of using an EKS module in Terraform, and why is it beneficial?**

The purpose of using an EKS module in Terraform is to simplify the creation and management of Amazon EKS clusters. By leveraging a pre-built module, developers can avoid writing extensive Terraform code to manage the numerous resources required for an EKS cluster. This module handles the creation of the cluster, worker nodes, and other necessary Kubernetes resources, making the process more efficient and less error-prone. Additionally, using a module allows for better version control and easier maintenance of the infrastructure.

**Q2. How do you specify the subnets for worker nodes in an EKS cluster using Terraform?**

To specify the subnets for worker nodes in an EKS cluster using Terraform, you need to reference the private subnets from the VPC module. Here’s an example:

```terraform
module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.0"

  cluster_name = "my-app-cluster"
  vpc_id       = module.vpc.vpc_id
  subnets      = module.vpc.private_subnets
  # Other required parameters...
}
```

In this example, `module.vpc.private_subnets` references the private subnets from the VPC module. This ensures that the worker nodes are launched in the private subnets for enhanced security.

**Q3. Explain how to configure the Kubernetes provider in Terraform for an EKS cluster.**

Configuring the Kubernetes provider in Terraform for an EKS cluster involves specifying the cluster endpoint and authentication details. Here’s an example:

```terraform
provider "kubernetes" {
  load_config_file = false
  host             = data.aws_eks_cluster.my_app_cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.my_app_cluster.certificate_authority[0].data)
  token            = data.aws_eks_cluster_auth.my_app_cluster.token
}

data "aws_eks_cluster" "my_app_cluster" {
  name = module.eks_cluster.cluster_name
}

data "aws_eks_cluster_auth" "my_app_cluster" {
  name = module.eks_cluster.cluster_name
}
```

In this example, `data.aws_eks_cluster.my_app_cluster` retrieves the cluster endpoint and CA certificate, while `data.aws_eks_cluster_auth.my_app_cluster` retrieves the authentication token. These values are then passed to the Kubernetes provider to establish a connection to the EKS cluster.

**Q4. What are the benefits of using versioned modules in Terraform, especially when working with EKS clusters?**

Using versioned modules in Terraform provides several benefits, particularly when working with EKS clusters:

1. **Consistency**: Versioned modules ensure that the same version of the module is used across different environments, reducing the risk of inconsistencies.
2. **Debugging**: If issues arise, having specific versions helps in pinpointing the exact module version that might be causing problems.
3. **Compatibility**: Versioning helps maintain compatibility with other modules and providers, ensuring that changes in one module do not break others.
4. **Security**: Versioned modules can be audited and reviewed for security vulnerabilities, ensuring that only trusted versions are used.

For example, using a specific version of the `terraform-aws-modules/eks/aws` module ensures that the EKS cluster is created with a known and tested set of configurations.

**Q5. How would you configure worker nodes in an EKS cluster using Terraform, and what are the advantages of using self-managed EC2 instances over managed node groups?**

Worker nodes in an EKS cluster can be configured using the `worker_groups` attribute in the EKS module. Here’s an example:

```terraform
module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.0"

  cluster_name = "my-app-cluster"
  vpc_id       = module.vpc.vpc_id
  subnets      = module.vpc.private_subnets
  worker_groups = [
    {
      name            = "worker-group-1"
      instance_type   = "t2.small"
      desired_capacity = 2
    },
    {
      name            = "worker-group-2"
      instance_type   = "t2.medium"
      desired_capacity = 1
    }
  ]
  # Other required parameters...
}
```

Advantages of using self-managed EC2 instances over managed node groups include:

1. **Customization**: Self-managed EC2 instances allow for greater customization of the worker nodes, including AMI selection, instance types, and additional software installations.
2. **Control**: Full control over the lifecycle of the EC2 instances, including scaling policies and termination protection.
3. **Cost Management**: Ability to optimize costs by choosing specific instance types and sizes based on workload requirements.

However, managed node groups offer ease of management and automatic scaling, which can be advantageous for certain use cases.

**Q6. What are some recent real-world examples of security breaches involving EKS clusters, and how can they be mitigated?**

One notable example is the breach involving misconfigured EKS clusters that exposed sensitive data due to improper IAM permissions and network configurations. For instance, a misconfigured IAM role allowed unauthorized access to the EKS cluster, leading to potential data exfiltration.

To mitigate such risks:

1. **IAM Permissions**: Ensure that IAM roles assigned to EKS clusters have the least privilege necessary. Regularly review and audit IAM policies.
2. **Network Security**: Use private subnets for worker nodes and restrict access to the EKS API server using security groups and network ACLs.
3. **Encryption**: Enable encryption for EBS volumes and S3 buckets used by the EKS cluster.
4. **Monitoring and Logging**: Implement robust monitoring and logging to detect and respond to suspicious activities promptly.

By following these best practices, organizations can significantly reduce the risk of security breaches involving EKS clusters.

---
<!-- nav -->
[[07-Kubernetes Authentication and Configuration with Terraform|Kubernetes Authentication and Configuration with Terraform]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/10-Creating EKS Cluster Using Terraform Module/00-Overview|Overview]]
