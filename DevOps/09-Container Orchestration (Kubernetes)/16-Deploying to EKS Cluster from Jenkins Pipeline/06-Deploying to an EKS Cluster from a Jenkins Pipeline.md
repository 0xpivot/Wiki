---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying to an EKS Cluster from a Jenkins Pipeline

In this section, we will explore the process of deploying applications to an Amazon Elastic Kubernetes Service (EKS) cluster using a Jenkins pipeline. This involves setting up the necessary tools and configurations to ensure seamless integration between Jenkins and the EKS cluster.

### Background Theory

#### What is an EKS Cluster?

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to stand up or maintain your own Kubernetes control plane. EKS supports the Kubernetes API, so you can use existing tools and plugins to interact with your cluster.

An EKS cluster consists of a control plane and worker nodes. The control plane manages the cluster and includes components like the API server, etcd, controller manager, and scheduler. Worker nodes are the compute instances that run your applications.

#### What is Jenkins?

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. Jenkins pipelines allow you to define your continuous integration and continuous delivery (CI/CD) processes as code, making them repeatable and easier to manage.

### Setting Up the Environment

To deploy to an EKS cluster from a Jenkins pipeline, we need to ensure that the necessary tools are installed and configured correctly within the Jenkins environment.

#### Installing `kubectl` in Jenkins Container

`kubectl` is the command-line tool for interacting with a Kubernetes cluster. To deploy applications to the EKS cluster, we need to have `kubectl` installed in the Jenkins container.

**Why Install `kubectl`?**

Without `kubectl`, Jenkins would not be able to communicate with the Kubernetes cluster. `kubectl` allows us to perform various operations such as creating, updating, and deleting resources in the cluster.

**How to Install `kubectl`?**

We can install `kubectl` directly within the Jenkins container by adding a step to the Jenkinsfile. Here’s an example:

```groovy
pipeline {
    agent any
    stages {
        stage('Install kubectl') {
            steps {
                sh 'curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.23.0/bin/linux/amd64/kubectl'
                sh 'chmod +x ./kubectl'
                sh 'mv ./kubectl /usr/local/bin/kubectl'
            }
        }
    }
}
```

This script downloads the `kubectl` binary, makes it executable, and moves it to `/usr/local/bin` so that it is available in the PATH.

#### Installing AWS IAM Authenticator

The AWS IAM Authenticator is a tool that enables authentication to an EKS cluster using AWS Identity and Access Management (IAM) roles and policies. This is necessary because the EKS cluster runs on an AWS account, and we need to authenticate with both Kubernetes and AWS.

**Why Use AWS IAM Authenticator?**

The AWS IAM Authenticator allows us to leverage AWS IAM roles and policies for authentication, which provides a more secure and manageable way to control access to the EKS cluster.

**How to Install AWS IAM Authenticator?**

Similar to `kubectl`, we can install the AWS IAM Authenticator within the Jenkins container. Here’s an example:

```groovy
pipeline {
    agent any
    stages {
        stage('Install AWS IAM Authenticator') {
            steps {
                sh 'curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.23.0/2021-12-14/bin/linux/amd64/aws-iam-authenticator'
                sh 'chmod +x ./aws-iam-authenticator'
                sh 'mv ./aws-iam-authenticator /usr/local/bin/aws-iam-authenticator'
            }
        }
    }
}
```

This script downloads the AWS IAM Authenticator binary, makes it executable, and moves it to `/usr/local/bin`.

### Configuring Authentication

Once the necessary tools are installed, we need to configure authentication to the EKS cluster. This involves setting up the `kubeconfig` file, which contains the configuration details required to connect to the cluster.

**What is `kubeconfig`?**

The `kubeconfig` file contains information about the clusters, users, and contexts that Kubernetes uses to connect to the cluster. It is typically located at `~/.kube/config` on the local machine.

**How to Configure `kubeconfig`?**

We can configure the `kubeconfig` file within the Jenkins pipeline by using the AWS CLI to retrieve the necessary credentials and then configuring `kubectl`.

Here’s an example:

```groovy
pipeline {
    agent any
    stages {
        stage('Configure kubeconfig') {
            steps {
                sh 'aws eks update-kubeconfig --name my-cluster --region us-west-2'
            }
        }
    }
}
```

This script uses the AWS CLI to update the `kubeconfig` file with the necessary credentials for the specified EKS cluster.

### Deploying Applications

With the necessary tools installed and the `kubeconfig` file configured, we can now deploy applications to the EKS cluster using the Jenkins pipeline.

**Example Deployment**

Let’s say we have a simple application defined in a `deployment.yaml` file. We can deploy this application using `kubectl` within the Jenkins pipeline.

Here’s an example:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy application') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

This script applies the `deployment.yaml` file to the EKS cluster, creating the necessary resources.

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Missing Tools

If the necessary tools (`kubectl` and AWS IAM Authenticator) are not installed, the deployment will fail.

**How to Prevent:**

Ensure that the installation steps are included in the Jenkins pipeline and that they are executed successfully before attempting to deploy.

#### Pitfall 2: Incorrect Configuration

If the `kubeconfig` file is not correctly configured, the deployment will fail due to authentication issues.

**How to Prevent:**

Verify that the `kubeconfig` file is correctly configured by checking the output of the `aws eks update-kubeconfig` command and ensuring that the necessary credentials are present.

### Real-World Examples

#### Example 1: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to escalate privileges by manipulating the `kubeconfig` file. This highlights the importance of securing the `kubeconfig` file and ensuring that only authorized users have access to it.

**How to Prevent:**

Use IAM roles and policies to restrict access to the `kubeconfig` file and ensure that only authorized users have the necessary permissions.

#### Example 2: AWS IAM Role Misconfiguration

A misconfigured IAM role can lead to unauthorized access to the EKS cluster. This can occur if the IAM role is not properly restricted or if it has unnecessary permissions.

**How to Prevent:**

Use least privilege principles when configuring IAM roles and ensure that they have only the necessary permissions to perform their intended tasks.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: vulnerable-image:latest
    ports:
    - containerPort: 8080
```

#### Secure Code Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: secure-image:latest
    ports:
    - containerPort: 8080
    securityContext:
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

In the secure code example, we have added a `securityContext` to the pod specification, which drops all capabilities and sets the root filesystem to read-only. This helps to mitigate potential security risks.

### Hands-On Labs

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including Kubernetes-related challenges.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **CloudGoat**: A set of labs designed to help you learn about AWS security best practices.

These labs provide practical experience in deploying applications to an EKS cluster using a Jenkins pipeline and help reinforce the concepts covered in this chapter.

### Conclusion

Deploying applications to an EKS cluster from a Jenkins pipeline involves several steps, including installing necessary tools, configuring authentication, and deploying the application. By following the steps outlined in this chapter and being aware of common pitfalls and real-world examples, you can ensure a successful and secure deployment process.

---
<!-- nav -->
[[05-Deploying to EKS Cluster from Jenkins Pipeline|Deploying to EKS Cluster from Jenkins Pipeline]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[07-Entering the Jenkins Container|Entering the Jenkins Container]]
