---
course: DevSecOps
topic: AWS and Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the purpose of adding a failure threshold flag to the HadoLint command?**

The purpose of adding a failure threshold flag to the HadoLint command is to control when the linter should cause a build to fail. By setting the failure threshold to warnings or higher, the build will only fail if there are warnings or errors detected by the linter. This allows developers to maintain a certain quality standard without failing builds over minor issues like informational messages.

**Q2. How do you modify the build spec HadoLint file and commit the changes to a Git repository?**

To modify the build spec HadoLint file and commit the changes to a Git repository, follow these steps:

1. Open the HadoLint file in an editor (e.g., Emacs).
2. Add the desired flag (e.g., `--failure-threshold=warning`) to the HadoLint command.
3. Save the file.
4. Use the `git add` command to stage the modified file for commit.
5. Commit the changes using `git commit -m "feature only fail with warnings or higher"`.
6. Push the changes to the remote repository using `git push`.

**Q3. Explain how the pipeline execution reflects the changes made to the HadoLint command.**

When the pipeline executes after modifying the HadoLint command with a failure threshold, it picks up the new configuration from the committed changes. The pipeline then runs the security tests according to the updated settings. If the previous run failed due to lower severity issues, the pipeline will now succeed if those issues are below the warning threshold. The success or failure of the pipeline stages directly reflects the new criteria set by the HadoLint command.

**Q4. Why did the pipeline succeed this time even though the test results were the same?**

The pipeline succeeded this time because the HadoLint command was configured to only fail on warnings or higher severity issues. Even though the test results were the same, the pipeline stage now succeeds because it ignores lower severity issues such as informational messages. The actual test execution and results did not change; the difference lies in how the pipeline interprets and handles the test outcomes based on the new failure threshold setting.

**Q5. How does adjusting the security test settings impact the development process in a DevSecOps environment?**

Adjusting the security test settings in a DevSecOps environment impacts the development process by ensuring that the build process maintains a consistent quality bar while allowing for more flexibility in handling less critical issues. For example, setting a failure threshold to warnings or higher means that builds won’t fail over minor issues, which can speed up the development cycle. However, it also means that developers need to pay attention to warnings and address them in a timely manner to avoid accumulating technical debt. This balance helps in maintaining a secure and efficient development workflow. 

**Q6. What recent real-world examples illustrate the importance of properly configuring security tests in a CI/CD pipeline?**

One recent real-world example is the Log4j vulnerability (CVE-2021-44228). Many organizations had their pipelines configured to only fail on high-severity issues, leading to missed opportunities to catch and mitigate the vulnerability early. Properly configuring security tests to detect and fail on medium to high-severity issues could have helped in identifying and addressing the Log4j vulnerability sooner. This highlights the importance of having a robust and sensitive security testing strategy in place to prevent such vulnerabilities from slipping through the cracks.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/02-Demo Adjusting a Security Test/01-Introduction to AWS and Automated Security Testing|Introduction to AWS and Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/01-AWS and Automated Security Testing/02-Demo Adjusting a Security Test/00-Overview|Overview]]
