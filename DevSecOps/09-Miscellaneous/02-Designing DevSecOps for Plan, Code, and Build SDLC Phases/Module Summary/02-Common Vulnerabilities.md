---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Common Vulnerabilities

- [ ] Check for SQL injection vulnerabilities.
- [ ] Check for XSS vulnerabilities.
- [ ] Check for buffer overflow vulnerabilities.
```

### Build Phase

#### Overview

The Build phase is where the codebase is compiled and packaged for deployment. During this phase, it is essential to integrate security practices into the build process to ensure that the final product is secure.

#### Vulnerability Scans

Vulnerability scans involve analyzing the compiled code for security vulnerabilities. This includes static analysis, dynamic analysis, and manual reviews.

##### Static Analysis

Static analysis involves analyzing the compiled code without executing it. This is done using tools that scan the code for potential security issues.

**Why Static Analysis Matters**

Static analysis is important because it helps identify security vulnerabilities early in the build process. By catching these issues before the code is deployed, teams can prevent security breaches and ensure that the final product is secure.

**How Static Analysis Works**

Static analysis tools work by scanning the compiled code for patterns that indicate potential security issues. These tools can identify issues such as SQL injection, cross-site scripting (XSS), and buffer overflows.

**Example: Static Analysis Tool Output**

```markdown
# Static Analysis Report

---
<!-- nav -->
[[01-Common Vulnerabilities Part 1|Common Vulnerabilities Part 1]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/Module Summary/00-Overview|Overview]] | [[03-Designing DevSecOps for Plan, Code, and Build SDLC Phases|Designing DevSecOps for Plan, Code, and Build SDLC Phases]]
