---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Gathering Information About EKS Clusters Using Python

Now that we have our EKS clusters set up, let's write a Python program to gather and display information about these clusters. Specifically, we want to get the status, Kubernetes version, and cluster endpoint for each cluster.

### Prerequisites

Before we start, ensure you have the following installed:

1. **Python**: Ensure Python is installed on your system.
2. **Boto3**: Install the AWS SDK for Python (`boto3`) using pip:

```sh
pip install boto3
```

### Python Program to Gather Cluster Information

Here's a Python script to gather and display the required information:

```python
import boto3

def get_clusters_info():
    eks_client = boto3.client('eks', region_name='us-west-2')
    
    clusters_info = []
    
    # List all clusters
    clusters_response = eks_client.list_clusters()
    clusters = clusters_response['clusters']
    
    for cluster_name in clusters:
        # Describe each cluster
        cluster_description = eks_client.describe_cluster(name=cluster_name)
        
        cluster_status = cluster_description['cluster']['status']
        kubernetes_version = cluster_description['cluster']['version']
        cluster_endpoint = cluster_description['cluster']['endpoint']
        
        clusters_info.append({
            'name': cluster_name,
            'status': cluster_status,
            'kubernetes_version': kubernetes_version,
            'endpoint': cluster_endpoint
        })
    
    return clusters_info

if __name__ == "__main__":
    clusters_info = get_clusters_info()
    
    for info in clusters_info:
        print(f"Cluster Name: {info['name']}")
        print(f"Status: {info['status']}")
        print(f"Kubernetes Version: {info['kubernetes_version']}")
        print(f"Endpoint: {info['endpoint']}")
        print("-" * 40)
```

### Explanation of the Python Code

1. **Import boto3**: Import the AWS SDK for Python.
2. **Initialize Client**: Initialize the EKS client with the specified region.
3. **List Clusters**: Use the `list_clusters` method to get a list of all clusters.
4. **Describe Each Cluster**: Iterate through each cluster and use the `describe_cluster` method to get detailed information.
5. **Store Information**: Store the required information in a list of dictionaries.
6. **Print Information**: Print the gathered information for each cluster.

### Adding a Simple Web Interface

To make the information more accessible, we can add a simple web interface using Flask, a lightweight web framework for Python.

#### Flask Setup

First, install Flask:

```sh
pip install flask
```

Then, modify the Python script to include a Flask app:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/clusters', methods=['GET'])
def get_clusters():
    clusters_info = get_clusters_info()
    return jsonify(clusters_info)

if __name__ == "__main__":
    app.run(debug=True)
```

### Explanation of the Flask Code

1. **Import Flask**: Import the Flask module.
2. **Create App**: Create a Flask app instance.
3. **Define Route**: Define a route `/clusters` to return the cluster information as JSON.
4. **Run App**: Run the Flask app in debug mode.

### Running the Flask App

To run the Flask app, execute the following command:

```sh
python app.py
```

This will start a local server, and you can access the cluster information by visiting `http://localhost:5000/clusters`.

### Real-World Examples and Security Considerations

#### Recent Breaches and CVEs

Recent breaches involving Kubernetes and EKS include:

- **CVE-2021-25741**: A vulnerability in the Kubernetes API server allowed unauthorized access to sensitive data.
- **CVE-2021-25742**: Another vulnerability in the Kubernetes API server allowed unauthorized access to sensitive data.

These vulnerabilities highlight the importance of keeping your Kubernetes and EKS clusters up-to-date and properly configured.

#### Secure Coding Practices

1. **IAM Roles**: Ensure IAM roles are properly configured and restricted to the minimum necessary permissions.
2. **Network Policies**: Implement network policies to restrict traffic between pods.
3. **Encryption**: Enable encryption for data at rest and in transit.
4. **Regular Audits**: Regularly audit your clusters for misconfigurations and vulnerabilities.

### How to Prevent / Defend

#### Detection

1. **Logging and Monitoring**: Enable logging and monitoring for your EKS clusters using tools like CloudWatch.
2. **Security Groups**: Use security groups to restrict access to your clusters.

#### Prevention

1. **IAM Policies**: Use IAM policies to restrict access to your clusters.
2. **Pod Security Policies**: Implement pod security policies to enforce security rules at the pod level.

#### Secure-Coding Fixes

**Vulnerable Code**:

```python
import boto3

def get_clusters_info():
    eks_client = boto3.client('eks', region_name='us-west-2')
    
    clusters_info = []
    
    # List all clusters
    clusters_response = eks_client.list_clusters()
    clusters = clusters_response['clusters']
    
    for cluster_name in clusters:
        # Describe each cluster
        cluster_description = eks_client.describe_cluster(name=cluster_name)
        
        cluster_status = cluster_description['cluster']['status']
        kubernetes_version = cluster_description['cluster']['version']
        cluster_endpoint = cluster_description['cluster']['endpoint']
        
        clusters_info.append({
            'name': cluster_name,
            'status': cluster_status,
            'kubernetes_version': kubernetes_version,
            'endpoint': cluster_endpoint
        })
    
    return clusters_info
```

**Secure Code**:

```python
import boto3

def get_clusters_info():
    eks_client = boto3.client('eks', region_name='us-west-2')
    
    clusters_info = []
    
    # List all clusters
    clusters_response = eks_client.list_clusters()
    clusters = clusters_response['clusters']
    
    for cluster_name in clusters:
        # Describe each cluster
        cluster_description = eks_client.describe_cluster(name=_validate_cluster_name(cluster_name))
        
        cluster_status = cluster_description['cluster']['status']
        kubernetes_version = cluster_description['cluster']['version']
        cluster_endpoint = cluster_description['cluster']['endpoint']
        
        clusters_info.append({
            'name': cluster_name,
            'status': cluster_status,
            'kubernetes_version': kubernetes_version,
            'endpoint': cluster_endpoint
        })
    
    return clusters_info

def _validate_cluster_name(cluster_name):
    if not isinstance(cluster_name, str) or len(cluster_name) > 100:
        raise ValueError("Invalid cluster name")
    return cluster_name
```

### Conclusion

In this chapter, we covered the creation and management of EKS clusters using Terraform and gathering information about these clusters using Python. We also explored adding a simple web interface using Flask and discussed security considerations and best practices for securing EKS clusters.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in managing and securing EKS clusters and related infrastructure.

---
<!-- nav -->
[[04-Introduction to EKS Clusters and Infrastructure Management|Introduction to EKS Clusters and Infrastructure Management]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/01-EKS Cluster Overview Using Python And Terraform/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/01-EKS Cluster Overview Using Python And Terraform/06-Practice Questions & Answers|Practice Questions & Answers]]
