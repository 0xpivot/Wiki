---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the OIDC provider in the context of an EKS cluster.**

The OIDC (OpenID Connect) provider in the context of an EKS (Elastic Kubernetes Service) cluster serves as an intermediary that provides identity to the components within the Kubernetes cluster. While EKS itself has an identity within AWS, the individual Kubernetes components (like pods and services) do not. The OIDC provider assigns these components an identity, allowing them to communicate with AWS services and APIs. This ensures that AWS trusts these components as part of the EKS cluster, facilitating secure interactions between the Kubernetes cluster and AWS services.

**Q2. How do you enable additional add-ons in an EKS cluster using Terraform?**

To enable additional add-ons in an EKS cluster using Terraform, you can utilize the `eks-addons` module. This involves copying the configuration for the add-ons and adjusting it to fit your specific requirements. For instance, you can enable the AWS load balancer controller, metric server, and cluster autoscaler by setting the corresponding flags to `true`. Here’s an example:

```hcl
module "eks_addons" {
  source = "terraform-aws-modules/eks/aws//modules/add-ons"

  cluster_name = module.eks.cluster_name
  cluster_oidc_issuer = module.eks.cluster_oidc_issuer

  enable_aws_load_balancer_controller = true
  enable_metric_server = true
  enable_cluster_autoscaler = true
}
```

This configuration enables the specified add-ons and integrates them into the EKS cluster.

**Q3. Why is it necessary to provide Helm access to the EKS cluster when deploying Helm charts?**

When deploying Helm charts into an EKS cluster, it is necessary to provide Helm access to the cluster because Helm needs to interact with the Kubernetes API to manage the deployment of applications. To achieve this, you must configure the Helm provider in your Terraform setup. This involves setting up the Helm provider with the necessary credentials to authenticate with the EKS cluster. Here’s an example of how to configure the Helm provider:

```hcl
provider "helm" {
  kubernetes_config_path = var.kubeconfig_path
}

resource "helm_release" "example" {
  name       = "example"
  repository = "https://charts.example.com"
  chart      = "example-chart"
  version    = "1.0.0"
}
```

By configuring the Helm provider, you ensure that Helm can authenticate and interact with the EKS cluster, allowing for seamless deployment of Helm charts.

**Q4. How do you validate that the add-ons have been successfully deployed in an EKS cluster?**

To validate that the add-ons have been successfully deployed in an EKS cluster, you can follow these steps:

1. Access the EKS cluster using the Kubernetes CLI (`kubectl`). Ensure you have the appropriate credentials and permissions to access the cluster.
2. Use `kubectl` commands to verify the presence and status of the add-ons. For example, to check the pods associated with the add-ons, you can run:

   ```sh
   kubectl get pods -n kube-system
   ```

   This command lists the pods in the `kube-system` namespace, where many of the add-ons are typically deployed.

3. Additionally, you can check the logs of the add-ons to ensure they are functioning correctly. For instance, to check the logs of the cluster autoscaler, you can run:

   ```sh
   kubectl logs -l app=cluster-autoscaler -n kube-system
   ```

By verifying the presence and functionality of the add-ons through these steps, you can confirm that they have been successfully deployed and are operational in the EKS cluster.

**Q5. What are the security implications of limiting access to the EKS cluster and how do you manage this?**

Limiting access to the EKS cluster is a critical security practice to prevent unauthorized access and potential breaches. By restricting access, you ensure that only authorized users and roles can interact with the cluster, reducing the risk of malicious activities.

To manage this, you can use IAM roles and policies to define who can access the cluster and what actions they can perform. Additionally, you can use Kubernetes RBAC (Role-Based Access Control) to further restrict access within the cluster. Here’s an example of how to manage access:

1. Create an IAM role with the necessary permissions to access the EKS cluster.
2. Assign this role to users or groups using IAM policies.
3. Within the cluster, use Kubernetes RBAC to define roles and bindings that limit access to specific resources and actions.

For example, to create a Kubernetes role and binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: kube-system
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: kube-system
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

By implementing these security measures, you can effectively manage and limit access to the EEKS cluster, enhancing overall security.

---
<!-- nav -->
[[10-Understanding EKS and OIDC Providers|Understanding EKS and OIDC Providers]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Configure EKS Add ons/00-Overview|Overview]]
