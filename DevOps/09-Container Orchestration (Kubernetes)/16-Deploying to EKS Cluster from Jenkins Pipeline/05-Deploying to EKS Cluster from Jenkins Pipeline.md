---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying to EKS Cluster from Jenkins Pipeline

### Background Theory

In the context of DevOps, deploying applications to a Kubernetes cluster, such as Amazon Elastic Kubernetes Service (EKS), from a continuous integration/continuous deployment (CI/CD) pipeline like Jenkins, requires several key components and steps. This process involves setting up authentication mechanisms, configuring the necessary tools, and ensuring secure communication between Jenkins and the EKS cluster.

### Key Components

#### EKS Cluster Configuration

When creating an EKS cluster, one of the critical outputs is the `kubeconfig` file. This file contains essential information for authenticating and connecting to the EKS cluster, including:

- **API Server Endpoint**: The URL of the Kubernetes API server.
- **Client Certificate and Key**: Used for mutual TLS authentication.
- **Cluster CA Certificate**: Used to verify the identity of the API server.
- **Namespace and Context**: Information about the default namespace and context to use when interacting with the cluster.

The `kubeconfig` file is crucial because it provides all the necessary details for a client (like Jenkins) to securely communicate with the EKS cluster.

#### Authentication Mechanisms

To authenticate and connect to the EKS cluster from Jenkins, two primary tools are required:

1. **Kubectl**: The command-line tool for interacting with Kubernetes clusters.
2. **AWS IAM Authenticator**: A tool that integrates AWS Identity and Access Management (IAM) with Kubernetes for authentication.

### Installing Kubectl and AWS IAM Authenticator

#### Kubectl Installation

Kubectl is the primary command-line tool used to interact with Kubernetes clusters. To install Kubectl, you can use the following commands:

```sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/
```

This script downloads the latest version of Kubectl, sets the execute permissions, and moves it to `/usr/local/bin/`.

#### AWS IAM Authenticator Installation

The AWS IAM Authenticator is required to authenticate with the EKS cluster using IAM roles. To install it, follow these steps:

```sh
curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.21.2/2021-07-05/bin/linux/amd64/aws-iam-authenticator
chmod +x aws-iam-authenticator
mv aws-iam-authenticator /usr/local/bin/
```

This script downloads the AWS IAM Authenticator, sets the execute permissions, and moves it to `/usr/local/bin/`.

### Configuring Jenkins to Connect to EKS

#### Setting Up Jenkins Environment

Jenkins typically runs in a lightweight container, which means it may lack some essential tools like editors or additional utilities. Therefore, you need to ensure that Jenkins has the necessary tools and configurations to interact with the EKS cluster.

#### Creating `kubeconfig` File

Since Jenkins does not have an editor installed by default, you will need to create the `kubeconfig` file manually. Here’s an example of how to create a `kubeconfig` file:

```yaml
apiVersion: v1
kind: Config
clusters:
- name: my-cluster
  cluster:
    server: https://<cluster-endpoint>
    certificate-authority-data: <base64-encoded-ca-cert>
users:
- name: my-user
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "my-cluster"
contexts:
- context:
    cluster: my-cluster
    user: my-user
  name: my-context
current-context: my-context
```

Replace `<cluster-endpoint>` and `<base64-encoded-ca-cert>` with the actual values from your EKS cluster.

### Jenkins Pipeline Configuration

To deploy to the EKS cluster from a Jenkins pipeline, you need to configure the pipeline to use the `kubeconfig` file and the necessary authentication mechanisms. Here’s an example of a Jenkins pipeline script:

```groovy
pipeline {
    agent any
    environment {
        KUBECONFIG = '/path/to/kubeconfig'
    }
    stages {
        stage('Deploy to EKS') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

### Pitfalls and Common Mistakes

#### Incorrect Permissions

One common mistake is not setting the correct permissions on the `kubeconfig` file. Ensure that the file has the appropriate read permissions for the Jenkins user.

#### Missing Tools

Another common issue is missing tools like `kubectl` or `aws-iam-authenticator`. Make sure these tools are installed and accessible within the Jenkins environment.

### Real-World Examples

#### Recent CVEs and Breaches

A notable breach involving Kubernetes was the **CVE-2021-25741**. This vulnerability allowed unauthorized access to Kubernetes clusters due to misconfigured RBAC policies. Ensuring proper RBAC policies and secure `kubeconfig` management can help mitigate such risks.

### How to Prevent / Defend

#### Detection

Regularly audit your Kubernetes clusters for misconfigurations and vulnerabilities. Tools like `kube-bench` can help identify potential issues.

#### Prevention

1. **Secure `kubeconfig` Management**: Store `kubeconfig` files securely and limit access to them.
2. **RBAC Policies**: Implement strict Role-Based Access Control (RBAC) policies to restrict access to resources.
3. **Network Policies**: Use Kubernetes Network Policies to control traffic flow within the cluster.
4. **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.

### Secure Code Fix Example

#### Vulnerable Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: vulnerable-image
    ports:
    - containerPort: 8080
```

#### Fixed Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: secure-image
    ports:
    - containerPort: 8080
    securityContext:
      runAsUser: 1000
      runAsGroup: 3000
      readOnlyRootFilesystem: true
```

### Conclusion

Deploying to an EKS cluster from a Jenkins pipeline involves setting up the necessary tools, configuring authentication mechanisms, and ensuring secure communication. By following best practices and implementing robust security measures, you can effectively manage and secure your Kubernetes deployments.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to Kubernetes and cloud security.
- **OWASP Juice Shop**: Provides a vulnerable application for learning web security concepts.
- **CloudGoat**: Focuses on AWS security and includes scenarios for EKS and other services.

These labs provide practical experience and reinforce the theoretical knowledge covered in this chapter.

---
<!-- nav -->
[[04-Introduction to Kubernetes and EKS Clusters|Introduction to Kubernetes and EKS Clusters]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[06-Deploying to an EKS Cluster from a Jenkins Pipeline|Deploying to an EKS Cluster from a Jenkins Pipeline]]
