---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Home Directory and Configuration

In this section, we will delve into the process of deploying applications to an Amazon Elastic Kubernetes Service (EKS) cluster using a Jenkins pipeline. This involves setting up the necessary configurations within the Jenkins environment, particularly focusing on the `.kube` directory and the associated credentials required for communication with the EKS cluster.

### Understanding the `.kube` Directory

The `.kube` directory is a hidden directory located in the home directory of the Jenkins user. This directory contains the `config` file, which is crucial for Kubernetes operations. The `config` file stores essential information such as the server API URL, certificate authority data, and authentication methods.

#### Server API URL

The server API URL specifies the endpoint where the Kubernetes cluster can be reached. This is typically the URL of the EKS cluster's API server. For example:

```yaml
server:
  url: https://<cluster-name>.<region>.eks.amazonaws.com
```

#### Certificate Authority Data

The certificate authority (CA) data is used to verify the identity of the Kubernetes cluster. This ensures that the connection between Jenkins and the EKS cluster is secure. The CA data is usually provided by AWS and is included in the `config` file as follows:

```yaml
clusters:
- name: <cluster-name>
  cluster:
    certificate-authority-data: <base64-encoded-ca-data>
```

#### Authentication with AWS IM Authenticator

To authenticate with AWS, the `aws-iam-authenticator` tool is used. This tool helps in generating the necessary tokens for authentication. The `config` file includes a reference to this tool:

```yaml
users:
- name: <user-name>
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "<cluster-name>"
```

### Setting Up Credentials in Jenkins

For Jenkins to interact with the EKS cluster, it requires AWS credentials. These credentials are typically stored in the Jenkins credential store. The credentials consist of an access key ID and a secret access key.

#### Creating an IAM User for Jenkins

It is a best practice to create a dedicated IAM user for Jenkins. This user should have the minimum set of permissions required to perform the necessary actions, such as deploying applications to the EKS cluster.

##### Steps to Create an IAM User

1. **Log in to the AWS Management Console**.
2. **Navigate to the IAM service**.
3. **Create a new IAM user**.
4. **Assign the necessary policies** to the user. For example, the `AmazonEKSClusterPolicy` and `AmazonEKSPodPolicy`.

Here is an example of creating an IAM user via the AWS CLI:

```bash
aws iam create-user --user-name JenkinsUser
aws iam attach-user-policy --user-name JenkinsUser --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
aws iam attach-user-policy --user-name JenkinsUser --policy-arn arn:aws:iam::aws:policy/AmazonEKSPodPolicy
```

### Configuring Jenkins with AWS Credentials

Once the IAM user is created, the next step is to configure Jenkins with these credentials.

#### Adding Credentials to Jenkins

1. **Log in to Jenkins**.
2. **Navigate to the Credentials section**.
3. **Add a new credential** of type "AWS Credentials".
4. **Enter the access key ID and secret access key**.

Here is an example of configuring Jenkins with AWS credentials via the Jenkins UI:

1. Go to `Manage Jenkins` > `Manage Credentials`.
2. Click on `Global credentials (unrestricted)`.
3. Click on `Add Credentials`.
4. Select `AWS Credentials`.
5. Enter the access key ID and secret access key.

### Example Configuration Files

Below are the complete configuration files and steps involved in setting up Jenkins for deployment to an EKS cluster.

#### Jenkins `config.xml` Example

```xml
<com.cloudbees.jenkins.plugins.awscredentials.AWSCredentialsImpl plugin="aws-credentials@1.27">
  <scope>GLOBAL</scope>
  <id>JenkinsUser</id>
  <description>AWS credentials for Jenkins</description>
  <accessKey>AKIAIOSFODNN7EXAMPLE</accessKey>
  <secretKey>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</secretKey>
</com.cloudbees.jenkins.plugins.awscredentials.AWSCredentialsImpl>
```

#### Jenkins Pipeline Script Example

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy to EKS') {
            steps {
                script {
                    def kubectl = tool 'kubectl'
                    sh "${kubectl} apply -f deployment.yaml"
                }
            }
        }
    }
}
```

### Diagrams and Topologies

Let's visualize the architecture and flow of the deployment process using Mermaid diagrams.

#### Architecture Diagram

```mermaid
graph LR
  A[Jenkins] --> B[.kube/config]
  B --> C[EKS Cluster]
  A --> D[AWS IAM User]
  D --> C
```

#### Sequence Diagram

```mermaid
sequenceDiagram
  participant Jenkins
  participant KubeConfig
  participant EKSCluster
  participant IAMUser
  Jenkins->>KubeConfig: Load .kube/config
  KubeConfig->>EKSCluster: Connect to EKS
  Jenkins->>IAMUser: Authenticate with AWS
  IAMUser->>EKSCluster: Authorize access
  Jenkins->>EKSCluster: Deploy application
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Using Default Admin Credentials

Using default admin credentials for Jenkins can lead to security vulnerabilities. It is crucial to create a dedicated IAM user with minimal permissions.

##### Prevention

1. **Create a dedicated IAM user** for Jenkins.
2. **Assign the necessary policies** to the user.
3. **Store the credentials securely** in Jenkins.

#### Pitfall: Insecure Communication

Insecure communication between Jenkins and the EKS cluster can expose sensitive data.

##### Prevention

1. **Use HTTPS** for all communications.
2. **Enable TLS encryption** for the Kubernetes API server.
3. **Verify the certificate authority** data in the `config` file.

### Real-World Examples and CVEs

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in the Kubernetes API server that allows unauthorized access to resources. This highlights the importance of securing the communication channel and using strong authentication mechanisms.

##### Impact

- Unauthorized access to Kubernetes resources.
- Potential data exposure and manipulation.

##### Mitigation

1. **Update to the latest version** of Kubernetes.
2. **Enable RBAC (Role-Based Access Control)**.
3. **Use strong authentication methods** like AWS IAM Authenticator.

### Conclusion

Deploying applications to an EKS cluster from a Jenkins pipeline involves several critical steps, including setting up the `.kube` directory, configuring AWS credentials, and ensuring secure communication. By following best practices and using dedicated IAM users, you can significantly enhance the security of your deployment process.

### Practice Labs

For hands-on experience with deploying to EKS clusters from Jenkins pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including CI/CD pipelines.
- **CloudGoat**: Provides a series of labs focused on cloud security, including AWS and Kubernetes configurations.

These labs will help you gain practical experience and reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[07-Entering the Jenkins Container|Entering the Jenkins Container]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/09-Practice Questions & Answers|Practice Questions & Answers]]
