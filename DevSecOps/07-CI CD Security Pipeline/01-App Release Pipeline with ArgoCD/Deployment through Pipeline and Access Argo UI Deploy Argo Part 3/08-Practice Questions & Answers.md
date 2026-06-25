---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of creating a new branch in Git and pushing it to a remote repository.**

To create a new branch in Git and push it to a remote repository, follow these steps:

1. **Create a new branch**: Use `git checkout -b <branch-name>` to create and switch to a new branch.
2. **Add changes**: Stage your changes with `git add .`.
3. **Commit changes**: Commit the staged changes with `git commit -m "Your commit message"`.
4. **Push the branch**: Push the newly created branch to the remote repository using `git push origin <branch-name>`.

This process ensures that your local changes are moved to a new branch and then pushed to the remote repository, triggering any associated CI/CD pipelines.

**Q2. How does the Argo CD GitOps workflow integrate with a CI/CD pipeline?**

The Argo CD GitOps workflow integrates with a CI/CD pipeline by:

1. **Branching and Merging**: When a new feature branch is pushed to the remote repository, the CI/CD pipeline is triggered.
2. **Provisioning Infrastructure**: The pipeline provisions the necessary infrastructure, such as an EKS cluster, from scratch.
3. **Deploying Applications**: Once the infrastructure is ready, the pipeline deploys the applications specified in the manifests.
4. **Syncing with Git Repository**: Argo CD watches the Git repository for changes and automatically syncs the cluster state with the desired state defined in the manifests.
5. **Automated End-to-End CI/CD**: In a full DevSecOps pipeline, the CI pipeline tests and scans the code, and upon successful completion, it triggers the CD pipeline to update the manifests and deploy the changes.

This integration ensures that the application state in the cluster is always aligned with the Git repository, providing a consistent and reliable deployment process.

**Q3. How would you authenticate with Kubernetes as an admin user and access the Argo CD UI?**

To authenticate with Kubernetes as an admin user and access the Argo CD UI, follow these steps:

1. **Set AWS Access Credentials**: Set the AWS access credentials for the Kubernetes admin user using `export AWS_ACCESS_KEY_ID=<access-key-id>` and `export AWS_SECRET_ACCESS_KEY=<secret-access-key>`.
2. **Assume External Admin Role**: Execute `aws sts assume-role --role-arn <role-arn> --role-session-name <session-name>` to assume the external admin role.
3. **Authenticate with Kubernetes**: Authenticate with Kubernetes using `aws eks update-kubeconfig --name <cluster-name>`.
4. **Access Argo CD UI**: Retrieve the password for the Argo CD UI from the secret using `kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 --decode` and perform a port-forward to access the UI: `kubectl port-forward svc/argocd-server -n argocd 8080:80`.

By following these steps, you can securely access the Argo CD UI and manage your applications.

**Q4. What are the key components of the Argo CD UI and how do they help in managing applications?**

The key components of the Argo CD UI include:

1. **Repositories**: Displays the Git repositories that are connected to Argo CD. You can view the repository URLs, types, and credentials.
2. **Applications**: Shows the applications deployed in the cluster. Each application entry provides details such as the source repository, branch, folder, and sync status.
3. **Sync Status**: Indicates whether the application has been synced from the Git repository and its current health status.
4. **Action Buttons**: Provides options to manually refresh the state or sync with the repository, although auto-sync is typically configured.

These components help in managing applications by providing a clear overview of the deployed applications, their sync status, and allowing manual intervention if needed.

**Q5. How would you troubleshoot an issue where no pods are being deployed in the online boutique namespace?**

To troubleshoot an issue where no pods are being deployed in the online boutique namespace, follow these steps:

1. **Check Application Sync Status**: Verify the sync status of the application in the Argo CD UI to ensure it is in a healthy state.
2. **Inspect Manifest Files**: Ensure that the manifest files in the GitOps repository are correctly formatted and contain the necessary deployment specifications.
3. **Review Logs**: Check the logs of the Argo CD server pod using `kubectl logs <pod-name> -n argocd` to identify any errors or warnings.
4. **Validate Secrets**: Confirm that the necessary secrets, such as the Git repository credentials, are correctly configured.
5. **Check Namespace Resources**: Use `kubectl get all -n online-boutique` to verify that no resources are present in the namespace, indicating that no deployments have been triggered.

By systematically checking these areas, you can identify and resolve the issue preventing the deployment of pods in the online boutique namespace.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/07-Setting Up the Kubernetes Admin User|Setting Up the Kubernetes Admin User]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/00-Overview|Overview]]
