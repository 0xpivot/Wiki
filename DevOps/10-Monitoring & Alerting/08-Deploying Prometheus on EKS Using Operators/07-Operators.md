---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Operators

### What Is an Operator?

An Operator is a custom controller that extends the Kubernetes API to manage complex applications. Unlike standard controllers like Deployments and StatefulSets, which manage simple, stateless or stateful applications, Operators can manage entire stacks of interdependent components.

### How Does an Operator Work?

Operators work by defining custom resources and controllers that watch for changes to these resources. When a change is detected, the Operator takes action to maintain the desired state of the application.

### Example: Prometheus Operator

The Prometheus Operator is a specific type of Operator designed to manage the Prometheus monitoring stack. It automates the deployment and management of Prometheus, Alertmanager, and other related components.

**Example:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      app: myapp
```

In this example, a Prometheus resource is defined with two replicas and a service account. The Operator will automatically create and manage the necessary pods and services to run Prometheus.

### Why Do We Need Operators?

Operators simplify the management of complex applications by abstracting away the details of deploying and maintaining multiple components. They ensure that the application remains in the desired state, even in the face of failures or changes.

### Common Pitfalls

One common pitfall is overusing Operators for simple applications. While Operators are powerful, they add complexity and overhead. For simple applications, standard controllers like Deployments and StatefulSets are often sufficient.

### How to Prevent / Defend

To prevent issues, use Operators only for complex applications that require advanced management capabilities. For simpler applications, stick with standard controllers. Additionally, ensure that you have proper documentation and training in place to understand and manage the Operator.

---
<!-- nav -->
[[06-Helm Charts|Helm Charts]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/08-Deploying Prometheus on EKS Using Operators/00-Overview|Overview]] | [[08-Setting Up an Amazon EKS Cluster|Setting Up an Amazon EKS Cluster]]
