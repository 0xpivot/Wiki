---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of "quick wins" in the context of implementing automated security testing.**

Automated security testing can be complex and resource-intensive, especially when starting out. A "quick win" strategy involves identifying and implementing simple, high-impact security measures that can be easily integrated into existing processes without significant overhead. These initial successes help build momentum and support within the team, making subsequent, more complex implementations smoother. Quick wins could include basic static code analysis tools or simple vulnerability scanners that provide immediate feedback and improvements.

**Q2. How would you facilitate the adoption of automated security testing within a development team, rather than mandating it?**

Facilitating the adoption of automated security testing requires a collaborative approach that encourages voluntary participation rather than imposing strict rules. This can be achieved by:

- Educating the team about the benefits of automated security testing through workshops and training sessions.
- Demonstrating the value of these tools with real-world examples and success stories.
- Providing easy-to-use tools and clear documentation.
- Offering incentives such as recognition for teams that successfully integrate security testing.
- Allowing teams to choose the tools and methods that best fit their projects.

By fostering a supportive environment, the team is more likely to embrace security testing voluntarily, leading to better overall adoption and effectiveness.

**Q3. Discuss the trade-offs involved in implementing automated security testing tools.**

Implementing automated security testing tools involves several trade-offs, including:

- **Cost vs. Benefit**: The cost of purchasing and maintaining security testing tools needs to be weighed against the potential benefits, such as reduced vulnerabilities and improved software quality.
- **Time vs. Security**: Automated security testing can add additional time to the development cycle. Teams need to balance the time spent on security testing with the urgency of delivering new features.
- **False Positives vs. True Positives**: Automated tools may generate false positives, which can lead to wasted time investigating non-issues. Conversely, missing true positives can leave vulnerabilities unaddressed.

For example, consider the recent CVE-2021-44228 (Log4j vulnerability). Organizations that had robust automated security testing in place were able to quickly identify and mitigate risks associated with this critical vulnerability, whereas those without such measures faced significant exposure.

**Q4. Why should automated security testing be considered a process rather than a product?**

Automated security testing should be viewed as a process because it involves ongoing activities and continuous improvement rather than a one-time purchase of a tool. Key reasons include:

- **Continuous Integration**: Security testing should be integrated into the entire software development lifecycle, from coding to deployment.
- **Adaptation to Threats**: New threats and vulnerabilities emerge regularly, requiring updates to security testing processes.
- **Feedback Loops**: Continuous feedback from security testing helps refine and improve the development process over time.

For instance, the Equifax breach in 2017 highlighted the importance of continuous monitoring and updating of security practices. By treating automated security testing as a process, organizations can stay ahead of emerging threats and maintain robust security postures.

**Q5. What are the key differences between the theoretical concepts covered in this course and the practical steps covered in the follow-up courses?**

The current course focuses on theoretical concepts related to automated security testing, such as understanding the principles, trade-offs, and strategic approaches. In contrast, the follow-up courses will delve into practical aspects, including:

- **Tooling**: Detailed instructions on how to use specific automated security testing tools for different types of code, containers, and infrastructure.
- **Integration**: Steps to integrate these tools into a CI/CD pipeline, ensuring that security testing becomes a seamless part of the development process.
- **Real-world Demos**: Practical demonstrations and hands-on exercises to apply the knowledge gained from the theoretical course.

This progression ensures that learners move from understanding the why and what of automated security testing to the how, providing a comprehensive learning experience.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/09-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/00-Overview|Overview]]
