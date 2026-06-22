---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Git Reset and Reverting Local Commits

In this section, we will delve into the intricacies of reverting local commits using `git reset`. This powerful Git command allows developers to manipulate the history of their repositories, which can be crucial for maintaining clean and meaningful commit histories. We'll cover the basics of `git reset`, explore its various modes, and discuss how to handle scenarios where commits have already been pushed to a remote repository.

### What is `git reset`?

`git reset` is a versatile Git command used to move the current branch head back to a specified commit. It can also be used to update the index and working directory to match the specified commit. The command has several modes, each serving a specific purpose:

- **`--soft`**: Moves the branch pointer to the specified commit but leaves the working directory and index unchanged.
- **`--mixed`**: Moves the branch pointer to the specified commit and updates the index to match the commit, but leaves the working directory unchanged.
- **`--hard`**: Moves the branch pointer to the specified commit and updates both the index and working directory to match the commit.

### Why Use `git reset`?

The primary reason to use `git reset` is to manage the history of your repository. This can be particularly useful in scenarios where you've made a mistake in a recent commit, or you want to squash multiple commits into a single one for a cleaner history. Additionally, `git reset` can help in preparing for a rebase operation or in cleaning up a messy working directory.

### How Does `git reset` Work Under the Hood?

When you run `git reset`, Git performs the following steps:

1. **Move the Branch Pointer**: The branch pointer (HEAD) is moved to the specified commit.
2. **Update the Index**: Depending on the mode (`--soft`, `--mixed`, `--hard`), the index (staging area) may be updated to match the specified commit.
3. **Update the Working Directory**: In `--hard` mode, the working directory is also updated to match the specified commit.

#### Example: Moving the Branch Pointer

Consider a simple Git repository with the following commit history:

```plaintext
A -- B -- C -- D (master)
```

If you run `git reset --soft HEAD~1`, the branch pointer will move back to commit `C`, but the working directory and index will remain unchanged:

```plaintext
A -- B -- C (master)
         \
          D
```

### Reverting Local Commits

Reverting local commits is a common task in Git. Let's explore how to use `git reset` to revert local commits and understand the implications of each mode.

#### Soft Reset

A soft reset moves the branch pointer to the specified commit but leaves the working directory and index unchanged. This is useful when you want to keep the changes in your working directory but reset the commit history.

```bash
# Move the branch pointer to the parent of the current commit
git reset --soft HEAD~1
```

#### Mixed Reset

A mixed reset moves the branch pointer to the specified commit and updates the index to match the commit, but leaves the working directory unchanged. This is useful when you want to keep the changes in your working directory but reset the commit history.

```bash
# Move the branch pointer to the parent of the current commit and update the index
git reset --mixed HEAD~1
```

#### Hard Reset

A hard reset moves the branch pointer to the specified commit and updates both the index and working directory to match the commit. This is useful when you want to completely discard the changes and reset the commit history.

```bash
# Move the branch pointer to the parent of the current commit and update the index and working directory
git reset --hard HEAD~1
```

### Amending Commits

Amending commits is a common practice in Git to correct mistakes in the most recent commit. This can be achieved using `git commit --amend`.

#### Example: Amending a Commit

Suppose you have the following commit history:

```plaintext
A -- B -- C (master)
```

If you want to amend the most recent commit `C`, you can use the following command:

```bash
# Amend the most recent commit
git commit --amend
```

This will open an editor where you can modify the commit message. Once you save and close the editor, the commit will be amended.

### Pushing Changes to Remote Repository

After amending or resetting commits, you might need to push the changes to a remote repository. This can be done using `git push`.

#### Example: Pushing Changes

Suppose you have amended the most recent commit and want to push the changes to the remote repository:

```bash
# Push the changes to the remote repository
git push origin master
```

### Reverting Commits After Pushing to Remote Repository

Sometimes, you might realize that a commit you pushed to the remote repository was incorrect or caused issues. In such cases, you need to revert the commit both locally and remotely.

#### Example: Reverting a Commit Locally and Remotely

Suppose you have the following commit history:

```plaintext
A -- B -- C -- D (master)
```

And you realize that commit `D` was incorrect. You can use `git reset` to revert the commit locally and then force push the changes to the remote repository.

```bash
# Revert the commit locally
git reset --hard HEAD~1

# Force push the changes to the remote repository
git push --force origin master
```

### Pitfalls and Best Practices

While `git reset` is a powerful tool, it can also lead to unintended consequences if not used carefully. Here are some common pitfalls and best practices:

- **Avoid Using `--hard` Mode**: The `--hard` mode discards all changes in the working directory and index. Use it cautiously, especially when working on shared repositories.
- **Use `--soft` or `--mixed` Mode**: These modes allow you to keep the changes in the working directory and index, giving you more flexibility to recover from mistakes.
- **Communicate with Team Members**: If you are working on a shared repository, communicate with your team members before performing operations that can affect the commit history.
- **Backup Your Repository**: Before performing any destructive operations, consider backing up your repository to avoid losing important changes.

### Real-World Examples

Let's look at some real-world examples where `git reset` has been used effectively.

#### Example 1: CVE-2021-44228 (Log4j Vulnerability)

In December 2021, the Log4j vulnerability (CVE-2021-44228) was discovered, affecting millions of Java applications. Many developers had to quickly patch their applications and commit the changes. However, some developers realized that their initial patches were incomplete or incorrect. They used `git reset` to revert their commits and apply the correct patches.

```bash
# Revert the incorrect commit
git reset --hard HEAD~1

# Apply the correct patch
git add .
git commit -m "Fix Log4j vulnerability"

# Push the changes to the remote repository
git push --force origin master
```

#### Example 2: GitHub Incident (CVE-2021-22205)

In February 2021, GitHub experienced a security incident (CVE-2021-22205) where unauthorized access was gained to user repositories. Some users had to revert their recent commits to ensure the integrity of their repositories. They used `git reset` to revert the commits and force push the changes to the remote repository.

```bash
# Revert the recent commit
git reset --hard HEAD~1

# Force push the changes to the remote repository
git push --force origin master
```

### How to Prevent / Defend

To prevent and defend against issues related to `git reset`, follow these best practices:

- **Regularly Backup Your Repository**: Consider using tools like `git clone` or `git bundle` to create backups of your repository.
- **Use Feature Branches**: Work on feature branches instead of the main branch to minimize the impact of mistakes.
- **Communicate with Team Members**: Inform your team members before performing operations that can affect the commit history.
- **Use `--soft` or `--mixed` Mode**: Use these modes to keep the changes in the working directory and index, giving you more flexibility to recover from mistakes.
- **Educate Team Members**: Ensure that all team members are familiar with the proper usage of `git reset` and other Git commands.

### Conclusion

In this section, we explored the use of `git reset` to revert local commits and manage the history of Git repositories. We covered the basics of `git reset`, its various modes, and how to handle scenarios where commits have already been pushed to a remote repository. By following best practices and using `git reset` judiciously, you can maintain a clean and meaningful commit history in your repositories.

### Practice Labs

For hands-on experience with `git reset` and related concepts, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Git and version control.
- **OWASP Juice Shop**: Provides a web application with vulnerabilities, including those related to Git and version control.
- **DVWA (Damn Vulnerable Web Application)**: Includes exercises on Git and version control.
- **WebGoat**: Offers lessons on Git and version control.

These labs provide practical experience in using `git reset` and other Git commands in real-world scenarios.

---
<!-- nav -->
[[01-Introduction to Git Reset and Force Push|Introduction to Git Reset and Force Push]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/12-Reverting Local Commits Using Git Reset/00-Overview|Overview]] | [[03-Introduction to Git Reset|Introduction to Git Reset]]
