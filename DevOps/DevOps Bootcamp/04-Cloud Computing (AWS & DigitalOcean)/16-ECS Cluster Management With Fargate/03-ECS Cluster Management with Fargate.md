---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## ECS Cluster Management with Fargate

### Introduction to ECS and Fargate

Amazon Elastic Container Service (ECS) is a fully managed container orchestration service that allows you to run Docker containers at scale. ECS supports two main types of launch configurations: EC2 and Fargate. While EC2 requires you to manage your own infrastructure, Fargate abstracts away the underlying infrastructure, allowing you to focus solely on deploying and managing your applications.

Fargate is a serverless compute engine for containers that allows you to run containers without having to manage the underlying infrastructure. This means you don't need to provision, patch, or scale any servers. Instead, you simply define your tasks and services, and Fargate handles the rest.

### Understanding Fargate Profiles

When you use Fargate with ECS, you need to define Fargate profiles. These profiles determine how tasks and services are scheduled onto Fargate. A Fargate profile consists of several key components:

1. **Profile Name**: A unique identifier for the profile.
2. **Role**: An IAM role that grants permissions to the tasks and services running in Fargate.
3. **Subnets**: The subnets within your VPC where the tasks and services will be deployed.
4. **Selectors**: Criteria that determine which tasks and services should be scheduled using Fargate.

#### Creating a Fargate Profile

Let's walk through the process of creating a Fargate profile step-by-step.

1. **Assign a Profile Name**:
    - In the AWS Management Console, navigate to the ECS console.
    - Select the cluster where you want to create the Fargate profile.
    - Click on "Fargate profiles" and then "Create Fargate profile".
    - Assign a name to the profile, such as `dev-profile`.

2. **Select the Role**:
    - AWS automatically suggests a suitable IAM role based on the profile requirements.
    - If no suitable role exists, you can create a new one.
    - The role must have permissions to access the necessary resources in your VPC.

3. **Define Subnets**:
    - Specify the subnets within your VPC where the tasks and services will be deployed.
    - Ensure that the subnets have appropriate routing and security group configurations.

4. **Configure Selectors**:
    - Selectors determine which tasks and services should be scheduled using Fargate.
    - You can specify selectors based on namespace and labels.

Here is an example of a Fargate profile definition in YAML:

```yaml
apiVersion: eks.amazonaws.com/v1alpha1
kind: FargateProfile
metadata:
  name: dev-profile
spec:
  clusterName: my-cluster
  podExecutionRoleArn: arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role
  selectors:
    - namespace: dev
      labels:
        app: web
```

### Why Provide Your Own VPC?

One common question is why you need to provide your own VPC even though Fargate provisions virtual machines on an AWS-managed account. The reason lies in the networking requirements of the pods.

When a pod is scheduled using Fargate, it receives an IP address from the range defined by the subnets in your VPC. This ensures that the pod can communicate with other services within your VPC, including those running on EC2 instances or other Fargate tasks.

#### Example: Pod Networking

Consider a scenario where you have a web application running in a pod scheduled using Fargate. The pod needs to communicate with a database service running in another pod within the same VPC. By providing your own VPC and subnets, you ensure that the pods can communicate seamlessly.

Here is an example of a pod definition in YAML:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
  labels:
    app: web
spec:
  containers:
    - name: web-container
      image: my-web-app:latest
      ports:
        - containerPort: 80
```

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized access, you can use AWS CloudTrail and Amazon VPC Flow Logs.

1. **CloudTrail**: Monitor API calls made to your ECS cluster and Fargate profiles.
2. **VPC Flow Logs**: Capture network traffic between pods and other services within your VPC.

#### Prevention

1. **IAM Role Permissions**: Ensure that the IAM role assigned to the Fargate profile has the minimum necessary permissions.
2. **Network Security Groups**: Configure security groups to restrict inbound and outbound traffic to only necessary ports and IP addresses.
3. **Subnet Configuration**: Ensure that the subnets used by Fargate have appropriate routing and NAT configurations.

#### Secure Code Fix

Here is an example of a vulnerable and secure Fargate profile configuration:

**Vulnerable Configuration**:
```yaml
apiVersion: eks.amazonaws.com/v1alpha1
kind: FargateProfile
metadata:
  name: dev-profile
spec:
  clusterName: my-cluster
  podExecutionRoleArn: arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role
  selectors:
    - namespace: dev
      labels:
        app: web
```

**Secure Configuration**:
```yaml
apiVersion: eks.amazonaws.com/v1alpha1
kind: FargateProfile
metadata:
  name: dev-profile
spec:
  clusterName: my-cluster
  podExecutionRoleArn: arn:aws:iam::123456789012:role/eks-fargate-pod-execution-role
  selectors:
    - namespace: dev
      labels:
        app: web
  subnets:
    - subnet-12345678
    - subnet-87654321
  securityGroups:
    - sg-12345678
```

### Real-World Examples

#### Recent Breaches

In 2022, a company experienced a breach due to misconfigured Fargate profiles. The issue was that the IAM role assigned to the Fargate profile had excessive permissions, allowing unauthorized access to sensitive data.

#### Secure Configuration Practices

To avoid such issues, follow these best practices:

1. **Least Privilege Principle**: Assign the least privilege necessary to the IAM role.
2. **Regular Audits**: Regularly audit your Fargate profiles and IAM roles for any misconfigurations.
3. **Automated Monitoring**: Use automated tools like AWS Config and AWS Trusted Advisor to monitor and alert on any changes to your Fargate profiles.

### Hands-On Labs

For hands-on practice with ECS and Fargate, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including some that touch on container orchestration.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **AWS Official Workshops**: Provides detailed workshops and labs for ECS and Fargate, including setup and management.

By following these steps and best practices, you can effectively manage your ECS clusters with Fargate, ensuring both security and efficiency in your containerized applications.

---
<!-- nav -->
[[02-ECS Cluster Management With Fargate|ECS Cluster Management With Fargate]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/16-ECS Cluster Management With Fargate/00-Overview|Overview]] | [[04-Namespace Creation in Kubernetes|Namespace Creation in Kubernetes]]
