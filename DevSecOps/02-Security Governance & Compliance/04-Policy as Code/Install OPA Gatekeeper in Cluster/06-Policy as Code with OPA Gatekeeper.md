---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code with OPA Gatekeeper

### Introduction to Policy as Code

Policy as Code is a practice where policies are defined using code rather than manual configurations. This approach allows for better version control, automation, and consistency across environments. One of the most popular tools for implementing Policy as Code is Open Policy Agent (OPA) with its Kubernetes-specific component, Gatekeeper.

### Why Use OPA Gatekeeper?

OPA Gatekeeper is a powerful tool for enforcing policies in Kubernetes clusters. It integrates seamlessly with Kubernetes and provides a declarative way to define and enforce policies. By using OPA Gatekeeper, you can ensure that your cluster adheres to organizational standards and security requirements.

#### Key Benefits:

- **Consistency**: Policies are defined in code, ensuring that they are applied consistently across different environments.
- **Version Control**: Policies can be stored in version control systems like Git, allowing you to track changes and revert to previous versions if needed.
- **Automation**: Policies can be automatically enforced during deployment, reducing the risk of human error.
- **Flexibility**: OPA supports a wide range of policy languages, including Rego, which is expressive and easy to understand.

### Prerequisites

Before installing OPA Gatekeeper, ensure that you have the following:

- A running Kubernetes cluster.
- `kubectl` installed and configured to interact with your cluster.
- `helm` installed for managing Kubernetes applications.

### Installing OPA Gatekeeper

To install OPA Gatekeeper, follow these steps:

1. **Add the Gatekeeper Helm Repository**:
   ```bash
   helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/helm
   helm repo update
   ```

2. **Install Gatekeeper**:
   ```bash
   helm install gatekeeper gatekeeper/gatekeeper --namespace gatekeeper-system --create-namespace
   ```

### Configuring Node Resources

When deploying resources such as Gatekeeper, Secrets Management, or ArgoCD, it is crucial to ensure that your cluster has sufficient resources to handle these workloads. The initial setup might involve smaller instance types, which may not be sufficient for running these controllers.

#### Instance Types

- **Micro Instances**: These are typically used for lightweight tasks and may not have enough CPU or memory to run complex controllers.
- **Small Instances**: These provide more resources and are suitable for running basic controllers.
- **Medium Instances**: These offer even more resources and are recommended for more demanding workloads.

#### Autoscaling

Kubernetes clusters often come with an autoscaler that can dynamically adjust the number of nodes based on resource demand. However, sometimes a single node may require more resources to run a specific controller.

#### Example Configuration

Let's assume you are using AWS EKS and need to configure the node group to use larger instance types.

```yaml
# eksctl.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: my-cluster
  region: us-west-2
nodeGroups:
  - name: ng-1
    instanceType: t3.small
    desiredCapacity: 3
```

In this configuration, we are setting the instance type to `t3.small`, which is a small instance type. You can change this to `t3.medium` or `t3.large` depending on your needs.

### Applying Changes with Terraform

If you are using Terraform to manage your infrastructure, you can apply these changes by modifying your Terraform configuration and running `terraform apply`.

#### Terraform Configuration Example

```hcl
resource "aws_eks_node_group" "example" {
  cluster_name = aws_eks_cluster.example.name
  node_group_name = "example"
  node_role_arn = aws_iam_role.node.arn
  subnet_ids = [aws_subnet.example.id]
  scaling_config {
    desired_size = 3
  }
  instance_types = ["t3.small"]
}
```

After making the necessary changes, run:

```bash
terraform init
terraform apply
```

### Ensuring Sufficient Resources

Even with autoscaling, it is important to ensure that individual nodes have enough resources to run the required controllers. Here are some considerations:

- **CPU and Memory Requirements**: Ensure that the chosen instance type meets the minimum CPU and memory requirements for the controllers.
- **Disk Space**: Some controllers may require additional disk space for logs or other data.

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-25741**: This vulnerability in Kubernetes allowed attackers to bypass admission controllers, including Gatekeeper. Ensuring that your cluster is up-to-date and properly configured can help mitigate such risks.
- **Breaches due to misconfigured policies**: Organizations have experienced breaches due to poorly defined or misconfigured policies. Using Policy as Code helps ensure that policies are consistent and correctly implemented.

### How to Prevent / Defend

#### Detection

- **Monitoring**: Use monitoring tools like Prometheus and Grafana to monitor the health and performance of your cluster.
- **Logging**: Enable detailed logging for all controllers and regularly review logs for suspicious activity.

#### Prevention

- **Regular Updates**: Keep your Kubernetes cluster and all controllers up-to-date with the latest security patches.
- **Secure Configuration**: Follow best practices for configuring your cluster and controllers. Use tools like `kube-bench` to audit your cluster's security posture.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**:
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
          input.review.object.metadata.labels == {}
          msg := "must have labels"
          obj := input.review.object
        }
```

**Secure Configuration**:
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
          input.review.object.metadata.labels == {}
          msg := "must have labels"
          obj := input.review.object
        }
        
        # Additional checks
        violation[{"msg": msg, "details": {"object": obj}}] {
          input.review.object.metadata.annotations == {}
          msg := "must have annotations"
          obj := input.review.object
        }
```

### Hands-On Labs

For hands-on practice with Policy as Code and OPA Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including Policy as Code.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **CloudGoat**: Provides a series of labs for practicing cloud security on AWS.

These labs will help you gain practical experience in implementing and managing Policy as Code in a Kubernetes environment.

### Conclusion

Implementing Policy as Code with OPA Gatekeeper is a powerful way to ensure that your Kubernetes cluster adheres to organizational standards and security requirements. By following best practices and using tools like Terraform and Helm, you can effectively manage and enforce policies in your cluster. Regular monitoring and updates are essential to maintaining a secure and compliant environment.

---
<!-- nav -->
[[05-Installing OPA Gatekeeper in a Kubernetes Cluster|Installing OPA Gatekeeper in a Kubernetes Cluster]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/07-Practice Questions & Answers|Practice Questions & Answers]]
