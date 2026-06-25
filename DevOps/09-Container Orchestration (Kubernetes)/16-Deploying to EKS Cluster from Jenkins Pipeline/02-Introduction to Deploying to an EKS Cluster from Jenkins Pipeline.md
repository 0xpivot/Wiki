---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Deploying to an EKS Cluster from Jenkins Pipeline

In this section, we will delve into the process of deploying applications to an Amazon Elastic Kubernetes Service (EKS) cluster using a Jenkins pipeline. This approach leverages the power of continuous integration and delivery (CI/CD) to automate the deployment process, ensuring consistency and reliability in your application deployments.

### Background Theory

Before diving into the specifics of the deployment process, it's essential to understand the underlying concepts:

#### Amazon Elastic Kubernetes Service (EKS)

Amazon EKS is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes cluster setup and management. EKS handles the availability and scalability of the Kubernetes control plane, allowing you to focus on deploying and managing your applications.

#### Jenkins

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. Jenkins pipelines enable you to define your entire CI/CD process as code, making it easier to manage and maintain.

#### Kubernetes Configuration

Kubernetes uses configuration files to define the desired state of your application. These files are typically written in YAML format and describe the resources required by your application, such as pods, services, and deployments.

### Setting Up the Environment

To deploy to an EKS cluster from a Jenkins pipeline, you need to ensure that the necessary environment is set up correctly. This includes configuring the AWS credentials and setting up the `kubectl` configuration file.

#### AWS Credentials

AWS credentials are required to authenticate with the EKS cluster. In the context of Jenkins, these credentials are typically stored as environment variables within the Jenkins job configuration.

```yaml
# Example Jenkinsfile snippet
environment {
    AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
    AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
}
```

#### `kubectl` Configuration File

The `kubectl` configuration file (`kubeconfig`) is used to store information about your clusters, including authentication details. By default, `kubectl` looks for this file in the `~/.kube` directory.

```yaml
# Example kubeconfig file
apiVersion: v1
kind: Config
clusters:
- name: my-cluster
  cluster:
    server: https://<cluster-endpoint>
users:
- name: my-user
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
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

### Configuring Jenkins Pipeline

Now that the environment is set up, we can configure the Jenkins pipeline to deploy to the EKS cluster.

#### Jenkinsfile Structure

A typical Jenkinsfile for deploying to an EKS cluster might look like this:

```groovy
pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/my-repo/my-app.git'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t my-app .'
            }
        }

        stage('Deploy') {
            steps {
                sh 'kubectl apply -f k8s/deployment.yaml'
            }
        }
    }
}
```

### Detailed Deployment Process

Let's break down the deployment process step-by-step:

#### Checkout Stage

In the checkout stage, the Jenkins pipeline checks out the source code from the repository.

```groovy
stage('Checkout') {
    steps {
        git 'https://github.com/my-repo/my-app.git'
    }
}
```

#### Build Stage

In the build stage, the Docker image is built using the `docker build` command.

```groovy
stage('Build') {
    steps {
        sh 'docker build -t my-app .'
    }
}
```

#### Deploy Stage

In the deploy stage, the `kubectl` command is used to apply the Kubernetes deployment configuration.

```groovy
stage('Deploy') {
    steps {
        sh 'kubectl apply -f k8s/deployment.yaml'
    }
}
```

### Kubernetes Deployment Configuration

The Kubernetes deployment configuration file (`deployment.yaml`) defines the desired state of the application. Here is an example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 80
```

### Authentication with AWS IAM Authenticator

The AWS IAM Authenticator is used to authenticate with the EKS cluster using AWS IAM roles. This ensures that only authorized users can access the cluster.

#### Configuring AWS IAM Authenticator

The `kubeconfig` file should be configured to use the AWS IAM Authenticator. This is done by specifying the `exec` plugin in the `kubeconfig` file.

```yaml
users:
- name: my-user
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "my-cluster"
```

### Running the Pipeline

Once the Jenkinsfile is committed to the repository, the pipeline can be triggered manually or automatically based on the branch configuration.

#### Triggering the Pipeline

To trigger the pipeline, navigate to the Jenkins dashboard and select the appropriate job. Click on "Build Now" to start the pipeline.

### Monitoring the Pipeline

The pipeline execution can be monitored through the Jenkins UI. Each stage of the pipeline is displayed, along with the status and logs.

#### Checking Logs

To check the logs of the pipeline execution, click on the build number and then select "Console Output".

### Real-World Examples

#### Recent CVEs and Breaches

One notable breach involving Kubernetes was the **CVE-2021-25741** vulnerability in the Kubernetes API server. This vulnerability allowed attackers to bypass RBAC (Role-Based Access Control) restrictions and gain unauthorized access to the cluster.

#### Secure Coding Practices

To prevent such vulnerabilities, it is crucial to follow secure coding practices. This includes:

- Using least privilege principles for IAM roles.
- Regularly updating and patching Kubernetes components.
- Implementing network policies to restrict traffic between pods.

### How to Prevent / Defend

#### Detection

To detect potential security issues, you can use tools like **kube-bench** and **kubescape**. These tools help you identify misconfigurations and vulnerabilities in your Kubernetes cluster.

```bash
# Example kube-bench command
./kube-bench --version=1.22 --check=controls
```

#### Prevention

To prevent security issues, follow these best practices:

- **Least Privilege**: Ensure that IAM roles have the minimum permissions required.
- **Regular Updates**: Keep Kubernetes components up-to-date with the latest security patches.
- **Network Policies**: Implement network policies to restrict traffic between pods.

#### Secure Code Fix

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: my-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**Secure Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: my-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
  resourceNames: ["my-pod"]
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

### Conclusion

Deploying to an EKS cluster from a Jenkins pipeline involves setting up the environment, configuring the Jenkins pipeline, and ensuring proper authentication and authorization. By following best practices and using secure coding techniques, you can minimize the risk of security vulnerabilities in your Kubernetes cluster.

### Further Reading

- **AWS Documentation**: Official documentation for Amazon EKS and AWS IAM.
- **Kubernetes Documentation**: Official documentation for Kubernetes.
- **Jenkins Documentation**: Official documentation for Jenkins and Jenkins pipelines.

By mastering these concepts, you will be well-equipped to deploy applications to an EKS cluster using a Jenkins pipeline.

---
<!-- nav -->
[[01-Introduction to Deploying to EKS Cluster from Jenkins Pipeline|Introduction to Deploying to EKS Cluster from Jenkins Pipeline]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[03-Introduction to Deploying to an EKS Cluster from a Jenkins Pipeline|Introduction to Deploying to an EKS Cluster from a Jenkins Pipeline]]
