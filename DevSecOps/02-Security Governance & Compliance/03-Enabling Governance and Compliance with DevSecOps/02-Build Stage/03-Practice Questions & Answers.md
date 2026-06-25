---
course: DevSecOps
topic: Enabling Governance and Compliance with DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the difference between Software Composition Analysis (SCA) and Static Application Security Testing (SAST)?**

Software Composition Analysis (SCA) focuses on analyzing the components used in a software project, checking their binary signatures against known vulnerabilities in public databases like the National Vulnerability Database. SCA helps identify and manage open-source components and their associated risks.

Static Application Security Testing (SAST), on the other hand, analyzes the source code directly without executing it. SAST tools scan the code for potential security flaws and coding errors that could lead to vulnerabilities. While SCA deals with third-party components, SAST deals with the actual code written by developers.

**Q2. How does implementing SCA in the build stage help ensure compliance and governance?**

Implementing SCA in the build stage helps ensure compliance and governance by identifying and managing open-source components and their associated vulnerabilities. By integrating SCA into the CI/CD pipeline, teams can automatically check for known vulnerabilities in the software components they use. This helps maintain compliance with security policies and standards, ensuring that only secure components are included in the final product. For example, if a project uses a version of a library that has a known critical vulnerability (like CVE-2021-44228 in Log4j), SCA tools will flag this issue, allowing the team to take corrective action before deployment.

**Q3. Explain how vulnerability scanning fits into a DevSecOps model.**

In a DevSecOps model, vulnerability scanning is integrated into the CI/CD pipeline to ensure that security checks are performed continuously and automatically. Traditionally, vulnerability scans were done manually on a periodic basis (e.g., monthly or quarterly). In contrast, DevSecOps emphasizes frequent and automated scanning to detect vulnerabilities early in the development cycle. This approach allows teams to address security issues promptly, reducing the risk of deploying vulnerable code. Tools like Qualys, EdgeScan, and Nessus/Tenable I.O. provide APIs and webhooks that can be easily integrated into CI/CD pipelines, making the process seamless and efficient.

**Q4. What are some common tools used for SCA and vulnerability scanning in the build stage?**

For Software Composition Analysis (SCA), some common tools include:
- JFrog X-Ray
- Veracode
- Checkmarx

For vulnerability scanning, commonly used tools include:
- Qualys
- EdgeScan
- Nessus/Tenable I.O.

These tools help identify vulnerabilities in both third-party components and the compiled software itself. They provide detailed reports on the vulnerabilities found, including their severity and potential impact, enabling teams to take appropriate actions to mitigate risks.

**Q5. How can you integrate vulnerability scanning into a CI/CD pipeline?**

Integrating vulnerability scanning into a CI/CD pipeline involves several steps:

1. **Select a Vulnerability Scanning Tool**: Choose a tool that provides APIs or webhooks for integration, such as Qualys, EdgeScan, or Nessus/Tenable I.O.

2. **Configure the Pipeline**: Modify the CI/CD pipeline configuration to include a step for running the vulnerability scan. This typically involves adding a script or plugin that invokes the scanning tool.

3. **Automate the Scan**: Use the tool’s API or webhook capabilities to trigger the scan automatically whenever new code is committed or merged into the repository.

4. **Provide Feedback**: Ensure that the results of the vulnerability scan are reported back to the pipeline and made visible to the development team. This can be done through the CI/CD platform’s reporting features or by integrating with a ticketing system.

5. **Set Policies**: Define policies for handling vulnerabilities, such as requiring fixes for high-severity issues before deployment.

Here’s an example using a hypothetical CI/CD tool and Qualys:

```yaml
stages:
  - build
  - test
  - scan
  - deploy

scan:
  stage: scan
  script:
    - curl -X POST https://qualys.example.com/api/v1/scan \
      -H 'Authorization: Bearer YOUR_API_KEY' \
      -d '{"target": "your-app", "type": "vulnerability"}'
  only:
    - master
```

This YAML snippet integrates a vulnerability scan into the pipeline, triggering it after the build and test stages but before deployment. The `curl` command sends a request to the Qualys API to initiate a scan on the specified target.

**Q6. Why is it important to run vulnerability scans frequently in a DevSecOps environment?**

Running vulnerability scans frequently in a DevSecOps environment is crucial for several reasons:

1. **Early Detection**: Frequent scanning helps detect vulnerabilities early in the development cycle, when they are easier and less costly to fix.

2. **Continuous Improvement**: Regular scanning ensures that security is an ongoing concern, not just a one-time check. This promotes a culture of continuous improvement and vigilance.

3. **Reduced Risk**: By catching and fixing vulnerabilities quickly, teams reduce the risk of deploying insecure code, which could lead to breaches or compliance failures.

4. **Compliance**: Many regulatory requirements mandate regular security assessments. Frequent scanning helps meet these obligations and ensures that the organization remains compliant.

For example, the Equifax breach in 2017 was partly due to a failure to patch a known vulnerability in Apache Struts. If Equifax had been running frequent vulnerability scans as part of a DevSecOps process, they might have identified and fixed the vulnerability before it was exploited.

**Q7. How does integrating SCA and vulnerability scanning into the CI/CD pipeline benefit the development team?**

Integrating SCA and vulnerability scanning into the CI/CD pipeline benefits the development team in several ways:

1. **Automation**: Automating these processes reduces manual effort and ensures consistency across builds.

2. **Immediate Feedback**: Developers receive immediate feedback on the security status of their code and dependencies, allowing them to address issues promptly.

3. **Improved Security**: By catching and addressing vulnerabilities early, the overall security posture of the application improves.

4. **Reduced Learning Curve**: Most modern tools provide easy-to-use integrations and clear reporting, minimizing the learning curve for developers.

5. **Enhanced Compliance**: Automated checks help ensure that the application meets security and compliance standards, reducing the risk of non-compliance penalties.

For instance, the SolarWinds supply chain attack in 2020 highlighted the importance of monitoring and securing third-party components. Integrating SCA into the CI/CD pipeline would have helped detect and mitigate such risks earlier, potentially preventing the widespread impact of the attack.

**Q8. What recent real-world examples demonstrate the importance of SCA and vulnerability scanning in the build stage?**

Recent real-world examples highlight the critical importance of SCA and vulnerability scanning:

1. **Log4j Vulnerability (CVE-2021-44228)**: The Log4j vulnerability affected millions of applications globally. SCA tools could have identified the presence of vulnerable Log4j versions in software projects, prompting timely updates and mitigations.

2. **SolarWinds Supply Chain Attack (2020)**: This attack involved malicious code injected into SolarWinds software updates. SCA tools could have flagged the presence of unauthorized or modified components, alerting organizations to the potential threat.

3. **Equifax Data Breach (2017)**: The breach was caused by a failure to patch a known vulnerability in Apache Struts. Regular vulnerability scanning could have identified this vulnerability, allowing Equifax to apply the necessary patches before the breach occurred.

These examples underscore the need for robust SCA and vulnerability scanning practices to protect against emerging threats and maintain the integrity of software projects.

---
<!-- nav -->
[[02-Build Stage in DevSecOps Pipeline|Build Stage in DevSecOps Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/02-Build Stage/00-Overview|Overview]]
