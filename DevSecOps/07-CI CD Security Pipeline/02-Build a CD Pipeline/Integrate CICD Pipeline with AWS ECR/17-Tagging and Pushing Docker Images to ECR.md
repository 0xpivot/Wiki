---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Tagging and Pushing Docker Images to ECR

### Background Theory

Tagging Docker images is a fundamental practice in container management. Tags allow you to identify different versions of an image and manage them effectively. In a CI/CD pipeline, tagging and pushing images to a registry like ECR is a critical step in ensuring that the correct version of the application is deployed.

### Why Tag and Push Images?

Tagging and pushing images to ECR serves several purposes:
1. **Version Control**: Allows you to track different versions of your application.
2. **Deployment Consistency**: Ensures that the same version of the image is deployed consistently across environments.
3. **Rollback Capability**: Enables easy rollback to previous versions if issues arise.

### How to Tag and Push Images

To tag and push Docker images to ECR, you typically follow these steps:
1. **Build the Image**: Build the Docker image with a specific tag.
2. **Tag the Image**: Add additional tags to the image.
3. **Push the Image**: Push the tagged images to the ECR repository.

Here’s an example of how to tag and push images to ECR:

```sh
# Build the Docker image with a specific tag
docker build -t <account-id>.dkr.ecr.us-west-2.amazonaws.com/myapp:$CI_COMMIT_SHORT_SHA .

# Tag the image with the 'latest' tag
docker tag <account-id>.dkr.ecr.us-west-2.amazonaws.com/myapp:$CI_COMMIT_SHORT_SHA <account-id>.dkr.ecr.us-west-2.amazonaws.com/myapp:latest

# Push the images to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/myapp:$CI_COMMIT_SHORT_SHA
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/myapp:latest
```

### Pitfalls and Best Practices

#### Pitfall: Overwriting Tags

Overwriting the `latest` tag can lead to unexpected behavior if the latest version of the image is not the intended one. Always ensure that the `latest` tag points to the most recent and stable version of the image.

#### Best Practice: Use Semantic Versioning

Use semantic versioning (e.g., `v1.0.0`, `v1.1.0`) for your tags to clearly indicate the version of the image. This helps in tracking and managing different versions of the application.

### How to Prevent / Defend

#### Detection

Monitor your ECR repository for unauthorized pushes or overwrites. Use AWS CloudTrail to log and audit API calls related to ECR.

#### Prevention

1. **Semantic Versioning**: Use semantic versioning for your tags.
2. **Access Control**: Implement strict access control policies to limit who can push images to the repository.
3. **Automated Testing**: Automate testing to ensure that the latest version of the image is stable and functional.

### Real-World Example

A company faced issues when the `latest` tag was overwritten by an unstable version of the image, causing downtime in production. This issue was resolved by implementing semantic versioning and strict access control policies.

---
<!-- nav -->
[[18-Setting Up the CD Pipeline|Setting Up the CD Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/20-Conclusion|Conclusion]]
