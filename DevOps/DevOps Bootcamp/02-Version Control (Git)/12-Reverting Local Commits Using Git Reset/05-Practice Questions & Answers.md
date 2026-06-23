---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. How do you use `git reset` to revert the last commit locally without discarding the changes?**

To revert the last commit locally without discarding the changes, you can use `git reset --soft HEAD~1`. This command will keep the changes in your working directory while removing the last commit from the history. Here’s how you can do it:

```bash
git reset --soft HEAD~1
```

After executing this command, you can modify the changes as needed and then commit them again.

**Q2. Explain the difference between `git reset --hard` and `git reset --soft`.**

`git reset --hard` moves the branch pointer to the specified commit and updates the working directory to match that commit. Any changes or uncommitted work since that commit will be lost.

```bash
git reset --hard HEAD~1
```

`git reset --soft`, on the other hand, moves the branch pointer to the specified commit but keeps the changes staged in the index. This allows you to modify the changes and commit them again.

```bash
git reset --soft HEAD~1
```

**Q3. How can you amend the last commit with additional changes?**

To amend the last commit with additional changes, you first need to stage the new changes and then use `git commit --amend`.

```bash
# Stage the new changes
git add .

# Amend the last commit
git commit --amend
```

This will open an editor where you can modify the commit message if needed. Once you save and close the editor, the changes will be included in the last commit.

**Q4. What is the purpose of `git revert` and how does it differ from `git reset`?**

`git revert` is used to create a new commit that undoes the changes introduced by a specified commit. Unlike `git reset`, which changes the history, `git revert` preserves the original commit and adds a new commit that reverses the changes.

To use `git revert`, you need the commit hash of the commit you want to revert:

```bash
git revert <commit-hash>
```

For example, if the commit hash is `abc123`, you would run:

```bash
git revert abc123
```

This will create a new commit that undoes the changes made in the specified commit.

**Q5. Why is it dangerous to use `git push --force` on shared branches like `master` or `develop`?**

Using `git push --force` on shared branches like `master` or `develop` can be dangerous because it overwrites the remote branch with the local branch, potentially causing conflicts for other developers who have pulled the old commits. If multiple developers have based their work on the old commits, forcing a push can lead to issues such as merge conflicts and broken builds.

For example, if Developer A pushes a commit to `master`, and Developer B pulls that commit, then Developer A uses `git push --force` to remove that commit, Developer B’s local branch will be out of sync with the remote branch. When Developer B tries to push their changes, Git will complain about the missing reference and the history being messed up.

**Q6. How would you safely undo a commit that has already been pushed to a remote repository?**

To safely undo a commit that has already been pushed to a remote repository, you can use `git revert`. This approach creates a new commit that reverses the changes of the original commit, preserving the history and avoiding conflicts with other developers.

First, identify the commit hash of the commit you want to revert:

```bash
git log
```

Then, use `git revert` with the commit hash:

```bash
git revert <commit-hash>
```

Finally, push the new revert commit to the remote repository:

```bash
git push origin <branch-name>
```

This method ensures that the history remains intact and other developers can continue working without issues.

---
<!-- nav -->
[[04-Understanding Git Reset and Revert|Understanding Git Reset and Revert]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/12-Reverting Local Commits Using Git Reset/00-Overview|Overview]]
