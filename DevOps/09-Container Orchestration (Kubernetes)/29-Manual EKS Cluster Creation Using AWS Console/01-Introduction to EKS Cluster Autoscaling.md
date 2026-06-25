---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to EKS Cluster Autoscaling

In the context of managing an Amazon Elastic Kubernetes Service (EKS) cluster, one of the most critical aspects is ensuring that the cluster can dynamically adjust its resources based on the current workload. This is where the concept of autoscaling comes into play. Autoscaling allows the cluster to automatically scale up or down the number of worker nodes based on the demand for resources. This ensures optimal utilization of resources and helps in reducing operational costs.

### What is EKS Cluster Autoscaling?

EKS cluster autoscaling is a feature that enables the automatic adjustment of the number of worker nodes in an EKS cluster. This is achieved through the use of an external component called the **Cluster Autoscaler**. The Cluster Autoscaler monitors the resource usage of the pods running in the cluster and adjusts the number of worker nodes accordingly.

#### Why Use EKS Cluster Autoscaling?

The primary reason to use EKS cluster autoscaling is to optimize resource utilization and reduce costs. By dynamically adjusting the number of worker nodes, you ensure that the cluster is neither over-provisioned nor under-provisioned. Over-provisioning leads to unnecessary costs, while under-provisioning can result in performance issues and pod scheduling failures.

### How Does EKS Cluster Autoscaling Work?

The EKS cluster autoscaling process involves several key components:

1. **Cluster Autoscaler**: An external component that runs outside the EKS cluster but interacts with it to manage the scaling of worker nodes.
2. **Auto Scaling Group (ASG)**: A group of EC2 instances managed by AWS Auto Scaling. The ASG defines the minimum and maximum number of instances that can be running at any given time.
3. **Pods and Resources**: The workloads running in the form of pods, which consume CPU, memory, and other resources.

#### Step-by-Step Mechanism

1. **Initialization**: The Cluster Autoscaler is deployed and configured to interact with the EKS cluster and the associated ASG.
2. **Monitoring**: The Cluster Autoscaler continuously monitors the resource usage of the pods running in the cluster.
3. **Scaling Decision**: Based on the resource usage, the Cluster Autoscaler decides whether to scale up or down the number of worker nodes.
4. **Scaling Action**: The Cluster Autoscaler communicates with the ASG to either launch new EC2 instances (scale up) or terminate existing ones (scale down).

### Configuring EKS Cluster Autoscaling

To configure EKS cluster autoscaling, you need to follow these steps:

1. **Create an Auto Scaling Group (ASG)**: Define the minimum and maximum number of EC2 instances that can be running in the ASG.
2. **Deploy the Cluster Autoscaler**: Deploy the Cluster Autoscaler as a Kubernetes deployment within the EKS cluster.
3. **Configure the Cluster Autoscaler**: Set the appropriate parameters for the Cluster Autoscaler, such as the target ASG and the range of node counts.

#### Example Configuration

Here is an example of how to create an ASG and deploy the Cluster Autoscaler:

```yaml
# Create an Auto Scaling Group (ASG)
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name eks-asg \
    --launch-template LaunchTemplateName=eks-launch-template \
    --min-size 2 \
    --max-size 5 \
    --desired-capacity 2 \
    --vpc-zone-identifier subnet-12345678,subnet-87654321

# Deploy the Cluster Autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-deployment.yaml
```

### Monitoring and Managing EKS Cluster Autoscaling

Once the Cluster Autoscaler is deployed and configured, you need to monitor its behavior and ensure that it is functioning correctly. This involves checking the logs, metrics, and events related to the Cluster Autoscaler.

#### Monitoring Tools

1. **AWS CloudWatch**: Monitor the metrics related to the ASG and the EC2 instances.
2. **Kubernetes Metrics Server**: Monitor the resource usage of the pods and nodes.
3. **Cluster Autoscaler Logs**: Check the logs of the Cluster Autoscaler deployment for any errors or warnings.

### Real-World Examples and Case Studies

#### Example 1: Cost Optimization in a Production Environment

A company running a production environment on EKS noticed that their cluster was often over-provisioned, leading to unnecessary costs. They implemented EKS cluster autoscaling and saw a significant reduction in their monthly AWS bill. The Cluster Autoscaler dynamically adjusted the number of worker nodes based on the actual workload, ensuring optimal resource utilization.

#### Example 2: Handling Spikes in Demand

Another company experienced sudden spikes in demand during promotional periods. Without autoscaling, they would have had to manually scale up the cluster, which was time-consuming and error-prone. By implementing EKS cluster autoscaling, they were able to handle the spikes in demand automatically, ensuring high availability and performance.

### Common Pitfalls and Best Practices

#### Pitfall 1: Incorrect Configuration of Minimum and Maximum Node Counts

One common pitfall is setting the minimum and maximum node counts incorrectly. If the minimum node count is too high, it can lead to unnecessary costs. Conversely, if the maximum node count is too low, it can result in performance issues during peak times.

#### Best Practice: Set Reasonable Minimum and Maximum Node Counts

Set the minimum node count based on the baseline workload and the maximum node count based on the expected peak workload. Regularly review and adjust these values based on historical data and future projections.

#### Pitfall 2: Ignoring Pod Scheduling Failures

Another pitfall is ignoring pod scheduling failures. If the Cluster Autoscaler fails to scale up the cluster due to resource constraints, it can result in pod scheduling failures, leading to downtime.

#### Best Practice: Monitor Pod Scheduling Failures

Regularly monitor pod scheduling failures and ensure that the Cluster Autoscaler is functioning correctly. If there are frequent scheduling failures, consider increasing the maximum node count or optimizing the resource requests and limits of the pods.

### How to Prevent / Defend

#### Detection

1. **Monitor Metrics**: Use AWS CloudWatch and Kubernetes Metrics Server to monitor the metrics related to the ASG and the EC2 instances.
2. **Check Logs**: Regularly check the logs of the Cluster Autoscaler deployment for any errors or warnings.

#### Prevention

1. **Set Reasonable Minimum and Maximum Node Counts**: Ensure that the minimum and maximum node counts are set based on the actual workload and future projections.
2. **Optimize Resource Requests and Limits**: Optimize the resource requests and limits of the pods to ensure efficient resource utilization.
3. **Regularly Review and Adjust Configuration**: Regularly review and adjust the configuration of the Cluster Autoscaler based on historical data and future projections.

#### Secure-Coding Fixes

Here is an example of how to configure the Cluster Autoscaler securely:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        args:
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expand=true
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/<your-cluster-name>
        - --balance-similar-node-groups=true
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-utilization-threshold=0.5
        - --skip-nodes-with-system-pods=false
        - --skip-nodes-with-pods-running-in-configured-namespaces=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-list=monitoring,logging
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex=.*-system$
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-p-ods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive=true
        - --skip-nodes-with-pods-running-in-configured-namespaces-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-insensitive-regex-match-all-case-ins-

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/29-Manual EKS Cluster Creation Using AWS Console/00-Overview|Overview]] | [[02-Introduction to EKS Cluster Creation Using AWS Console|Introduction to EKS Cluster Creation Using AWS Console]]
