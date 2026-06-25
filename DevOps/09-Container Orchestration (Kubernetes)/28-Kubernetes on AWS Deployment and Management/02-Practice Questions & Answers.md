---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What are the three container services offered by AWS, and how do they differ?**

The three container services offered by AWS are:

1. **Elastic Container Service (ECS)**: ECS is a fully managed container orchestration service that allows you to run Docker containers without having to manage the underlying infrastructure. It integrates well with other AWS services like EC2, VPC, and IAM.

2. **Elastic Kubernetes Service (EKS)**: EKS is a managed Kubernetes service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane. EKS supports the full Kubernetes API, so you can use existing tools and plugins.

3. **Elastic Container Registry (ECR)**: ECR is a fully managed Docker registry that makes it easy to store, manage, and deploy Docker images. ECR is integrated with ECS and EKS, allowing you to securely store and retrieve images used in your containerized applications.

**Q2. How do you deploy a Kubernetes cluster on AWS using the EKS service from the AWS Management Console?**

To deploy a Kubernetes cluster on AWS using the EKS service from the AWS Management Console, follow these steps:

1. Sign in to the AWS Management Console and navigate to the EKS dashboard.
2. Click on "Create cluster."
3. Choose a name for your cluster and select the Kubernetes version you want to use.
4. Configure the VPC settings, including subnets and security groups.
5. Set up the worker nodes by selecting the instance types, AMI, and number of instances.
6. Review the configuration and click "Create."

After creating the cluster, you can connect to it using `kubectl` by downloading the configuration file from the EKS console.

**Q3. Explain how to configure auto-scaling for a Kubernetes cluster on AWS.**

Auto-scaling for a Kubernetes cluster on AWS can be configured using the AWS Auto Scaling Group feature. Here’s how you can set it up:

1. **Create an Auto Scaling Group**: In the AWS Management Console, go to the EC2 Dashboard and create an Auto Scaling Group. Specify the minimum and maximum number of instances, and set scaling policies based on CPU utilization, memory usage, or custom metrics.

2. **Integrate with EKS Worker Nodes**: Ensure that the instances in the Auto Scaling Group are properly configured as worker nodes for your EKS cluster. This typically involves setting up the appropriate IAM roles and node group configurations.

3. **Configure Kubernetes Horizontal Pod Autoscaler (HPA)**: Within Kubernetes, you can use the HPA to scale the number of pods based on observed CPU utilization or other metrics. This can be done using the `kubectl autoscale` command or by defining a `HorizontalPodAutoscaler` resource in your Kubernetes manifest files.

By combining AWS Auto Scaling with Kubernetes HPA, you can achieve efficient scaling of both the infrastructure and the workload.

**Q4. How can you create an EKS cluster using the EKS Control CLI tool?**

Creating an EKS cluster using the EKS Control CLI tool (`eksctl`) is straightforward and can be done with a few commands. Here’s how:

1. **Install eksctl**: First, ensure you have the `eksctl` tool installed. You can download it from the official GitHub repository.

2. **Create a Cluster Configuration File**: Create a YAML file that specifies the details of your cluster, such as the region, VPC settings, and node group configurations.

3. **Run eksctl create cluster**: Use the following command to create the cluster:
   ```bash
   eksctl create cluster --config-file=cluster.yaml
   ```

This command will create the EKS cluster and associated resources according to the specifications in your configuration file.

**Q5. How do you integrate deploying to an EKS cluster from a Jenkins CI/CD pipeline?**

Integrating deployment to an EKS cluster from a Jenkins CI/CD pipeline involves several steps:

1. **Set Up Jenkins**: Ensure Jenkins is set up and has access to the necessary credentials to interact with AWS and EKS.

2. **Configure Jenkins Pipeline**: Define a Jenkinsfile that includes stages for building, testing, and deploying your application. Use the `kubectl` command to apply changes to the EKS cluster.

3. **Use Jenkins Plugins**: Utilize Jenkins plugins like the Kubernetes plugin or the AWS CloudFormation plugin to simplify interactions with AWS and EKS.

4. **Deploy Application**: In the Jenkinsfile, include steps to build Docker images, push them to ECR, and then deploy them to the EKS cluster using `kubectl`.

Here is an example snippet of a Jenkinsfile:
```groovy
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-app .'
            }
        }
        stage('Push to ECR') {
            steps {
                script {
                    def ecrRepo = aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    sh "docker tag my-app:latest ${ecrRepo}/my-app:latest"
                    sh "docker push ${ecrRepo}/my-app:latest"
                }
            }
        }
        stage('Deploy to EKS') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

By following these steps, you can automate the deployment process from Jenkins to an EKS cluster, ensuring a smooth and efficient CI/CD pipeline.

---
<!-- nav -->
[[02-Overview of Kubernetes on AWS|Overview of Kubernetes on AWS]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/28-Kubernetes on AWS Deployment and Management/00-Overview|Overview]]
