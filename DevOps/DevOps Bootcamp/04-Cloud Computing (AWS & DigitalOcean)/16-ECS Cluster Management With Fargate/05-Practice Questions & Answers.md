---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the key differences between using Fargate and EC2 instances for running pods in an ECS cluster.**

Fargate and EC2 instances differ significantly in how they manage and provision compute resources:

- **Provisioning**: Fargate provisions virtual machines (VMs) on AWS-managed accounts, whereas EC2 instances are directly managed within the user's AWS account.
- **Resource Allocation**: Fargate allocates a VM per pod, ensuring isolation and dedicated resources for each pod. In contrast, EC2 instances can host multiple pods, sharing the same underlying VM.
- **Management**: Fargate abstracts away the management of underlying infrastructure, allowing users to focus solely on application deployment. EC2 requires manual management of instances, including scaling, patching, and lifecycle management.
- **Limitations**: Fargate imposes certain limitations, such as not supporting stateful applications or daemon sets, while EC2 provides more flexibility in handling various types of applications.

**Q2. How would you configure a Fargate profile to selectively schedule pods based on namespace and labels?**

To configure a Fargate profile to selectively schedule pods based on namespace and labels, follow these steps:

1. **Create a Role**: Define an IAM role with necessary permissions for Fargate to interact with AWS services, such as pulling container images from Amazon ECR.
2. **Define Profile Rules**: Create a Fargate profile with specific selectors:
   - **Namespace Selector**: Specify the namespace (e.g., `dev`) where pods should be scheduled via Fargate.
   - **Label Selector**: Define labels (e.g., `profile=fargate`) that pods must have to be scheduled via Fargate.
3. **Configure Subnets**: Ensure the profile uses appropriate private subnets for pod scheduling.
4. **Apply Configuration**: Use `kubectl` to apply the Fargate profile to your EKS cluster.

Example configuration:
```yaml
apiVersion: eks.amazonaws.com/v1alpha1
kind: FargateProfile
metadata:
  name: dev-profile
spec:
  clusterName: my-cluster
  selectors:
    - namespace: dev
      labels:
        profile: fargate
  subnetArns:
    - arn:aws:ec2:region:account-id:subnet/subnet-id
```

**Q3. Why is it necessary to provide VPC and subnet information when configuring a Fargate profile, even though the actual VMs are provisioned in an AWS-managed account?**

Providing VPC and subnet information is crucial for several reasons:

- **IP Address Assignment**: Pods scheduled via Fargate receive IP addresses from the specified VPC subnets, ensuring network connectivity within the user's VPC.
- **Network Isolation**: By specifying private subnets, you ensure that pods are isolated from public networks, enhancing security.
- **Consistent Networking**: Using the same VPC and subnet configuration ensures consistent networking policies and configurations across both Fargate and EC2-based pods.

**Q4. What are the limitations of using Fargate for running pods in an ECS cluster, and how can you mitigate these limitations?**

Fargate has several limitations:

- **Stateful Applications**: Fargate does not support stateful applications or daemon sets, which require persistent storage and node-level operations.
- **Resource Isolation**: Each pod runs in its own VM, leading to higher resource consumption compared to EC2 instances hosting multiple pods.

To mitigate these limitations:

- **Use EC2 Instances for Stateful Workloads**: Deploy stateful applications and daemon sets on EC2 instances within the same EKS cluster.
- **Mixed Setup**: Utilize a mixed setup with both Fargate and EC2 instances, leveraging the strengths of each for different types of workloads.

**Q5. How would you clean up an EKS cluster that uses both Fargate and EC2 instances, ensuring all resources are properly terminated?**

To clean up an EKS cluster that uses both Fargate and EC2 instances, follow these steps:

1. **Delete Fargate Profiles**: Remove all Fargate profiles associated with the cluster.
2. **Delete Node Groups**: Terminate all EC2 instances managed by node groups.
3. **Delete Cluster**: Delete the EKS cluster itself.
4. **Clean Up IAM Roles**: Remove IAM roles created for the cluster, node groups, and Fargate.
5. **Verify Termination**: Ensure all resources are terminated by checking the AWS console or using CLI commands.

Example commands:
```bash
# Delete Fargate Profile
eksctl delete fargateprofile --cluster=my-cluster --name=dev-profile

# Delete Node Group
eksctl delete nodegroup --cluster=my-cluster --name=my-node-group

# Delete EKS Cluster
eksctl delete cluster --name=my-cluster

# Clean Up IAM Roles
aws iam delete-role --role-name EKS_Fargate_Role
aws iam delete-role --role-name EKS_Cluster_Role
aws iam delete-role --role-name EKS_Node_Group_Role
```

**Q6. Describe a recent real-world example where Fargate was used effectively, and explain how it benefited the deployment.**

A notable example is the use of Fargate in the deployment of microservices architectures, such as in the Netflix platform. Netflix leverages Fargate for stateless applications, benefiting from:

- **Simplified Management**: Reduced operational overhead by offloading infrastructure management to AWS.
- **Scalability**: Seamless scaling of stateless services without the need for manual intervention.
- **Cost Efficiency**: Pay-per-use model aligns costs with actual usage, optimizing resource allocation.

By using Fargate, Netflix can focus on developing and deploying applications without worrying about the underlying infrastructure, leading to faster innovation and more reliable services.

---
<!-- nav -->
[[04-Namespace Creation in Kubernetes|Namespace Creation in Kubernetes]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/16-ECS Cluster Management With Fargate/00-Overview|Overview]]
