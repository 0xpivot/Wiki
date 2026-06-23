---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring Cleanup Policies

### Cleanup Policies

Cleanup policies allow you to automatically remove old or unused artifacts from the repository. This helps free up storage space and maintain a clean repository.

#### Creating a Cleanup Policy

To create a cleanup policy, navigate to **Administration > Cleanup Policies**. Click on **Create Cleanup Policy** and fill in the required details:

- **Policy Name**: A descriptive name for the policy.
- **Repository**: The repository to which the policy applies.
- **Retention**: The retention period for artifacts.

Click **Save** to create the policy.

### Example Scenario

Suppose you want to remove artifacts that have not been accessed for more than 30 days. You can create a cleanup policy with a retention period of 30 days.

---
<!-- nav -->
[[01-Introduction to Artifact Repositories and Artifact Repository Managers|Introduction to Artifact Repositories and Artifact Repository Managers]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/37-Nexus Artifact Repository Management Setup And Usage/00-Overview|Overview]] | [[03-Creating Repositories for Different Artifact Types|Creating Repositories for Different Artifact Types]]
