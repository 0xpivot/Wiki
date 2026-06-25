---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to GitLab Runners

In the realm of Continuous Integration and Continuous Deployment (CI/CD), GitLab Runners play a pivotal role. They are the workers that execute the tasks defined in your CI/CD pipelines. Understanding how to configure and manage these runners is essential for setting up an efficient and secure CI/CD environment.

### What is a GitLab Runner?

A GitLab Runner is a software component that listens for CI/CD job requests from the GitLab server and executes them. These runners can be configured to run on various operating systems and can be set up to handle different types of jobs, such as building, testing, and deploying applications.

### Why Use GitLab Runners?

Using GitLab Runners allows you to distribute the workload across multiple machines, which can significantly speed up your CI/CD processes. Additionally, runners can be customized to meet specific requirements, such as using certain tools or environments for particular tasks.

### How Does a GitLab Runner Work?

When a pipeline is triggered in GitLab, the server sends job requests to the runners. Each runner then executes the specified tasks and reports the results back to the GitLab server. This process is managed through a registration token and a unique runner identifier.

### Prerequisites

Before configuring a GitLab Runner, ensure you have:

1. **Access to a GitLab instance**: You need to have a GitLab account and access to the repository where you want to set up the pipeline.
2. **SSH access to the runner machine**: You should have SSH access to the machine where you plan to install the GitLab Runner.
3. **Ubuntu OS**: The machine should be running Ubuntu, as mentioned in the transcript.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/02-Introduction to GitLab Runner|Introduction to GitLab Runner]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Self Managed GitLab Runner for Pipeline Jobs/04-Introduction to Self-Managed GitLab Runners|Introduction to Self-Managed GitLab Runners]]
