---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code in DevSecOps

### Introduction to Policy as Code

Policy as Code is an approach to managing security policies within a DevSecOps environment. This method allows organizations to define, enforce, and audit security policies using code, making them more manageable, consistent, and auditable. In the context of Kubernetes, this involves creating and enforcing constraints on the resources deployed in the cluster. One such constraint is the rejection of privileged containers, which can pose significant security risks.

### Understanding Privileged Containers

A privileged container is a container that runs with elevated privileges, essentially bypassing many of the security restrictions imposed by the container runtime. This means that a privileged container can access host resources and perform operations that a non-privileged container cannot. While this can be useful for certain administrative tasks, it also introduces significant security risks.

#### Why Reject Privileged Containers?

Rejecting privileged containers is crucial because they can:

1. **Bypass Security Policies**: Privileged containers can access host resources and perform operations that violate the intended security policies.
2. **Increase Attack Surface**: By allowing access to host resources, privileged containers increase the potential attack surface.
3. **Compromise Host Integrity**: A compromised privileged container can potentially compromise the entire host.

### Constraint Templates and Custom Resources

In Kubernetes, constraints can be enforced using custom resources and constraint templates. These templates define the structure and behavior of the constraints, while the custom resources instantiate these constraints with specific configurations.

#### Constraint Template for Privileged Containers

Let's define a constraint template to reject privileged containers. This template will be used to create a custom resource definition (CRD) that enforces the policy.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-privileged-containers
spec:
  validationFailureAction: enforce
  background: false
  rules:
    - name: deny-privileged-containers
      match:
        resources:
          kinds:
            - Pod
      validate:
        message: "Pods with privileged containers are not allowed."
        pattern:
          spec:
            containers:
              - securityContext:
                  privileged: false
```

This constraint template defines a rule that matches all `Pod` resources and validates that none of the containers within the pod have the `securityContext.privileged` field set to `true`.

### Deploying the Constraint

Once the constraint template is defined, it needs to be deployed in the Kubernetes cluster. This involves creating the custom resource definition (CRD) and deploying the constraint.

#### Creating the CRD

The CRD is created automatically when the constraint template is applied to the cluster. Here is an example of how to apply the constraint template:

```sh
kubectl apply -f deny-privileged-containers.yaml
```

This command applies the constraint template to the cluster, creating the necessary CRD.

### Testing the Constraint

To test the constraint, we can modify the configuration of a microservice to include a privileged container and observe the result.

#### Modifying Microservice Configuration

Consider a microservice with the following configuration:

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
        - name: card-service-container
          image: card-service-image
          securityContext:
            privileged: false
            readOnlyRootFilesystem: true
```

Now, let's modify the `securityContext` to set `privileged` to `true`:

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
        - name: card-service-container
          image: card-service-image
          securityContext:
            privileged: true
            readOnlyRootFilesystem: true
```

#### Applying the Modified Configuration

When we attempt to apply the modified configuration, the constraint will reject the deployment due to the presence of a privileged container.

```sh
kubectl apply -f card-service-deployment.yaml
```

The output will indicate that the deployment was rejected due to the violation of the security policy:

```
Error from server (BadRequest): error when creating "card-service-deployment.yaml": admission webhook "validate.kyverno.svc-fail" denied the request: [deny-privileged-containers] Pods with privileged containers are not allowed.
```

### How to Prevent / Defend Against Privileged Containers

#### Detection

To detect the presence of privileged containers, you can use tools like Kyverno, which provides built-in policies to identify and reject such containers. Additionally, you can use Kubernetes auditing to log and monitor access to privileged containers.

#### Prevention

Preventing the use of privileged containers involves:

1. **Enforcing Policies**: Use constraint templates and custom resources to enforce policies that reject privileged containers.
2. **Auditing**: Regularly audit your Kubernetes cluster to ensure compliance with security policies.
3. **Secure Coding Practices**: Ensure that all microservices and deployments are configured securely, avoiding the use of privileged containers.

#### Secure-Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

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
        - name: card-service-container
          image: card-service-image
          securityContext:
            privileged: true
            readOnlyRootFilesystem: true
```

**Secure Configuration:**

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
        - name: card-service-container
          image: card-service-image
          securityContext:
            privileged: false
            readOnlyRootFilesystem: true
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the Kubernetes API server vulnerability (CVE-2021-25741), which allowed attackers to escalate privileges and gain control over the cluster. This vulnerability highlights the importance of enforcing strict security policies, including the rejection of privileged containers.

### Hands-On Labs

For hands-on practice with Policy as Code, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice securing microservices.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster to practice securing and auditing.

These labs provide practical experience in defining and enforcing security policies in a Kubernetes environment.

### Conclusion

Policy as Code is a powerful approach to managing security policies in a DevSecOps environment. By defining and enforcing constraints on privileged containers, organizations can significantly reduce their security risks. Through the use of constraint templates, custom resources, and regular audits, organizations can ensure that their Kubernetes clusters remain secure and compliant with security policies.

---
<!-- nav -->
[[05-Policy as Code Rejecting Privileged Containers|Policy as Code Rejecting Privileged Containers]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[07-Policy as Code in DevSecOps|Policy as Code in DevSecOps]]
