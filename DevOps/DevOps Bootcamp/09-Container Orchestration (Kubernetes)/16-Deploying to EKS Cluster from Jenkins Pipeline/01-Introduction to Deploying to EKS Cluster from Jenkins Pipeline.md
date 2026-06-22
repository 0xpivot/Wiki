---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Deploying to EKS Cluster from Jenkins Pipeline

In this section, we will delve into the process of deploying applications to an Amazon Elastic Kubernetes Service (EKS) cluster using a Jenkins pipeline. This involves setting up Jenkins to interact with both the Kubernetes cluster and the AWS environment, ensuring proper authentication and authorization. We'll cover the necessary steps, configurations, and tools required to achieve this seamless integration.

### Background Theory

#### What is Jenkins?

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. It is widely used in continuous integration and continuous delivery (CI/CD) pipelines to automate the testing and deployment processes.

#### What is Amazon EKS?

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to stand up or maintain your own Kubernetes control plane. EKS supports the Kubernetes API, so you can use any Kubernetes-compliant tool with EKs.

#### Why Use Jenkins with EKS?

Using Jenkins with EKS allows you to automate the deployment of your applications to a Kubernetes cluster. This setup ensures that your deployments are consistent, repeatable, and can be triggered automatically based on certain events (like code commits).

### Setting Up Jenkins to Interact with EKS

To deploy to an EKS cluster from a Jenkins pipeline, you need to ensure that Jenkins has the necessary tools and credentials to communicate with both the Kubernetes cluster and the AWS environment.

#### Installing `kubectl` on Jenkins Server

The first step is to ensure that the `kubectl` command-line tool is available on the Jenkins server. `kubectl` is the primary command-line tool for interacting with Kubernetes clusters.

##### Step-by-Step Installation

1. **SSH into Jenkins Server**: Access the Jenkins server via SSH. In this example, the Jenkins server is running inside a Docker container on a DigitalOcean droplet.

```bash
ssh root@<DigitalOcean_Droplet_IP>
```

2. **Identify Jenkins Container**: List the running Docker containers to identify the Jenkins container.

```bash
docker ps
```

3. **Install `kubectl` Inside Jenkins Container**:

```bash
docker exec -it <jenkins_container_id> /bin/bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.23.0/bin/linux/amd64/kubectl
chmod +x kubectl
mv kubectl /usr/local/bin/
```

This installs `kubectl` inside the Jenkins container, making it available for use within the Jenkins pipeline.

### Configuring Authentication with AWS and EKS

To authenticate with both AWS and the EKS cluster, you need to set up the necessary credentials and configurations.

#### AWS Credentials

AWS credentials consist of an Access Key ID and a Secret Access Key. These credentials are used to authenticate with AWS services.

##### Step-by-Step Configuration

1. **Create an IAM User**: Create an IAM user with the necessary permissions to manage the EKS cluster and other AWS resources.

2. **Retrieve Access Key ID and Secret Access Key**: Retrieve the Access Key ID and Secret Access Key for the IAM user.

3. **Store AWS Credentials Securely**: Store the AWS credentials securely within Jenkins. You can use Jenkins credentials management to store these credentials.

```yaml
credentials:
  - id: aws-credentials
    username: <Access_Key_ID>
    password: <Secret_Access_Key>
```

4. **Configure AWS CLI**: Configure the AWS CLI inside the Jenkins container to use these credentials.

```bash
aws configure set aws_access_key_id <Access_Key_ID>
aws configure set aws_secret_access_key <Secret_Access_Key>
```

### Configuring `kubectl` with EKS

Once `kubectl` is installed and AWS credentials are configured, you need to set up `kubectl` to interact with the EKS cluster.

#### Step-by-Step Configuration

1. **Get Cluster Endpoint and Certificate Authority Data**: Retrieve the cluster endpoint and certificate authority data from the EKS console or using the AWS CLI.

```bash
aws eks describe-cluster --name <cluster_name> --query "cluster.{endpoint:endpoint,certificateAuthorityData:certificateAuthority.data}"
```

2. **Create `kubeconfig` File**: Create a `kubeconfig` file that contains the necessary information to connect to the EKS cluster.

```yaml
apiVersion: v1
kind: Config
clusters:
  - name: <cluster_name>
    cluster:
      server: <cluster_endpoint>
      certificate-authority-data: <certificate_authority_data>
users:
  - name: <user_name>
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1alpha1
        command: aws
        args:
          - sts
          - get-token
          - --cluster-name
          - <cluster_name>
contexts:
  - context:
      cluster: <cluster_name>
      user: <user_name>
    name: <context_name>
current-context: <context_name>
```

3. **Set `KUBECONFIG` Environment Variable**: Set the `KUBECONFIG` environment variable to point to the `kubeconfig` file.

```bash
export KUBECONFIG=/path/to/kubeconfig
```

### Jenkins Pipeline Configuration

With `kubectl` and AWS credentials configured, you can now set up the Jenkins pipeline to deploy to the EKS cluster.

#### Example Jenkinsfile

Here is an example of a Jenkinsfile that deploys an application to an EKS cluster:

```groovy
pipeline {
    agent { docker 'maven:3.6.3-openjdk-11' }

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-credentials').username
        AWS_SECRET_ACCESS_KEY = credentials('aws-credentials').password
        KUBECONFIG = '/path/to/kubeconfig'
    }

    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def app = load 'deploy-app.groovy'
                    app.deploy()
                }
            }
        }
    }
}
```

#### deploy-app.groovy

Here is an example of a Groovy script (`deploy-app.groovy`) that uses `kubectl` to deploy an application:

```groovy
def call() {
    sh 'kubectl apply -f deployment.yaml'
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Incorrect `kubeconfig` Configuration

Incorrect configuration of the `kubeconfig` file can lead to authentication failures when trying to connect to the EKS cluster.

##### How to Prevent

- Ensure that the `kubeconfig` file contains the correct cluster endpoint and certificate authority data.
- Verify that the `kubeconfig` file is correctly formatted and accessible to the Jenkins pipeline.

#### Pitfall: Exposing AWS Credentials

Exposing AWS credentials can lead to unauthorized access to your AWS resources.

##### How to Prevent

- Use Jenkins credentials management to securely store AWS credentials.
- Limit the permissions of the IAM user associated with the credentials to the minimum necessary.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in the AWS SDK for Java that could allow an attacker to bypass authentication checks. This highlights the importance of keeping your AWS SDK and related tools up to date.

#### Example: AWS Misconfiguration Leading to Data Exposure

A misconfigured AWS S3 bucket led to the exposure of sensitive data. This underscores the importance of properly securing and managing AWS resources.

### Conclusion

Deploying to an EKS cluster from a Jenkins pipeline requires careful setup and configuration. By following the steps outlined above, you can ensure that Jenkins has the necessary tools and credentials to interact with both the Kubernetes cluster and the AWS environment. Proper configuration and security practices are essential to prevent common pitfalls and ensure the integrity of your deployments.

### Practice Labs

For hands-on practice with deploying to EKS from Jenkins, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve Jenkins and Kubernetes.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes. It includes scenarios involving Jenkins and Kubernetes.
- **CloudGoat**: A series of labs designed to help you learn about cloud security on AWS. It includes scenarios involving EKS and Jenkins.

These labs provide practical experience in setting up and securing Jenkins pipelines that deploy to EKS clusters.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[02-Introduction to Deploying to an EKS Cluster from Jenkins Pipeline|Introduction to Deploying to an EKS Cluster from Jenkins Pipeline]]
