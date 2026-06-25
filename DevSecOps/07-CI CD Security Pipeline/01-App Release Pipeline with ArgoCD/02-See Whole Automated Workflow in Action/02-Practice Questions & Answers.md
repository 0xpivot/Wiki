---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how the automated workflow described in the lecture operates from a commit to the online boutique repository to the final deployment in the cluster.**

The automated workflow starts with a commit to the online boutique repository. This commit triggers a new pipeline that performs several tasks:

1. **CI Steps**: Tests the application changes and runs security scans.
2. **Build New Image**: Builds a new Docker image with a new image tag.
3. **Push to Repository**: Pushes the new image to the container registry.
4. **GitOps Trigger**: Triggers a pipeline execution in the GitOps repository, which updates the customization YAML file.
5. **ArgoCD Sync**: Since ArgoCD is listening for changes in the `dev` folder, it automatically pulls the updated YAML file and applies the changes in the Kubernetes cluster.
6. **Pod Update**: The old pod is destroyed, and a new pod with the updated version is created.

This process ensures that the entire workflow is automated, from code changes to deployment, without manual intervention.

**Q2. How would you revert a change to a microservice to an older version using the described workflow?**

To revert a change to a microservice to an older version, follow these steps:

1. **Update Version**: Modify the version number in the online boutique pipeline or directly in the code to the desired older version.
2. **Commit Changes**: Commit the changes to the online boutique repository.
3. **Trigger Pipeline**: The commit triggers the pipeline, which updates the image tag and pushes it to the repository.
4. **GitOps Execution**: The GitOps repository pipeline is triggered, updating the customization YAML file with the new version.
5. **Sync with Cluster**: ArgoCD detects the new changes and syncs the cluster with the updated YAML file, rolling out the older version of the microservice.

For example, if you want to revert the `ad-service` from version `0.8.1` to `0.8.0`, you would update the version in the customization YAML file to `0.8.0`, commit the changes, and let the automated pipeline handle the rest.

**Q3. Why is separating application code and deployment code into different repositories beneficial?**

Separating application code and deployment code into different repositories offers several benefits:

1. **Clarity and Organization**: It clearly delineates responsibilities and makes the codebase more understandable.
2. **Version Control**: Different teams can manage and version control their respective parts independently.
3. **Security**: Limits exposure of sensitive deployment configurations to only those who need access.
4. **Flexibility**: Allows for independent updates and rollouts of application code and deployment configurations.
5. **Best Practices**: Aligns with best practices in DevSecOps, promoting a clear separation of concerns.

For instance, the application code repository focuses on the business logic and features, while the GitOps repository handles the deployment details such as Kubernetes manifests. This separation ensures that changes in one area do not inadvertently affect the other.

**Q4. How does the use of GitOps in this workflow enhance security and reliability?**

Using GitOps enhances security and reliability in several ways:

1. **Immutable Infrastructure**: Ensures that the state of the cluster is always derived from the source of truth in the Git repository, preventing unauthorized changes.
2. **Audit Trails**: Every change to the cluster is recorded in the Git history, providing a clear audit trail.
3. **Automated Rollbacks**: In case of issues, automated rollbacks can be performed by reverting the Git repository to a previous state.
4. **Consistency**: Ensures that the environment is consistently deployed across different stages (development, testing, production).
5. **Access Control**: Restricts who can make changes to the deployment configurations, reducing the risk of accidental or malicious modifications.

For example, if a recent vulnerability (e.g., CVE-2023-XXXX) affects a specific version of a microservice, the team can quickly update the version in the GitOps repository and roll out the fix across the cluster, ensuring that all instances are patched.

**Q5. What are the key components involved in the automated workflow described in the lecture?**

The key components involved in the automated workflow include:

1. **Source Code Repository**: Where the application code resides (e.g., online boutique repository).
2. **Continuous Integration (CI) Pipeline**: Automates the testing and security scanning of code changes.
3. **Container Registry**: Stores the built Docker images with unique tags.
4. **GitOps Repository**: Contains the deployment configurations (Kubernetes manifests, YAML files).
5. **ArgoCD**: A declarative, continuous delivery tool for Kubernetes that syncs the cluster state with the GitOps repository.
6. **Pipeline Triggers**: Mechanisms that automatically start the pipeline upon code changes.
7. **Cluster**: The Kubernetes cluster where the applications are deployed.

These components work together to ensure that any changes in the source code repository are automatically tested, built, and deployed to the cluster, maintaining consistency and reliability throughout the development lifecycle.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/11-See Whole Automated Workflow in Action/01-Introduction to App Release Pipeline with ArgoCD|Introduction to App Release Pipeline with ArgoCD]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/11-See Whole Automated Workflow in Action/00-Overview|Overview]]
