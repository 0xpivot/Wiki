---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why policy as code is necessary in a DevSecOps environment.**

Policy as code is necessary in a DevSecOps environment because it allows organizations to enforce consistent security and compliance standards across all Kubernetes manifest files. This approach automates the validation process, ensuring that only correctly configured and secure manifests are deployed. Without policy as code, manual reviews by Kubernetes administrators would be required for each manifest, which is not scalable or efficient, especially when dealing with multiple product teams and large numbers of manifest files.

**Q2. How does policy as code integrate with the CI/CD pipeline?**

Policy as code integrates with the CI/CD pipeline by adding automated checks that validate Kubernetes manifest files against predefined policies before deployment. These checks are typically implemented as part of the deployment workflow, ensuring that any manifest pushed to the GitOps repository is validated for compliance and security. If a manifest violates any policy, the deployment is halted, preventing misconfigured or insecure applications from being deployed to the cluster.

**Q3. What are some benefits of using policy as code in a Kubernetes environment?**

The benefits of using policy as code in a Kubernetes environment include:

1. **Scalability**: Automated checks can handle a large number of manifest files without requiring manual intervention.
2. **Consistency**: Policies ensure that all applications adhere to the same security and compliance standards.
3. **Efficiency**: Automating the validation process reduces the workload on Kubernetes administrators and speeds up the deployment process.
4. **Security**: By enforcing security best practices, policy as code helps prevent common misconfigurations that could lead to vulnerabilities.

**Q4. How can Kubernetes administrators create and enforce custom policies using policy as code?**

Kubernetes administrators can create and enforce custom policies using policy as code by defining policies in a declarative format (e.g., YAML or JSON). These policies specify what configurations are allowed or disallowed within the Kubernetes manifests. Tools like Open Policy Agent (OPA) can be used to define these policies and enforce them during the CI/CD pipeline. For example, a policy might prohibit the use of privileged containers or require specific resource limits.

```yaml
# Example policy to prevent privileged containers
apiVersion: opa.example.com/v1
kind: Policy
metadata:
  name: no-privileged-containers
spec:
  match:
    - apiGroups: ["*"]
      resources: ["pods"]
      verbs: ["create", "update"]
  rule: |
    package kubernetes.policies

    deny[msg] {
      input.spec.containers[_].securityContext.privileged == true
      msg := "Privileged containers are not allowed"
    }
```

**Q5. Discuss a recent real-world example where policy as code could have prevented a security breach.**

In the case of the SolarWinds supply chain attack (CVE-2020-10161), attackers compromised the SolarWinds software update mechanism to distribute a backdoor called SUNBURST. If SolarWinds had implemented policy as code, they could have enforced strict policies around software updates and dependencies. For instance, policies could have been defined to ensure that only trusted sources were allowed to push updates, and any deviations from expected behavior would trigger alerts or block the deployment. This could have helped detect and prevent the malicious updates from being distributed.

**Q6. How can policy as code help in preventing misconfigurations in Kubernetes clusters?**

Policy as code helps in preventing misconfigurations in Kubernetes clusters by providing a framework to define and enforce security policies. Misconfigurations such as overly permissive permissions, missing resource limits, or unsecured access to sensitive data can be detected and blocked before deployment. For example, policies can be set to ensure that all pods have resource requests and limits defined, that secrets are encrypted, and that network policies restrict unnecessary traffic. This proactive approach ensures that only securely configured applications are deployed, reducing the risk of vulnerabilities due to misconfigurations.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/07-Why Policy as Code/02-Policy as Code in DevSecOps|Policy as Code in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/07-Why Policy as Code/00-Overview|Overview]]
