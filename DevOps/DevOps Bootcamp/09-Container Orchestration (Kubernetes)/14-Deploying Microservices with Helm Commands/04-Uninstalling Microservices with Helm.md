---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Uninstalling Microservices with Helm

Before diving into the deployment process using Helm, it's crucial to understand how to properly uninstall microservices from your Kubernetes cluster. This ensures that your environment is clean and ready for new deployments.

### Uninstall Script

The uninstallation process typically involves running a script that contains a series of `helm uninstall` commands. These commands remove the specified Helm releases from the cluster, effectively cleaning up the environment.

#### Example Uninstall Script

```bash
#!/bin/bash

# Uninstall Redis
helm uninstall redis --namespace default

# Uninstall Cart
helm uninstall cart --namespace default

# Add more services as needed
```

This script iterates through each service and removes it from the cluster. The `--namespace` flag specifies the namespace in which the Helm release was installed. By default, it is set to `default`.

#### What Happens During Uninstallation

When you run `helm uninstall`, Helm performs several actions:

1. **Deletes the Release**: Helm removes the metadata associated with the release from the Tiller database.
2. **Terminates Pods**: The Kubernetes cluster terminates the pods associated with the release.
3. **Cleans Up Resources**: Any resources created by the Helm chart (such as ConfigMaps, Secrets, etc.) are also cleaned up.

### Why Uninstall?

Uninstalling services is essential for maintaining a clean and manageable cluster. Without proper uninstallation, old resources can clutter the cluster, leading to potential conflicts and resource leaks.

### Pitfalls of Improper Uninstallation

If you do not properly uninstall services, you may encounter issues such as:

- **Resource Leaks**: Old resources continue to consume cluster resources.
- **Conflicts**: New deployments may conflict with leftover resources from previous installations.
- **Security Risks**: Old, potentially vulnerable services may remain active, posing security risks.

### How to Prevent / Defend

To ensure proper uninstallation:

1. **Use Scripts**: Automate the uninstallation process using scripts to avoid manual errors.
2. **Verify Deletion**: After uninstallation, verify that all resources have been removed using `kubectl get all`.
3. **Regular Cleanup**: Regularly review and clean up the cluster to maintain optimal performance and security.

---
<!-- nav -->
[[03-Deploying Microservices with Helm Commands|Deploying Microservices with Helm Commands]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/14-Deploying Microservices with Helm Commands/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/14-Deploying Microservices with Helm Commands/05-Practice Questions & Answers|Practice Questions & Answers]]
