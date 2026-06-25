---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Separation of Concerns

### What is Separation of Concerns?

Separation of concerns is a design principle that aims to divide a program into distinct sections, each addressing a separate concern. In the context of CI/CD pipelines, this means separating the application code from the deployment configurations.

### Why Separate Application Code from Deployment Configurations?

Separating application code from deployment configurations provides several benefits:

- **Clarity**: Each component of the system is easier to understand and maintain.
- **Flexibility**: Changes to the deployment configuration do not require changes to the application code.
- **Security**: Limiting access to sensitive deployment configurations reduces the risk of unauthorized access.

### Real-World Example: GitHub Repository Structure

Consider a GitHub repository structure where the application code is stored in one repository and the deployment configurations are stored in another.

#### Application Code Repository

```plaintext
my-application/
├── src/
│   ├── main.py
│   └── ...
└── tests/
    └── test_main.py
```

#### Deployment Configuration Repository

```plaintext
my-deployment-config/
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
└── README.md
```

### How to Prevent / Defend

**Detection**:
- Regularly review the repository structure to ensure that application code and deployment configurations are properly separated.
- Use automated tools to enforce repository structure policies.

**Prevention**:
- Implement strict access controls for the deployment configuration repository.
- Use tools like `git hooks` to prevent accidental commits of deployment configurations to the application code repository.

**Secure-Coding Fixes**:
```yaml
# Example of a deployment.yaml file
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
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
        image: my-image:latest
        ports:
        - containerPort: 8080
```

---
<!-- nav -->
[[08-Secure CICD Pipeline|Secure CICD Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Overview of CI or CD Pipelines to Git repositories/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Overview of CI or CD Pipelines to Git repositories/10-Conclusion|Conclusion]]
