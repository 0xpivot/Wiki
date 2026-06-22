---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Mermaid Diagrams

### CD Pipeline Architecture

```mermaid
graph TD
    A[Source Control] --> B(Build)
    B --> C(Test)
    C --> D(Security Check)
    D --> E(Push to ECR)
    E --> F(Deploy to EC2)
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant SourceControl
    participant Build
    participant Test
    participant SecurityCheck
    participant ECR
    participant EC2

    SourceControl->>Build: Trigger Build
    Build->>Test: Run Tests
    Test->>SecurityCheck: Run Security Check
    SecurityCheck->>ECR: Push to ECR
    ECR->>EC2: Deploy to EC2
```

---
<!-- nav -->
[[12-Integration of CICD Pipeline with AWS ECR|Integration of CICD Pipeline with AWS ECR]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[14-Pitfalls and Common Mistakes|Pitfalls and Common Mistakes]]
