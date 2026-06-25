---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Understanding EKS Blueprints and Helm Charts

### Background Theory

EKS (Elastic Kubernetes Service) Blueprints are a set of pre-configured templates designed to simplify the deployment and management of Kubernetes clusters on Amazon Web Services (AWS). These blueprints provide a standardized approach to setting up various components such as cluster autoscalers, monitoring tools, and security configurations. One of the key components managed through these blueprints is the cluster autoscaler, which dynamically adjusts the number of worker nodes based on the workload demand.

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. Helm charts are collections of files that describe a related set of Kubernetes resources. These charts can be customized using `values.yaml` files, which allow users to specify configuration parameters for the resources being deployed.

### Cluster Autoscaler in EKS Blueprints

The cluster autoscaler is a critical component in managing the scalability of Kubernetes clusters. It automatically scales the number of worker nodes in a cluster based on the current workload. This ensures that the cluster has enough resources to handle the load without wasting resources when the load decreases.

#### Configuration Options in Helm Charts

When deploying the cluster autoscaler using Helm charts, the configuration options are defined in the `values.yaml` file. These options control various aspects of the autoscaler's behavior, such as enabling or disabling scaling operations, setting thresholds for scaling, and configuring timeouts.

To understand the configuration options available for the cluster autoscaler, we need to examine the Helm chart repository. The chart repository for the cluster autoscaler is hosted on GitHub within the Kubernetes organization. Specifically, the repository is located at:

```markdown
https://github.com/kubernetes/autoscaler/tree/master/charts/cluster-autoscaler
```

This repository contains the Helm chart for the cluster autoscaler, along with the `values.yaml` file that defines the configuration options.

### Exploring the Configuration Options

Let's dive into the `values.yaml` file to understand the available configuration options. Here is an excerpt from the `values.yaml` file:

```yaml
# values.yaml for cluster-autoscaler
replicaCount: 1
image:
  repository: k8s.gcr.io/autoscaling/cluster-autoscaler
  tag: v1.21.0
  pullPolicy: IfNotPresent
resources:
  limits:
    cpu: 100m
    memory: 300Mi
  requests:
    cpu: 100m
    memory: 300Mi
nodeSelector: {}
tolerations: []
affinity: {}
scaleDownEnabled: true
scaleUpThreshold: 10
scaleDownThreshold: 10
scaleDownDelayAfterAdd: 10m
scaleDownDelayAfterDelete: 10m
scaleDownUnneededTime: 10m
scaleDownUtilizationThreshold: 0.5
```

In this file, we can see several configuration options:

- `replicaCount`: The number of replicas for the autoscaler pod.
- `image`: The Docker image used for the autoscaler.
- `resources`: CPU and memory resource limits and requests.
- `nodeSelector`, `tolerations`, and `affinity`: Node selection criteria.
- `scaleDownEnabled`: Whether scale-down operations are enabled.
- `scaleUpThreshold` and `scaleDownThreshold`: Thresholds for scaling operations.
- `scaleDownDelayAfterAdd` and ` `scaleDownDelayAfterDelete`: Delays after node addition/deletion.
- `scaleDownUnneededTime`: Time a node must be unneeded before being scaled down.
- `scaleDownUtilizationThreshold`: Utilization threshold for scaling down.

### Customizing the Autoscaler Configuration

To customize the autoscaler configuration, we can modify the `values.yaml` file. For example, to disable scale-down operations, we can set `scaleDownEnabled` to `false`. Here is an example of a modified `values.yaml` file:

```yaml
# Customized values.yaml for cluster-autoscaler
replicaCount: 1
image:
  repository: k8s.gcr.io/autoscaling/cluster-autoscaler
  tag: v1.21.0
  pullPolicy: IfNotPresent
resources:
  limits:
    cpu: 100m
    memory: 300Mi
  requests:
    cpu: 100m
    memory: 300Mi
nodeSelector: {}
tolerations: []
affinity: {}
scaleDownEnabled: false
scaleUpThreshold: 10
scaleDownThreshold: 10
scaleDownDelayAfterAdd: 10m
scaleDownDelayAfterDelete: 10m
scaleDownUnneededTime: 10m
scaleDownUtilizationThreshold: 0.5
```

### Deploying the Customized Autoscaler

To deploy the customized autoscaler, we can use the following Helm commands:

```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install my-autoscaler autoscaler/cluster-autoscaler --values ./custom-values.yaml
```

Here, `./custom-values.yaml` is the path to the customized `values.yaml` file.

### Monitoring and Troubleshooting the Autoscaler

Monitoring the autoscaler's performance is crucial to ensure that it is functioning correctly. Kubernetes provides several tools for monitoring, such as Prometheus and Grafana. Additionally, the autoscaler logs can be inspected to identify any issues.

For example, to view the autoscaler logs, we can use the following command:

```bash
kubectl logs -n kube-system $(kubectl get pods -n kube-system | grep cluster-autoscaler | awk '{print $1}')
```

### Real-World Examples and Recent CVEs

Recent CVEs and breaches involving Kubernetes and autoscalers highlight the importance of proper configuration and monitoring. For instance, CVE-2021-25741 affected the cluster autoscaler, allowing unauthorized access to sensitive information. To mitigate such vulnerabilities, it is essential to keep the autoscaler and its dependencies up-to-date and to implement strict access controls.

### How to Prevent / Defend

#### Detection

To detect potential issues with the autoscaler, regular monitoring and logging are essential. Tools like Prometheus and Grafana can be used to monitor the autoscaler's performance metrics. Additionally, Kubernetes audit logs can be reviewed to identify any unauthorized access attempts.

#### Prevention

To prevent unauthorized access and ensure the security of the autoscaler, the following measures can be taken:

1. **Keep Dependencies Updated**: Regularly update the autoscaler and its dependencies to the latest versions.
2. **Implement Access Controls**: Use RBAC (Role-Based Access Control) to restrict access to the autoscaler.
3. **Secure Configurations**: Ensure that sensitive configuration options are properly secured and not exposed to unauthorized users.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
# Vulnerable values.yaml
scaleDownEnabled: true
scaleUpThreshold: 10
scaleDownThreshold: 10
scaleDownDelayAfterAdd: 10m
scaleDownDelayAfterDelete: 10m
scaleDownUnneededTime: 10m
scaleDownUtilizationThreshold: 0.5
```

**Secure Configuration:**

```yaml
# Secure values.yaml
scaleDownEnabled: false
scaleUpThreshold: 10
scaleDownThreshold: 10
scaleDownDelayAfterAdd: 10m
scaleDownDelayAfterDelete: 10m
scaleDownUnneededTime: 10m
scaleDownUtilizationThreshold: 0.5
```

### Hands-On Labs

To practice troubleshooting and tuning the autoscaler, the following labs can be used:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing security skills.
- **WebGoat**: An interactive training application for learning about web application security.

These labs provide a practical environment to test and troubleshoot the autoscaler configurations.

### Conclusion

Understanding and customizing the configuration options for the cluster autoscaler in EKS Blueprints is crucial for effective cluster management. By exploring the Helm chart repository and modifying the `values.yaml` file, we can fine-tune the autoscaler's behavior to meet specific requirements. Regular monitoring and implementing security best practices are essential to ensure the autoscaler operates securely and efficiently.

---
<!-- nav -->
[[07-Understanding EKS Blueprints and Autoscaling|Understanding EKS Blueprints and Autoscaling]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Troubleshooting and Tuning Autoscaler/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Troubleshooting and Tuning Autoscaler/09-Practice Questions & Answers|Practice Questions & Answers]]
