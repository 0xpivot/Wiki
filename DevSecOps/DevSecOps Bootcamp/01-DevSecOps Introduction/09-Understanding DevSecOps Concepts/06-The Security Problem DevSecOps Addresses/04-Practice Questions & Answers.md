---
course: DevSecOps
topic: Understanding DevSecOps Concepts
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the main differences between the waterfall methodology and agile methodologies in the context of software development.**

The waterfall methodology follows a linear sequential process, where each phase must be completed before moving onto the next. It starts with requirements gathering, followed by design, coding, testing, and maintenance. This approach is rigid and does not allow for changes once a phase is completed.

In contrast, agile methodologies emphasize iterative development and adaptability. Agile projects are divided into smaller, manageable units called sprints, with daily scrums to discuss progress and plan next steps. This allows for continuous delivery of value and quick feedback loops, enabling teams to adjust and improve throughout the project lifecycle.

**Q2. How does the traditional waterfall methodology impact information security processes in software development?**

In the traditional waterfall methodology, security processes are often treated as a series of sequential steps, similar to the overall development process. A security risk assessment is conducted early on, followed by a security plan, code review, penetration testing, and regular audits. These steps are typically completed in a specific order, with each step having prerequisites that must be met before proceeding. This can lead to significant delays and inefficiencies, as security issues may only be identified late in the development cycle, requiring costly rework and retesting.

**Q3. What are the primary sources of friction between information security and software development in a traditional waterfall environment?**

The primary sources of friction include:

1. **Security as an Afterthought**: Security is often considered only after the initial development phases, leading to potential vulnerabilities being overlooked until later stages.
2. **Security Sign-off Delays Projects**: Security assessments can delay project timelines, especially if issues are identified late in the development process.
3. **Once-Off Security Assessments**: Traditional methods rely on periodic assessments rather than continuous security monitoring, which can leave gaps in protection.
4. **High Cost of Retesting**: When security issues are found late, retesting and fixing can be expensive and time-consuming.
5. **Perception of Security as Too Slow**: Security processes are often seen as slowing down the development pace, which can be detrimental in fast-paced environments.
6. **Skill Shortages**: There is a lack of skilled security professionals relative to the number of developers, leading to gaps in secure software development practices.

**Q4. How can DevSecOps principles help alleviate the friction between information security and software development?**

DevSecOps integrates security practices into the entire software development lifecycle, making security a shared responsibility across development, operations, and security teams. By embedding security into every stage of the development process, DevSecOps aims to:

1. **Reduce Security as an Afterthought**: Security is considered from the beginning, ensuring that security practices are integrated into the design and development phases.
2. **Minimize Security Delays**: Continuous integration and automated testing help identify and fix security issues earlier, reducing delays.
3. **Promote Continuous Security**: Security is not just a one-time assessment but a continuous process, allowing for ongoing monitoring and improvement.
4. **Lower Retesting Costs**: Automated tools and continuous testing reduce the need for extensive retesting, lowering costs.
5. **Improve Development Speed**: By addressing security concerns early and continuously, DevSecOps helps maintain a faster development pace without compromising security.
6. **Enhance Skill Distribution**: Training and collaboration among teams ensure that security knowledge is distributed more widely, reducing the reliance on a small number of security experts.

**Q5. Discuss recent real-world examples (CVEs/breaches) that highlight the importance of integrating security into the software development lifecycle.**

One notable example is the Equifax data breach in 2017 (CVE-2017-5638). This breach exposed sensitive personal information of over 143 million individuals due to a vulnerability in Apache Struts, a web application framework. The breach occurred because Equifax failed to patch a known vulnerability in a timely manner, highlighting the importance of continuous security monitoring and timely updates.

Another example is the Capital One data breach in 2019 (CVE-2019-11253), where a misconfigured firewall allowed unauthorized access to sensitive customer data. This breach underscores the need for robust security configurations and continuous security assessments to prevent such vulnerabilities.

Both breaches illustrate the critical importance of integrating security into the software development lifecycle to prevent such incidents and protect sensitive data.

---
<!-- nav -->
[[03-The Security Problem DevSecOps Addresses|The Security Problem DevSecOps Addresses]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/06-The Security Problem DevSecOps Addresses/00-Overview|Overview]]
