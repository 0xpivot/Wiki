---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how the EKS cluster autoscaler interacts with the AWS Auto Scaling Group.**

The EKS cluster autoscaler interacts with the AWS Auto Scaling Group by leveraging the configuration defined in the Auto Scaling Group to manage the number of EC2 instances within the specified minimum and maximum limits. The autoscaler runs inside the Kubernetes cluster and monitors the utilization of EC2 instances. When it detects underutilization, it redistributes pods across fewer instances and scales down the number of instances. Conversely, when it detects insufficient resources to schedule new pods, it scales up by launching new EC2 instances according to the maximum size defined in the Auto Scaling Group. This interaction ensures that the cluster efficiently manages its resources while adhering to the predefined scaling boundaries.

**Q2. How do you configure the necessary permissions for the EC2 instances to enable autoscaling in EKS?**

To configure the necessary permissions for the EC2 instances to enable autoscaling in EKS, you need to create a custom IAM policy and attach it to the node group IAM role. The custom policy should include permissions for EC2 and Auto Scaling operations. Here’s an example of the JSON content for the policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "autoscaling:Describe*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:CompleteLifecycleAction",
                "autoscaling:DeleteLifecycleHook",
                "autoscaling:PutLifecycleHook",
                "autoscaling:RecordLifecycleActionHeartbeat"
            ],
            "Resource": "*"
        }
    ]
}
```

After creating this policy, attach it to the node group IAM role to ensure the EC2 instances have the required permissions to interact with the Auto Scaling Group.

**Q3. What are the key tags required for the autoscaler to discover and interact with the Auto Scaling Group in AWS?**

The key tags required for the autoscaler to discover and interact with the Auto Scaling Group in AWS are `kubernetes.io/cluster/<cluster-name>` and `kubernetes.io/cluster-autoscaler/enabled`. These tags help the autoscaler identify the appropriate Auto Scaling Group and determine if autoscaling is enabled for the cluster. For example, if the cluster name is `eks-cluster-test`, the tags would be:

- `kubernetes.io/cluster/eks-cluster-test`
- `kubernetes.io/cluster-autoscaler/enabled`

These tags are typically configured automatically when setting up the node group, but they can be verified and modified if necessary.

**Q4. How would you modify the autoscaler deployment to ensure it uses the correct Kubernetes version and image tag?**

To modify the autoscaler deployment to ensure it uses the correct Kubernetes version and image tag, you need to update the deployment configuration with the appropriate version and image tag. Here’s an example of how to do this:

1. Edit the deployment configuration using `kubectl edit`:

```bash
kubectl edit deployment -n kube-system cluster-autoscaler
```

2. Update the `image` field with the correct version and tag. For example, if your Kubernetes version is `1.18`, the image tag should be `1.18.x`:

```yaml
spec:
  template:
    spec:
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.18.3
```

3. Save the changes and verify that the deployment has been updated correctly:

```bash
kubectl get deployment -n kube-system cluster-autoscaler
```

This ensures that the autoscaler is compatible with your Kubernetes cluster version and operates as expected.

**Q5. Describe the process of scaling down EC2 instances using the EKS cluster autoscaler.**

The process of scaling down EC2 instances using the EKS cluster autoscaler involves several steps:

1. **Monitoring Utilization**: The autoscaler continuously monitors the utilization of EC2 instances in the cluster.
   
2. **Identifying Underutilized Instances**: When the autoscaler detects that multiple instances are underutilized, it identifies which instances can be safely terminated without affecting the running pods.

3. **Pod Redistribution**: The autoscaler redistributes the pods from the identified instances to the remaining instances. This ensures that the workload continues to run without interruption.

4. **Termination of Instances**: Once the pods have been redistributed, the autoscaler terminates the underutilized instances. This reduces the number of active EC2 instances, thereby saving costs.

5. **Logging and Verification**: The autoscaler logs the actions taken during the scaling process. You can check the logs to verify that the scaling operation was successful and to understand the sequence of events.

For example, if you set the minimum size of the Auto Scaling Group to 1 and the current number of instances is 2, the autoscaler will evaluate the instances and terminate one of them if it finds that the remaining instance can handle the workload. This process is reflected in the autoscaler logs, showing the steps taken to scale down the instances.

**Q6. How does the EKS cluster autoscaler handle the creation of new EC2 instances when the current instances are overloaded?**

When the current EC2 instances in an EKS cluster are overloaded and unable to schedule new pods, the cluster autoscaler handles the creation of new EC2 instances through the following steps:

1. **Detection of Overload**: The autoscaler detects that the current instances are overloaded and cannot accommodate new pods.

2. **Scaling Up Decision**: Based on the configuration of the Auto Scaling Group, the autoscaler decides to scale up by launching new EC2 instances.

3. **Launching New Instances**: The autoscaler triggers the launch of new EC2 instances according to the maximum size defined in the Auto Scaling Group. This ensures that the cluster has sufficient resources to schedule the new pods.

4. **Pod Scheduling**: Once the new instances are up and running, the autoscaler schedules the pending pods onto these new instances.

5. **Logging and Monitoring**: The autoscaler logs the actions taken during the scaling process. You can check the logs to verify that the scaling operation was successful and to understand the sequence of events.

For example, if you increase the replica count of a deployment and the current instances cannot handle the additional load, the autoscaler will scale up by launching new EC2 instances. This process is reflected in the autoscaler logs, showing the steps taken to scale up the instances and schedule the new pods.

**Q7. What are the trade-offs involved in using the EKS cluster autoscaler for managing EC2 instances?**

Using the EKS cluster autoscaler for managing EC2 instances involves several trade-offs:

1. **Cost Savings vs. Latency**: The primary benefit of using the autoscaler is cost savings. By dynamically adjusting the number of EC2 instances based on workload, you can avoid paying for idle resources. However, this comes at the cost of increased latency when new instances need to be launched. Starting and initializing new EC2 instances takes time, which can delay the scheduling of new pods.

2. **Resource Utilization vs. Availability**: The autoscaler aims to optimize resource utilization by terminating underutilized instances. While this improves efficiency, it may reduce the immediate availability of resources. If the workload suddenly increases, the autoscaler needs to scale up quickly, which can introduce delays.

3. **Complexity vs. Simplicity**: Implementing and maintaining the autoscaler adds complexity to your cluster management. You need to configure the autoscaler properly, monitor its performance, and troubleshoot issues. On the other hand, a simpler approach might involve manually managing the number of instances, which can be less efficient but easier to manage.

4. **Scalability vs. Predictability**: The autoscaler enables better scalability by automatically adjusting the number of instances. However, this can make it harder to predict the exact number of instances and their associated costs. Manual management offers more predictability but sacrifices the flexibility of dynamic scaling.

In summary, the EKS cluster autoscaler provides significant benefits in terms of cost savings and resource optimization, but it also introduces trade-offs related to latency, availability, complexity, and predictability. Careful consideration of these factors is essential when deciding whether to use the autoscaler in your EKS cluster.

---
<!-- nav -->
[[05-Understanding Port Mapping in Kubernetes Services|Understanding Port Mapping in Kubernetes Services]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/17-EKS Cluster Autoscaling with AWS Auto Scaling Groups/00-Overview|Overview]]
