---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Introduction to EKS Blueprints and Secure CI/CD Practices

In this chapter, we will delve into the process of deploying an application workload in an Amazon Elastic Kubernetes Service (EKS) cluster using EKS Blueprints. Specifically, we will focus on creating a repository for a custom microservices application and deploying it into the cluster using secure Continuous Integration and Continuous Deployment (CI/CD) practices. This chapter aims to provide a comprehensive understanding of the entire process, including the theoretical background, practical implementation, and security considerations.

### Background Theory

Before diving into the practical aspects, let's understand the key concepts involved:

#### Amazon Elastic Kubernetes Service (EKS)

Amazon EKS is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes cluster setup and management. EKS handles the provisioning, scaling, and management of the control plane nodes, allowing you to focus on deploying and managing your applications.

#### EKS Blueprints

EKS Blueprints is a feature that provides pre-configured templates for setting up EKS clusters with specific configurations. These blueprints can help you quickly set up a cluster with best practices and security features already in place. This is particularly useful for developers and DevOps teams who want to get started quickly without having to manually configure every aspect of the cluster.

#### Microservices Architecture

A microservices architecture is a design approach where an application is composed of small, independent services that communicate with each other using well-defined APIs. Each microservice is responsible for a specific business function and can be developed, deployed, and scaled independently. This architecture allows for greater flexibility and scalability compared to monolithic applications.

#### CI/CD Pipeline

Continuous Integration (CI) and Continuous Deployment (CD) are practices that automate the integration and deployment of code changes. CI involves automatically building and testing code changes as they are committed to a version control system. CD extends this by automatically deploying the tested code to production or staging environments. Together, these practices ensure that code changes are validated and deployed efficiently and reliably.

### Setting Up the Repository

The first step in deploying our microservices application is to create a repository for the application code. This repository will serve as the central location for storing and managing the application code.

#### Creating the Repository

To create the repository, we can use a version control system like Git. Here’s an example of how to create a new Git repository:

```bash
# Initialize a new Git repository
mkdir my-microservices-app
cd my-microservices-app
git init
```

Once the repository is initialized, we can start adding our microservices code to it. Each microservice can be organized into its own directory within the repository.

#### Example Directory Structure

Here’s an example of how the repository might be structured:

```
my-microservices-app/
├── microservice-1/
│   ├── Dockerfile
│   ├── src/
│   └── tests/
├── microservice-2/
│   ├── Dockerfile
│   ├── src/
│   └── tests/
├── .gitignore
└── README.md
```

Each microservice directory contains its own `Dockerfile` for building the Docker image, a `src` directory for the source code, and a `tests` directory for the test cases.

### Configuring the CI/CD Pipeline

Next, we need to set up a CI/CD pipeline to automate the build, test, and deployment processes. There are several tools available for setting up CI/CD pipelines, such as Jenkins, GitLab CI, CircleCI, and AWS CodePipeline.

#### Using AWS CodePipeline

AWS CodePipeline is a fully managed continuous delivery service that helps you automate your release processes. Here’s how to set up a basic CI/CD pipeline using AWS CodePipeline:

1. **Source Stage**: This stage retrieves the code from the repository. We can use AWS CodeCommit, GitHub, or Bitbucket as the source provider.

2. **Build Stage**: This stage builds the Docker images for each microservice. We can use AWS CodeBuild for this purpose.

3. **Deploy Stage**: This stage deploys the built Docker images to the EKS cluster. We can use AWS CodeDeploy or kubectl commands for this.

#### Example CodePipeline Configuration

Here’s an example of how the CodePipeline configuration might look:

```yaml
pipeline:
  name: MyMicroservicesAppPipeline
  stages:
    - name: Source
      actions:
        - name: SourceAction
          actionTypeId:
            category: Source
            owner: AWS
            provider: CodeCommit
            version: 1
          configuration:
            RepositoryName: my-microservices-app
            BranchName: main
    - name: Build
      actions:
        - name: BuildAction
          actionTypeId:
            category: Build
            owner: AWS
            provider: CodeBuild
            version: 1
          configuration:
            ProjectName: MyMicroservicesAppBuild
    - name: Deploy
      actions:
        - name: DeployAction
          actionTypeId:
            category: Deploy
            owner: AWS
            provider: CodeDeploy
            version: 1
          configuration:
            ApplicationName: MyMicroservicesApp
            DeploymentGroupName: MyMicroservicesAppDeploymentGroup
```

### Deploying the Application to EKS

Once the CI/CD pipeline is set up, we can deploy the application to the EKS cluster. This involves pushing the Docker images to a container registry (such as Amazon ECR) and then deploying them to the EKS cluster using Kubernetes manifests.

#### Pushing Docker Images to ECR

First, we need to push the Docker images to Amazon ECR. Here’s an example of how to do this:

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Tag and push the Docker images
docker tag microservice-1:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/microservice-1:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/microservice-1:latest

docker tag microservice-2:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/microservice-2:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/microservice-2:latest
```

#### Deploying to EKS

Next, we need to deploy the Docker images to the EKS cluster using Kubernetes manifests. Here’s an example of a `deployment.yaml` file for one of the microservices:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservice-1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: microservice-1
  template:
    metadata:
      labels:
        app: microservice-1
    spec:
      containers:
      - name: microservice-1
        image: <account-id>.dkr.ecr.us-west-2.amazonaws.com/microservice-1:latest
        ports:
        - containerPort: 8080
```

We can apply this manifest to the EKS cluster using `kubectl`:

```bash
kubectl apply -f deployment.yaml
```

### Security Considerations

Deploying applications to a Kubernetes cluster involves several security considerations. Here are some key points to keep in mind:

#### Access Token Expiration

Access tokens used to authenticate with the EKS cluster should have a limited expiration time to reduce the risk of unauthorized access. This can be achieved by configuring the token expiration settings in the authentication provider.

#### Role-Based Access Control (RBAC)

RBAC is a fundamental security feature in Kubernetes that allows you to control access to resources based on roles and permissions. You should define roles and role bindings to restrict access to specific resources and operations.

#### Network Policies

Network policies can be used to control traffic between pods and external networks. By defining network policies, you can ensure that only authorized traffic is allowed to flow between different parts of your application.

#### Image Scanning

Regularly scanning Docker images for vulnerabilities is crucial to maintaining the security of your application. Tools like Trivy or Clair can be integrated into your CI/CD pipeline to scan images for known vulnerabilities.

### How to Prevent / Defend

#### Detection

To detect potential security issues, you can use tools like Kubernetes Audit Logs to monitor API calls and detect unauthorized access attempts. Additionally, you can use security scanners like Trivy or Clair to scan Docker images for known vulnerabilities.

#### Prevention

To prevent unauthorized access and ensure the security of your application, follow these best practices:

1. **Use Short-Lived Access Tokens**: Configure access tokens to expire after a short period to minimize the window of opportunity for unauthorized access.

2. **Implement RBAC**: Define roles and role bindings to restrict access to specific resources and operations. Ensure that users and services have the minimum necessary permissions.

3. **Use Network Policies**: Define network policies to control traffic between pods and external networks. Restrict access to only authorized traffic.

4. **Scan Docker Images**: Regularly scan Docker images for vulnerabilities using tools like Trivy or Clair. Integrate these scans into your CI/CD pipeline to ensure that only secure images are deployed.

#### Secure Coding Fixes

Here’s an example of how to implement secure coding practices:

**Vulnerable Code**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: insecure-pod
spec:
  containers:
  - name: insecure-container
    image: insecure-image:latest
    ports:
    - containerPort: 8080
```

**Secure Code**

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
      runAsUser: 1000
      allowPrivilegeEscalation: false
```

In the secure version, we have added a `securityContext` to the container specification to ensure that the container runs with a non-root user and does not allow privilege escalation.

### Conclusion

In this chapter, we have covered the process of deploying a microservices application to an EKS cluster using EKS Blueprints and secure CI/CD practices. We have discussed the theoretical background, practical implementation, and security considerations involved in this process. By following the best practices outlined in this chapter, you can ensure that your application is deployed securely and efficiently.

### Practice Labs

For hands-on practice with EKS and CI/CD, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes labs for EKS and CI/CD.
- **flaws.cloud**: A cloud security training platform that includes labs for EKS and CI/CD.
- **AWS Official Workshops**: AWS offers various workshops and labs that cover EKS and CI/CD practices.

By completing these labs, you can gain practical experience in deploying and securing microservices applications in an EKS cluster.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/03-Access Token Expiration/00-Overview|Overview]] | [[02-Understanding Temporary Access Tokens in EKS Blueprints|Understanding Temporary Access Tokens in EKS Blueprints]]
