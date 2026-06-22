---
course: DevSecOps
topic: Understanding DevSecOps Concepts
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the main friction points that traditional security approaches face in a fast-moving software development environment.**

Traditional security approaches often involve manual inspections and periodic audits, which do not align well with the rapid pace of modern software development. In a fast-moving environment, such as one using agile methodologies, security checks that are not integrated into the continuous integration/continuous deployment (CI/CD) pipeline can become bottlenecks. This leads to delays, increased costs, and potential security vulnerabilities being overlooked due to the pressure to release new features quickly.

**Q2. How does DevOps resolve some of the issues that existed between development and operations teams?**

DevOps addresses the siloed nature of development and operations by promoting collaboration and communication between these teams. By integrating development and operations processes, DevOps ensures that both teams work together throughout the entire lifecycle of an application. This includes sharing responsibilities for testing, deployment, and monitoring, leading to faster feedback loops and more efficient resolution of issues. The use of automation tools and practices like continuous integration and delivery (CI/CD) further enhances this collaboration by reducing manual errors and speeding up the release process.

**Q3. What is the primary goal of moving towards a DevSecOps environment?**

The primary goal of transitioning to a DevSecOps environment is to embed security practices directly into the software development lifecycle. This means integrating security measures at every stage of development, from planning and coding to testing and deployment. By doing so, security becomes a shared responsibility across all teams involved in the development process, rather than being treated as an afterthought or separate task. This approach aims to reduce security risks, improve compliance, and enhance overall product quality through consistent and automated security checks.

**Q4. How can security as code or scripting help in achieving better security outcomes in a DevSecOps environment?**

Security as code involves treating security policies and controls as code that can be version-controlled, tested, and deployed alongside application code. This practice helps ensure that security measures are consistently applied across all environments and that changes to security policies can be tracked and reviewed. Scripting allows for the automation of security tasks, such as vulnerability scanning, compliance checks, and penetration testing, which can be run as part of the CI/CD pipeline. This automation reduces the likelihood of human error and ensures that security checks are performed regularly and reliably. For example, using tools like Ansible or Terraform for infrastructure as code (IaC) can enforce security configurations across cloud resources, ensuring that security settings are correctly applied and updated over time.

**Q5. Provide an example of how recent real-world breaches could have been mitigated with a DevSecOps approach.**

One notable example is the Capital One data breach in 2019 (CVE-2019-11778), where a misconfigured web application firewall allowed unauthorized access to sensitive customer data. A DevSecOps approach could have helped mitigate this issue by integrating security into the development process. For instance, implementing automated security testing and configuration management tools could have detected the misconfiguration earlier. Additionally, regular security audits and penetration testing as part of the CI/CD pipeline could have identified and fixed the vulnerability before it was exploited. Embedding security practices like these into the software development lifecycle would have significantly reduced the risk of such breaches occurring.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/Module Summary/05-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/Module Summary/00-Overview|Overview]]
