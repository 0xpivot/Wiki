---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the purpose of using commit hashes when debugging a bug in a codebase?**

The purpose of using commit hashes when debugging a bug is to pinpoint the exact state of the code at a specific point in time. By checking out a particular commit using its unique hash, developers can revert the entire codebase to that historical state. This allows them to reproduce the bug in the environment where it originally occurred, making it easier to identify and fix the root cause. For example, if a tester reports that a bug started appearing after a certain commit, developers can check out that commit and analyze the code to understand what changes might have introduced the bug.

**Q2. How can you use Git to go back to a specific commit and test the codebase at that point in time?**

To go back to a specific commit and test the codebase at that point in time, you can use the `git checkout` command followed by the commit hash. For instance, if you have a commit hash `abc123`, you can run:

```bash
git checkout abc123
```

This will place your repository in a "detached HEAD" state, meaning you are no longer on any branch but instead directly on the specified commit. From there, you can test the codebase as it existed at that commit. To return to the latest commit on your branch, simply run:

```bash
git checkout <branch-name>
```

where `<branch-name>` is the name of the branch you wish to return to.

**Q3. Explain the concept of a "detached HEAD" in Git and why it is important when debugging bugs.**

A "detached HEAD" in Git occurs when you check out a specific commit rather than a branch. In this state, the HEAD points directly to a commit rather than to a branch. This is important because it allows you to work with the codebase as it existed at a specific point in time without affecting the current branch. When debugging bugs, a detached HEAD lets you test and inspect the code in the exact state it was in when the bug was introduced, helping you to isolate and resolve issues more effectively.

**Q4. How can you create a new branch from a specific commit while debugging a bug?**

To create a new branch from a specific commit while debugging a bug, first check out the desired commit using its hash:

```bash
git checkout <commit-hash>
```

Once you are in the detached HEAD state, you can create a new branch from that commit:

```bash
git checkout -b <new-branch-name>
```

This creates a new branch named `<new-branch-name>` starting from the commit you checked out. You can then work on this new branch to further investigate and fix the bug.

**Q5. Why is it uncommon to make changes directly in a previous state of the application when debugging?**

It is uncommon to make changes directly in a previous state of the application when debugging because the primary goal is to reproduce and understand the bug, not to modify the codebase in that historical state. Making changes directly in a previous state could lead to confusion and complicate the debugging process. Instead, developers typically use the historical state to diagnose the problem and then apply fixes in the current branch. Once the issue is understood, the necessary changes are made in the active development branch to ensure that the bug is properly addressed in the most recent version of the codebase.

---
<!-- nav -->
[[01-Understanding Git Commit History for Bug Debugging|Understanding Git Commit History for Bug Debugging]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/06-Exploring Git Commit History For Bug Debugging/00-Overview|Overview]]
