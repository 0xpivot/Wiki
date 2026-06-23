---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Git Reset

In the realm of version control systems, Git stands out as a powerful tool that enables developers to manage changes to their codebase efficiently. One of the essential operations in Git is the ability to revert local commits, which can be achieved through the `git reset` command. This chapter will delve deep into the mechanics of `git reset`, explaining how it works, why it is necessary, and how to use it effectively. We will cover various scenarios, provide detailed examples, and discuss potential pitfalls and how to avoid them.

### What is `git reset`?

The `git reset` command is used to move the HEAD pointer to a specified commit. Depending on the options used, it can also modify the index (staging area) and working directory. The primary purpose of `git reset` is to undo changes that have been committed locally but not yet pushed to a remote repository.

#### Why Use `git reset`?

There are several reasons why you might want to use `git reset`:

1. **Undoing Local Changes**: If you realize that your latest commit(s) contain errors or are not needed, you can use `git reset` to revert those changes.
2. **Preparing for a Clean Commit History**: Sometimes, you may want to clean up your commit history before pushing changes to a remote repository. `git reset` allows you to do this by removing unnecessary commits.
3. **Reverting to a Previous State**: If you want to revert your project to a previous state, `git reset` provides a way to do this.

### How `git reset` Works

The `git reset` command operates based on the following parameters:

- **HEAD**: The current commit that the branch points to.
- **Commit Hash**: A unique identifier for each commit.
- **Options**: Different options (`--soft`, `--mixed`, `--hard`) determine how much of the commit is undone.

#### Options Explained

1. **`--soft`**:
   - Moves the HEAD pointer to the specified commit.
   - Keeps the changes in the staging area.
   - Useful when you want to keep the changes but create a new commit.

2. **`--mixed`** (default):
   - Moves the HEAD pointer to the specified commit.
   - Resets the staging area to match the specified commit.
   - Leaves the working directory unchanged.
   - Useful when you want to unstage changes but keep them in the working directory.

3. **`--hard`**:
   - Moves the HEAD pointer to the specified commit.
   - Resets both the staging area and the working directory to match the specified commit.
   - Discards all changes in the working directory.
   - Useful when you want to completely revert to a previous state.

### Example Scenario

Let's consider a scenario where you have made some changes to your code and committed them locally. You then realize that these changes were incorrect and need to be reverted.

#### Initial Setup

Assume you have a simple project with a file named `index.js`. Here is an initial version of the file:

```javascript
// index.js
console.log("Initial code");
```

You make some changes to this file:

```javascript
// index.js
console.log("Initial code");
console.log("Additional log line");
```

You then stage and commit these changes:

```bash
$ git add .
$ git commit -m "Add additional log line"
```

At this point, your Git log might look like this:

```bash
$ git log --oneline
c012345 Add additional log line
b012345 Initial commit
```

### Reverting the Last Commit

To revert the last commit, you can use the `git reset` command with the `--hard` option. This will move the HEAD pointer to the previous commit and discard all changes in the working directory.

#### Step-by-Step Process

1. **Identify the Commit to Reset To**:
   - Use `git log` to find the commit hash of the commit you want to reset to.
   - In our case, we want to reset to the commit before `c012345`.

2. **Reset the Commit**:
   - Use the `git reset --hard` command followed by the commit hash or `HEAD~1` to reset to the previous commit.

```bash
$ git reset --hard HEAD~1
```

After executing this command, your Git log will look like this:

```bash
$ git log --oneline
b012345 Initial commit
```

And your `index.js` file will revert to its original state:

```javascript
// index.js
console.log("Initial code");
```

### Detailed Explanation of `git reset --hard`

When you run `git reset --hard HEAD~1`, the following happens:

1. **Move HEAD Pointer**: The HEAD pointer is moved to the commit specified by `HEAD~1`.
2. **Reset Staging Area**: The staging area is reset to match the contents of the specified commit.
3. **Reset Working Directory**: The working directory is reset to match the contents of the specified commit.
4. **Discard Changes**: Any changes in the working directory that were not part of the specified commit are discarded.

### Potential Pitfalls and How to Avoid Them

#### Losing Uncommitted Changes

One of the most significant risks of using `git reset --hard` is losing uncommitted changes. If you have made changes to your files that are not yet committed, using `git reset --hard` will discard these changes permanently.

**How to Prevent / Defend**:

1. **Backup Your Work**: Before running `git reset --hard`, ensure that you have a backup of your work. You can do this by creating a branch or copying your files to another location.
2. **Use `git stash`**: If you have uncommitted changes that you want to keep, use `git stash` to save them temporarily. After running `git reset --hard`, you can apply the stashed changes using `git stash pop`.

Example:

```bash
$ git stash
$ git reset --hard HEAD~1
$ git stash pop
```

#### Accidentally Resetting to the Wrong Commit

Another risk is accidentally resetting to the wrong commit. If you specify the wrong commit hash or use the wrong number of commits to reset, you may end up in an unintended state.

**How to Prevent / Defend**:

1. **Double-Check Commit Hashes**: Always double-check the commit hashes before running `git reset --hard`.
2. **Use `git reflog`**: The `git reflog` command shows a log of all actions performed in the repository, including resets. This can help you recover from accidental resets.

Example:

```bash
$ git reflog
$ git reset --hard <commit-hash>
```

### Real-World Examples and Recent Breaches

While `git reset` itself is not directly related to security breaches, improper use of Git commands can lead to data loss or exposure of sensitive information. For example, if a developer accidentally resets to a commit that contains sensitive data and pushes that commit to a remote repository, it could result in a data breach.

**Recent Example**: In 2021, a developer accidentally committed and pushed a file containing API keys to a public GitHub repository. While this was not due to `git reset`, it highlights the importance of being cautious when using Git commands.

### Conclusion

The `git reset` command is a powerful tool for managing changes in your Git repository. By understanding how it works and using it carefully, you can effectively revert local commits and maintain a clean commit history. Always be mindful of the potential risks and take steps to prevent data loss or exposure.

### Practice Labs

For hands-on practice with `git reset`, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on Git and version control.
- **OWASP Juice Shop**: Provides a web application with various security challenges, including Git-related tasks.

These labs will help you gain practical experience with `git reset` and other Git commands.

### Summary

In this chapter, we covered the `git reset` command in detail, explaining its purpose, how it works, and how to use it effectively. We provided real-world examples, detailed explanations, and practical advice on how to prevent common pitfalls. By mastering `git reset`, you can become more proficient in managing your Git repositories and maintaining a clean commit history.

---
<!-- nav -->
[[02-Introduction to Git Reset and Reverting Local Commits|Introduction to Git Reset and Reverting Local Commits]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/12-Reverting Local Commits Using Git Reset/00-Overview|Overview]] | [[04-Understanding Git Reset and Revert|Understanding Git Reset and Revert]]
