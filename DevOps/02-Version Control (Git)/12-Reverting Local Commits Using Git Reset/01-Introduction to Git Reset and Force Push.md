---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Git Reset and Force Push

In this section, we will delve into the process of reverting local commits using `git reset` and the implications of performing a force push (`git push --force`). This is a powerful but potentially dangerous operation that requires a thorough understanding of its mechanics and consequences. We will cover the background theory, step-by-step mechanics, real-world examples, and best practices for preventing misuse.

### Background Theory

Git is a distributed version control system that allows developers to track changes in their codebase. Each commit represents a snapshot of the project at a specific point in time. When working collaboratively, developers often push their changes to a remote repository, which serves as a central hub for all team members.

#### What is `git reset`?

`git reset` is a command used to move the current branch head to a specified commit. Depending on the options used, it can also modify the staging area (index) and the working directory. There are three main modes:

1. **Soft**: Moves the branch head but does not affect the index or working directory.
2. **Mixed** (default): Moves the branch head and updates the index but leaves the working directory unchanged.
3. **Hard**: Moves the branch head, updates the index, and resets the working directory to match the specified commit.

#### What is `git push --force`?

`git push --force` is a command used to overwrite the history of a remote branch. This means that the remote branch will be updated to match the local branch, even if it results in losing commits that were previously pushed.

### Step-by-Step Mechanics

Let's walk through the process of reverting local commits and then pushing those changes to a remote repository using `git push --force`.

#### Scenario Setup

Imagine you have made several commits locally and pushed them to a remote repository. However, you realize that one of these commits was incorrect and needs to be removed. Here’s how you can achieve this:

1. **Identify the Commit to Remove**: First, identify the commit hash of the commit you want to remove. You can use `git log` to view the commit history.

    ```sh
    git log
    ```

2. **Reset to the Desired State**: Use `git reset` to move the branch head to the desired state. For example, if you want to remove the last commit, you can use:

    ```sh
    git reset HEAD~1
    ```

    This command moves the branch head one commit back, effectively removing the last commit from the branch.

3. **Force Push to Remote Repository**: After resetting the local branch, you need to force push the changes to the remote repository. This will overwrite the remote branch history.

    ```sh
    git push --force
    ```

### Real-World Examples

#### Example 1: Removing an Erroneous Commit

Suppose you have a project with the following commit history:

```sh
$ git log --oneline
cdef123 Fix typo in README.md
ab12345 Add new feature
zyx9876 Initial commit
```

You realize that the commit `cdef123` was erroneous and needs to be removed. Here’s how you can do it:

1. **Reset to the Previous Commit**:

    ```sh
    git reset ab12345
    ```

2. **Force Push to Remote Repository**:

    ```sh
    git push --force
    ```

After these steps, the remote repository will no longer contain the commit `cdef123`.

#### Example 2: Overwriting Remote Branch History

Consider a scenario where you have a remote branch `feature-branch` with the following commit history:

```sh
$ git log --oneline origin/feature-branch
cdef123 Fix typo in README.md
ab12345 Add new feature
zyx9876 Initial commit
```

You want to remove the commit `cdef123` and force push the changes to the remote branch. Here’s how you can do it:

1. **Fetch the Latest Changes**:

    ```sh
    git fetch origin
    ```

2. **Checkout the Feature Branch**:

    ```sh
    git checkout feature-branch
    ```

3. **Reset to the Previous Commit**:

    ```sh
    git reset ab12345
    ```

4. **Force Push to Remote Repository**:

    ```sh
    git push --force
    ```

### Pitfalls and Risks

While `git reset` and `git push --force` are powerful tools, they come with significant risks, especially when used in shared branches like `develop` or `master`. Here are some key points to consider:

1. **Impact on Collaborators**: If other developers have pulled the commit you are removing, they will lose their work if they rebase or pull from the remote repository. This can lead to confusion and potential data loss.

2. **History Loss**: Force pushing can result in the loss of commit history, which can be problematic for auditing and tracking purposes.

3. **Conflicts**: If multiple developers are working on the same branch, force pushing can cause conflicts and inconsistencies in the codebase.

### How to Prevent / Defend

To mitigate the risks associated with `git reset` and `git push --force`, follow these best practices:

1. **Use Separate Branches**: Always perform risky operations on separate branches rather than shared branches like `develop` or `master`.

2. **Communicate with Team Members**: Before performing a force push, communicate with your team members to ensure they are aware of the changes and can take appropriate action.

3. **Backup**: Before making any drastic changes, create a backup of the current state of the repository. This can be done by creating a new branch or using a tool like `git clone`.

4. **Use `git reflog`**: If you accidentally remove a commit, you can use `git reflog` to recover it. This command shows the history of all actions performed on the repository, including resets and force pushes.

    ```sh
    git reflog
    ```

5. **Secure Coding Practices**: Ensure that your team follows secure coding practices, such as code reviews and automated testing, to minimize the need for drastic changes.

### Detection and Prevention

#### Detection

To detect unauthorized force pushes, you can set up hooks and monitoring tools. For example, you can use a pre-receive hook to check for force pushes and notify the team.

```sh
#!/bin/sh
# Check for force push
if [ "$GIT_REFLOG_ACTION" = "forced-update" ]; then
  echo "Force push detected!"
  exit 1
fi
```

#### Prevention

To prevent unauthorized force pushes, you can configure your Git server to restrict force pushes to certain users or branches. For example, in a GitLab environment, you can configure branch protection rules to disallow force pushes on critical branches.

### Complete Example

Here is a complete example of reverting a local commit and force pushing to a remote repository:

#### Initial Commit History

```sh
$ git log --oneline
cdef123 Fix typo in README.md
ab12345 Add new feature
zyx9876 Initial commit
```

#### Reset to Previous Commit

```sh
git reset ab12345
```

#### Force Push to Remote Repository

```sh
git push --force
```

#### Full HTTP Request and Response

When you perform a force push, the HTTP request and response look like this:

```http
POST /repos/username/repository/git/refs/heads/feature-branch HTTP/1.1
Host: github.com
Authorization: token YOUR_GITHUB_TOKEN
Content-Type: application/json

{
  "sha": "ab12345",
  "force": true
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "ref": "refs/heads/feature-branch",
  "url": "https://api.github.com/repos/username/repository/git/refs/heads/feature-branch",
  "object": {
    "type": "commit",
    "sha": "ab12345",
    "url": "https://api.github.com/repos/username/repository/git/commits/ab12345"
  }
}
```

### Conclusion

Reverting local commits using `git reset` and force pushing to a remote repository is a powerful but risky operation. By understanding the mechanics, potential pitfalls, and best practices, you can use these tools effectively and safely. Always communicate with your team and follow secure coding practices to minimize the risks.

### Practice Labs

For hands-on practice with these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Git and version control systems.
- **OWASP Juice Shop**: Provides a web application with various vulnerabilities, including those related to Git and version control.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide practical experience in handling Git operations and understanding their implications in a collaborative development environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/02-Version Control (Git)/12-Reverting Local Commits Using Git Reset/00-Overview|Overview]] | [[02-Introduction to Git Reset and Reverting Local Commits|Introduction to Git Reset and Reverting Local Commits]]
