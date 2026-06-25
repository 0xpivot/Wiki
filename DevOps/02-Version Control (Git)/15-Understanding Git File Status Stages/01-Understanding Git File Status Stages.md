---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Git File Status Stages

When working with files in Git, it's crucial to understand the different statuses a file can have and the stages through which changes go. This knowledge helps you manage your code effectively, ensuring that you keep track of modifications and maintain a clean history. In this section, we'll delve into the various stages of changes in Git, their significance, and how to manage them.

### Working Directory

The first stage is the **working directory**. This is where you make changes to your files. When you create a new file or modify an existing one, these changes reside in your working directory until you decide to move them to the next stage.

#### What Is the Working Directory?

The working directory is the local copy of your project where you perform all your edits. It contains the most recent version of your files as you work on them.

#### Why Is the Working Directory Important?

The working directory is essential because it allows you to make changes without immediately affecting the rest of your project. You can experiment, test, and refine your code in this environment before deciding whether to commit these changes.

#### How Does It Work Under the Hood?

When you create or modify a file in your working directory, Git tracks these changes but does not automatically include them in your repository. They remain in your working directory until you explicitly tell Git to stage them.

#### Example: Creating a New File

Let's create a new file called `README.md` and add some content to it:

```bash
echo "This is my new project." > README.md
```

Now, let's check the status of our working directory:

```bash
git status
```

The output might look like this:

```plaintext
On branch main
No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

This indicates that `README.md` is currently in the working directory and has not been staged or committed yet.

### Staging Area

The second stage is the **staging area**. Once you've made changes in your working directory, you can choose to stage these changes. Staging means you're preparing these changes to be committed to your repository.

#### What Is the Staging Area?

The staging area is a temporary holding place for changes you plan to commit. It allows you to selectively choose which changes to include in your next commit.

#### Why Is the Staging Area Important?

The staging area provides flexibility. You can stage only specific changes, allowing you to commit logically grouped changes rather than all changes at once. This helps maintain a clean and meaningful commit history.

#### How Does It Work Under the Hood?

When you stage a file, Git creates a snapshot of the current state of that file and stores it in the staging area. This snapshot is what will be committed when you run `git commit`.

#### Example: Staging a File

To stage the `README.md` file, you can use the following command:

```bash
git add README.md
```

Now, let's check the status again:

```bash
git status
```

The output might look like this:

```plaintext
On branch main
No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

This indicates that `README.md` is now staged and ready to be committed.

### Local Repository

The final stage is the **local repository**. Once you've staged your changes, you can commit them to your local repository. This action records the changes permanently in your project's history.

#### What Is the Local Repository?

The local repository is where all your commits are stored. Each commit represents a snapshot of your project at a particular point in time.

#### Why Is the Local Repository Important?

The local repository serves as a record of your project's history. It allows you to track changes, revert to previous states, and collaborate with others.

#### How Does It Work Under the Hood?

When you commit changes, Git creates a new commit object that references the staged snapshot. This commit object includes metadata such as the author, timestamp, and commit message.

#### Example: Committing Changes

To commit the staged changes, you can use the following command:

```bash
git commit -m "Add README.md"
```

Now, let's check the status again:

```bash
git status
```

The output might look like this:

```plaintext
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

This indicates that all changes have been committed, and your working directory is clean.

### Summary of Stages

Here's a summary of the stages a file goes through in Git:

1. **Working Directory**: Changes are made here.
2. **Staging Area**: Changes are prepared for commit here.
3. **Local Repository**: Changes are recorded here.

### Practical Example: Managing a Project

Let's walk through a practical example of managing a project using Git.

#### Step 1: Initialize a New Repository

First, initialize a new Git repository:

```bash
mkdir my-project
cd my-project
git init
```

#### Step 2: Create and Modify Files

Create a new file and make some changes:

```bash
echo "This is my new project." > README.md
echo "function hello() { console.log('Hello, World!'); }" > index.js
```

#### Step 3: Check the Status

Check the status of your working directory:

```bash
git status
```

Output:

```plaintext
On branch main
No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md
        index.js

nothing added to commit but untracked files present (use "git add" to track)
```

#### Step 4: Stage the Files

Stage the files you want to commit:

```bash
git add README.md
git add index.js
```

#### Step 5: Check the Status Again

Check the status to confirm the files are staged:

```bash
git status
```

Output:

```plaintext
On branch main
No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
        new file:   index.js
```

#### Step 6: Commit the Changes

Commit the staged changes:

```bash
git commit -m "Initial commit"
```

#### Step 7: Check the Status Again

Check the status to confirm the commit:

```bash
git status
```

Output:

```plaintext
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Forgetting to Stage Changes

One common mistake is forgetting to stage changes before committing. This can lead to missing changes in your commit history.

**How to Avoid It**: Always check the status of your working directory before committing. Use `git status` to ensure all changes are staged.

#### Pitfall 2: Committing Too Many Changes at Once

Another pitfall is committing too many unrelated changes at once. This can make it difficult to track changes and revert to previous states.

**How to Avoid It**: Use the staging area to selectively stage changes. Commit small, logical groups of changes to maintain a clean commit history.

### Real-World Examples

#### Example 1: CVE-2021-22205

In 2021, a vulnerability was discovered in GitLab that allowed unauthorized access to repositories. This vulnerability highlights the importance of maintaining a clean and secure commit history.

**Impact**: Unauthorized users could access sensitive information in repositories.

**Prevention**: Ensure that all commits are properly reviewed and that access controls are in place.

#### Example 2: GitHub Data Breach

In 2020, a data breach occurred on GitHub, exposing user credentials. This incident underscores the importance of securing your Git repositories.

**Impact**: User credentials were exposed, leading to potential unauthorized access.

**Prevention**: Use strong authentication mechanisms and regularly review access controls.

### How to Prevent / Defend

#### Detection

To detect issues in your Git workflow, you can use tools like:

- **Git hooks**: Scripts that run automatically during certain events (e.g., pre-commit hooks).
- **Static analysis tools**: Tools that analyze your code for potential issues (e.g., ESLint).

#### Prevention

To prevent issues, follow these best practices:

- **Regularly review your commit history**: Ensure that all commits are meaningful and well-documented.
- **Use access controls**: Limit access to repositories based on roles and responsibilities.
- **Secure your environment**: Use strong authentication mechanisms and regularly update your systems.

#### Secure Coding Fixes

Here's an example of a vulnerable commit and its secure counterpart:

**Vulnerable Commit**

```bash
git commit -m "Fix bug in login page"
```

**Secure Commit**

```bash
git commit -m "Fix bug in login page: Add input validation"
```

By providing a detailed commit message, you make it easier to track changes and understand the context of each commit.

### Conclusion

Understanding the different stages of changes in Git is crucial for effective version control. By mastering the working directory, staging area, and local repository, you can manage your code more efficiently and maintain a clean commit history. Regularly reviewing your workflow and using tools to detect and prevent issues will help you stay secure and productive.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers Git basics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including Git usage.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing security skills, including Git management.

These labs provide real-world scenarios to apply your knowledge of Git and version control.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/02-Version Control (Git)/15-Understanding Git File Status Stages/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/15-Understanding Git File Status Stages/02-Practice Questions & Answers|Practice Questions & Answers]]
