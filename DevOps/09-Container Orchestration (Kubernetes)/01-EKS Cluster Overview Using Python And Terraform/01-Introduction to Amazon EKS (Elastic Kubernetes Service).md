---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Amazon EKS (Elastic Kubernetes Service)

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane. Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. With EKS, you can use Kubernetes to run and manage your containerized applications on AWS without having to install and maintain your own Kubernetes control plane.

### Why Use Amazon EKS?

1. **Managed Control Plane**: EKS manages the Kubernetes control plane, which includes the API server, scheduler, and controller manager. This means you don't have to worry about maintaining these components.
2. **High Availability**: EKS provides high availability for your Kubernetes control plane across multiple Availability Zones within a region.
3. **Integration with AWS Services**: EKS integrates seamlessly with other AWS services like VPC, IAM, and CloudWatch, providing a robust environment for deploying and managing containerized applications.
4. **Security**: EKS supports IAM roles for service accounts, which allows you to securely control access to your Kubernetes resources using IAM policies.

### Setting Up an EKS Cluster

To interact with an EKS cluster programmatically, you can use the AWS SDK for Python (Boto3) or Terraform. In this chapter, we'll focus on using Boto3 to interact with an EKS cluster.

#### Prerequisites

Before you start, ensure you have the following:

1. **AWS Account**: You need an active AWS account.
2. **IAM Role**: An IAM role with permissions to create and manage EKS clusters.
3. **Python Environment**: A Python environment with Boto3 installed.

### Creating an EKS Client

To interact with an EKS cluster using Boto3, you first need to create an EKS client. Here’s how you can do it:

```python
import boto3

# Create an EKS client for the Paris region
eks_client = boto3.client('eks', region_name='eu-west-3')
```

In the above code snippet, `boto3.client` creates an EKS client for the specified region (`eu-west-3`, which corresponds to the Paris region).

### Listing Clusters

Once you have an EKS client, you can use it to list all the clusters in the specified region. The `list_clusters` method returns a list of cluster names.

```python
response = eks_client.list_clusters()

# Print the list of cluster names
print(response['clusters'])
```

The `list_clusters` method does not require any parameters. It simply returns a dictionary containing a list of cluster names.

### Detailed Example

Let's walk through a detailed example of listing clusters and checking their status.

#### Step 1: List Clusters

First, we list all the clusters in the specified region.

```python
import boto3

# Create an EKS client for the Paris region
eks_client = boto3.client('eks', region_name='eu-west-3')

# List all clusters in the region
response = eks_client.list_clusters()

# Print the list of cluster names
print("Clusters:", response['clusters'])
```

#### Step 2: Check Cluster Status

Next, we can check the status of each cluster. To do this, we need to call the `describe_cluster` method for each cluster.

```python
for cluster_name in response['clusters']:
    cluster_info = eks_client.describe_cluster(name=cluster_name)
    print(f"Cluster Name: {cluster_name}")
    print(f"Status: {cluster_info['cluster']['status']}")
    print(f"Endpoint: {cluster_info['cluster']['endpoint']}")
    print(f"ARN: {cluster_info['cluster']['arn']}")
```

### Full Example Code

Here is the complete code to list clusters and check their status:

```python
import boto3

# Create an EKS client for the Paris region
eks_client = boto3.client('eks', region_name=' 'eu-west-3')

# List all clusters in the region
response = eks_client.list_clusters()

# Print the list of cluster names
print("Clusters:", response['clusters'])

# Check the status of each cluster
for cluster_name in response['clusters']:
    cluster_info = eks_client.describe_cluster(name=cluster_name)
    print(f"Cluster Name: {cluster_name}")
    print(f"Status: {cluster_info['cluster']['status']}")
    print(f"Endpoint: {cluster_info['cluster']['endpoint']}")
    print(f"ARN: {cluster_info['cluster']['arn']}")
```

### HTTP Request and Response

When you make a request to the EKS API, it sends an HTTP request and receives an HTTP response. Here is an example of the HTTP request and response for the `list_clusters` method:

#### HTTP Request

```http
POST / HTTP/1.1
Host: eks.eu-west-3.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonEKS.ListClusters
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231010/eu-west-3/eks/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=fe5f3bc675e1e4cc6af4538b1c1c93407fa87a8d9480e1be8c9d8bfbf1c4b8c2
X-Amz-Date: 20231010T193642Z
Content-Length: 0
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 46
Date: Tue, 10 Oct 2023 19:36:42 GMT
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890ab

{
    "clusters": ["my-cluster"]
}
```

### Common Pitfalls and How to Avoid Them

1. **Incorrect Region**: Ensure you are using the correct region when creating the EKS client. Using the wrong region can result in errors.
2. **Insufficient Permissions**: Make sure the IAM role you are using has the necessary permissions to list and describe clusters.
3. **Network Issues**: Ensure your network configuration allows outbound traffic to the EKS API endpoint.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Enable CloudTrail logging to monitor API calls made to the EKS service. Use CloudWatch to monitor the health and status of your EKS clusters.
- **IAM Policies**: Regularly review IAM policies to ensure they provide the least privilege necessary for your EKS operations.

#### Prevention

- **IAM Roles**: Use IAM roles for service accounts to control access to your EKS resources.
- **Network Configuration**: Configure your VPC to allow only necessary traffic to the EKS API endpoint.

#### Secure Coding Fixes

**Vulnerable Code**

```python
import boto3

# Incorrect region
eks_client = boto3.client('eks', region_name='us-east-1')

response = eks_client.list_clusters()
print(response['clusters'])
```

**Secure Code**

```python
import boto3

# Correct region
eks_client = boto3.client('eks', region_name='eu-west-3')

response = eks_client.list_clusters()
print(response['clusters'])
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-20225**: This vulnerability allowed unauthorized access to Kubernetes clusters due to misconfigured IAM roles. Ensure IAM roles are correctly configured and reviewed regularly.
- **Breaches**: Several organizations have experienced breaches due to misconfigured EKS clusters. Regular monitoring and auditing can help prevent such incidents.

### Practice Labs

For hands-on practice with EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to Kubernetes and container security.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed on EKS for security testing.
- **CloudGoat**: A cloud security training platform that includes scenarios for securing EKS clusters.

By following these steps and best practices, you can effectively manage and secure your EKS clusters using Python and Boto3.

---
<!-- nav -->
[[01-EKS Cluster Overview Using Python and Terraform|EKS Cluster Overview Using Python and Terraform]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/01-EKS Cluster Overview Using Python And Terraform/00-Overview|Overview]] | [[03-Introduction to EKS Cluster Management Using Python and Terraform|Introduction to EKS Cluster Management Using Python and Terraform]]
