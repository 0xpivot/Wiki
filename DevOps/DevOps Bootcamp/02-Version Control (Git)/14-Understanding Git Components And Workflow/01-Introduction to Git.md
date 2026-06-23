---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Git

Git is the most widely-used version control system today, primarily due to its robust features and flexibility. Version control systems (VCS) allow developers to track changes in code over time, collaborate effectively, and maintain a history of modifications. While alternatives like Subversion (SVN) exist, Git has become the de facto standard for modern development projects.

### Why Git?

Git offers several advantages over other VCS:

1. **Distributed Nature**: Unlike centralized systems like SVN, Git is distributed. Each developer has a full copy of the repository, including its entire history. This allows for offline operations and faster performance.
   
2. **Branching and Merging**: Git excels at branching and merging, which are essential for feature development and experimentation. Branches can be created and merged quickly and easily.

3. **Speed**: Git is designed to be fast, especially for large projects. Operations like cloning, committing, and branching are typically very quick.

4. **Data Integrity**: Git uses SHA-1 hashes to ensure data integrity. Every commit and file is checked for corruption, ensuring that the codebase remains consistent.

5. **Flexibility**: Git supports various workflows, from simple linear workflows to complex feature branching strategies.

### Components of Git

To understand Git fully, it's important to grasp its core components and how they interact. The primary components include:

1. **Remote Repository**
2. **Local Repository**
3. **Staging Area**
4. **Git Client**

#### Remote Repository

The remote repository is the central location where the codebase is stored. It serves as the single source of truth for the project. Developers can fetch the latest code from the remote repository and push their changes back to it.

**Purpose**: 
- Central storage for the codebase.
- Collaboration hub for multiple developers.
- Backup and recovery point.

**UI Interaction**:
Most remote repositories come with a user interface (UI) that allows users to interact with the codebase visually. Platforms like GitHub, GitLab, and Bitbucket provide web-based interfaces for managing repositories.

**Example**: GitHub Repository
```markdown
https://github.com/user/repo
```

**Raw HTTP Request Example**:
```http
GET /repos/user/repo HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Accept: application/vnd.github.v3+json
```

**Response**:
```json
{
  "id": 123456,
  "name": "repo",
  "full_name": "user/repo",
  "private": false,
  "owner": {
    "login": "user",
    "id": 12345
  },
  "html_url": "https://github.com/user/repo",
  "clone_url": "https://github.com/user/repo.git"
}
```

#### Local Repository

The local repository is a clone of the remote repository stored on a developer's machine. It contains a full copy of the codebase and its history. Changes are made locally and then pushed to the remote repository.

**Purpose**:
- Local development environment.
- Offline access to the codebase.
- Staging area for changes before pushing to the remote.

**Example**: Cloning a Repository
```bash
git clone https://github.com/user/repo.git
```

**Raw HTTP Request Example**:
```http
GET /repos/user/repo/contents HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Accept: application/vnd.github.v3+json
```

**Response**:
```json
[
  {
    "name": "README.md",
    "path": "README.md",
    "sha": "abc123",
    "size": 123,
    "type": "file",
    "content": "..."
  }
]
```

#### Staging Area

The staging area, also known as the index, is a temporary holding area for changes before they are committed. It allows developers to selectively choose which changes to include in the next commit.

**Purpose**:
- Selective commits.
- Preview changes before committing.
- Preparation for final commit.

**Example**: Adding Files to Staging
```bash
git add .
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/blobs HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "content": "This is the new content.",
  "encoding": "utf-8"
}
```

**Response**:
```json
{
  "content": "This is the new content.",
  "encoding": "utf-8",
  "sha": "def456"
}
```

#### Git Client

The Git client is the tool used to interact with both the local and remote repositories. It can be a command-line interface (CLI) or a graphical user interface (GUI).

**Purpose**:
- Execute Git commands.
- Manage local and remote repositories.
- Provide a user-friendly interface.

**Example**: Command-Line Interface
```bash
git status
```

**Raw HTTP Request Example**:
```http
GET /repos/user/repo/status HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Accept: application/vnd.github.v3+json
```

**Response**:
```json
{
  "branch": "main",
  "ahead_by": 0,
  "behind_by": 0,
  "untracked_files": [],
  "staged_changes": [],
  "unstaged_changes": []
}
```

### Git Workflow

Understanding the workflow is crucial for effective use of Git. The typical workflow includes the following steps:

1. **Clone the Repository**
2. **Create a Branch**
3. **Make Changes**
4. **Stage Changes**
5. **Commit Changes**
6. **Push Changes**
7. **Merge Changes**

#### Clone the Repository

Cloning the repository creates a local copy of the remote repository.

**Command**:
```bash
git clone https://github.com/user/repo.git
```

**Raw HTTP Request Example**:
```http
GET /repos/user/repo/contents HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Accept: application/vnd.github.v3+json
```

**Response**:
```json
[
  {
    "name": "README.md",
    "path": "README.md",
    "sha": "abc123",
    "size": 123,
    "type": "file",
    "content": "..."
  }
]
```

#### Create a Branch

Creating a branch allows developers to work on new features or bug fixes without affecting the main branch.

**Command**:
```bash
git checkout -b feature-branch
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/refs HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "ref": "refs/heads/feature-branch",
  "sha": "abc123"
}
```

**Response**:
```json
{
  "ref": "refs/heads/feature-branch",
  "url": "https://api.github.com/repos/user/repo/git/refs/heads/feature-branch",
  "object": {
    "sha": "abc123",
    "type": "commit",
    "url": "https://api.github.com/repos/user/repo/git/commits/abc123"
  }
}
```

#### Make Changes

Changes are made to the codebase locally.

**Example**: Modify a File
```bash
echo "New content" >> README.md
```

**Raw HTTP Request Example**:
```http
PUT /repos/user/repo/contents/README.md HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "message": "Update README.md",
  "content": "TmV3IGNvbnRlbnQ=",
  "sha": "abc123"
}
```

**Response**:
```json
{
  "content": {
    "name": "README.md",
    "path": "README.md",
    "sha": "def456",
    "size": 123,
    "type": "file",
    "content": "TmV3IGNvbnRlbnQ="
  },
  "commit": {
    "id": "def456",
    "tree_id": "ghi789",
    "distinct": true,
    "message": "Update README.md",
    "timestamp": "2023-10-01T12:00:00Z",
    "author": {
      "name": "User Name",
      "email": "user@example.com"
    },
    "committer": {
      "name": "User Name",
      "email": "user@example.com"
    }
  }
}
```

#### Stage Changes

Staging changes prepares them for the next commit.

**Command**:
```bash
git add README.md
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/blobs HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "content": "New content",
  "encoding": "utf-8"
}
```

**Response**:
```json
{
  "content": "New content",
  "encoding": "utf-8",
  "sha": "def456"
}
```

#### Commit Changes

Committing changes saves the staged changes to the local repository.

**Command**:
```bash
git commit -m "Add new content to README.md"
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/commits HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "message": "Add new content to README.md",
  "tree": "ghi789",
  "parents": ["abc123"]
}
```

**Response**:
```json
{
  "id": "def456",
  "tree_id": "ghi789",
  "distinct": true,
  "message": "Add new content to README.md",
  "timestamp": "2023-10-01T12:00:00Z",
  "author": {
    "name": "User Name",
    "email": "user@example.com"
  },
  "committer": {
    "name": "User Name",
    "email": "user@example.com"
  }
}
```

#### Push Changes

Pushing changes sends the local commits to the remote repository.

**Command**:
```bash
git push origin feature-branch
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/refs HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "ref": "refs/heads/feature-branch",
  "sha": "def456"
}
```

**Response**:
```json
{
  "ref": "refs/heads/feature-branch",
  "url": "https://api.github.com/repos/user/repo/git/refs/heads/feature-branch",
  "object": {
    "sha": "def456",
    "type": "commit",
    "url": "https://api.github.com/repos/user/repo/git/commits/def456"
  }
}
```

#### Merge Changes

Merging changes combines the changes from one branch into another, typically the main branch.

**Command**:
```bash
git checkout main
git merge feature-branch
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/merges HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "base": "main",
  "head": "feature-branch"
}
```

**Response**:
```json
{
  "sha": "ghi789",
  "merged": true,
  "message": "Merge branch 'feature-branch' into 'main'"
}
```

### Common Pitfalls and How to Avoid Them

#### Conflicts

Conflicts occur when two developers make changes to the same part of the codebase. Resolving conflicts requires careful review and merging.

**Example**: Conflict Resolution
```bash
git checkout main
git merge feature-branch
# Resolve conflicts manually
git add .
git commit -m "Resolve conflicts"
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/merges HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "base": "main",
  "head": "feature-branch"
}
```

**Response**:
```json
{
  "sha": "ghi789",
  "merged": true,
  "message": "Merge branch 'feature-branch' into 'main'"
}
```

#### Accidental Commits

Accidental commits can happen when changes are not properly staged or reviewed.

**Example**: Reverting a Commit
```bash
git revert HEAD
```

**Raw HTTP Request Example**:
```http
POST /repos/user/repo/git/commits HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Content-Type: application/json
{
  "message": "Revert commit",
  "tree": "ghi789",
  "parents": ["def456"]
}
```

**Response**:
```json
{
  "id": "jkl012",
  "tree_id": "ghi789",
  "distinct": true,
  "message": "Revert commit",
  "timestamp": "2023-10-01T12:00:00Z",
  "author": {
    "name": "User Name",
    "email": "user@example.com"
  },
  "committer": {
    "name": "User Name",
    "email": "user@example.com"
  }
}
```

### How to Prevent / Defend

#### Detection

Regularly reviewing commit history and using automated tools can help detect issues early.

**Example**: Reviewing Commit History
```bash
git log --oneline
```

**Raw HTTP Request Example**:
```http
GET /repos/user/repo/commits HTTP/1.1
Host: api.github.com
Authorization: token YOUR_ACCESS_TOKEN
Accept: application/vnd.github.v3+json
```

**Response**:
```json
[
  {
    "sha": "def456",
    "commit": {
      "message": "Add new content to README.md",
      "author": {
        "name": "User Name",
        "email": "user@example.com"
      },
      "committer": {
        "name": "User Name",
        "email": "user@example.com"
      }
    }
  }
]
```

#### Prevention

Using best practices and tools can prevent many common issues.

**Best Practices**:
- Regularly review and test code changes.
- Use automated testing and continuous integration (CI) pipelines.
- Follow a consistent branching strategy.

**Tools**:
- Code review tools like GitHub Pull Requests.
- Automated testing frameworks like Jenkins or CircleCI.

#### Secure Coding Fixes

Comparing vulnerable and secure code patterns can help identify and fix issues.

**Vulnerable Pattern**:
```bash
git commit -m "Add new content to README.md"
```

**Secure Pattern**:
```bash
git add README.md
git commit -m "Add new content to README.md"
```

### Conclusion

Understanding Git and its components is essential for effective version control and collaboration. By mastering the workflow and avoiding common pitfalls, developers can ensure smooth and secure development processes.

### Practice Labs

For hands-on experience with Git, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on web application security, including Git usage in a secure context.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including Git usage.
- **DVWA (Damn Vulnerable Web Application)**: Another insecure web app for learning security concepts, including Git integration.

These labs provide practical experience with Git in a controlled environment, helping to reinforce theoretical knowledge with real-world scenarios.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/02-Version Control (Git)/14-Understanding Git Components And Workflow/00-Overview|Overview]] | [[02-Understanding Git Components and Workflow|Understanding Git Components and Workflow]]
