---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to ArgoCD and Application Release Pipelines

ArgoCD is an open-source declarative continuous delivery tool for Kubernetes. It enables you to manage your applications using GitOps principles, ensuring that your cluster state is defined by your Git repository. This chapter will delve into configuring ArgoCD in Infrastructure as Code (IaC) and deploying applications using ArgoCD. We'll cover the theoretical foundations, practical steps, and security considerations involved in setting up and managing ArgoCD applications.

### What is ArgoCD?

ArgoCD is a declarative, extensible continuous delivery tool for Kubernetes. It allows you to manage your applications using GitOps principles, which means your cluster state is defined by your Git repository. This approach ensures that your applications are deployed consistently and reliably.

#### Why Use ArgoCD?

- **Declarative Deployment**: You define the desired state of your applications in Git, and ArgoCD ensures that the actual state matches the desired state.
- **GitOps Principles**: By using Git as the single source of truth, you can track changes, collaborate with team members, and roll back to previous versions easily.
- **Extensibility**: ArgoCD supports custom resources and integrations, making it highly flexible for different use cases.

### Custom Resource Definitions (CRDs)

Custom Resource Definitions (CRDs) allow you to extend the Kubernetes API with your own custom resources. In the context of ArgoCD, CRDs are used to define the structure of the `Application` resource.

#### What is a CRD?

A CRD is a Kubernetes object that defines a new type of resource. It allows you to create custom resources that can be managed like any other Kubernetes resource.

#### Example CRD for ArgoCD Application

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: applications.argoproj.io
spec:
  group: argoproj.io
  names:
    kind: Application
    listKind: ApplicationList
    plural: applications
    singular: application
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
```

This CRD defines the `Application` resource, which is used to describe the desired state of an application in ArgoCD.

### Creating an ArgoCD Application

An ArgoCD application is a custom resource that describes the desired state of an application in your cluster. It specifies the source of the application (e.g., a Git repository) and the destination (e.g., a Kubernetes cluster).

#### Specifying Source and Destination

The `Application` resource has two main parts: `source` and `destination`.

- **Source**: Specifies the location of the application manifests in a Git repository.
- **Destination**: Specifies the target Kubernetes cluster and namespace where the application will be deployed.

#### Example Application Manifest

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
```

In this example, the `online-boutique` application is defined with the following properties:

- **repoURL**: The URL of the Git repository containing the application manifests.
- **targetRevision**: The branch or commit to use as the source of truth.
- **path**: The directory within the repository where the application manifests are located.
- **server**: The URL of the Kubernetes API server.
- **namespace**: The namespace where the application will be deployed.

### Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. In the context of ArgoCD, IaC means defining your cluster state in Git and using ArgoCD to ensure that the actual state matches the desired state.

#### Benefits of IaC

- **Consistency**: Ensures that your infrastructure is consistent across different environments.
- **Reproducibility**: Allows you to reproduce your infrastructure at any time.
- **Collaboration**: Enables team members to collaborate on infrastructure changes.
- **Auditability**: Provides a history of changes to your infrastructure.

### Configuring ArgoCD in IaC

To configure ArgoCD in IaC, you need to define the `Application` resource in your Git repository and use ArgoCD to sync the desired state with the actual state.

#### Steps to Configure ArgoCD

1. **Define the Application Manifest**: Create a YAML file that defines the `Application` resource.
2. **Commit the Manifest to Git**: Add the manifest to your Git repository and commit the changes.
3. **Sync with ArgoCD**: Use ArgoCD to sync the desired state with the actual state.

#### Example Workflow

1. **Create the Application Manifest**:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
```

2. **Commit the Manifest to Git**:

```bash
git add k8s/online-boutique.yaml
git commit -m "Add online-boutique application"
git push origin main
```

3. **Sync with ArgoCD**:

```bash
argocd app sync online-boutique
```

### Real-World Examples

#### Example 1: Online Boutique Application

Consider an e-commerce platform called "Online Boutique." The application consists of several microservices, each defined in a separate Git repository. Using ArgoCD, you can define an `Application` resource for each microservice and ensure that the desired state is synced with the actual state.

#### Example 2: Multi-Repository Setup

In a more complex setup, you might have multiple repositories for different components of your application. For example, you might have a repository for frontend services and another for backend services. You can define separate `Application` resources for each repository and ensure that they are synced independently.

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Incorrect Source Configuration

If the `source` configuration is incorrect, ArgoCD will not be able to find the application manifests in the specified Git repository. Ensure that the `repoURL`, `targetRevision`, and `path` are correctly configured.

#### Pitfall 2: Incorrect Destination Configuration

If the `destination` configuration is incorrect, ArgoCD will not be able to deploy the application to the correct Kubernetes cluster and namespace. Ensure that the `server` and `namespace` are correctly configured.

#### Pitfall 3: Missing Dependencies

If the application depends on other resources (e.g., secrets, config maps), ensure that these dependencies are also defined in the Git repository and are synced with ArgoCD.

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Regularly audit your Git repository to ensure that the `Application` resources are correctly configured.
- **Automated Testing**: Use automated testing to verify that the desired state matches the actual state.

#### Prevention

- **Code Reviews**: Perform code reviews to ensure that the `Application` resources are correctly configured.
- **Access Controls**: Use access controls to ensure that only authorized users can modify the `Application` resources.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
```

##### Fixed Code

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
```

In the fixed code, the `targetRevision` is set to a specific branch (`main`) instead of `HEAD`. This ensures that the application is deployed from a stable branch.

### Conclusion

In this chapter, we covered the theoretical foundations, practical steps, and security considerations involved in setting up and managing ArgoCD applications. We explored the concepts of Custom Resource Definitions (CRDs), creating an ArgoCD application, and configuring ArgoCD in Infrastructure as Code (IaC). We also provided real-world examples and discussed common pitfalls and how to avoid them. By following these guidelines, you can ensure that your applications are deployed consistently and securely using ArgoCD.

### Practice Labs

For hands-on experience with ArgoCD, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve using ArgoCD.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security techniques, including those involving ArgoCD.
- **Kubernetes Goat**: A hands-on lab for practicing Kubernetes security, including the use of ArgoCD.

These labs provide a practical way to apply the concepts learned in this chapter and gain hands-on experience with ArgoCD.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/01-Introduction to ArgoCD Deployment|Introduction to ArgoCD Deployment]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/03-Introduction to ArgoCD and GitOps|Introduction to ArgoCD and GitOps]]
