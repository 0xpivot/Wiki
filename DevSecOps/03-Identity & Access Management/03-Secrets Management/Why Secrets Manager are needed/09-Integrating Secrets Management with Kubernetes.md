---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Integrating Secrets Management with Kubernetes

In a Kubernetes environment, secrets can be managed using Kubernetes Secrets. These secrets can be integrated with external secrets managers like AWS Secrets Manager and HashiCorp Vault.

### Creating Kubernetes Secrets

To create a Kubernetes Secret, you can use the following command:

```bash
kubectl create secret generic mysecret --from-literal=username=myuser --from-literal=password=mypassword
```

This command creates a new secret named `mysecret` with a username and password.

### Using External Secrets Managers

To integrate Kubernetes with external secrets managers, you can use tools like `kubeseal` for HashiCorp Vault and `aws-secrets-manager-kubernetes-sidecar` for AWS Secrets Manager.

#### Example with HashiCorp Vault

```bash
helm install vault hashicorp/vault --set 'server.dev.enabled=true'
kubectl apply -f https://raw.githubusercontent.com/hashicorp/vault-helm/main/examples/kubernetes-sidecar.yaml
```

This deploys a Vault server and a Kubernetes sidecar that integrates with Vault.

#### Example with AWS Secrets Manager

```bash
kubectl apply -f https://raw.githubusercontent.com/aws-samples/aws-secrets-manager-kubernetes-sidecar/main/deployment.yaml
```

This deploys a sidecar that integrates with AWS Secrets Manager.

### How to Prevent / Defend

#### Detection

Regularly monitor access logs and audit trails to detect unauthorized access attempts.

#### Prevention

- **Use RBAC**: Restrict access to secrets based on least privilege principles.
- **Enable Encryption**: Ensure secrets are encrypted both at rest and in transit.
- **Automate Rotation**: Regularly rotate secrets to minimize exposure.

#### Secure Coding Fixes

**Vulnerable Code Example:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mycontainer
    image: myimage
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: mysecret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: mysecret
          key: password
```

**Secure Code Example:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mycontainer
    image: myimage
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: mysecret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: mysecret
          key: password
  volumes:
  - name: mysecret-volume
    secret:
      secretName: mysecret
```

### Real-World Example

Consider a scenario where a Kubernetes pod uses secrets stored in AWS Secrets Manager. An attacker gains access to the pod and attempts to retrieve the secrets. With proper RBAC and encryption, the attacker would be unable to access the secrets.

---
<!-- nav -->
[[08-HashiCorp Vault|HashiCorp Vault]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/10-Conclusion|Conclusion]]
