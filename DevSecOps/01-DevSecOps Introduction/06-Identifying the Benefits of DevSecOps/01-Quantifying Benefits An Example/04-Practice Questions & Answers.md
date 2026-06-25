---
course: DevSecOps
topic: Identifying the Benefits of DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of "shifting left" in the context of DevSecOps and how it relates to reducing costs associated with security vulnerabilities.**

Shifting left in DevSecOps refers to the practice of integrating security activities earlier in the software development lifecycle (SDLC). Traditionally, security testing was often deferred until the later stages of development or even post-deployment. Shifting left means incorporating security considerations and testing during the initial phases of development, such as design and requirements gathering.

This approach is beneficial because it aligns with the findings from NIST and other research institutions that show the cost of fixing bugs increases significantly the later they are discovered. Security vulnerabilities are treated as bugs, and thus, the same principles apply. By identifying and addressing security issues early, organizations can reduce the overall cost of remediation and minimize the risk of vulnerabilities making it to production.

For example, if a security flaw is found during the design phase, it might only require minor adjustments to the design documents and coding practices. However, if the same flaw is discovered after the product has been deployed, it could involve extensive code changes, potential downtime, and even financial penalties due to data breaches. Therefore, shifting left helps in reducing these costs and risks.

**Q2. How does the introduction of DevSecOps contribute to reducing the time required for rework or fixing security vulnerabilities? Provide a specific example.**

DevSecOps contributes to reducing the time required for rework or fixing security vulnerabilities by embedding security practices throughout the entire software development lifecycle. This proactive approach ensures that security is considered from the very beginning, rather than being an afterthought.

For instance, consider a scenario where a web application is being developed. Without DevSecOps, security testing might only occur after the application is fully coded and tested for functionality. If a critical vulnerability is then discovered, developers would need to go back through the codebase to locate and fix the issue, which can be time-consuming and disruptive.

In contrast, with DevSecOps, security testing tools and practices are integrated into continuous integration/continuous deployment (CI/CD) pipelines. Automated security scans can run alongside functional tests, providing immediate feedback on potential security issues. Developers can address these issues promptly while the code is still fresh in their minds, significantly reducing the time and effort required for rework.

A recent example of this is the widespread adoption of static application security testing (SAST) tools within CI/CD pipelines. These tools automatically scan code for known vulnerabilities and provide actionable insights, allowing teams to fix issues quickly and efficiently.

**Q3. Describe how the classic bug cost diagram supports the business case for implementing DevSecOps.**

The classic bug cost diagram illustrates the increasing cost of fixing bugs as they are discovered later in the software development lifecycle. According to NIST and other research institutions, the cost of fixing a bug can increase exponentially as the project progresses from design to production.

For example, a bug found during the design phase might cost $100 to fix, whereas the same bug found during the testing phase could cost $10,000, and if discovered post-deployment, it could cost upwards of $1 million. This exponential cost increase is due to the compounding effects of having to rework code, test fixes, and potentially deal with system downtime and reputational damage.

In the context of security vulnerabilities, which are essentially bugs that can compromise system integrity and confidentiality, the same cost model applies. By implementing DevSecOps, organizations can shift security testing to earlier stages of the SDLC, thereby catching and fixing vulnerabilities before they become costly to address.

Thus, the classic bug cost diagram provides a strong business case for DevSecOps by demonstrating that early identification and remediation of security vulnerabilities can save significant amounts of money and resources. This makes a compelling argument for investing in DevSecOps practices to improve overall security posture and reduce operational costs.

**Q4. How can the principles of DevSecOps be applied to mitigate the risks associated with recent security breaches, such as those involving unpatched vulnerabilities?**

Recent security breaches, such as those involving unpatched vulnerabilities, highlight the importance of timely and effective patch management. DevSecOps principles can be applied to mitigate these risks by ensuring that security is integrated into every stage of the software development lifecycle.

One key principle is continuous monitoring and automated testing. By integrating security testing tools into CI/CD pipelines, organizations can continuously scan for known vulnerabilities and ensure that patches are applied promptly. For example, using tools like OWASP ZAP or SonarQube can help identify and address vulnerabilities early in the development process.

Another principle is fostering a culture of collaboration between development, operations, and security teams. This ensures that security concerns are addressed proactively and that everyone is accountable for maintaining a secure environment. Regular security training and awareness programs can also help keep the team updated on the latest threats and best practices.

For instance, the Equifax breach in 2017, which exposed sensitive personal information of millions of consumers, was caused by an unpatched Apache Struts vulnerability. Applying DevSecOps principles could have helped prevent this breach by ensuring that the vulnerability was identified and patched before it could be exploited.

By adopting these principles, organizations can reduce the likelihood of similar breaches occurring in the future and maintain a robust security posture.

---
<!-- nav -->
[[03-Quantifying the Benefits of DevSecOps|Quantifying the Benefits of DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/06-Identifying the Benefits of DevSecOps/03-Quantifying Benefits An Example/00-Overview|Overview]]
