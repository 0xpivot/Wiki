---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Understanding EKS Blueprints and Autoscaling

### Introduction to EKS Blueprints

Amazon Elastic Kubernetes Service (EKS) Blueprints is a feature that simplifies the deployment and management of Kubernetes clusters on AWS. It provides pre-configured templates (blueprints) that include various add-ons and configurations to help users quickly set up and manage their clusters. One of the key components managed through these blueprints is the cluster autoscaler, which dynamically adjusts the number of worker nodes based on the workload demands.

### Cluster Autoscaler Configuration

The cluster autoscaler is crucial for maintaining optimal resource utilization and cost efficiency in a Kubernetes cluster. It scales the number of nodes up or down based on the current demand for resources. Proper configuration of the autoscaler ensures that the cluster remains responsive and efficient.

#### Key Configuration Options

- **Scale Down Unneeded Time**: This option specifies the duration after which an unused node will be considered for removal. Setting this value appropriately helps in balancing between responsiveness and cost savings.
  
- **Skip Nodes with Local Storage**: This flag determines whether nodes with local storage should be considered for scaling down. Disabling this can lead to data loss if the node is removed.

- **Skip Nodes with System Pods**: This flag decides whether nodes hosting system pods should be considered for scaling down. Disabling this can affect the stability of the cluster.

### Configuring Autoscaler via Helm Charts

In the context of EKS Blueprints, the configuration of the autoscaler is often done using Helm charts. Helm is a package manager for Kubernetes that allows for the definition of complex applications as charts. These charts can be customized and deployed using `helm install` or `helm upgrade`.

#### Example Configuration

Let's walk through the configuration process step-by-step:

1. **Identify the Chart Value**: The chart value `extraArgs` is used to pass additional arguments to the autoscaler. This includes the `--scale-down-unneeded-time` and `--skip-nodes-with-local-storage` flags.

2. **Set the Values**: 
    - Set `--scale-down-unneeded-time` to `1m` (one minute).
    - Set `--skip-nodes-with-local-storage` to `false`.
    - Set `--skip-nodes-with-system-pods` to `false`.

```yaml
# Example Helm Chart Configuration
cluster-autoscaler:
  extraArgs:
    scale-down-unneeded-time: "1m"
    skip-nodes-with-local-storage: "false"
    skip-nodes-with-system-pods: "false"
```

### Committing and Triggering the Pipeline

Once the configuration is set, the next steps involve committing the changes and triggering the pipeline to apply them to the cluster.

1. **Commit Changes**:
    - Ensure the changes are committed to the version control system (e.g., Git).

2. **Trigger Pipeline**:
    - The pipeline should be triggered to deploy the updated configuration. This typically involves a CI/CD tool like Jenkins, GitHub Actions, or AWS CodePipeline.

```bash
# Example Git Commands
git add .
git commit -m "Update autoscaler configuration"
git push origin main
```

### Verifying Configuration Application

After the pipeline runs successfully, it's essential to verify that the configuration has been applied correctly.

1. **Check Pod Status**:
    - Use `kubectl get pods` to ensure the autoscaler pod is running.

2. **Inspect Deployment Configuration**:
    - Use `kubectl get deployment <deployment-name> -o yaml` to inspect the deployment configuration and confirm the new settings.

```bash
# Example kubectl Commands
kubectl get pods
kubectl get deployment cluster-autoscaler -o yaml
```

### Validating Autoscaler Behavior

To ensure the autoscaler behaves as expected, monitor the cluster and observe the scaling behavior.

1. **Monitor Node Scaling**:
    - Watch for nodes being added or removed based on workload demand.

2. **Check Logs**:
    - Review the logs of the autoscaler pod to understand its decision-making process.

```bash
# Example Log Check Command
kubectl logs -n kube-system $(kubectl get pods -n kube-system | grep cluster-autoscaler | awk '{print $1}')
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities related to Kubernetes and autoscalers highlight the importance of proper configuration and monitoring. For instance, CVE-2021-25741 affected the Kubernetes API server, leading to unauthorized access and potential misconfiguration of critical components like the autoscaler.

### How to Prevent / Defend

#### Detection

- **Monitoring Tools**: Use tools like Prometheus and Grafana to monitor autoscaler metrics and detect anomalies.
- **Audit Logs**: Enable audit logging in Kubernetes to track changes and identify unauthorized modifications.

#### Prevention

- **Secure Configuration Management**: Use tools like Kustomize or Helm to manage configurations securely and consistently.
- **Role-Based Access Control (RBAC)**: Implement strict RBAC policies to limit who can modify the autoscaler configuration.

#### Secure Coding Fixes

Compare the insecure and secure versions of the configuration:

```yaml
# Insecure Configuration
cluster-autoscaler:
  extraArgs:
    scale-down-unneeded-time: "1h"
    skip-nodes-with-local-storage: "true"
    skip-nodes-with-system-pods: "true"

# Secure Configuration
cluster-autoscaler:
  extraArgs:
    scale-down-unneeded-time: "1m"
    skip-nodes-with-local-storage: "false"
    skip-nodes-with-system-pods: "false"
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide insights into securing Kubernetes deployments.
- **CloudGoat**: Provides scenarios for securing AWS services, including EKS.
- **Pacu**: A framework for testing and exploiting AWS services, useful for understanding security gaps in EKS configurations.

### Conclusion

Properly configuring and managing the cluster autoscaler in EKS Blueprints is essential for maintaining a responsive and cost-effective Kubernetes cluster. By understanding the key configuration options, committing and triggering the pipeline, verifying the configuration, and validating the behavior, you can ensure your cluster operates optimally. Additionally, staying vigilant about recent vulnerabilities and implementing robust detection and prevention strategies will further enhance the security and reliability of your Kubernetes environment.

---
<!-- nav -->
[[04-Understanding EKS Blueprints and Autoscaler Functionality|Understanding EKS Blueprints and Autoscaler Functionality]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Troubleshooting and Tuning Autoscaler/00-Overview|Overview]] | [[06-Understanding EKS Blueprints and Autoscaling Part 2|Understanding EKS Blueprints and Autoscaling Part 2]]
