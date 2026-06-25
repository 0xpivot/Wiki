---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Cluster Autoscaler in Amazon EKS

### Introduction to Cluster Autoscaler

The Cluster Autoscaler is a crucial component in managing the scalability and cost-efficiency of your Kubernetes clusters, especially in managed services like Amazon Elastic Kubernetes Service (EKS). Its primary function is to automatically adjust the number of worker nodes in your cluster based on the current demand, ensuring that you neither over-provision nor under-provision resources.

#### What is Cluster Autoscaler?

Cluster Autoscaler is a Kubernetes controller that dynamically scales the number of nodes in a Kubernetes cluster. It ensures that the cluster has enough resources to run all the pods that are scheduled to run, while also removing idle nodes to save costs. This is particularly useful in environments where the workload fluctuates over time, such as during peak hours or when certain applications are deployed.

#### Why Use Cluster Autoscaler?

Using Cluster Autoscaler provides several benefits:

1. **Cost Efficiency**: By automatically adjusting the number of nodes, you avoid paying for idle resources, which can significantly reduce your cloud costs.
2. **Scalability**: It ensures that your cluster can handle varying workloads without manual intervention, improving the overall reliability and performance of your applications.
3. **Resource Optimization**: It helps in optimizing resource utilization by ensuring that all pods have sufficient resources to run.

### Configuring Cluster Autoscaler in EKS

To configure the Cluster Autoscaler in an EKS cluster, you need to follow these steps:

1. **Install the Cluster Autoscaler**: You can install the Cluster Autoscaler using Helm charts or by deploying the necessary manifests directly into your cluster.
2. **Configure Node Groups**: Ensure that your EKS node groups are configured to allow the Cluster Autoscaler to scale up and down.
3. **Monitor and Validate**: Once installed, you need to monitor and validate that the Cluster Autoscaler is functioning correctly.

#### Installing the Cluster Autoscaler

Here’s how you can install the Cluster Autoscaler using Helm:

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install cluster-autoscaler eks/cluster-autoscaler \
    --namespace kube-system \
    --set autoDiscovery.clusterName=<your-cluster-name> \
    --set awsRegion=<your-region>
```

Replace `<your-cluster-name>` and `<your-region>` with your actual cluster name and region.

#### Configuring Node Groups

Ensure that your EKS node groups are configured to allow the Cluster Autoscaler to scale up and down. This typically involves setting the minimum and maximum number of nodes in the node group.

```yaml
apiVersion: eks.aws.amazon.com/v1alpha1
kind: NodeGroup
metadata:
  name: my-node-group
spec:
  minSize: 2
  maxSize: 10
  desiredSize: 2
  instanceTypes:
    - t3.medium
  amiType: AL2_x86_64
  subnetIds:
    - subnet-xxxxxx
    - subnet-yyyyyy
  tags:
    k8s.io/cluster-autoscaler/enabled: "true"
```

### Monitoring and Validating the Cluster Autoscaler

Once the Cluster Autoscaler is installed and configured, you need to monitor and validate that it is functioning correctly. This involves checking the status of the nodes and the logs of the Cluster Autoscaler.

#### Checking Node Status

You can check the status of the nodes using `kubectl`:

```bash
kubectl get nodes
```

This will list all the nodes in your cluster along with their status.

#### Checking Cluster Autoscaler Logs

To check the logs of the Cluster Autoscaler, you can use the following command:

```bash
kubectl logs -n kube-system -l app=cluster-autoscaler
```

This will display the logs of the Cluster Autoscaler, which can help you understand what actions it is taking.

### Example Scenario: Cluster Autoscaler Not Removing Nodes

In the given scenario, the Cluster Autoscaler is not removing nodes as expected. Let’s analyze this issue step-by-step.

#### Analyzing the Issue

1. **Check Current Workload**: Verify if the current workload requires more than the minimum number of nodes.
2. **Check Autoscaler Logs**: Review the logs of the Cluster Autoscaler to understand its behavior.

```bash
kubectl logs -n kube-system -l app=cluster-autoscaler
```

From the logs, you can see that the Cluster Autoscaler is performing the following actions:

1. **Checking Unschedulable Pods**: It checks if there are any pods that are scheduled but do not have anywhere to run due to lack of resources.
2. **Calculating Unneeded Nodes**: It calculates whether there are any unneeded nodes that can be removed.
3. **Starting Scaling Down**: It starts the process of scaling down by removing idle nodes.

However, it does not actually remove the nodes as expected. This could be due to various reasons such as:

- **Pod Disruption Budgets (PDB)**: There might be Pod Disruption Budgets that prevent the removal of nodes.
- **Taints and Tolerations**: There might be taints and tolerations that prevent the removal of nodes.
- **Node Affinity**: There might be node affinity rules that prevent the removal of nodes.

#### How to Prevent / Defend

To ensure that the Cluster Autoscaler functions correctly, you need to address the potential issues mentioned above.

1. **Review Pod Disruption Budgets**: Ensure that there are no Pod Disruption Budgets that prevent the removal of nodes.

```yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: my-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

2. **Review Taints and Tolerations**: Ensure that there are no taints and tolerations that prevent the removal of nodes.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "my-app"
    effect: "NoSchedule"
```

3. **Review Node Affinity**: Ensure that there are no node affinity rules that prevent the removal of nodes.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

### Conclusion

The Cluster Autoscaler is a powerful tool for managing the scalability and cost-efficiency of your Kubernetes clusters. By configuring it correctly and monitoring its behavior, you can ensure that your cluster is always optimized for both performance and cost. Always review and address potential issues such as Pod Disruption Budgets, taints and tolerations, and node affinity to ensure that the Cluster Autoscaler functions as expected.

### Practice Labs

For hands-on practice with Cluster Autoscaler in EKS, consider the following labs:

- **CloudGoat**: A set of labs designed to teach cloud security concepts, including EKS and Cluster Autoscaler.
- **flaws.cloud**: A platform for learning cloud security, including EKS and Cluster Autoscaler configurations.
- **AWS Official Workshops**: AWS offers official workshops and labs that cover EKS and Cluster Autoscaler in depth.

These labs provide real-world scenarios and exercises to help you master the configuration and management of the Cluster Autoscaler in EKS.

---
<!-- nav -->
[[08-Introduction to EKS Blueprints and Helm Charts|Introduction to EKS Blueprints and Helm Charts]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Configure EKS Add ons/00-Overview|Overview]] | [[10-Understanding EKS and OIDC Providers|Understanding EKS and OIDC Providers]]
