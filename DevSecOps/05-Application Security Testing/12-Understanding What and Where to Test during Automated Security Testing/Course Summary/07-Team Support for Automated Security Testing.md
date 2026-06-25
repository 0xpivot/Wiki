---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Team Support for Automated Security Testing

### Importance of Team Support

Team support is crucial for the successful implementation of automated security testing. When the entire team is on board, the process is more likely to be effective and sustainable.

#### Steps to Gain Team Support

1. **Communicate the Benefits**: Clearly communicate the benefits of automated security testing to the team. Highlight how it can improve the overall security of the application.
2. **Involve the Team**: Involve team members in the decision-making process. This can help build buy-in and ensure that the process is tailored to the team's needs.
3. **Provide Training**: Provide training and resources to help team members understand how to use automated security testing tools effectively.

### Case Study: Configuration Management

#### Background Theory

Configuration management involves ensuring that system configurations are secure. Misconfigurations can lead to security vulnerabilities, so it is important to validate configurations regularly.

#### Implementation Steps

1. **Choose a Tool**: Select a configuration management tool that supports your environment. Popular choices include `kube-bench` for Kubernetes clusters and `OpenSCAP` for general Linux systems.
2. **Configure the Tool**: Set up the tool to validate your system configurations. This typically involves specifying the location of your configuration files.
3. **Run the Validation**: Execute the configuration validation. The tool will check your configurations against a set of security benchmarks.
4. **Review and Fix Issues**: Review the reported issues and address them. This may involve modifying the configuration files to meet security standards.

#### Code Example

```yaml
# Insecure Kubernetes configuration
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    securityContext:
      privileged: true

# Secure Kubernetes configuration
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    securityContext:
      privileged: false
```

### How to Prevent / Defend

1. **Use Security Benchmarks**: Validate configurations against established security benchmarks such as CIS Benchmarks.
2. **Regular Audits**: Perform regular audits to ensure that configurations remain secure over time.
3. **Automated Validation**: Integrate configuration validation into your CI/CD pipeline to ensure that configurations are validated automatically.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/06-Quick Wins in Automated Security Testing|Quick Wins in Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/08-Trade-offs in Automated Security Testing|Trade-offs in Automated Security Testing]]
