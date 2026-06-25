---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Handling Environment Variables

One of the critical aspects of setting up a CI/CD pipeline is handling environment variables. In our case, we need to pass the microservice name and version as environment variables to the GitOps pipeline.

### Passing Environment Variables

We can pass the environment variables from the CI pipeline to the GitOps pipeline using parameters in ArgoCD. Here's how we can do it:

```yaml
deploy_microservice:
  stage: deploy
  script:
    - echo "Deploying microservice..."
    - argocd app set my-microservice --param=image=my-microservice:$CI_COMMIT_SHORT_SHA
    - argocd app set my-microservice --param=ms_name=$MS_NAME
    - argocd app set my-microservice --param=ms_version=$MS_VERSION
```

### Explanation of Environment Variables

- **MS_NAME**: The name of the microservice.
- **MS_VERSION**: The version of the microservice.

These environment variables are passed to the ArgoCD application, which uses them to configure the deployment.

---
<!-- nav -->
[[05-Creating a CI Pipeline that Triggers a GitOps Pipeline Using ArgoCD|Creating a CI Pipeline that Triggers a GitOps Pipeline Using ArgoCD]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/07-Hands-On Labs|Hands-On Labs]]
