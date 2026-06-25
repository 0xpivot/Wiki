---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS ECR and Its Benefits Over Docker Hub

In this section, we will delve into the process of replacing Docker Hub with AWS Elastic Container Registry (ECR) for managing Docker images. This transition is particularly beneficial when you are already deploying applications to an Amazon EKS (Elastic Kubernetes Service) cluster. By using ECR, you can streamline your deployment pipeline and take advantage of several features that Docker Hub does not offer.

### What is AWS ECR?

AWS Elastic Container Registry (ECR) is a fully managed Docker container registry service provided by Amazon Web Services (AWS). It allows you to store, manage, and deploy Docker container images. ECR integrates seamlessly with other AWS services, such as Amazon ECS (Elastic Container Service) and Amazon EKS, making it an ideal choice for containerized applications running on AWS infrastructure.

### Why Replace Docker Hub with AWS ECR?

Docker Hub is a popular public registry for Docker images, but it comes with limitations, especially when it comes to private repositories. Here are some key reasons to consider switching to AWS ECR:

1. **Unlimited Private Repositories**: Unlike Docker Hub, which limits you to one private repository, ECR allows you to create an unlimited number of private repositories. This is particularly useful when you have multiple applications or microservices that require their own isolated repositories.

2. **Integration with AWS Services**: ECR integrates seamlessly with other AWS services, such as EKS and ECS. This integration simplifies the deployment and management of containerized applications on AWS.

3. **Security and Compliance**: ECR provides enhanced security features, including encryption at rest and in transit, IAM (Identity and Access Management) policies for access control, and support for signing and verifying images using AWS Signer.

4. **Performance and Scalability**: ECR is designed to handle high throughput and large-scale deployments. It automatically scales to meet the demands of your applications, ensuring optimal performance.

### Background Theory: Container Registries and Their Role

A container registry is a storage location for Docker images. These images contain all the necessary components to run a containerized application. A container registry acts as a central repository where developers can store, manage, and distribute these images.

#### Key Concepts in Container Registries

1. **Repositories**: A repository is a collection of related Docker images. Each repository can have multiple tags, allowing you to store different versions of the same image.

2. **Tags**: Tags are used to identify specific versions of an image within a repository. Commonly used tags include `latest`, `v1.0`, etc.

3. **Images**: An image is a read-only template that contains the instructions needed to run a container. Images are built from a Dockerfile and stored in a registry.

4. **Layers**: Docker images are composed of layers, which are essentially filesystem changes. Layers allow for efficient storage and distribution of images, as only the changed layers need to be transferred.

### Transitioning from Docker Hub to AWS ECR

To transition from Docker Hub to AWS ECR, you need to follow a series of steps. These steps include creating an ECR repository, configuring credentials in Jenkins, building and tagging the image, logging in to ECR, and pushing the image to the repository.

#### Step 1: Create an ECR Repository

The first step is to create an ECR repository where your Docker images will be hosted. You can create a repository using the AWS Management Console, AWS CLI, or AWS SDKs.

##### Using the AWS Management Console

1. Log in to the AWS Management Console.
2. Navigate to the ECR service.
3. Click on "Repositories" and then "Create repository".
4. Enter a name for your repository and click "Create".

##### Using the AWS CLI

You can also create an ECR repository using the AWS CLI. Here is an example command:

```sh
aws ecr create-repository --repository-name my-app-repo
```

This command creates a new repository named `my-app-repo`.

#### Step 2: Configure Credentials in Jenkins

Once you have created the ECR repository, you need to configure credentials in Jenkins to authenticate with ECR. This involves creating an IAM user or role with the necessary permissions to access the ECR repository.

##### Creating an IAM User

1. Log in to the AWS Management Console.
2. Navigate to the IAM service.
3. Click on "Users" and then "Add user".
4. Enter a username and select "Programmatic access".
5. Attach the `AmazonEC2ContainerRegistryPowerUser` policy to the user.
6. Complete the user creation process.

##### Configuring Jenkins Credentials

After creating the IAM user, you need to configure the credentials in Jenkins.

1. In Jenkins, navigate to "Manage Jenkins" > "Manage Credentials".
2. Click on "Global credentials (unsecured)".
3. Click on "Add Credentials".
4. Select "Username with password" as the credential type.
5. Enter the access key ID and secret access key of the IAM user.
6. Provide a description and click "OK".

#### Step 3: Build and Tag the Image

Next, you need to build and tag the Docker image with the ECR repository name. This involves modifying your Docker build process to use the ECR repository URL.

##### Example Dockerfile

Here is an example Dockerfile:

```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

##### Building and Tagging the Image

To build and tag the image, you can use the following commands:

```sh
docker build -t my-app .
docker tag my-app:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-app-repo:latest
```

Replace `<aws_account_id>` with your AWS account ID and `<region>` with the region where your ECR repository is located.

#### Step 4: Docker Login to ECR

Before pushing the image to ECR, you need to log in to the ECR registry using the credentials configured in Jenkins.

##### Logging In to ECR

You can log in to ECR using the `aws ecr get-login-password` command followed by `docker login`:

```sh
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```

Replace `<region>` with the region where your ECR repository is located and `<aws_account_id>` with your AWS account ID.

#### Step 5: Push the Image to ECR

Finally, you can push the image to the ECR repository using the `docker push` command:

```sh
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-app-repo:latest
```

Replace `<aws_account_id>` with your AWS account ID and `<region>` with the region where your E[... continued]

---
<!-- nav -->
[[01-Introduction to AWS ECR and EKS Integration|Introduction to AWS ECR and EKS Integration]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/18-Replacing Docker Hub with AWS ECR/00-Overview|Overview]] | [[03-Introduction to AWS ECR and Its Integration with Kubernetes|Introduction to AWS ECR and Its Integration with Kubernetes]]
