---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the purpose of threat modeling in the DevSecOps lifecycle?**

Threat modeling is a critical step in the DevSecOps lifecycle aimed at identifying potential structural vulnerabilities in an application from the perspective of a hypothetical attacker. The goal is to foresee weaknesses that could be exploited and to design the system to be more robust against these threats. This proactive approach ensures that security is integrated into the development process early on, reducing risks and enhancing overall system resilience.

**Q2. Explain the difference between Static Code Analysis (SCA) and Software Composition Analysis (SAS).**

Static Code Analysis (SCA) involves analyzing source code without executing it to find security flaws, bugs, and compliance issues. It checks the code for adherence to coding standards and identifies potential vulnerabilities.

Software Composition Analysis (SAS), on the other hand, focuses on analyzing the software components and libraries used in an application to identify any known vulnerabilities or license compliance issues. SAS tools scan the dependencies and provide insights into the security posture of the external components used in the project.

**Q3. How does threat modeling contribute to the build phase in the DevSecOps lifecycle?**

During the build phase, threat modeling contributes by helping developers understand potential vulnerabilities that could arise from the code they write. By using tools like the Microsoft TREP modeling tool, developers can identify and prioritize threats, ensuring that the build process includes necessary security measures. This proactive identification of threats allows for the integration of security controls and patches before the application moves to testing or production phases.

**Q4. Describe the Stride methodology used in threat modeling.**

Stride is an acronym for Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege. This methodology is used to categorize different types of threats that an application might face:

- **Spoofing**: Impersonating another user or system.
- **Tampering**: Unauthorized modification of resources.
- **Repudiation**: Actions that cannot be proven to have occurred.
- **Information Disclosure**: Exposure of sensitive information.
- **Denial of Service**: Disruption of services.
- **Elevation of Privilege**: Unauthorized access to higher-level permissions.

By assessing an application against these categories, developers can ensure that their systems are robust and secure against a wide range of potential attacks.

**Q5. Why is it recommended to use specific tools for threat modeling instead of doing it manually?**

Using specific tools for threat modeling is recommended because these tools are designed to automate the process of identifying and prioritizing threats. They can analyze complex systems and provide detailed reports on potential vulnerabilities much faster than manual methods. Tools like the Microsoft TREP modeling tool can propose a variety of threats based on the type of solution being built, allowing developers to assess their applications more comprehensively and efficiently. This automation ensures that no potential threats are overlooked and that the threat modeling process is consistent and thorough.

**Q6. Provide an example of how threat modeling was used in a recent real-world scenario.**

In the context of recent real-world scenarios, consider the SolarWinds supply chain attack (CVE-2020-1014). This attack involved a sophisticated threat actor compromising the SolarWinds Orion software update mechanism to distribute a backdoor called Sunburst. If SolarWinds had implemented comprehensive threat modeling, they might have identified the risk of attackers exploiting their software update process. Threat modeling could have highlighted the importance of securing the update mechanism and implementing robust validation checks to prevent unauthorized modifications. This proactive approach could have potentially mitigated the impact of the attack.

---
<!-- nav -->
[[01-Introduction to Threat Modeling in DevSecOps|Introduction to Threat Modeling in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/03-Threat Modeling/00-Overview|Overview]]
