---
course: DevSecOps
topic: Adopt DevSecOps in Organizations
tags: [devsecops]
---

## Traditional Software Development Silos

In traditional software development, teams were often organized into distinct silos, each with its own responsibilities and goals. These silos typically included:

- **Development Team**: Responsible for writing code and implementing features.
- **Operations Team**: Managed the infrastructure, ensuring systems were up and running.
- **Security Team**: Conducted audits and identified vulnerabilities, usually late in the development cycle.

This approach led to several significant issues:

### Slow Release Cycles

The division of labor meant that each team had to wait for the others to complete their tasks before moving forward. For instance, developers would finish coding, then hand off the project to the operations team for deployment. Only after deployment would the security team review the system for vulnerabilities. This sequential process significantly slowed down the release cycle.

### Last-Minute Security Issues

Because security was often an afterthought, many vulnerabilities were discovered late in the development cycle. This could lead to rushed fixes, which might introduce new bugs or further delays. Moreover, the pressure to meet deadlines often resulted in compromises on security measures.

### Finger-Pointing Culture

When security issues arose in production, there was often a blame game. Developers might argue that the security team should have caught the issues earlier. Operations teams might claim that the code was flawed. Security teams might say that the operations team failed to maintain a secure environment. This finger-pointing culture created a toxic work environment and hindered collaboration.

### Real-World Example: Equifax Breach (CVE-2017-5638)

One of the most notable examples of the consequences of this siloed approach is the Equifax breach in 2017. The breach exposed sensitive data of approximately 147 million consumers. The vulnerability exploited was a flaw in Apache Struts, a popular web application framework. Despite the availability of a patch, the operations team failed to apply it in a timely manner. This incident highlights the dangers of a fragmented approach to security and operations.

---
<!-- nav -->
[[06-How DevSecOps Works|How DevSecOps Works]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/01-Adopt DevSecOps in Organizations/Final Summary The DevSecOps Transformation/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/01-Adopt DevSecOps in Organizations/Final Summary The DevSecOps Transformation/08-Practice Questions & Answers|Practice Questions & Answers]]
