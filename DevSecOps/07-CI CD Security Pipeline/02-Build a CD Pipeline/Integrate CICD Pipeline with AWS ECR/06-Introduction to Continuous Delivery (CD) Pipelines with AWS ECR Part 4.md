---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Continuous Delivery (CD) Pipelines with AWS ECR

Continuous Delivery (CD) is a practice where code changes are automatically tested and prepared for release to production. In the context of containerized applications, integrating a CD pipeline with Amazon Elastic Container Registry (ECR) allows developers to automate the building, tagging, and pushing of Docker images to a secure registry. This chapter will delve into the details of setting up such a pipeline, explaining the concepts, steps, and best practices involved.

### Background Theory

#### What is Continuous Delivery?

Continuous Delivery (CD) is a software development practice where teams produce software in short cycles, ensuring that the application can be reliably released at any time. It involves automating the build, test, and deployment processes to ensure that the software can be deployed to production quickly and safely.

#### What is Amazon Elastic Container Registry (ECR)?

Amazon Elastic Container Registry (ECR) is a managed Docker container registry service provided by AWS. It enables users to store, manage, and deploy Docker container images. ECR integrates seamlessly with other AWS services like ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service), making it a popular choice for container-based applications.

### Setting Up the CD Pipeline

To integrate a CD pipeline with AWS ECR, we need to perform several key steps:

1. **Building the Docker Image**
2. **Tagging the Docker Image**
3. **Pushing the Docker Image to ECR**

#### Building the Docker Image

The first step in the CD pipeline is to build the Docker image. This involves creating a `Dockerfile` that specifies the base image, dependencies, and commands to run the application.

```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

This `Dockerfile` starts with a Python 3.9 slim base image, sets the working directory to `/app`, copies the `requirements.txt` file, installs the required packages, and finally copies the rest of the application files.

#### Tagging the Docker Image

After building the Docker image, we need to tag it. Tagging allows us to identify different versions of the image. Typically, we use two tags: a specific version tag and a `latest` tag.

```bash
# Build and tag the Docker image
docker build -t my-app:1.0.0 .
docker tag my-app:1.0.0 my-app:latest
```

In this example, we build the image with the tag `my-app:1.0.0` and then create a `latest` tag pointing to the same image.

#### Pushing the Docker Image to ECR

Once the image is tagged, we need to push it to the ECR repository. This involves logging into the ECR registry and then pushing the image.

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Push the Docker image to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/my-app:1.0.0
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/my-app:latest
```

Here, `<account-id>` is your AWS account ID, and `us-west-2` is the region where your ECR repository is located.

### Optimizing the Build Command

The build command can become quite lengthy, especially when dealing with long repository and registry names. To optimize this, we can use environment variables to store these names.

```bash
# Define environment variables
export IMAGE_NAME=my-app
export IMAGE_TAG=1.0.0
export LATEST_TAG=latest
export ECR_REGISTRY=<account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and tag the Docker image
docker build -t $IMAGE_NAME:$IMAGE_TAG .
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$LATEST_TAG

# Push the Docker image to ECR
docker push $ECR_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
docker push $ECR_REGISTRY/$IMAGE_NAME:$LATEST_TAG
```

By using environment variables, we make the build command more readable and maintainable.

### Diagramming the CD Pipeline

Let's visualize the CD pipeline using a mermaid diagram:

```mermaid
graph TD
    A[Source Code] --> B[Build Docker Image]
    B --> C[Tag Image]
    C --> D[Push to ECR]
    D --> E[Deploy to Production]
```

This diagram shows the flow of the CD pipeline, starting from the source code, through building and tagging the Docker image, pushing it to ECR, and finally deploying it to production.

### Real-World Example: Recent Breaches

One recent example of a breach involving container registries is the compromise of Docker Hub in 2021. Attackers gained access to private repositories and pushed malicious images. This highlights the importance of securing your container registry and implementing proper access controls.

### Common Pitfalls and How to Avoid Them

#### Pitfall: Insecure Docker Images

**What:** Using insecure Docker images can lead to vulnerabilities in your application.

**Why:** Docker images often contain pre-installed software and libraries, which may have known vulnerabilities.

**How to Prevent:**

1. **Use Secure Base Images:** Always start with a secure base image. For example, use Alpine Linux instead of Debian for smaller images.
2. **Scan for Vulnerabilities:** Use tools like Trivy or Clair to scan your Docker images for known vulnerabilities.
3. **Keep Dependencies Updated:** Regularly update your dependencies to the latest versions.

**Secure Code Fix:**

```dockerfile
# Vulnerable Dockerfile
FROM python:3.9-slim
RUN pip install flask==1.0.0

# Secure Dockerfile
FROM python:3.9-slim
RUN pip install flask==2.0.0
```

#### Pitfall: Exposing Sensitive Information

**What:** Exposing sensitive information in Docker images can lead to data breaches.

**Why:** Developers might accidentally include sensitive information like API keys or database credentials in their Docker images.

**How to Prevent:**

1. **Use Environment Variables:** Store sensitive information in environment variables instead of hardcoding them in the Dockerfile.
2. **Use Secrets Management Tools:** Use tools like AWS Secrets Manager or HashiCorp Vault to manage secrets securely.

**Secure Code Fix:**

```dockerfile
# Vulnerable Dockerfile
FROM python:3.9-slim
ENV DATABASE_URL=postgres://user:password@localhost/db

# Secure Dockerfile
FROM python:3.9-slim
ENV DATABASE_URL=
```

### Detection and Prevention

#### Detection

1. **Regular Scans:** Use tools like Trivy or Clair to regularly scan your Docker images for vulnerabilities.
2. **Logging and Monitoring:** Implement logging and monitoring to detect unauthorized access to your ECR repository.

#### Prevention

1. **Access Controls:** Implement strict access controls using IAM policies to limit who can access your ECR repository.
2. **Image Signing:** Use image signing to ensure that only trusted images are deployed.

### Complete Example

Let's walk through a complete example of setting up a CD pipeline with AWS ECR.

#### Step 1: Build the Docker Image

```bash
# Build the Docker image
docker build -t my-app:1.0.0 .
```

#### Step 2: Tag the Docker Image

```bash
# Tag the Docker image
docker tag my-app:1.0.0 my-app:latest
```

#### Step 3: Push the Docker Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Push the Docker image to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/my-app:1.0.0
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/my-app:latest
```

### Conclusion

Integrating a CD pipeline with AWS ECR involves building, tagging, and pushing Docker images to a secure registry. By following best practices and using environment variables, we can optimize the build process and ensure the security of our container images. Regular scanning and access controls are essential to prevent vulnerabilities and unauthorized access.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy:** Focuses on web application security but includes sections on container security.
- **AWS Official Workshops:** Provides detailed walkthroughs on setting up CD pipelines with AWS services, including ECR.
- **CloudGoat:** Offers scenarios for practicing cloud security, including ECR and other AWS services.

These labs will help you gain practical experience in setting up and securing a CD pipeline with AWS ECR.

---
<!-- nav -->
[[05-Introduction to Continuous Delivery (CD) Pipelines with AWS ECR Part 3|Introduction to Continuous Delivery (CD) Pipelines with AWS ECR Part 3]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[07-Introduction to Continuous Delivery (CD) Pipelines with AWS ECR|Introduction to Continuous Delivery (CD) Pipelines with AWS ECR]]
