---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Helm Charts

### What Is a Helm Chart?

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. A Helm Chart is a collection of files that describe a related set of Kubernetes resources. Helm uses these charts to install and manage applications in a consistent and repeatable manner.

### How Does Helm Work?

Helm works by defining a set of templates that describe the Kubernetes resources to be deployed. These templates are parameterized, allowing you to customize the deployment with different values.

### Example: Prometheus Helm Chart

The Prometheus Helm Chart is a pre-defined set of templates that can be used to deploy the Prometheus monitoring stack. It includes all the necessary resources, such as Deployments, StatefulSets, ConfigMaps, and Services.

**Example:**
```yaml
# values.yaml
replicaCount: 2
serviceAccount:
  name: prometheus
serviceMonitorSelector:
  matchLabels:
    app: myapp
```

In this example, a `values.yaml` file is used to customize the deployment of the Prometheus Helm Chart. The `replicaCount` is set to 2, and a `serviceAccount` and `serviceMonitorSelector` are defined.

### Why Do We Need Helm Charts?

Helm Charts simplify the deployment and management of complex applications by providing a consistent and repeatable way to define and deploy Kubernetes resources. They reduce the risk of errors and inconsistencies that can occur when deploying applications manually.

### Common Pitfalls

One common pitfall is using Helm Charts for simple applications. While Helm is powerful, it adds complexity and overhead. For simple applications, deploying resources directly using Kubernetes manifests may be sufficient.

### How to Prevent / Defend

To prevent issues, use Helm Charts only for complex applications that require advanced management capabilities. For simpler applications, stick with direct deployment using Kubernetes manifests. Additionally, ensure that you have proper documentation and training in place to understand and manage the Helm Charts.

---
<!-- nav -->
[[05-Deploying Prometheus on EKS Using Operators|Deploying Prometheus on EKS Using Operators]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/08-Deploying Prometheus on EKS Using Operators/00-Overview|Overview]] | [[07-Operators|Operators]]
