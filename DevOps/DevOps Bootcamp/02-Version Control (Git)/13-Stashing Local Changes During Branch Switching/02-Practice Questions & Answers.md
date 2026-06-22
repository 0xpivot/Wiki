---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using `git stash` during branch switching.**

The purpose of using `git stash` during branch switching is to temporarily save local changes that haven't been committed yet. This allows developers to switch branches without having to commit unfinished work or lose local modifications. By stashing changes, developers can easily return to their work-in-progress after performing tasks on other branches.

**Q2. How would you use `git stash` to temporarily hide local changes while switching to another branch?**

To temporarily hide local changes while switching to another branch, follow these steps:

1. Use `git stash` to save your current changes.
   ```bash
   git stash
   ```
2. Verify that the changes are hidden by checking the status.
   ```bash
   git status
   ```
3. Switch to the desired branch.
   ```bash
   git checkout <branch-name>
   ```

**Q3. Explain how to retrieve stashed changes after switching back to the original branch.**

To retrieve stashed changes after switching back to the original branch, use the following command:

```bash
git stash pop
```

This command applies the most recent stash to your working directory and removes it from the stash list. If you want to keep the stash in the list after applying it, use `git stash apply`.

**Q4. Describe a scenario where stashing changes might be particularly useful.**

A common scenario where stashing changes is particularly useful is when a developer is working on a feature branch and needs to quickly switch to another branch to address an urgent issue or review some code. For example, if a developer is fixing a bug in a feature branch and encounters an issue that requires checking the master branch, they can stash their current changes, switch to the master branch, resolve the issue, and then return to the feature branch to unstash their changes and continue working.

**Q5. How can `git stash` help in debugging a feature that stopped working after making changes?**

`git stash` can help in debugging a feature that stopped working after making changes by allowing the developer to temporarily hide their recent changes and test the application in its previous state. Here’s how:

1. Use `git stash` to hide the recent changes.
   ```bash
   git stash
   ```
2. Test the application to see if the feature was working before the changes were made.
3. If the feature works without the changes, the issue likely lies within the recent changes.
4. Retrieve the stashed changes using `git stash pop`.
   ```bash
   git stash pop
   ```

This approach helps isolate whether the recent changes are causing the issue, enabling targeted debugging efforts.

**Q6. What happens if you have multiple stashes and want to apply a specific one?**

If you have multiple stashes and want to apply a specific one, you can use the `git stash apply` command with the stash ID. The stash IDs are listed when you run `git stash list`. For example, if you want to apply the second most recent stash, you can use:

```bash
git stash apply stash@{1}
```

This command applies the specified stash to your working directory without removing it from the stash list. If you want to remove the stash after applying it, use `git stash pop` instead.

---
<!-- nav -->
[[01-Introduction to Stashing Local Changes During Branch Switching|Introduction to Stashing Local Changes During Branch Switching]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/13-Stashing Local Changes During Branch Switching/00-Overview|Overview]]
