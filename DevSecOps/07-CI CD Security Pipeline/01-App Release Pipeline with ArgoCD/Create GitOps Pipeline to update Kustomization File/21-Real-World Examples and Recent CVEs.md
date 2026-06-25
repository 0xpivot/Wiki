---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Real-World Examples and Recent CVEs

### Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in the Kubernetes API server that allows an attacker to bypass authentication and authorization mechanisms. This vulnerability highlights the importance of securing the CI/CD pipeline and ensuring that only trusted images are deployed to the cluster.

#### How to Prevent / Defend

- **Image Scanning**: Use tools like Trivy or Clair to scan Docker images for vulnerabilities before deploying them.
- **Immutable Infrastructure**: Ensure that images are immutable and signed to prevent tampering.
- **RBAC Policies**: Implement Role-Based Access Control (RBAC) policies to restrict access to the Kubernetes API server.

```yaml
# Example RBAC policy
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Example: CVE-2021-39142

CVE-2021-39142 is a vulnerability in the Kubernetes Dashboard that allows an attacker to gain unauthorized access to the dashboard. This vulnerability underscores the importance of securing the dashboard and limiting access to it.

#### How to Prevent / Defend

- **Secure Dashboard Access**: Limit access to the Kubernetes Dashboard using network policies and RBAC.
- **Use HTTPS**: Ensure that the Kubernetes Dashboard is accessed over HTTPS to prevent man-in-the-middle attacks.
- **Regular Updates**: Keep the Kubernetes Dashboard and other components up to date with the latest security patches.

```yaml
# Example Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  ingress: []
```

---
<!-- nav -->
[[22-Hands-On Labs|Hands-On Labs]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[24-Setting Up Git Configuration for Commit Messages|Setting Up Git Configuration for Commit Messages]]
