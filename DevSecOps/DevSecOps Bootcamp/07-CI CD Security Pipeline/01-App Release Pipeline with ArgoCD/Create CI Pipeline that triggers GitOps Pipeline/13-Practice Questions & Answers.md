---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of a CI pipeline that triggers a GitOps pipeline.**

The purpose of a CI (Continuous Integration) pipeline that triggers a GitOps pipeline is to automate the deployment process. In this setup, the CI pipeline performs tasks such as building and testing the code, while the GitOps pipeline handles the deployment by updating the infrastructure state through version-controlled manifests. By linking these pipelines, you ensure that any changes in the codebase are automatically tested and deployed in a controlled manner, maintaining consistency and reducing manual intervention.

**Q2. How would you configure a CI pipeline to trigger a GitOps pipeline using GitLab CI?**

To configure a CI pipeline to trigger a GitOps pipeline using GitLab CI, you would follow these steps:

1. Define a job in your `.gitlab-ci.yml` file that will trigger the GitOps pipeline.
2. Use the `trigger` keyword to specify the project and branch of the GitOps pipeline.
3. Set the `strategy` to `depend` to ensure that the CI job waits for the GitOps pipeline to complete before finishing.
4. Pass necessary environment variables to the GitOps pipeline.

Here’s an example configuration:

```yaml
stages:
  - build
  - test
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application"

test_job:
  stage: test
  script:
    - echo "Running tests"

deploy_job:
  stage: deploy
  trigger:
    project: 'your-group/online-boutique-gitops'
    branch: 'main'
    strategy: depend
  variables:
    MS_NAME: 'ad-service'
    MS_VERSION: '0.8.1'
```

In this example, the `deploy_job` triggers the GitOps pipeline in the `online-boutique-gitops` project and waits for it to complete. The `MS_NAME` and `MS_VERSION` environment variables are passed to the GitOps pipeline.

**Q3. Why is it important to use the `strategy: depend` when triggering another pipeline?**

Using the `strategy: depend` when triggering another pipeline ensures that the triggering job waits for the triggered pipeline to complete before it finishes. This is important because it allows the triggering job to handle the success or failure of the triggered pipeline. If the triggered pipeline fails, the triggering job will also fail, ensuring that the entire deployment process is atomic and consistent. Without this strategy, the triggering job might finish prematurely, leading to incomplete or inconsistent deployments.

**Q4. How does the CI pipeline determine which microservice was changed in a monorepo structure?**

In a monorepo structure, the CI pipeline determines which microservice was changed by analyzing the code changes and identifying which microservice folder the changes were made into. If the microservices are well-structured and cleanly isolated, changes should typically be made to a single microservice at a time. The pipeline can evaluate the changes and identify the affected microservice by checking which subdirectory or module was modified. For example, if the `ad-service` directory was updated, the pipeline would recognize that changes were made to the `ad-service` microservice.

**Q5. Explain how environment variables are used to pass information between the CI and GitOps pipelines.**

Environment variables are used to pass information between the CI and GitOps pipelines by setting them in the CI pipeline and making them available to the GitOps pipeline. When a job in the CI pipeline uses the `trigger` keyword to start another pipeline, it can pass environment variables to that pipeline. These variables can contain critical information such as the name and version of the microservice being deployed.

For instance, in the CI pipeline, you might set `MS_NAME` and `MS_VERSION` environment variables. When the GitOps pipeline is triggered, it can access these variables to know which microservice to update and with which version. This ensures that the deployment process is dynamic and can adapt to the specific changes in the codebase.

**Q6. What recent real-world examples demonstrate the importance of automated CI/CD pipelines with GitOps?**

One recent real-world example is the Kubernetes cluster compromise incident involving the SolarWinds supply chain attack. In this case, attackers exploited vulnerabilities in the SolarWinds software to gain unauthorized access to numerous organizations' networks. Automated CI/CD pipelines with GitOps principles could have helped mitigate the impact of such attacks by ensuring that any changes to the infrastructure were tracked and reviewed through version control systems. This would allow organizations to quickly detect and respond to unauthorized changes, reducing the risk of breaches and improving overall security posture.

Another example is the widespread adoption of GitOps practices by companies like Shopify and Weaveworks, which have reported significant improvements in their deployment processes. By automating their CI/CD pipelines and using GitOps to manage infrastructure as code, these companies have achieved faster and more reliable deployments while reducing the risk of human error.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/12-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/00-Overview|Overview]]
