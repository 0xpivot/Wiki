---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Networking Configuration for EKS Cluster

In the context of creating an Amazon Elastic Kubernetes Service (EKS) cluster, the networking configuration plays a crucial role. This configuration ensures that the control plane, which is managed by AWS, can communicate effectively with the worker nodes. The control plane is responsible for managing the cluster's state and ensuring that the desired state is maintained across all nodes.

### Control Plane Overview

The control plane consists of several components, including:

- **API Server**: Acts as the front end for the Kubernetes control plane, handling all communication with the cluster.
- **Scheduler**: Assigns newly created pods to nodes based on resource availability and other constraints.
- **Controller Manager**: Runs controllers that manage various aspects of the cluster, such as node registration and replication.
- **etcd**: A highly reliable key-value store used to store the cluster’s configuration data.

These components are managed by AWS, ensuring high availability and reliability. The control plane communicates with the worker nodes through a network of virtual private clouds (VPCs) and subnets.

### Worker Nodes and Node Groups

Worker nodes are the compute instances that run the actual applications and services within the Kubernetes cluster. Each worker node runs a set of processes, including `kubelet`, which is responsible for maintaining the state of the pods on the node.

#### `kubelet` Process

`kubelet` is a critical component of the worker nodes. Its primary responsibilities include:

- **Pod Management**: Ensuring that the pods are running as specified by the deployment configurations.
- **Resource Allocation**: Allocating CPU, memory, and other resources to the pods.
- **Communication**: Communicating with the Kubernetes API server to report the status of the pods and receive new instructions.
- **AWS Integration**: Making API calls to AWS services to manage resources and perform other tasks.

### Creating Node Groups

Creating individual EC2 instances for each worker node would be impractical, especially for large clusters. Instead, AWS provides the concept of **node groups**, which allow you to manage a collection of worker nodes as a single entity.

#### Benefits of Node Groups

- **Scalability**: Easily scale up or down by adjusting the number of nodes in the group.
- **Management**: Simplified management of multiple nodes through a single interface.
- **Consistency**: Ensure consistent configuration across all nodes in the group.

### Example: Creating a Node Group

To create a node group, you need to define the following parameters:

- **Node Group Name**
- **Instance Type**
- **Subnets**
- **Security Groups**
- **IAM Role**

Here is an example of creating a node group using the AWS Management Console:

```mermaid
sequenceDiagram
    participant User
    participant AWSConsole
    participant EKSCluster
    participant NodeGroup
    User->>AWSConsole: Navigate to EKS Cluster
    AWSConsole->>User: Display Cluster Details
    User->>AWSConsole: Click on "Create Node Group"
    AWSConsole->>User: Prompt for Node Group Details
    User->>AWSConsole: Enter Node Group Name, Instance Type, Subnets, Security Groups, IAM Role
    AWSConsole->>EKSCluster: Create Node Group
    EKSCluster->>NodeGroup: Initialize Node Group
    NodeGroup->>EKSCluster: Confirm Node Group Creation
```

### IAM Role for `kubelet`

For `kubelet` to function correctly, it needs permissions to make API calls to AWS services. This is achieved by attaching an IAM role to the node group.

#### IAM Role Configuration

An IAM role is an entity that defines a set of permissions for a particular task. In this case, the role allows `kubelet` to interact with AWS services.

Here is an example of an IAM role policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:AttachVolume",
                "ec2:DetachVolume",
                "ec2:ModifyInstanceAttribute",
                "ec2:StopInstances",
                "ec2:TerminateInstances",
                "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeInstanceHealth",
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeLaunchConfigurations",
                "autoscaling:DescribeScalingActivities",
                "autoscaling:DescribeTags",
                "autoscaling:SetDesiredCapacity",
                "autoscaling:CompleteLifecycleAction",
                "cloudwatch:PutMetricData",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
                "sts:AssumeRole"
            ],
            "Resource": "*"
        }
    ]
}
```

### Full HTTP Request and Response Example

When `kubelet` makes an API call to AWS, it sends an HTTP request. Here is an example of such a request and its response:

```http
POST / HTTP/1.1
Host: ec2.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/ec2/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5f356c2793805cf2ce94ca0b894fc37b48d72e285887f9f3f4f88d8df1f055
X-Amz-Date: 20150101T120000Z
Content-Length: 123

Action=DescribeInstances&Version=2014-10-01
```

```http
HTTP/1.1 200 OK
Content-Type: application/xml
Content-Length: 1234

<?xml version="1.0"?>
<DescribeInstancesResponse xmlns="http://ec2.amazonaws.com/doc/2014-10-01/">
  <reservationSet>
    <item>
      <reservationId>r-12345678</reservationId>
      <ownerId>123456789012</ownerId>
      <groupSet/>
      <instancesSet>
        <item>
          <instanceId>i-12345678</instanceId>
          <imageId>ami-12345678</imageId>
          <instanceState>
            <code>16</code>
            <name>running</name>
          </instanceState>
          <privateDnsName>ip-10-0-0-1.ec2.internal</privateD
```

### Common Pitfalls and How to Prevent Them

#### Incorrect IAM Role Permissions

One common pitfall is not providing the correct permissions to the IAM role attached to the node group. This can result in `kubelet` being unable to perform necessary operations.

**How to Prevent:**

- Ensure the IAM role has the necessary permissions by reviewing the policy document.
- Test the role by manually making API calls to verify that the permissions are correctly configured.

#### Inconsistent Network Configuration

Another issue is inconsistent network configuration between the control plane and worker nodes. This can lead to connectivity issues and failed deployments.

**How to Prevent:**

- Verify that the VPC and subnet configurations are consistent across all nodes.
- Use the AWS Management Console to check the network settings and ensure they match the requirements of the EKS cluster.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to escalate privileges by manipulating the `kubelet` process. This vulnerability highlights the importance of securing the `kubelet` and ensuring that it has the minimum necessary permissions.

**How to Prevent:**

- Regularly update the Kubernetes and `kubelet` versions to the latest patches.
- Implement strict access controls and monitor the `kubelet` logs for suspicious activity.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    securityContext:
      privileged: true
```

#### Secure Code Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    securityContext:
      privileged: false
```

### Conclusion

Creating an EKS cluster involves careful planning and configuration of both the control plane and worker nodes. By understanding the roles of `kubelet` and the importance of IAM roles, you can ensure that your cluster is secure and efficient. Regular updates and monitoring are essential to maintain the integrity of your Kubernetes environment.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on Kubernetes and container security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: Provides a series of labs focused on AWS security, including EKS and IAM roles.

By completing these labs, you can gain hands-on experience with the concepts discussed in this chapter.

---
<!-- nav -->
[[13-Kubernetes Secrets and Security|Kubernetes Secrets and Security]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/29-Manual EKS Cluster Creation Using AWS Console/00-Overview|Overview]] | [[15-Subnets and Firewall Rules|Subnets and Firewall Rules]]
