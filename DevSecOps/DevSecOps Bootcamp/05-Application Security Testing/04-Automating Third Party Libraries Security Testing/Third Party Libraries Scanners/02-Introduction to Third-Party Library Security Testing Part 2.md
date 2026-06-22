---
course: DevSecOps
topic: Automating Third Party Libraries Security Testing
tags: [devsecops]
---

## Introduction to Third-Party Library Security Testing

In the realm of DevSecOps, ensuring the security of third-party libraries is paramount. These libraries are often included in applications to leverage existing functionality, reduce development time, and improve maintainability. However, third-party libraries can introduce significant security risks if they contain known vulnerabilities or are not kept up-to-date. To mitigate these risks, organizations employ automated security testing tools that scan third-party libraries for vulnerabilities.

### Why Automated Scanning Matters

Automated scanning tools help identify and remediate security issues in third-party libraries before they can be exploited. These tools can integrate seamlessly into the continuous integration/continuous deployment (CI/CD) pipeline, ensuring that security checks are performed consistently and efficiently. By automating the process, teams can focus on developing high-quality, secure applications rather than manually checking for vulnerabilities.

### Phases for Deploying Scanners

Third-party library scanners can be deployed at various stages of the software development lifecycle:

1. **Build Phase**: During the build phase, the automation or build server retrieves code from the repository, fingerprints it, and matches it against lists of known vulnerabilities.
2. **Artifact Storage**: When artifacts are pushed to a registry or stored on an artifact server, scanners can perform additional checks.
3. **Pre-Commit Phase**: Integrated Development Environments (IDEs) can check for outdated third-party libraries before code is committed.

### Asynchronous Scanning

Scans can be performed asynchronously, meaning they do not necessarily occur immediately after a code commit. This approach is beneficial because some scans can take a long time and may not provide immediate value if the results are not directly related to recent code changes.

### Intelligent Fingerprinting

Some scanners use intelligent fingerprinting techniques to identify third-party libraries accurately. These techniques involve analyzing the codebase to create unique identifiers that can be matched against vulnerability databases. While these methods are highly effective, they can also be complex and time-consuming.

### Periodic Scans

Given the complexity and time required for thorough scans, it is often recommended to perform periodic scans rather than scanning after every code commit. This ensures that the results are not muddied by unrelated code changes and provides a clearer picture of the overall security posture.

---
<!-- nav -->
[[01-Introduction to Third-Party Library Security Testing Part 1|Introduction to Third-Party Library Security Testing Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/Third Party Libraries Scanners/00-Overview|Overview]] | [[03-Introduction to Third-Party Library Security Testing|Introduction to Third-Party Library Security Testing]]
