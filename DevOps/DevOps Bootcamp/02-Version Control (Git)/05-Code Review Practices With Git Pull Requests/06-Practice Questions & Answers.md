---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of code review practices using Git pull requests.**

The purpose of code review practices using Git pull requests is to ensure that the code being merged into the main branch (often referred to as `master`) is thoroughly checked for correctness, maintainability, and adherence to coding standards. This process helps prevent bugs and issues from entering the production environment by having another set of eyes review the changes. Additionally, it facilitates knowledge sharing among team members and helps less experienced developers learn from more seasoned ones.

**Q2. How does the code review process help in maintaining the quality of the `master` branch?**

The code review process helps maintain the quality of the `master` branch by ensuring that only well-tested and reviewed code is merged into it. By having another developer review the changes, potential issues such as bugs, security vulnerabilities, or code that does not adhere to best practices can be identified and corrected before the code is integrated. This process acts as a gatekeeper, preventing problematic code from reaching the `master` branch, thereby maintaining its stability and reliability.

**Q3. Describe the steps involved in creating and approving a pull request in Git.**

To create and approve a pull request in Git, follow these steps:

1. **Develop the Feature**: Work on your feature branch and complete the necessary changes.
2. **Test Locally**: Ensure that the changes work correctly by testing them locally.
3. **Commit Changes**: Commit the changes to your feature branch.
4. **Push to Remote Repository**: Push the feature branch to the remote repository.
5. **Create Pull Request**: Navigate to the remote repository and create a pull request from your feature branch to the target branch (usually `master`).
6. **Assign Reviewer**: Assign a reviewer who has expertise in the area of the changes or leave it unassigned if any team member can review.
7. **Review Changes**: The assigned reviewer will check the changes, look at the commits, and provide feedback through comments.
8. **Approve or Reject**: Based on the review, the reviewer can either approve the pull request or reject it with suggestions for improvement.
9. **Merge Changes**: Once approved, the changes can be merged into the target branch (`master`).

**Q4. Why is it important to keep the `master` branch in a deployable state?**

Keeping the `master` branch in a deployable state is crucial because it ensures that the codebase is always ready for deployment to production. This means that the `master` branch should contain only tested and validated code, free from bugs and unfinished features. By maintaining this state, teams can quickly respond to emergencies or release updates without worrying about the stability and functionality of the code. This practice also supports continuous integration and delivery (CI/CD) processes, allowing for frequent and reliable deployments.

**Q5. How does code review contribute to the growth and learning of developers within a team?**

Code review contributes to the growth and learning of developers within a team by providing opportunities for knowledge sharing and feedback. When a more experienced developer reviews the code of a less experienced one, they can offer insights, suggest improvements, and highlight best practices. This interaction helps the junior developer understand common pitfalls and learn from the expertise of others. Additionally, code review encourages developers to communicate and collaborate effectively, fostering a culture of continuous learning and improvement.

**Q6. What happens if a pull request is rejected during the review process?**

If a pull request is rejected during the review process, the developer who created the pull request needs to address the feedback provided by the reviewer. This typically involves making the suggested changes, fixing any issues identified, and then re-submitting the pull request for further review. The cycle of review and revision continues until the code meets the required standards and is approved for merging into the `master` branch. This iterative process ensures that the final code is of high quality and aligns with the project’s goals and standards.

**Q7. Discuss recent real-world examples where a lack of proper code review led to significant issues.**

One notable example is the 2019 Capital One data breach, where a misconfigured web application firewall allowed unauthorized access to sensitive customer data. Although this incident was primarily due to configuration errors rather than code review failures, it highlights the importance of thorough review processes. Another example is the 2018 Equifax data breach, where a vulnerability in Apache Struts was exploited due to outdated software. While not directly related to code review, these incidents underscore the broader need for rigorous testing and review practices to prevent security breaches and other critical issues.

---
<!-- nav -->
[[05-Screenshots|Screenshots]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/05-Code Review Practices With Git Pull Requests/00-Overview|Overview]]
