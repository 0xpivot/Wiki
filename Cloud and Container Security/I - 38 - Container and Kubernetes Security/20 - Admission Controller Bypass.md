---
tags: [kubernetes, admission-controllers, bypass, vapt, k8s]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.20 Admission Controller Bypass"
---

# Admission Controller Bypass

## Introduction
In the Kubernetes API request lifecycle, an HTTP request must pass through Authentication (AuthN), Authorization (AuthZ - usually RBAC), and finally **Admission Control** before an object is persisted into `etcd`. 

Admission controllers act as the last line of defense. They can intercept, mutate, or validate requests. From a security perspective, organizations heavily rely on Validating Admission Webhooks (like OPA Gatekeeper, Kyverno, or Datree) to enforce security baselines (e.g., "Do not allow `privileged: true` pods", "Do not allow images from untrusted registries").

Bypassing these controllers allows an attacker to deploy malicious workloads that violate organizational security policies, paving the way for cluster takeover.

## Core Concepts & Architecture

### The API Request Lifecycle

```text
+----------------+      +---------+      +---------+      +-----------------------+      +--------+
|  User/Attacker | ---> |  AuthN  | ---> |  AuthZ  | ---> | Admission Controllers | ---> |  etcd  |
|  (kubectl)     |      | (Valid?)|      | (RBAC)  |      |  Mutating / Validating|      | (Saved)|
+----------------+      +---------+      +---------+      +-----------+-----------+      +--------+
                                                                      |
                                                          +-----------v-----------+
                                                          | Webhook Servers       |
                                                          | - OPA Gatekeeper      |
                                                          | - Kyverno             |
                                                          | - Custom Webhooks     |
                                                          +-----------------------+
```

1. **MutatingAdmissionWebhook**: Modifies the object before it is saved (e.g., automatically injecting a sidecar container).
2. **ValidatingAdmissionWebhook**: Inspects the object and accepts or rejects it based on policies. Runs *after* all mutating webhooks.

## Vectors for Bypassing Admission Controllers

### 1. Exploiting Namespace Exemptions (Fail-Open / Exclusions)
Admission controllers often exclude critical namespaces like `kube-system` to prevent a misconfigured webhook from locking out cluster administrators or preventing essential services from booting.
- **The Flaw**: If an attacker discovers that they can deploy pods into an exempted namespace, the webhook rules will not apply.
- **Enumeration**: 
  ```bash
  # Check ValidatingWebhookConfiguration for excluded namespaces
  kubectl get validatingwebhookconfigurations -o yaml | grep -A 5 namespaceSelector
  ```
- **Exploitation**: If `kube-system` or an `exempt-namespace` is found and the attacker has RBAC to create pods there, they simply deploy their privileged pod to that namespace.

### 2. Failure Policy Abuses (Fail-Open)
Webhooks have a `failurePolicy` that dictates what happens if the external webhook server is down or unreachable.
- `Ignore`: (Fail-Open) The request is allowed.
- `Fail`: (Fail-Closed) The request is rejected.
- **Exploitation**: If the policy is `Ignore`, an attacker can attempt a Denial of Service (DoS) against the webhook deployment (e.g., flooding it with requests, or taking down its pod if they have sufficient permissions). Once the webhook is unresponsive, the API server will allow the malicious pod through.

### 3. Unsupported or Uninspected Fields
Many legacy OPA Gatekeeper policies were written strictly targeting the `containers` array in a Pod specification.
- **InitContainers Bypass**: If the policy only checks `spec.containers`, an attacker can launch a privileged container via `spec.initContainers`.
  ```yaml
  spec:
    initContainers:
    - name: bypass-container
      image: ubuntu
      securityContext:
        privileged: true # Webhook might only check standard 'containers' array
  ```
- **EphemeralContainers Bypass**: Ephemeral containers are used for debugging. If the webhook does not hook the `/ephemeralcontainers` subresource, an attacker can attach a privileged ephemeral container to an existing, non-privileged pod.

### 4. Controller Workload Evasion (Pod vs Deployment)
Some custom admission webhooks only hook the creation of `Pods`.
- **Bypass**: If an attacker creates a `Deployment`, `DaemonSet`, or `CronJob`, the admission controller might not inspect those high-level objects. The *Controller Manager* then creates the `Pod` on behalf of the deployment. Because the Controller Manager's Service Account (e.g., `system:serviceaccount:kube-system:replicaset-controller`) might be exempted from the webhook to prevent loops, the malicious pod goes through.
- **Reverse Bypass**: Conversely, if the webhook only checks `Deployments` but fails to check raw `Pods`, an attacker can just create a raw Pod directly.

### 5. Race Conditions / TOCTOU (Time-of-Check to Time-of-Use)
If there is a flaw in how Mutating and Validating webhooks interact, it is sometimes possible to pass a payload that gets mutated *after* it has been validated, though Kubernetes architecture executes Mutating *before* Validating to explicitly prevent this. 
However, TOCTOU vulnerabilities can exist if the Validating webhook queries external state (like fetching an image manifest) that an attacker modifies immediately after validation but before the Kubelet pulls the image.

### 6. Subresource API Bypasses
Certain API subresources allow modifications without triggering the main resource's admission hooks.
For instance, the `/status` or `/binding` subresources. If an attacker has permissions to `create` bindings directly, they might bind an existing pod to a different node, bypassing scheduling restrictions.

## Defense & Mitigation

1. **Strict Namespace Selectors**: Minimize namespace exclusions. If `kube-system` must be excluded, strictly lock down RBAC so no standard users can create resources there.
2. **Comprehensive Policy Definition**: Ensure policies apply to `Pod` and all higher-level workload controllers (`Deployment`, `DaemonSet`, `Job`, etc.).
3. **Check All Container Types**: Policies must iterate over `spec.containers`, `spec.initContainers`, and `spec.ephemeralContainers`.
4. **Fail-Closed Configuration**: Use `failurePolicy: Fail` for critical security webhooks, ensuring high availability of the webhook service (multiple replicas, PDBs) to prevent blocking legitimate traffic.
5. **Migrate to Pod Security Admission (PSA)**: Custom webhooks for basic pod security are prone to developer oversight. Use native PSA for baseline security restrictions.


## Deep Dive: Reverse Engineering Validating Webhooks
To bypass a custom admission controller, an attacker must understand its logic. Often, the webhook's source code is not accessible, requiring a black-box approach.

### Fuzzing the Webhook
Attackers can fuzz the Kubernetes API to determine the exact constraints of the webhook.
```bash
#!/bin/bash
# Fuzzing allowed image registries
REGISTRIES=("docker.io" "quay.io" "gcr.io" "ghcr.io" "attacker.com" "127.0.0.1" "localhost")

for REG in "${REGISTRIES[@]}"; do
  cat <<YAML_EOF | kubectl apply -f - 2>&1 | grep "denied the request"
apiVersion: v1
kind: Pod
metadata:
  name: fuzz-pod
spec:
  containers:
  - name: fuzzer
    image: ${REG}/alpine
YAML_EOF
  if [ $? -ne 0 ]; then
    echo "[!] Allowed: $REG"
  fi
done
```

### Dry-Run Bypass Verification
Kubernetes provides the `--dry-run=server` flag, which executes the AuthN, AuthZ, and Admission Control steps without actually persisting the object to `etcd`. This is an incredibly powerful tool for attackers to test bypasses silently without triggering runtime security alerts (since the pod is never created).

```bash
# Testing a bypass payload silently
kubectl create -f malicious-pod.yaml --dry-run=server
```

### Kyverno Specific Bypasses
Kyverno is a popular policy engine. A common misconfiguration in Kyverno policies is matching only on specific verbs like `CREATE` but failing to match on `UPDATE`.
- **Bypass**: Deploy a benign pod that passes the Kyverno policy upon `CREATE`.
- **Exploitation**: Issue an `UPDATE` API call to modify the pod spec (e.g., changing the image to a malicious one or adding a volume mount). If Kyverno doesn't hook the `UPDATE` operation, the malicious modification succeeds.

### OPA Gatekeeper Evasion Techniques
OPA Gatekeeper uses Rego policies. Rego is complex, and poorly written policies often fail to handle array iterations correctly.
For example, a policy might check if `hostNetwork: true` is set, but what if the field is completely omitted? 
Another common evasion is using JSON patch formats or applying changes via server-side apply (`kubectl apply --server-side`), which can sometimes confuse webhook parsers that expect traditional client-side patches.

```yaml
# A deeply nested array might evade simple Rego checks
spec:
  ephemeralContainers:
  - name: debug
    image: busybox
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"] # If the policy only checks spec.containers
```

### Manipulating Webhook Timeout
Webhooks have a `timeoutSeconds` field. If the webhook server takes longer than this to respond, the API server follows the `failurePolicy`. 
If an attacker can slow down the webhook server (e.g., by sending hundreds of complex pod specs that require heavy Rego evaluation, causing high CPU load on the Gatekeeper pods), they can trigger a timeout and force a fail-open state.

## Chaining Opportunities
- **[[19 - Lateral Movement in K8s]]**: Once an admission controller is bypassed, an attacker can deploy a privileged pod, escaping to the host and initiating node-to-cluster lateral movement.
- **[[21 - Supply Chain — Malicious Container Images]]**: Webhooks designed to block untrusted image registries can be bypassed to pull malicious images from attacker-controlled Docker Hub accounts.
- **[[17 - Kubernetes RBAC Auditing]]**: Identifying which namespaces the attacker has write access to is critical for exploiting namespace exemptions in webhooks.

## Related Notes
- [[22 - Defense — Pod Security Admission, Network Policies, RBAC Hardening]]
- [[08 - Container Breakouts]]
