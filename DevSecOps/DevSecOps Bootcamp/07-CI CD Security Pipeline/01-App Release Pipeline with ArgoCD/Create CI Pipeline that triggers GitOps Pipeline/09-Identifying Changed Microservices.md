---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Identifying Changed Microservices

In a monorepo structure, where multiple microservices are stored in a single repository, it's crucial to identify which microservice has been changed. This helps in triggering the appropriate pipeline steps for the affected microservice.

### Identifying Changed Microservices

GitLab CI/CD provides a mechanism to identify which files have been changed in a commit. We can use this information to determine which microservice has been modified.

Here's an example of how to identify changed microservices in a `.gitlab-ci.yml` file:

```yaml
identify_changed_microservice:
  stage: build
  script:
    - changed_files=$(git diff --name-only HEAD^ HEAD)
    - if echo "$changed_files" | grep -q 'microservice1'; then
        echo "Microservice 1 has been changed."
        export MS_NAME=microservice1
      fi
    - if echo "$changed_files" | grep -q 'microservice2'; then
        echo "Microservice 2 has been changed."
        export MS_NAME=microservice2
      fi
```

### Explanation of Identifying Changed Microservices

- **Changed Files**: The `git diff --name-only HEAD^ HEAD` command lists the files that have been changed in the latest commit.
- **Conditional Checks**: The `if` statements check if the changed files belong to a specific microservice and set the `MS_NAME` environment variable accordingly.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/08-How to Prevent  Defend|How to Prevent  Defend]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/10-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]]
