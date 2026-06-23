---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to GitOps and ArgoCD

GitOps is a set of practices that uses Git as a single source of truth for declarative infrastructure and application configurations. This approach enables teams to manage their infrastructure and applications using familiar Git workflows, such as pull requests, branches, and tags. ArgoCD is a popular open-source tool that implements GitOps principles to automate the deployment and management of applications in Kubernetes clusters.

### Key Concepts

- **Declarative Configuration**: Describing the desired state of your system in a declarative manner, typically using YAML files.
- **Single Source of Truth**: Using a Git repository as the central place to store all configuration files.
- **Pull Requests**: Leveraging Git's pull request mechanism to review and approve changes before they are applied.
- **Automated Deployment**: Automating the deployment process to ensure consistency and reduce human error.

### Why GitOps?

GitOps offers several benefits:

- **Version Control**: All changes are tracked in a version-controlled system, making it easy to roll back to previous states.
- **Auditability**: Every change is recorded, providing a clear audit trail.
- **Collaboration**: Teams can collaborate on infrastructure and application changes using familiar Git workflows.
- **Automation**: Automated deployment pipelines ensure that changes are consistently applied across environments.

### Real-World Example: Recent Breaches

One notable breach that highlights the importance of proper GitOps practices is the SolarWinds supply chain attack (CVE-2020-1014). In this case, attackers compromised the build server and injected malicious code into the SolarWinds Orion software. This demonstrates the critical need for secure and auditable processes in managing infrastructure and applications.

### Setting Up a GitOps Pipeline with ArgoCD

To set up a GitOps pipeline using ArgoCD, you need to follow these steps:

1. **Install ArgoCD**: Deploy ArgoCD in your Kubernetes cluster.
2. **Configure Repositories**: Set up Git repositories to store your application and infrastructure configurations.
3. **Define Application Manifests**: Write declarative manifests for your applications.
4. **Sync Applications**: Use ArgoCD to sync your applications from the Git repositories to the Kubernetes cluster.

#### Step-by-Step Guide

1. **Install ArgoCD**

   To install ArgoCD, you can use the following Helm chart:

   ```bash
   helm repo add argo https://argoproj.github.io/argo-helm
   helm repo update
   helm install argocd argo/argo-cd --namespace argocd --create-namespace
   ```

2. **Configure Repositories**

   You need to configure your Git repositories to store your application and infrastructure configurations. For example, you might have a repository named `online-boutique`.

3. **Define Application Manifests**

   Define your application manifests in the Git repository. These manifests describe the desired state of your applications.

   ```yaml
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: online-boutique
   spec:
     project: default
     source:
       repoURL: https://github.com/example/online-boutique.git
       targetRevision: HEAD
       path: kustomize
     destination:
       server: https://kubernetes.default.svc
       namespace: online-boutique
   ```

4. **Sync Applications**

   Use ArgoCD to sync your applications from the Git repositories to the Kubernetes cluster.

   ```bash
   argocd app create online-boutique \
     --repo https://github.com/example/online-boutique.git \
     --path kustomize \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace online-boutique
   ```

### Authentication and Access Control

When setting up a GitOps pipeline, it is crucial to handle authentication and access control securely. This section covers how to authenticate with Git repositories and manage access control.

#### Authentication with Git Repositories

To authenticate with Git repositories, you can use various methods, including SSH keys, HTTPS with username and password, and access tokens.

##### Using HTTPS with Username and Password

If you are not connected to the Git repository using SSH keys, you can use HTTPS with a username and password to authenticate. This method is straightforward but less secure than other methods.

```bash
https://username:password@github.com/example/online-boutique.git
```

##### Using Access Tokens

Access tokens provide a more secure way to authenticate with Git repositories. They can be created in the settings of your Git provider (e.g., GitLab).

```bash
https://access_token@github.com/example/online-boutique.git
```

### Granular Access Control

Granular access control is essential to ensure that each pipeline has access only to the necessary repositories. This principle is known as least privilege access.

#### Creating Access Tokens

In GitLab, you can create access tokens for specific projects or groups. This feature is available in premium subscriptions.

1. **Navigate to Settings**
   - Go to the settings of your GitLab project or group.
2. **Create Access Token**
   - Navigate to the access tokens section and create a new token with the necessary permissions.

```bash
# Example of creating an access token in GitLab
curl --request POST --url https://gitlab.example.com/api/v4/users/access_tokens \
     --header 'PRIVATE-TOKEN: <your_private_token>' \
     --data 'name=OnlineBoutiqueToken' \
     --data 'scopes=read_repository'
```

#### Free Subscription Limitations

If you are using a free GitLab subscription, you may not have access to the feature to create project-specific access tokens. In this case, you can use a global access token, but it is less secure.

### How to Prevent / Defend

#### Detection

To detect unauthorized access or changes, you can use tools like Git hooks, webhooks, and continuous monitoring solutions.

```bash
# Example of a Git hook to monitor changes
#!/bin/bash
git diff --cached --name-only | grep -q 'kustomize/' && echo "Kustomize changes detected"
```

#### Prevention

To prevent unauthorized access and changes, implement the following measures:

- **Use SSH Keys**: Prefer SSH keys over HTTPS with username and password.
- **Limit Access Tokens**: Ensure that access tokens have the minimum necessary permissions.
- **Audit Logs**: Enable audit logs to track all changes made to the Git repositories.

#### Secure Coding Fixes

Compare the insecure and secure versions of accessing a Git repository.

**Insecure Version**

```bash
https://username:password@github.com/example/online-boutique.git
```

**Secure Version**

```bash
https://access_token@github.com/example/online-boutique.git
```

### Complete Example

Here is a complete example of setting up a GitOps pipeline with ArgoCD, including the full HTTP request and response.

#### Full HTTP Request

```http
POST /api/v4/users/access_tokens HTTP/1.1
Host: gitlab.example.com
Authorization: Bearer <your_private_token>
Content-Type: application/json

{
  "name": "OnlineBoutiqueToken",
  "scopes": ["read_repository"]
}
```

#### Full HTTP Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 12345,
  "name": "OnlineBoutiqueToken",
  "revoked": false,
  "created_at": "2023-10-01T12:00:00Z",
  "last_used_at": null,
  "expires_at": null,
  "token": "<generated_access_token>"
}
```

### Expected Result

The expected result is a successfully created access token with the specified permissions.

### Common Pitfalls

- **Hardcoding Credentials**: Avoid hardcoding credentials in your scripts or manifests.
- **Insufficient Permissions**: Ensure that access tokens have the minimum necessary permissions.
- **Lack of Monitoring**: Implement monitoring to detect unauthorized access or changes.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA**: Damn Vulnerable Web Application for learning web application security.
- **WebGoat**: An interactive web application security training tool.

### Conclusion

By following the steps outlined in this chapter, you can set up a secure GitOps pipeline using ArgoCD. Proper authentication and access control are crucial to ensuring the security of your Git repositories and applications. Regular monitoring and auditing are also essential to detect and prevent unauthorized access.

---
<!-- nav -->
[[09-Introduction to GitOps and ArgoCD Part 6|Introduction to GitOps and ArgoCD Part 6]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[11-Introduction to GitOps and ArgoCD Part 8|Introduction to GitOps and ArgoCD Part 8]]
