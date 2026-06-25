---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Policy as Code: Rejecting Privileged Containers

### Introduction to Policy as Code

Policy as Code is a modern approach to managing infrastructure and application policies in a declarative manner. This method allows teams to define, enforce, and audit policies using code, which can be version-controlled, tested, and deployed alongside the rest of the application. In the context of Kubernetes, Policy as Code enables administrators to enforce strict security policies across the cluster, ensuring that no unauthorized configurations are allowed to run.

### Why Avoid Running Privileged Containers?

Running containers with root privileges poses significant security risks. A container running as root has full access to the underlying host system, which can lead to severe consequences if the container is compromised. Here’s why avoiding privileged containers is crucial:

1. **Increased Attack Surface**: A container running as root can potentially escape its isolation and gain control over the host system. This is particularly dangerous because it can lead to a full compromise of the host.
   
2. **Privilege Escalation**: If an attacker gains access to a container running as root, they can leverage this privilege to escalate their access to the host system. This can result in unauthorized actions such as reading sensitive files, modifying system configurations, or even executing arbitrary commands.

3. **Security Best Practices**: Following security best practices means minimizing the privileges of processes running in containers. By running containers with non-root users, you reduce the potential damage an attacker can cause if they manage to breach the container.

### Security Best Practices for Image Security

In the previous chapters, we discussed the importance of image security and image scanning. These practices help ensure that the images used in containers are free from vulnerabilities and malicious content. One of the key checks performed during image scanning is to verify whether the image is configured to run as root. Tools like Clair, Trivy, and Aqua Security provide comprehensive scanning capabilities to identify such issues.

However, even if an image is scanned and found to be secure, the configuration of the Kubernetes pod can override these settings. This is where Policy as Code comes into play to enforce strict security policies.

### Creating Constraint Templates and Constraints

To enforce a policy that disallows running privileged containers, we can use Open Policy Agent (OPA) Gatekeeper, a popular tool for implementing Policy as Code in Kubernetes. Gatekeeper allows us to define custom constraints and templates to enforce specific policies.

#### Step-by-Step Guide to Create a Constraint Template

1. **Define the Constraint Template**:
   A constraint template defines the structure and logic of the policy. Below is an example of a constraint template that checks whether a pod is running with root privileges.

   ```yaml
   apiVersion: templates.gatekeeper.sh/v1
   kind: ConstraintTemplate
   metadata:
     name: k8sprivilegecontainer
   spec:
     crd:
       spec:
         names:
           kind: K8sPrivilegeContainer
     targets:
       - target: admission.k8s.gatekeeper.sh
         rego: |
           package k8sprivilegecontainer

           violation[{"msg": msg, "details": {"kind": input.request.object.kind, "name": input.request.object.metadata.name}}] {
             input.request.operation == "CREATE"
             input.request.object.kind == "Pod"
             input.request.object.spec.securityContext.privileged == true
             msg = sprintf("%s %s is attempting to run with root privileges", [input.request.object.kind, input.request.object.metadata.name])
           }
   ```

2. **Apply the Constraint Template**:
   Apply the constraint template to your Kubernetes cluster using `kubectl`.

   ```sh
   kubectl apply -f constraint-template.yaml
   ```

3. **Create a Constraint**:
   Once the constraint template is applied, you can create a constraint to enforce the policy.

   ```yaml
   apiVersion: constraints.gatekeeper.sh/v1beta1
   kind: K8sPrivilegeContainer
   metadata:
     name: no-privileged-pods
   spec:
     match:
       kinds:
         - apiGroups: ["apps"]
           kinds: ["Deployment"]
   ```

4. **Apply the Constraint**:
   Apply the constraint to your Kubernetes cluster using `kubectl`.

   ```sh
   kubectl apply -f constraint.yaml
   ```

### Example of a Full HTTP Request and Response

When a pod is created with root privileges, Gatekeeper will intercept the request and deny it based on the constraint. Below is an example of a full HTTP request and response:

```http
POST /apis/admissionregistration.k8s.io/v1/mutatingwebhookconfigurations HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Authorization: Bearer <token>

{
  "apiVersion": "admissionregistration.k8s.io/v1",
  "kind": "MutatingWebhookConfiguration",
  "metadata": {
    "name": "gatekeeper-validating-webhook"
  },
  "webhooks": [
    {
      "name": "validation.gatekeeper.sh",
      "rules": [
        {
          "apiGroups": ["*"],
          "apiVersions": ["*"],
          "resources": ["pods"],
          "scope": "Namespaced"
        }
      ],
      "clientConfig": {
        "service": {
          "namespace": "gatekeeper-system",
          "name": "gatekeeper-apiserver"
        },
        "path": "/mutate",
        "caBundle": "<ca-bundle>"
      },
      "sideEffects": "None",
      "admissionReviewVersions": ["v1", "v1beta1"]
    }
  ]
}
```

Response:

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "Pod is attempting to run with root privileges",
  "reason": "Forbidden",
  "details": {
    "kind": "Pod",
    "name": "example-pod"
  },
  "code": 403
}
```

### How to Prevent / Defend

#### Detection

To detect whether a pod is running with root privileges, you can use tools like `kubectl` to inspect the pod configuration. Additionally, you can set up monitoring and alerting systems to notify you if any pods are running with elevated privileges.

```sh
kubectl get pod example-pod -o json | jq '.spec.securityContext.privileged'
```

#### Prevention

1. **Use Non-Root Users**: Ensure that all containers are configured to run as non-root users. This can be done by setting the `securityContext.runAsUser` field in the pod specification.

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: example-pod
   spec:
     containers:
     - name: example-container
       image: example-image
       securityContext:
         runAsUser: 1000
   ```

2. **Enforce Policies Using Gatekeeper**: As demonstrated earlier, use Gatekeeper to enforce policies that disallow running privileged containers.

3. **Image Scanning**: Continue to use image scanning tools to ensure that the images used in containers are secure and do not contain root user configurations.

#### Secure-Coding Fixes

Here is an example of a pod configuration that runs with root privileges and the corresponding secure version:

**Vulnerable Configuration**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    securityContext:
      privileged: true
```

**Secure Configuration**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    securityContext:
      runAsUser: 1000
```

### Real-World Examples and Recent CVEs

Recent breaches have highlighted the importance of securing container configurations. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous applications and systems. If a container running with root privileges was exploited, the attacker could gain full control of the host system, leading to severe data breaches and system compromises.

### Conclusion

By enforcing strict policies using Policy as Code, you can significantly enhance the security of your Kubernetes clusters. Avoiding the use of privileged containers is a critical security best practice that helps mitigate the risk of container escapes and privilege escalations. Tools like Gatekeeper provide powerful mechanisms to enforce these policies and ensure that your infrastructure remains secure.

### Hands-On Labs

For hands-on practice with Policy as Code and Kubernetes security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various security topics, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing and training.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes challenges related to Policy as Code.

These labs provide practical experience in implementing and enforcing security policies in Kubernetes environments.

---
<!-- nav -->
[[04-Policy as Code Rejecting Privileged Containers Part 4|Policy as Code Rejecting Privileged Containers Part 4]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Define Policy to reject Privileged Containers/00-Overview|Overview]] | [[06-Policy as Code in DevSecOps Part 1|Policy as Code in DevSecOps Part 1]]
