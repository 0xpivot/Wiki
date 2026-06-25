---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Local to Remote Git Workflow

In the context of DevOps, managing code repositories is a fundamental task. Often, developers start working on a project locally, creating and modifying files on their local machine. At some point, they may decide to host their code on a remote Git repository such as GitHub, GitLab, or Bitbucket. This process involves transforming a local directory into a Git repository and then pushing the changes to a remote server. This chapter will cover the entire workflow, including the necessary steps, potential pitfalls, and best practices.

### Background Theory

Git is a distributed version control system designed to handle everything from small to very large projects with speed and efficiency. It was created by Linus Torvalds in 2005 for the development of the Linux kernel. Git stores snapshots of the project's state rather than differences between files, which makes it efficient and fast.

A Git repository consists of three main components:

1. **Working Directory**: This is where you modify files.
2. **Staging Area**: This is where you prepare a snapshot of the project to commit.
3. **Repository Data**: This is where Git stores metadata and object database.

When you initialize a Git repository (`git init`), Git creates a `.git` directory in your project root. This directory contains all the necessary files and folders to manage the repository.

### Creating a Local Git Repository

Let's assume you have a local project that is not yet a Git repository. You can transform it into a Git repository using the `git init` command.

#### Step-by-Step Process

1. **Navigate to Your Project Directory**:
    ```sh
    cd path/to/your/project
    ```

2. **Initialize the Git Repository**:
    ```sh
    git init
    ```

This command creates a `.git` directory in your project root, initializing the repository.

#### Example

Suppose you have a Node.js project with the following structure:
```
my-node-project/
├── index.js
├── package.json
└── README.md
```

To initialize a Git repository in this project:
```sh
cd my-node-project
git init
```

After running `git init`, you should see a new `.git` directory in your project:
```sh
ls -a
# .  ..  .git  index.js  package.json  README.md
```

### Adding Files to the Staging Area

Once the repository is initialized, you can start tracking changes to your files. The first step is to add files to the staging area using the `git add` command.

#### Step-by-Step Process

1. **Add All Files to the Staging Area**:
    ```sh
    git add .
    ```

This command stages all files in the current directory and its subdirectories.

2. **Check the Status of the Repository**:
    ```sh
    git status
    ```

This command shows the current state of the repository, indicating which files are staged and ready to be committed.

#### Example

Continuing with our Node.js project:
```sh
git add .
git status
```

The output might look like this:
```sh
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   index.js
	new file:   package.json
	new file:   README.md
```

### Committing Changes

After staging the files, you can commit them to the repository using the `git commit` command.

#### Step-by-Step Process

1. **Commit the Staged Files**:
    ```sh
    git commit -m "Initial commit"
    ```

This command creates a new commit with the specified message.

#### Example

Continuing with our Node.js project:
```sh
git commit -m "Initial commit"
```

The output might look like this:
```sh
[master (root-commit) 1234567] Initial commit
 3 files changed, 10 insertions(+)
 create mode 100644 index.js
 create mode 100644 package.json
 create mode 100644 README.md
```

### Pushing to a Remote Repository

Once your local repository is set up and committed, you can push the changes to a remote repository.

#### Step-by-Step Process

1. **Create a Remote Repository**:
    - Go to GitHub, GitLab, or Bitbucket and create a new repository.
    - Note the URL of the newly created repository.

2. **Add the Remote Repository**:
    ```sh
    git remote add origin https://github.com/username/repository.git
    ```

3. **Push the Local Commits to the Remote Repository**:
    ```sh
    git push -u origin master
    ```

#### Example

Suppose you have created a new repository on GitHub with the URL `https://github.com/username/my-node-project.git`.

To add the remote repository and push the changes:
```sh
git remote add origin https://github.com/username/my-node-project.git
git push -u origin master
```

The output might look like this:
```sh
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 4 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (5/5), 442 bytes | 442.00 KiB/s, done.
Total 5 (delta 0), reused 0 (delta 0)
remote: Resolving deltas: 100% (0/0), done.
To https://github.com/username/my-node-project.git
 * [new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

### Mermaid Diagrams

Here is a mermaid diagram illustrating the workflow:

```mermaid
graph TD
    A[Local Project] --> B[git init]
    B --> C[git add .]
    C --> D[git commit -m "Initial commit"]
    D --> E[Create Remote Repository]
    E --> F[git remote add origin <URL>]
    F --> G[git push -u origin master]
```

### Potential Pitfalls and Best Practices

#### Common Mistakes

1. **Forgetting to Stage Files**:
    - Ensure you stage all files before committing.
    - Use `git add .` to stage all files or `git add <filename>` to stage specific files.

2. **Incorrect Remote URL**:
    - Double-check the remote URL to ensure it points to the correct repository.

3. **Untracked Files**:
    - Use `git status` to check for untracked files and ensure they are either added or ignored.

#### Best Practices

1. **Use `.gitignore`**:
    - Create a `.gitignore` file to specify files and directories that should be ignored by Git.
    - Example `.gitignore`:
        ```plaintext
        node_modules/
        .env
        ```

2. **Regular Commits**:
    - Make regular commits to keep your history clean and meaningful.
    - Use descriptive commit messages to explain the changes.

3. **Branch Management**:
    - Use branches for feature development and merge them back to the main branch once complete.
    - Example:
        ```sh
        git checkout -b feature/new-feature
        # Develop and commit changes
        git checkout master
        git merge feature/new-feature
        ```

### Real-World Examples

#### Recent Breaches and CVEs

While the process of pushing local code to a remote Git repository is generally secure, there have been instances where sensitive information was accidentally committed and pushed to public repositories. For example:

- **CVE-2020-14882**: This vulnerability involved the accidental exposure of AWS access keys in a public GitHub repository. The keys were used to gain unauthorized access to AWS resources.

- **GitHub Data Exposure Incident (2021)**: In this incident, several users accidentally committed sensitive data such as API keys and credentials to public repositories, leading to potential security risks.

### How to Prevent / Defend

#### Detection

1. **Pre-commit Hooks**:
    - Use pre-commit hooks to automatically check for sensitive information before committing.
    - Example hook script:
        ```sh
        #!/bin/sh
        grep -q 'AWS_ACCESS_KEY_ID' $(git diff --cached --name-only)
        if [ $? -eq 0 ]; then
            echo "Sensitive information detected! Aborting commit."
            exit 1
        fi
        ```

2. **Static Analysis Tools**:
    - Use static analysis tools like `git-secrets` to scan for sensitive information in your codebase.
    - Example usage:
        ```sh
        git secrets --register-aws
        git secrets --scan
        ```

#### Prevention

1. **Secure Coding Practices**:
    - Avoid committing sensitive information such as API keys, passwords, and credentials to version control systems.
    - Use environment variables or configuration management tools to store sensitive data securely.

2. **Configuration Hardening**:
    - Configure your Git settings to enforce strict policies, such as requiring signed commits.
    - Example configuration:
        ```sh
        git config --global user.signingkey <your-GPG-key-id>
        git config --global commit.gpgsign true
        ```

#### Secure-Coding Fixes

##### Vulnerable Code Example

Suppose you accidentally committed an AWS access key to your repository:
```sh
echo "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE" > .env
git add .env
git commit -m "Add environment variables"
```

##### Corrected Secure Version

To prevent this, you should use environment variables or a configuration management tool:
```sh
# .env.example
export AWS_ACCESS_KEY_ID=

# .gitignore
.env
```

### Complete Example

#### Full HTTP Request and Response

When pushing to a remote repository, Git uses HTTP(S) to communicate with the server. Here is an example of the HTTP request and response:

**HTTP Request**:
```http
POST /repos/username/repository/git/commits HTTP/1.1
Host: github.com
Authorization: token <your-access-token>
Content-Type: application/json

{
  "message": "Initial commit",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "committer": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "tree": {
    "sha": "1234567890abcdef1234567890abcdef12345678"
  }
}
```

**HTTP Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "commit": {
    "url": "https://api.github.com/repos/username/repository/commits/1234567890abcdef1234567890abcdef12345678",
    "sha": "1234567890abcdef1234567890abcdef12345678",
    "html_url": "https://github.com/username/repository/commit/1234567890abcdef1234567890abcdef12345678",
    "author": {
      "name": "Your Name",
      "email": "you@example.com",
      "date": "2023-01-01T00:00:00Z"
    },
    "committer": {
      "name": "Your Name",
      "email": "you@example.com",
      "date": "2023-01-01T00:00:00Z"
    },
    "message": "Initial commit",
    "tree": {
      "url": "https://api.github.com/repos/username/repository/git/trees/1234567890abcdef1234567890abcdef12345678",
      "sha": "1234567890abcdef1234567890abcdef12345678"
    },
    "parents": []
  }
}
```

### Practice Labs

To practice these concepts, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified web security training application.

These labs provide a safe environment to practice and learn about various aspects of DevOps and web application security.

By following these steps and best practices, you can effectively manage your local and remote Git repositories, ensuring that your code is version-controlled and secure.

---
<!-- nav -->
[[02-Introduction to Git and Remote Repositories|Introduction to Git and Remote Repositories]] | [[DevOps/DevOps Bootcamp/02-Version Control (Git)/11-Pushing Local Code to Remote Git Repository/00-Overview|Overview]] | [[04-Understanding Git Repositories and Remote Connections|Understanding Git Repositories and Remote Connections]]
