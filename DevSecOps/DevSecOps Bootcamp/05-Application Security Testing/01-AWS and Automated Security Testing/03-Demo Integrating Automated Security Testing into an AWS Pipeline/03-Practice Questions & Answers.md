---
course: DevSecOps
topic: AWS and Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how automated security testing can be integrated into an AWS pipeline.**

Automated security testing can be integrated into an AWS pipeline by adding a new stage dedicated to security checks. This involves creating a new CodeBuild project that uses a specific tool, such as Hadolint, to perform security tests on Docker images. The steps include:

1. Creating a new CodeBuild project with the necessary build spec file that defines the security testing process.
2. Configuring the project to use the appropriate Docker image and enabling necessary permissions.
3. Modifying the existing pipeline to include the new security testing stage by adding a new action group and specifying the CodeBuild project.
4. Ensuring that the pipeline triggers the security testing stage appropriately and handles the output correctly.

**Q2. How would you configure a CodeBuild project to use Hadolint for Docker image linting?**

To configure a CodeBuild project to use Hadolint for Docker image linting, follow these steps:

1. Define a `buildspec.yml` file that includes the necessary commands to pull the Hadolint Docker image and run the linting process.
2. Create a new CodeBuild project and specify the `buildspec.yml` file as the build specification.
3. Set the environment to use an appropriate Docker container, such as Amazon Linux.
4. Ensure the CodeBuild project has the necessary permissions to run Docker commands by enabling the `privileged` flag.
5. Configure the CodeBuild project to use the specified Docker image version and runtime.

Here is an example `buildspec.yml` file:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      docker: 19
  build:
    commands:
      - docker pull hadolint/hadolint
      - docker run --rm -i hadolint/hadolint < Dockerfile
```

**Q3. Why did the security testing stage fail even though the Hadolint output contained only informational messages?**

The security testing stage failed because the default behavior of the pipeline might be configured to fail on any non-zero exit status from the Hadolint command, regardless of whether the messages are informational or not. To fix this, the pipeline needs to be configured to only fail on warnings or higher severity messages.

One way to address this is by modifying the `buildspec.yml` file to filter out informational messages before checking the exit status. Here’s an example:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      docker: 19
  build:
    commands:
      - docker pull hadolint/hadolint
      - docker run --rm -i hadolint/hadolint < Dockerfile | grep -v 'INFO' || true
```

In this example, `grep -v 'INFO'` filters out informational messages, and `|| true` ensures the command does not cause the pipeline to fail if informational messages are present.

**Q4. What recent real-world examples can illustrate the importance of integrating automated security testing into CI/CD pipelines?**

Recent real-world examples include:

1. **CVE-2021-21972**: A vulnerability in the Log4j library led to widespread exploitation due to insecure configurations and dependencies. Integrating automated security testing into CI/CD pipelines could have helped identify and mitigate such vulnerabilities early in the development cycle.

2. **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack involved the compromise of software updates, leading to the infiltration of multiple organizations. Automated security testing could have helped detect malicious changes in the software supply chain.

3. **Apache Struts Vulnerability (CVE-2017-5638)**: This vulnerability allowed remote code execution in applications using Apache Struts. Automated security testing could have identified the presence of vulnerable versions of Apache Struts during the build process.

By integrating automated security testing into CI/CD pipelines, organizations can proactively identify and remediate security issues before they become critical vulnerabilities.

---
<!-- nav -->
[[02-Introduction to Automated Security Testing in AWS Pipelines|Introduction to Automated Security Testing in AWS Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/03-Demo Integrating Automated Security Testing into an AWS Pipeline/00-Overview|Overview]]
