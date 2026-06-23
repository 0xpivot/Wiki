---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## EKS Cluster Overview Using Python and Terraform

### Introduction to Amazon EKS (Elastic Kubernetes Service)

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to stand up or maintain your own Kubernetes control plane. Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. With EKS, you can use Kubernetes to run and manage your containerized applications on AWS without needing to install and operate your own Kubernetes control plane.

#### Why Use EKS?

1. **Managed Control Plane**: AWS manages the Kubernetes control plane, including etcd, API server, controller manager, and scheduler. This reduces the operational burden of maintaining the control plane.
2. **High Availability**: EKS clusters are highly available and span multiple Availability Zones within a region.
3. **Integration with AWS Services**: EKS integrates seamlessly with other AWS services such as VPC, IAM, and CloudWatch.
4. **Security**: EKS provides robust security features, including encryption at rest and in transit, IAM roles for service accounts, and VPC networking.

### Understanding EKS Cluster States

When working with EKS clusters, it's crucial to understand the different states a cluster can be in. These states provide insight into the current status of the cluster and help in managing and troubleshooting the cluster effectively.

#### Cluster States

An EKS cluster can be in one of the following states:

1. **Creating**: The cluster is being created.
2. **Active**: The cluster is ready for use.
3. **Deleting**: The cluster is being deleted.
4. **Failed**: The cluster creation or deletion has failed.
5. **Updating**: The cluster is being updated.

These states are important because they indicate the current operational status of the cluster. For instance, if a cluster is in the `Creating` state, you cannot perform operations that require the cluster to be `Active`. Similarly, if a cluster is in the `Failed` state, you need to troubleshoot and resolve the issues before proceeding.

### Retrieving Cluster Information Using Python

To interact with an EKS cluster programmatically, you can use the Boto3 library, which is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python. Boto3 allows you to create, configure, and manage AWS services using Python code.

#### Prerequisites

Before you start, ensure you have the following:

1. **Python Installed**: Ensure Python is installed on your machine.
2. **Boto3 Installed**: Install Boto3 using pip:
    ```bash
    pip install boto3
    ```
3. **AWS CLI Configured**: Configure the AWS CLI with your credentials:
    ```bash
    aws configure
    ```

#### Retrieving Cluster Status

Let's retrieve the status of an EKS cluster using Python and Boto3.

```python
import boto3

# Initialize the EKS client
eks_client = boto3.client('eks')

# Define the cluster name
cluster_name = 'my-cluster'

# Retrieve the cluster details
response = eks_client.describe_cluster(name=cluster_name)

# Extract the cluster status
cluster_status = response['cluster']['status']

print(f"Cluster {cluster_name} status is {cluster_status}")
```

#### Explanation

1. **Initialize the EKS Client**:
    ```python
    eks_client = boto3.client('eks')
    ```
    This initializes the EKS client using Boto3.

2. **Define the Cluster Name**:
    ```python
    cluster_name = 'my-cluster'
    ```
    Replace `'my-cluster'` with the actual name of your EKS cluster.

3. **Retrieve the Cluster Details**:
    ```python
    response = eks_client.describe_cluster(name=cluster_name)
    ```
    This retrieves the details of the specified E_ cluster.

4. **Extract the Cluster Status**:
    ```python
    cluster_status = response['cluster']['status']
    ```
    The `response` object contains a dictionary with the cluster details. The `status` key within the `cluster` dictionary holds the current status of the cluster.

5. **Print the Cluster Status**:
    ```python
    print(f"Cluster {cluster_name} status is {cluster_status}")
    ```

### Retrieving Cluster Endpoint

The cluster endpoint is the URL used to communicate with the Kubernetes API server. This endpoint is essential for interacting with the cluster using tools like `kubectl`.

#### Retrieving the Cluster Endpoint

Let's extend the previous script to also retrieve the cluster endpoint.

```python
import boto3

# Initialize the EKS client
eks_client = boto3.client('eks')

# Define the cluster name
cluster_name = 'my-cluster'

# Retrieve the cluster details
response = eks_client.describe_cluster(name=cluster_name)

# Extract the cluster status and endpoint
cluster_status = response['cluster']['status']
cluster_endpoint = response['cluster']['endpoint']

print(f"Cluster {cluster_name} status is {cluster_status}")
print(f"Cluster {cluster_name} endpoint is {cluster_endpoint}")
```

#### Explanation

1. **Extract the Cluster Endpoint**:
    ```python
    cluster_endpoint = response['cluster']['endpoint']
    ```
    The `endpoint` key within the `cluster` dictionary holds the URL of the Kubernetes API server.

2. **Print the Cluster Endpoint**:
    ```python
    print(f"Cluster {cluster_name} endpoint is {cluster_endpoint}")
    ```

### Handling Repeated Code

In the provided script, we are retrieving the cluster details twice. To avoid redundancy, we can store the response in a variable and reuse it.

```python
import boto3

# Initialize the EKS client
eks_client = boto3.client('eks')

# Define the cluster name
cluster_name = 'my-cluster'

# Retrieve the cluster details
response = eks_client.describe_cluster(name=cluster_name)

# Extract the cluster status and endpoint
cluster_status = response['cluster']['status']
cluster_endpoint = response['cluster']['endpoint']

print(f"Cluster {cluster_name} status is {cluster_status}")
print(f"Cluster {cluster_name} endpoint is {cluster_endpoint}")
```

### How to Prevent / Defend

#### Detection

1. **Monitoring Cluster State**: Use AWS CloudWatch to monitor the state of your EKS clusters. Set up alarms for specific states like `Failed` or `Deleting`.
2. **Logging**: Enable logging for your EKS clusters to capture detailed information about cluster operations and events.

#### Prevention

1. **Proper Configuration**: Ensure that your EKS clusters are properly configured with the necessary permissions and settings.
2. **Regular Updates**: Keep your EKS clusters and associated components up to date with the latest security patches and updates.

#### Secure Coding Fixes

1. **Use IAM Roles for Service Accounts**: Implement IAM roles for service accounts to control access to AWS resources from within your Kubernetes pods.
2. **Enable Encryption**: Enable encryption at rest for your EKS clusters to protect data stored in the cluster.

### Real-World Examples

#### Example 1: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that could allow an attacker to escalate privileges and gain unauthorized access to the cluster. This vulnerability affects Kubernetes versions prior to 1.20.7, 1.19.10, and 1.18.15.

**Impact**: An attacker could exploit this vulnerability to gain unauthorized access to the Kubernetes API server and potentially take control of the entire cluster.

**Mitigation**: Ensure that your EKS clusters are running the latest versions of Kubernetes and apply the necessary security patches.

#### Example 2: AWS Breach in 2021

In 2021, AWS experienced a breach that affected some of its customers. The breach was caused by a misconfiguration in an internal AWS service, which allowed unauthorized access to customer data.

**Impact**: The breach resulted in unauthorized access to customer data stored in S3 buckets and other AWS services.

**Mitigation**: Implement strict access controls and monitoring for your AWS resources. Use IAM roles and policies to restrict access to sensitive data and services.

### Conclusion

Understanding the states of an EKS cluster and how to retrieve and manage cluster information using Python and Boto3 is crucial for effective DevOps practices. By following best practices and implementing security measures, you can ensure the integrity and availability of your EKS clusters.

### Practice Labs

For hands-on practice with EKS and Kubernetes, consider the following labs:

1. **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for learning web application security.
2. **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
3. **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
4. **WebGoat**: An interactive, gamified training application for learning about web application security.

By completing these labs, you can gain practical experience in managing and securing EKS clusters and Kubernetes environments.

### Mermaid Diagrams

#### Cluster State Diagram

```mermaid
stateDiagram-v2
    [*] --> Creating
    Creating --> Active
    Creating --> Failed
    Active --> Updating
    Active --> Deleting
    Updating --> Active
    Updating --> Failed
    Deleting --> [*]
    Deleting --> Failed
```

This diagram illustrates the possible states and transitions of an EKS cluster. Understanding these states and transitions is essential for managing and troubleshooting your EKS clusters effectively.

### Complete Example

#### Full HTTP Request and Response

Here is a complete example of a request to describe an EKS cluster and the corresponding response:

**HTTP Request**

```http
POST / HTTP/1.1
Host: eks.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonEKS.DescribeCluster
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-west-2/eks/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=7b9f55c7b59e4b8b2d409b73f4b903d4b95e9b7f80f6c73e0d95b7d4f5d7c7b9
X-Amz-Date: 20230401T000000Z

{
    "name": "my-cluster"
}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 245
Date: Mon, 01 Apr 2023 00:00:00 GMT

{
    "cluster": {
        "name": "my-cluster",
        "arn": "arn:aws:eks:us-west-2:123456789012:cluster/my-cluster",
        "createdAt": "2023-04-01T00:00:00Z",
        "version": "1.20",
        "endpoint": "https://my-cluster.example.com",
        "status": "ACTIVE",
        "resourcesVpcConfig": {
            "subnetIds": ["subnet-12345678", "subnet-23456789"],
            "securityGroupIds": ["sg-12345678"],
            "vpcId": "vpc-12345678",
            "publicAccessCidrs": ["0.0.0.0/0"]
        },
        "roleArn": "arn:aws:iam::123456789012:role/eks-service-role",
        "platformVersion": "eks.5"
    }
}
```

#### Explanation of Headers

- **Content-Type**: Specifies the media type of the resource. In this case, it is `application/x-amz-json-1.1`.
- **Authorization**: Contains the AWS signature for the request.
- **X-Amz-Date**: Specifies the date and time of the request.
- **X-Amz-Target**: Specifies the target service and operation. In this case, it is `AmazonEKS.DescribeCluster`.

### Conclusion

Understanding the states of an EKS cluster and how to retrieve and manage cluster information using Python and Boto3 is crucial for effective DevOps practices. By following best practices and implementing security measures, you can ensure the integrity and availability of your EKS clusters.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/01-EKS Cluster Overview Using Python And Terraform/00-Overview|Overview]] | [[02-Introduction to Amazon EKS (Elastic Kubernetes Service)|Introduction to Amazon EKS (Elastic Kubernetes Service)]]
