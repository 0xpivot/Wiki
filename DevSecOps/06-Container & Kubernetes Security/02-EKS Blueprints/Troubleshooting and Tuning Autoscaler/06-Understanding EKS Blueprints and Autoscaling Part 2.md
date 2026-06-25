---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Understanding EKS Blueprints and Autoscaling

### Introduction to EKS Blueprints

EKS (Elastic Kubernetes Service) Blueprints are pre-configured templates designed to simplify the deployment of Kubernetes clusters on AWS. These blueprints provide a set of default configurations and best practices that help users quickly set up and manage their Kubernetes clusters. One of the key features of EKS Blueprints is the ability to integrate with various AWS services and tools, including the Kubernetes Autoscaler.

### Autoscaling in EKS Clusters

Autoscaling is a critical feature in Kubernetes clusters, especially in managed services like EKS. It allows the cluster to dynamically adjust the number of worker nodes based on the current workload. This ensures optimal resource utilization and cost efficiency. There are two types of autoscaling in Kubernetes:

1. **Horizontal Pod Autoscaler (HPA)**: Adjusts the number of replicas of a pod based on observed CPU utilization or other custom metrics.
2. **Cluster Autoscaler**: Adjusts the number of worker nodes in the cluster based on the demand for resources.

In the context of EKS, the Cluster Autoscaler is particularly important because it helps maintain the desired number of nodes, ensuring that the cluster can handle varying workloads efficiently.

### Troubleshooting Autoscaler Issues

When troubleshooting autoscaler issues, it is essential to understand the current state of the cluster and the behavior of the autoscaler. In the given scenario, the autoscaler is marking some nodes for removal but is not reducing the number of nodes as expected. Let's break down the steps involved in diagnosing and resolving this issue.

#### Checking Autoscaler Logs

The first step is to check the logs of the autoscaler to understand its current state and actions. The autoscaler runs in the `kube-system` namespace, and you can view its logs using the following command:

```bash
kubectl logs -n kube-system -l app=cluster-autoscaler --tail=-1
```

This command will provide continuous information about the autoscaler's actions. From the logs, you can see that the autoscaler is marking some nodes for removal and has been unneeded for a certain period.

#### Verifying Resource Consumption

To determine whether the autoscaler is functioning correctly, you need to check the actual resource consumption of the nodes. Since a metric server is installed in the cluster, you can use its commands to check the resource usage of the nodes.

```bash
kubectl top node
```

This command provides the utilization of resources for all the nodes in the cluster. The output might look something like this:

```plaintext
NAME                            CPU(cores)   CPU%      MEMORY(bytes)   MEMORY%
ip-10-0-1-10.ec2.internal       1m           0%        10Mi            0%
ip-10-0-1-20.ec2.internal       1m           0%        10Mi            0%
ip-10-0-1-30.ec2.internal       1m           0%        10Mi            0%
```

From the output, you can see that the CPU usage is very low (1%) for each node. However, the memory usage is high, which explains why the autoscaler is not reducing the number of nodes.

#### Checking Pod Resource Consumption

To further diagnose the issue, you should check the resource consumption of the pods running on the nodes. You can use the following command to get the resource usage of the pods:

```bash
kubectl top pod
```

This command will provide the CPU and memory usage of each pod. By analyzing the output, you can identify which pods are consuming the most resources.

#### Instance Type Analysis

Finally, you should analyze the instance type being used in the cluster. In this case, the cluster is using `t3.micro` instances, which have very low memory configurations. This explains why the autoscaler is not reducing the number of nodes, as the existing nodes are not sufficient to handle the workload.

### How to Prevent / Defend

To prevent autoscaler issues and ensure optimal resource utilization, follow these best practices:

1. **Monitor Resource Usage**: Regularly monitor the resource usage of your nodes and pods. Use tools like Prometheus and Grafana to visualize and analyze the data.
2. **Optimize Pod Configurations**: Ensure that your pods are configured with appropriate resource requests and limits. This helps the autoscaler make informed decisions.
3. **Choose Appropriate Instance Types**: Select instance types that match the resource requirements of your workloads. Avoid using instances with very low memory configurations unless absolutely necessary.
4. **Configure Autoscaler Settings**: Fine-tune the settings of the autoscaler to better match your workload patterns. For example, you can adjust the `--scale-down-delay-after-delete` parameter to control how quickly the autoscaler scales down nodes.

### Example Configuration

Here is an example of how to configure the autoscaler with specific settings:

```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
```

And here is an example of how to configure the Cluster Autoscaler:

```yaml
apiVersion: kubeadm.k8s.io/v1beta2
kind: ClusterConfiguration
kubernetesVersion: v1.20.0
controlPlaneEndpoint: "192.168.1.100:6443"
networking:
  podSubnet: "10.244.0.0/16"
apiServerExtraArgs:
  enable-admission-plugins: "NodeRestriction"
controllerManagerExtraArgs:
  node-cidr-mask-size: "24"
schedulerExtraArgs:
  bind-address: "0.0.0.0"
---
apiVersion: kubeadm.k8s.io/v1beta2
kind: InitConfiguration
nodeRegistration:
  criSocket: /var/run/dockershim.sock
---
apiVersion: kubeadm.k8s.io/v1beta2
kind: JoinConfiguration
controlPlane:
  endpoint: "192.168.1.100:6443"
  certificateKey: "your-certificate-key"
nodeRegistration:
  criSocket: /var/run/dockershim.sock
```

### Real-World Examples

Recent real-world examples of autoscaler issues include:

- **CVE-2021-25741**: A vulnerability in the Kubernetes API server allowed unauthorized access to sensitive information. This could potentially affect the autoscaler's functionality if the API server is compromised.
- **AWS Outage in May 2021**: An outage in the AWS US-East-1 region affected many EKS clusters. This highlighted the importance of monitoring and configuring autoscalers to handle unexpected disruptions.

### Conclusion

Understanding and effectively managing the autoscaler in an EKS cluster is crucial for maintaining optimal resource utilization and cost efficiency. By regularly monitoring resource usage, optimizing pod configurations, choosing appropriate instance types, and fine-tuning autoscaler settings, you can ensure that your cluster operates smoothly and securely.

### Practice Labs

For hands-on practice with EKS Blueprints and autoscaling, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security, including Kubernetes-related topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: Provides a series of labs focused on AWS security and compliance.

These labs will help you gain practical experience in deploying and managing EKS clusters with autoscaling capabilities.

---
<!-- nav -->
[[05-Understanding EKS Blueprints and Autoscaling Part 1|Understanding EKS Blueprints and Autoscaling Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Troubleshooting and Tuning Autoscaler/00-Overview|Overview]] | [[07-Understanding EKS Blueprints and Autoscaling|Understanding EKS Blueprints and Autoscaling]]
