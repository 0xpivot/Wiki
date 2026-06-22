---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating Repositories for Different Artifact Types

### Repository Types

Nexus supports various types of repositories, including:

- **Maven Repositories**: For storing Maven artifacts.
- **NPM Repositories**: For storing Node.js packages.
- **Docker Repositories**: For storing Docker images.
- **Raw Repositories**: For storing generic artifacts.

### Creating a Maven Repository

To create a Maven repository, navigate to **Repositories > Create Repository**. Select **Maven Hosted** and fill in the required details:

- **Repository ID**: A unique identifier for the repository.
- **Repository Name**: A descriptive name for the repository.
- **Storage Location**: The location where artifacts will be stored.

Click **Create** to create the repository.

### Example Scenario

Suppose you have a project that uses Maven as the build tool. You can create a Maven repository to store the artifacts produced by the build process.

---
<!-- nav -->
[[02-Configuring Cleanup Policies|Configuring Cleanup Policies]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[04-Difference Between Components and Assets|Difference Between Components and Assets]]
