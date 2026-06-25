---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of automated Kubernetes manifest configuration checks and why they are important.**

Automated Kubernetes manifest configuration checks involve setting up policies and constraints within a Kubernetes cluster to ensure that all manifests adhere to predefined security standards. These checks act as guardrails to prevent the deployment of misconfigured or insecure Kubernetes resources. They are important because they help maintain a consistent and secure environment by preventing human errors or intentional shortcuts that could compromise security. This automation ensures that even inexperienced users or those who might take shortcuts due to laziness are prevented from deploying insecure configurations.

**Q2. How would you configure automated security checks for Kubernetes manifest files?**

To configure automated security checks for Kubernetes manifest files, you can use tools like Open Policy Agent (OPA) Gatekeeper or Kyverno. Here’s a basic example using Kyverno:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: pod-security-policy
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: disallow-root
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Pods should not run as root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsUser: 0
```

This policy enforces that pods should not run as root. By creating such policies, you can automate the enforcement of security best practices across your cluster.

**Q3. What are some common security no-goes that should be defined as policies in a Kubernetes cluster?**

Common security no-goes that should be defined as policies include:

1. **Running Containers as Root**: Preventing containers from running as root to reduce privilege escalation risks.
2. **Insecure Image Pull Policies**: Ensuring images are pulled securely and from trusted sources.
3. **Missing Resource Limits**: Setting resource limits to prevent denial-of-service attacks.
4. **Sensitive Data Exposure**: Ensuring secrets are stored securely and not exposed in manifests.
5. **Outdated Images**: Enforcing the use of up-to-date container images to avoid known vulnerabilities.

These policies help mitigate common security risks associated with Kubernetes deployments.

**Q4. How does automating these checks fit into a CI/CD pipeline?**

Automating Kubernetes manifest checks fits seamlessly into a CI/CD pipeline by integrating the security validation step into the deployment workflow. For example, you can add a step in your CI/CD tool (like Jenkins, GitLab CI, or GitHub Actions) to run the manifest checks before deploying to the cluster. If the checks fail, the deployment process stops, preventing insecure configurations from reaching production. This ensures that only validated and secure configurations are deployed, maintaining the integrity and security of the cluster.

**Q5. Provide a recent real-world example of a Kubernetes security breach and explain how automated manifest checks could have prevented it.**

One notable example is the **CVE-2021-25741**, a vulnerability in the Kubernetes API server that allowed unauthorized access to sensitive information. Automated manifest checks could have helped prevent this by enforcing strict policies around API server configurations and access controls. For instance, policies could be set to ensure that only authorized users have access to sensitive APIs and that default configurations are secure. By continuously validating these settings, organizations can proactively prevent such breaches.

**Q6. Why is it important to apply these policies across all namespaces and resources in a Kubernetes cluster?**

Applying policies across all namespaces and resources ensures uniform security enforcement throughout the cluster. This is crucial because:

1. **Consistency**: Ensures that all parts of the cluster adhere to the same security standards.
2. **Compliance**: Helps meet regulatory requirements by ensuring all resources comply with security policies.
3. **Security**: Reduces the risk of security gaps by covering all areas of the cluster.
4. **Automation**: Simplifies management by automating the enforcement of security policies across the entire cluster.

By applying policies universally, organizations can maintain a high level of security and consistency, reducing the likelihood of security breaches.

---
<!-- nav -->
[[02-Policy as Code in Kubernetes|Policy as Code in Kubernetes]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/08-Summary/00-Overview|Overview]]
