---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is a fundamental concept in modern DevSecOps practices. It involves defining, managing, and enforcing policies using code rather than manual processes. This approach ensures consistency, automation, and traceability in policy enforcement across development and operations environments. In the context of Kubernetes, policy as code enables the automatic enforcement of best practices and security measures, reducing the likelihood of human error and ensuring compliance with organizational standards.

### Resource Limits in Kubernetes

One of the key best practices in Kubernetes is setting resource limits on every container within a pod. Resource limits help manage the allocation of CPU and memory resources, preventing a single container from monopolizing the available resources and causing performance degradation or failures in other containers.

#### Why Set Resource Limits?

- **Performance Optimization**: By setting resource limits, you ensure that each container gets a fair share of the available resources, optimizing overall system performance.
- **Resource Isolation**: Resource limits prevent one container from consuming all available resources, thus isolating the impact of one container on others.
- **Predictable Behavior**: With resource limits, you can predict how much CPU and memory a container will consume, making it easier to plan and scale your applications.

#### How to Define Resource Limits

Resource limits are defined in the Kubernetes manifest files (YAML or JSON) for deployments. Here’s an example of how to set resource limits:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image:latest
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: "256Mi"
```

In this example, the `my-container` is configured with a maximum limit of 1 CPU core and 512 MiB of memory. Additionally, it requests at least 0.5 CPU cores and 256 MiB of memory.

#### Automating Policy Enforcement

To automate the enforcement of resource limits, you can use tools like Open Policy Agent (OPA) or Kyverno. These tools allow you to define policies that check Kubernetes manifests for compliance with predefined rules.

Here’s an example of a Kyverno policy that enforces resource limits:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: enforce-resource-limits
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: require-resource-limits
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Pod must have resource limits defined."
      pattern:
        spec:
          containers:
          - resources:
              limits:
                cpu: ?string
                memory: ?string
```

This policy checks every pod created in the cluster and ensures that each container within the pod has resource limits defined. If a pod is submitted without resource limits, the policy will reject the deployment.

### Node Port Services in Production

Another important best practice is avoiding the use of NodePort services in a production environment. NodePort services expose a service on a static port on every node in the cluster, which can pose significant security risks.

#### Why Avoid NodePort Services in Production?

- **Security Risks**: Exposing services via NodePort means that any node in the cluster can be accessed directly from the internet, increasing the attack surface.
- **Network Complexity**: Managing multiple services exposed via NodePort can become complex, especially in large clusters.
- **Scalability Issues**: As the number of services grows, the number of open ports on each node increases, leading to potential conflicts and management overhead.

#### How to Define and Enforce NodePort Service Policies

To enforce the prohibition of NodePort services in a production environment, you can define a policy that checks for and rejects any service of type `NodePort`.

Here’s an example of a Kyverno policy that enforces this rule:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: prohibit-nodeport-services
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: disallow-nodeport
    match:
      resources:
        kinds:
        - Service
    validate:
      message: "Service type NodePort is not allowed in production."
      pattern:
        spec:
          type: "ClusterIP"
```

This policy ensures that any service created in the cluster must be of type `ClusterIP`, which is more suitable for internal communication within the cluster.

### Setting Required Labels and Annotations

Labels and annotations are metadata attached to Kubernetes resources. They can be used to categorize resources, provide additional information, and enforce organizational policies.

#### Why Use Labels and Annotations?

- **Organization and Management**: Labels help organize resources into logical groups, making it easier to manage and query them.
- **Automation and Integration**: Annotations can be used to store additional metadata that can be consumed by automation tools or integrations.

#### How to Define and Enforce Label and Annotation Policies

You can define policies that require certain labels or annotations to be present on resources. Here’s an example of a Kyverno policy that enforces the presence of a `team` label on all pods:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-team-label
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: enforce-team-label
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Pod must have a 'team' label."
      pattern:
        metadata:
          labels:
            team: ?string
```

This policy ensures that every pod created in the cluster must have a `team` label defined.

### Custom Company-Specific Policies

Organizations often have specific requirements and configurations that need to be enforced. These custom policies can cover a wide range of scenarios, such as restricting certain types of resources, enforcing naming conventions, or ensuring compliance with internal security guidelines.

#### How to Define Custom Policies

Custom policies can be defined using the same tools and techniques as the examples above. Here’s an example of a Kyverno policy that enforces a custom requirement:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: custom-policy-example
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: enforce-custom-requirement
    match:
      resources:
        kinds:
        - Deployment
    validate:
      message: "Deployment must have a 'custom-requirement' annotation."
      pattern:
        metadata:
          annotations:
            custom-requirement: ?string
```

This policy ensures that every deployment created in the cluster must have a `custom-requirement` annotation defined.

### How to Prevent / Defend

#### Detection

To detect violations of policy as code, you can use monitoring and logging tools integrated with your policy enforcement solution. For example, Kyverno provides detailed logs and audit trails that can be monitored to identify policy violations.

#### Prevention

Prevention involves configuring your policy enforcement solution to automatically reject non-compliant resources. This can be achieved by setting the `validationFailureAction` to `enforce` in your policies, as shown in the examples above.

#### Secure Coding Fixes

Here’s an example of a vulnerable deployment manifest and its secure counterpart:

**Vulnerable Deployment Manifest:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-vulnerable-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image:latest
```

**Secure Deployment Manifest:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-secure-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image:latest
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: 256Mi
```

#### Configuration Hardening

Configuration hardening involves ensuring that your policy enforcement solution is properly configured and maintained. This includes regular updates, testing, and validation of policies to ensure they remain effective against new threats and vulnerabilities.

### Real-World Examples and Breaches

Recent breaches and vulnerabilities have highlighted the importance of policy as code in maintaining security and compliance. For example, the SolarWinds supply chain attack (CVE-2020-1014) demonstrated the risks of unsecured and unmonitored systems. Implementing strict policies around resource limits, service types, and metadata can help mitigate such risks.

### Hands-On Labs

For hands-on practice with policy as code in Kubernetes, consider the following labs:

- **Kubernetes Goat**: A hands-on lab that focuses on Kubernetes security and policy enforcement.
- **Kyverno Documentation**: The official Kyverno documentation provides numerous examples and tutorials for implementing policy as code in Kubernetes.

By following these guidelines and practicing with real-world examples, you can effectively implement and enforce policies as code in your DevSecOps environment, ensuring robust security and compliance.

---
<!-- nav -->
[[03-Policy as Code in DevSecOps Part 1|Policy as Code in DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Defining Policies/00-Overview|Overview]] | [[05-Policy as Code in DevSecOps|Policy as Code in DevSecOps]]
