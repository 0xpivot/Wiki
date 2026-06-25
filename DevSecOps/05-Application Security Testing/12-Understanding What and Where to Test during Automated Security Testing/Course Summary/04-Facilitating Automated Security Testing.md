---
course: DevSecOps
topic: Understanding What and Where to Test during Automated Security Testing
tags: [devsecops]
---

## Facilitating Automated Security Testing

### Encouraging Adoption

To encourage the adoption of automated security testing, focus on facilitating the process rather than mandating it. This involves making it easy and beneficial for the entire team to participate.

#### Steps to Facilitate Adoption

1. **Educate the Team**: Provide training and resources to help team members understand the importance of automated security testing.
2. **Integrate Seamlessly**: Ensure that automated security testing tools integrate seamlessly with existing development workflows.
3. **Provide Feedback**: Regularly provide feedback on the results of automated security testing to help team members understand the value of the process.

### Case Study: Dependency Scanning

#### Background Theory

Dependency scanning tools analyze project dependencies to identify known vulnerabilities. This is particularly important for projects that rely heavily on third-party libraries, as these libraries can introduce security risks.

#### Implementation Steps

1. **Choose a Tool**: Select a dependency scanning tool that supports your package manager. Popular choices include `npm audit`, `pip-audit`, and `Dependabot`.
2. **Configure the Tool**: Set up the tool to scan your project dependencies. This typically involves specifying the location of your package manifest files.
3. **Run the Scan**: Execute the dependency scan. The tool will check your dependencies against a database of known vulnerabilities.
4. **Review and Update Dependencies**: Review the reported vulnerabilities and update your dependencies accordingly.

#### Code Example

```bash
# Vulnerable dependencies
npm install express@4.17.1

# Secure dependencies
npm install express@4.18.2
```

### How to Prevent / Defend

1. **Regular Updates**: Keep dependencies up to date to ensure that known vulnerabilities are patched.
2. **Automated Scanning**: Integrate dependency scanning into your CI/CD pipeline to ensure that vulnerabilities are caught early.
3. **Vulnerability Database**: Use a reliable vulnerability database to stay informed about known vulnerabilities in your dependencies.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/03-Case-by-Case Approach|Case-by-Case Approach]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/12-Understanding What and Where to Test during Automated Security Testing/Course Summary/05-Process vs. Product|Process vs. Product]]
