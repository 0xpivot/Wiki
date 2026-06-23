---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the three stages of a file's status in Git and provide an example of how you would move a file from one stage to another.**

The three stages of a file's status in Git are:

1. **Untracked**: The file exists in the working directory but is not being tracked by Git. For example, a newly created file.
2. **Staged**: The file has been added to the staging area, indicating that the changes are ready to be committed. For example, after running `git add <file>`.
3. **Committed**: The changes have been committed to the local repository. For example, after running `git commit`.

To move a file from untracked to staged, you would run `git add <file>`. To move it from staged to committed, you would run `git commit -m "Commit message"`.

**Q2. How would you determine the current status of your local Git repository, including which branch you are on and what changes are pending?**

To determine the current status of your local Git repository, including which branch you are on and what changes are pending, you would use the `git status` command. This command provides detailed information about the current state of the repository, including:

- Which branch you are currently on.
- Files that have been modified but not yet staged.
- Files that have been staged but not yet committed.
- Any untracked files.

For example, running `git status` might show:

```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        new_file.txt
```

**Q3. Why is it important to use the `git status` command regularly when working on a project over multiple days?**

Using the `git status` command regularly is important because it helps you keep track of the changes you have made in your local repository. When working on a project over multiple days, you might forget what changes you have made since your last session. Running `git status` allows you to:

- See which branch you are currently on.
- Identify any untracked files that you may have forgotten about.
- Determine which changes are staged and ready to be committed.
- Check if there are any changes that you have not yet committed.

This ensures that you stay organized and aware of the state of your project, making it easier to manage and collaborate with others.

**Q4. How would you selectively add only certain files to the staging area while leaving others untracked?**

To selectively add only certain files to the staging area while leaving others untracked, you would use the `git add` command followed by the specific file names. For example, if you have multiple files and you only want to add `file1.txt` and `file2.txt` to the staging area, you would run:

```bash
git add file1.txt file2.txt
```

This will add only these specified files to the staging area, leaving any other files untracked. You can verify this by running `git status`, which will show the selected files as staged and the rest as untracked.

**Q5. Explain the purpose of the `git commit` command and describe how you would use it to commit changes to your local repository.**

The `git commit` command is used to save the changes that have been staged to the local repository. When you commit changes, you create a snapshot of the current state of the repository at that point in time. This is essential for version control and allows you to revert to previous states if needed.

To use `git commit`, you first need to ensure that the changes you want to commit are staged using `git add`. Then, you can run `git commit` with a commit message describing the changes. For example:

```bash
git commit -m "Add new feature X"
```

This command commits the staged changes and adds a descriptive message to the commit log. After committing, you can push the changes to a remote repository using `git push`.

**Q6. How does the `git log` command help you understand the history of changes in your local repository?**

The `git log` command displays the commit history of the local repository, showing details about each commit such as the author, the commit message, and the date and time of the commit. This helps you understand the sequence of changes made to the project and who made them.

For example, running `git log` might produce output similar to:

```
commit 1234567890abcdef1234567890abcdef12345678
Author: John Doe <john.doe@example.com>
Date:   Mon Jan 1 12:00:00 2023 +0000

    Add new feature X

commit 876543210fedcba1234567890abcdef12345678
Author: Jane Smith <jane.smith@example.com>
Date:   Sun Dec 31 11:00:00 2022 +0000

    Fix bug Y
```

This output shows the commit history, allowing you to trace the evolution of the project and identify specific changes made at different points in time.

---
<!-- nav -->
[[01-Understanding Git File Status Stages|Understanding Git File Status Stages]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/15-Understanding Git File Status Stages/00-Overview|Overview]]
