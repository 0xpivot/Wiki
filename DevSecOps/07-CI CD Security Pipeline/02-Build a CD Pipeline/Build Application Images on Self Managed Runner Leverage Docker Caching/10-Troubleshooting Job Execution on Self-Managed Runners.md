---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Troubleshooting Job Execution on Self-Managed Runners

### Understanding Self-Managed Runners

Self-managed runners are custom runners that you manage yourself, as opposed to using hosted runners provided by services like GitHub Actions or GitLab CI. These runners are typically installed on your own infrastructure and are responsible for executing jobs defined in your CI/CD pipeline.

### Common Issues with Self-Managed Runners

One common issue with self-managed runners is that they may crash or become unresponsive when a job is canceled. This can leave the runner in a pending state, where it does not pick up new jobs until it is restarted.

### How to Restart a GitLab Runner

If a job is canceled and the runner becomes unresponsive, you can restart the GitLab runner to resolve the issue. Here’s how you can do it:

```sh
# Check the status of the GitLab runner
sudo systemctl status gitlab-runner

# Restart the GitLab runner
sudo systemctl restart gitlab-runner
```

Alternatively, you can manually run the GitLab runner to force it to check for new jobs:

```sh
# Run the GitLab runner in non-blocking mode
gitlab-runner run -d
```

### Real-World Example: Runner Crash During Job Cancellation

Consider a scenario where a developer cancels a long-running job on a self-managed GitLab runner. After cancellation, the runner enters a pending state and does not pick up new jobs. This causes delays in the CI/CD pipeline, leading to missed deadlines and frustrated team members. By restarting the runner, the team can quickly resolve the issue and resume normal operations.

### How to Prevent / Defend Against Runner Crashes

#### Detection

Set up monitoring and alerting for your self-managed runners. Tools like Prometheus and Grafana can help you monitor the health and performance of your runners.

#### Prevention

Regularly update and maintain your self-managed runners to ensure they are running the latest version. This can help mitigate bugs and issues that may cause crashes.

#### Secure Coding Practices

Ensure that your CI/CD pipeline is designed to handle job cancellations gracefully. Use robust error handling and logging to track and debug issues when they occur.

### Example of a Robust CI/CD Pipeline

Here’s an example of a GitLab CI/CD pipeline configuration that includes error handling and logging:

```yaml
stages:
  - build
  - test
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application..."
    - docker build -t myapp .
  artifacts:
    paths:
      - dist/

test_job:
  stage: test
  script:
    - echo "Running tests..."
    - npm test
  when: on_success

deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - docker push myapp
  when: manual
  only:
    - master
```

This pipeline includes error handling and logging to ensure that issues are tracked and resolved effectively.

---
<!-- nav -->
[[09-Monitoring Disk Space on Self-Managed Runners|Monitoring Disk Space on Self-Managed Runners]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Build Application Images on Self Managed Runner Leverage Docker Caching/00-Overview|Overview]] | [[11-Understanding Dangling Docker Images|Understanding Dangling Docker Images]]
