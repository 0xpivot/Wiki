---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of adding temporary permissions to a Kubernetes admin for testing purposes.**

Temporary permissions are often added to a Kubernetes admin to facilitate testing and debugging tasks. These permissions might include the ability to create pods, execute commands within containers, and perform other actions necessary for verifying the functionality of the system. Once the testing is complete, these permissions can be removed to maintain security and minimize the risk of unauthorized access. For instance, granting `create` permissions for pods and `exec` access allows the admin to create a test pod and interact with it to verify network connectivity and service interactions.

**Q2. How would you configure an authorization policy to deny all traffic to a specific service within a namespace?**

To configure an authorization policy that denies all traffic to a specific service within a namespace, you would define an authorization policy with a `deny` action and specify the target service using selectors. Here’s an example:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-frontend-policy
  namespace: online-boutique
spec:
  action: DENY
  rules:
  - from:
    - source:
        namespaces: ["*"]
    to:
    - operation:
        hosts: ["frontend.online-boutique.svc.cluster.local"]
        ports: ["80"]
```

This policy denies all traffic to the `frontend` service on port 80 from any namespace. Ensure that the namespace where the policy is applied has Istio sidecar injection enabled to enforce the policy.

**Q3. Why is it important to ensure that Istio sidecars are injected into pods when configuring authorization policies?**

It is crucial to ensure that Istio sidecars are injected into pods because authorization policies are enforced by the Istio proxies (sidecars). If a pod does not have an Istio sidecar, the authorization policies will not be effective for that pod. For example, if you attempt to restrict traffic from the `online-boutique` namespace to the `argo-cd` namespace, but the `argo-cd` pods do not have Istio sidecars, the policies will not be enforced, and traffic may still flow unrestricted. To ensure enforcement, you must enable sidecar injection for the relevant namespaces, as shown below:

```yaml
sitecar.istio.io/inject: "true"
```

**Q4. How would you modify an existing Helm chart to enable Istio sidecar injection for all pods in a namespace?**

To modify an existing Helm chart to enable Istio sidecar injection for all pods in a namespace, you would update the Helm chart values to include the appropriate label. Here’s an example of how to achieve this:

1. Create a new values file for the Helm chart:

```yaml
# argocd-values.yaml
global:
  podLabels:
    sitecar.istio.io/inject: "true"
```

2. Update the Helm chart to use this values file:

```bash
helm upgrade --install argocd argocd/argocd -f argocd-values.yaml
```

This ensures that all pods created by the Helm release will have the `sitecar.istio.io/inject` label set to `true`, enabling Istio sidecar injection.

**Q5. What recent real-world examples or CVEs highlight the importance of properly configuring authorization policies in Kubernetes clusters?**

One notable example is the Kubernetes API server vulnerability (CVE-2021-25741), which allowed attackers to bypass authentication and authorization mechanisms. This vulnerability underscores the critical importance of properly configuring authorization policies to prevent unauthorized access and ensure secure communication within the cluster.

Another example is the misconfiguration of RBAC (Role-Based Access Control) policies, which led to unauthorized access in several organizations. Ensuring that RBAC policies are correctly defined and regularly reviewed helps mitigate such risks.

**Q6. How would you troubleshoot a scenario where an authorization policy is not being enforced as expected?**

To troubleshoot a scenario where an authorization policy is not being enforced as expected, follow these steps:

1. **Verify Istio Sidecar Injection**: Ensure that the pods in question have Istio sidecars injected. You can check this by inspecting the pod descriptions:

   ```bash
   kubectl describe pod <pod-name>
   ```

2. **Check Authorization Policy Configuration**: Review the authorization policy configuration to ensure it is correctly defined and applied to the intended namespace and services.

3. **Inspect Istio Proxy Logs**: Check the logs of the Istio proxies to identify any issues with policy enforcement. You can access the logs using:

   ```bash
   kubectl logs <pod-name> -c istio-proxy
   ```

4. **Validate Network Traffic**: Use tools like `curl` or `kubectl exec` to simulate traffic and verify if the policy is being enforced as expected.

By systematically checking these aspects, you can identify and resolve issues preventing the proper enforcement of authorization policies.

---
<!-- nav -->
[[13-Configuring Authorization Policies in Istio|Configuring Authorization Policies in Istio]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure Authorization Policies/00-Overview|Overview]]
