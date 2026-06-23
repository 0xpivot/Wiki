---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Specifying and Fixating Image Versions

### Background Theory

In the context of containerized applications, especially those deployed using Kubernetes, specifying and fixing the version of the Docker images used is a critical best practice. This ensures consistency across deployments and helps avoid unexpected behavior due to changes in the underlying image.

### Why Versioning Matters

Versioning your Docker images provides several benefits:

1. **Consistency**: Ensures that all instances of a microservice are running the exact same version of the codebase.
2. **Reproducibility**: Facilitates debugging and rolling back to previous versions if issues arise.
3. **Security**: Allows you to track and apply security patches consistently across all instances.

### How to Implement Versioning

To implement versioning, you should specify the exact version of the Docker image in your Kubernetes deployment configuration. This can be done in the `spec.template.spec.containers` section of your deployment YAML file.

#### Example Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-microservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-microservice
  template:
    metadata:
      labels:
        app: my-microservice
    spec:
      containers:
      - name: my-microservice-container
        image: myregistry/my-microservice:0.2.3
        ports:
        - containerPort: 8080
```

### Common Pitfalls

1. **Using Latest Tags**: Avoid using `latest` tags as they can lead to inconsistent deployments.
2. **Manual Updates**: Ensure that all updates to the image version are coordinated and tested thoroughly.

### Real-World Example

Consider a scenario where a company deploys a microservice without specifying the exact image version. A new version of the image is pushed to the registry, and the deployment automatically pulls the latest version. This leads to unexpected behavior and downtime. By specifying the exact version, such issues can be avoided.

### How to Prevent / Defend

1. **Automated Testing**: Implement automated testing for new image versions before deploying them.
2. **Rollback Mechanism**: Ensure that you have a rollback mechanism in place to revert to a known good version if issues arise.

---
<!-- nav -->
[[08-Single Point of Failure in Kubernetes Clusters|Single Point of Failure in Kubernetes Clusters]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/10-Practice Questions & Answers|Practice Questions & Answers]]
