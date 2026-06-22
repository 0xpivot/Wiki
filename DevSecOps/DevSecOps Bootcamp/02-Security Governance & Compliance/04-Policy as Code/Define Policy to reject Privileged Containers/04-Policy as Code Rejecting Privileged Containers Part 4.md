---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Rejecting Privileged Containers

### Introduction to Policy as Code

Policy as Code is an approach to managing infrastructure and application policies using code. This method allows teams to define, enforce, and audit policies consistently across environments. In the context of container orchestration systems like Kubernetes, policies can control various aspects such as resource allocation, security settings, and access controls. One critical aspect of security in containerized environments is the management of privileged containers.

### What Are Privileged Containers?

A privileged container is one that runs with elevated permissions, similar to the root user on a host system. This means the container has access to all devices and capabilities available on the host. While this can be useful for certain tasks, it poses significant security risks. A malicious actor could exploit a privileged container to gain full control over the host system.

#### Why Are Privileged Containers Dangerous?

Privileged containers are dangerous because they bypass many of the security mechanisms designed to isolate containers from the host system. Here are some key reasons:

1. **Elevation of Privileges**: A process running in a privileged container can perform actions that would typically require root privileges on the host.
2. **Access to Host Resources**: Privileged containers can access all host resources, including sensitive files and hardware devices.
3. **Escape Vulnerabilities**: If a container escapes its isolation, it can potentially take over the entire host system.

### Real-World Examples of Privileged Container Risks

Several high-profile incidents highlight the dangers of privileged containers:

- **CVE-2019-5736 (Container Breakout)**: This vulnerability allowed attackers to escape from a container and gain root access to the host system. The exploit was possible due to a flaw in the `containerd` runtime, which is commonly used in Kubernetes.
- **Docker Security Incident (2014)**: An attacker exploited a vulnerability in Docker to gain root access to thousands of servers running Docker containers. This incident underscored the importance of securing container environments.

### Setting Up Policies to Reject Privileged Containers

To mitigate the risks associated with privileged containers, organizations can implement policies that explicitly disallow them. In Kubernetes, this can be achieved using admission controllers like Gatekeeper, which enforces custom policies defined in the Open Policy Agent (OPA) framework.

#### Step-by-Step Guide to Implementing the Policy

1. **Install Gatekeeper**: Gatekeeper is an open-source project that provides a framework for enforcing policies in Kubernetes clusters. You can install it using the following Helm chart:

    ```bash
    helm repo add open-policy-agent https://open-policy-agent.github.io/gatekeeper/charts
    helm repo update
    helm install gatekeeper open-policy-agent/gatekeeper --namespace gatekeeper-system --create-namespace
    ```

2. **Define the Policy**: Create a policy that rejects privileged containers. The policy can be defined using the OPA language. Here’s an example policy:

    ```yaml
    apiVersion: config.gatekeeper.sh/v1alpha1
    kind: ConstraintTemplate
    metadata:
      name: k8sprivilegeescalation
    spec:
      crd:
        spec:
          names:
            kind: K8SPrivilegeEscalation
      targets:
        - target: admission.k8s.gatekeeper.sh
          rego: |
            package k8sprivilegeescalation
            
            violation[{"msg": msg}] {
              input.request.object.spec.securityContext.privileged == true
              msg := sprintf("Privileged containers are not allowed")
            }
    ---
    apiVersion: constraints.gatekeeper.sh/v1beta1
    kind: K8SPrivilegeEscalation
    metadata:
      name: deny-privileged-containers
    spec:
      match:
        kinds:
          - group: apps
            kind: Deployment
          - group: ""
            kind: Pod
    ```

3. **Apply the Policy**: Apply the policy to your cluster using `kubectl`:

    ```bash
    kubectl apply -f path/to/policy.yaml
    ```

### Testing the Policy

To test the policy, create a deployment that attempts to run a privileged container:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: card-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: card-service
  template:
    metadata:
      labels:
        app: card-service
    spec:
      containers:
      - name: card-service
        image: myregistry/card-service:latest
        securityContext:
          privileged: true
```

Push this deployment to your cluster:

```bash
kubectl apply -f path/to/deployment.yaml
```

If the policy is correctly enforced, the deployment will fail with an error indicating that privileged containers are not allowed.

### Handling Rejections and Fixing the Issue

When a deployment is rejected due to the policy, you need to modify the deployment to remove the privileged setting:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: card-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: card-service
  template:
    metadata:
      labels:
        app: card-service
    spec:
      containers:
      - name: card-service
        image: myregistry/card-service:latest
        securityContext:
          privileged: false
```

Push the modified deployment:

```bash
kubectl apply -f path/to/fixed-deployment.yaml
```

The deployment should now succeed, and the pod should enter a healthy state.

### How to Prevent / Defend Against Privileged Containers

#### Detection

To detect privileged containers, you can use tools like `kube-bench`, which checks your Kubernetes cluster against CIS benchmarks. Additionally, you can monitor your cluster for any pods that are running with elevated privileges using the following command:

```bash
kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.securityContext != null and .spec.securityContext.privileged == true)'
```

#### Prevention

1. **Enforce Policies**: As demonstrated earlier, enforce policies that disallow privileged containers.
2. **Audit Regularly**: Regularly audit your cluster to ensure that no unauthorized privileged containers are running.
3. **Use Least Privilege Principle**: Always run containers with the least amount of privileges necessary for their operation.

#### Secure Coding Fixes

Here’s a comparison of the insecure and secure versions of the deployment:

**Insecure Version:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: card-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: card-service
  template:
    metadata:
      labels:
        app: card-service
    spec:
      containers:
      - name: card-service
        image: myregistry/card-service:latest
        securityContext:
          privileged: true
```

**Secure Version:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: card-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: card-service
  template:
    metadata:
      labels:
        app: card-service
    spec:
      containers:
      - name: card-service
        image: myregistry/card-service:latest
        securityContext:
          privileged: false
```

### Conclusion

Implementing policies to reject privileged containers is a crucial step in securing your containerized environment. By leveraging tools like Gatekeeper and enforcing strict policies, you can significantly reduce the risk of security breaches. Regular audits and adherence to the principle of least privilege further enhance the security posture of your Kubernetes cluster.

### Hands-On Practice

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security, including policy enforcement.
- **CloudGoat**: Provides a series of challenges and exercises to learn about securing Kubernetes clusters.
- **Kubernetes Goat**: Another interactive platform for learning Kubernetes security practices.

These labs provide practical experience in implementing and testing policies to reject privileged containers, ensuring you have a comprehensive understanding of the topic.

---
<!-- nav -->
[[03-Policy as Code Rejecting Privileged Containers Part 3|Policy as Code Rejecting Privileged Containers Part 3]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[05-Policy as Code Rejecting Privileged Containers|Policy as Code Rejecting Privileged Containers]]
