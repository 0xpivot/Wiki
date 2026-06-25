---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Configuring Authorization Policies in Istio

Authorization policies in Istio allow you to control access to services based on various criteria. This section will cover how to configure authorization policies to restrict access to specific services.

### Background Theory

Authorization policies in Istio are defined using YAML files and are applied to namespaces or specific services. These policies can enforce rules based on user identity, IP addresses, and other attributes. The following is a basic structure of an authorization policy:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: <policy-name>
  namespace: <namespace>
spec:
  selector:
    matchLabels:
      app: <app-label>
  action: ALLOW|DENY
  rules:
  - from:
    - source:
        principals: ["<principal>"]
        ipBlocks: ["<ip-block>"]
    to:
    - operation:
        methods: ["<method>"]
        paths: ["<path>"]
```

### Example Scenario

In this scenario, we want to ensure that the microservices or pods within the `online-boutique` namespace should not be able to communicate with the front-end service on a specific port. The request should come from an external client, not from within the same namespace.

### Step-by-Step Configuration

#### Step 1: Define the Policy

We will define an authorization policy that denies access to the front-end service from within the `online-boutique` namespace. We will create this policy in our GitOps repository under the `platform/Istio` folder.

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
  namespace: online-boutique
spec:
  selector:
    matchLabels:
      app: frontend
  action: DENY
  rules:
  - from:
    - source:
        notPrincipals: ["cluster.local/ns/online-boutique/*"]
```

#### Step 2: Apply the Policy

To apply the policy, we need to deploy the YAML file to the cluster. This can be done using `kubectl`:

```sh
kubectl apply -f path/to/frontend-policy.yaml
```

### Detailed Explanation

- **Namespace**: The policy is applied to the `online-boutique` namespace.
- **Selector**: The policy targets the `frontend` service within the namespace.
- **Action**: The policy denies access.
- **Rules**: The rule specifies that the source should not be from the `online-boutique` namespace.

### Pitfalls and Common Mistakes

- **Incorrect Namespace**: Ensure that the policy is applied to the correct namespace.
- **Label Mismatch**: Make sure the labels in the selector match the labels of the target service.
- **Principal Specification**: Incorrectly specifying principals can lead to unintended access.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can monitor the logs and metrics provided by Istio. You can set up alerts for denied access attempts.

#### Prevention

- **Secure Configuration**: Ensure that the authorization policies are correctly configured and applied.
- **Regular Audits**: Regularly review and audit the authorization policies to ensure they are still effective.

#### Secure Code Fix

Here is an example of a vulnerable configuration and the corrected secure version:

**Vulnerable Configuration:**

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
  namespace: online-boutique
spec:
  selector:
    matchLabels:
      app: frontend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["*"]
```

**Corrected Secure Configuration:**

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
  namespace: online-boutique
spec:
  selector:
    matchLabels:
      app: frontend
  action: DENY
  rules:
  - from:
    - source:
        notPrincipals: ["cluster.local/ns/online-boutique/*"]
```

### Complete Example

#### Full HTTP Request and Response

When applying the policy, the following HTTP request and response might occur:

**HTTP Request:**

```http
POST /frontend/path HTTP/1.1
Host: frontend.online-boutique.svc.cluster.local
Content-Type: application/json
Authorization: Bearer <token>

{
  "data": "some data"
}
```

**HTTP Response:**

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "Access denied"
}
```

### Hands-On Labs

For hands-on practice with configuring authorization policies in Istio, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on service mesh and Istio.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be secured using Istio policies.
- **Kubernetes Goat**: Focuses on Kubernetes security and includes scenarios for configuring Istio policies.

By following these steps and practicing with real-world examples, you can effectively configure authorization policies in Istio to secure your microservices.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/12-Introduction to Service Mesh with Istio|Introduction to Service Mesh with Istio]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/14-Practice Questions & Answers|Practice Questions & Answers]]
