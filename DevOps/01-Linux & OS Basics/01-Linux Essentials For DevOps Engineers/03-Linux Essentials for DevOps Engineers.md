---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Linux Essentials for DevOps Engineers

### Introduction

As a DevOps engineer, proficiency in Linux is crucial. Linux is the backbone of many modern computing environments, especially in cloud and server-based operations. Understanding the Linux file system, mastering essential Linux commands, and being adept at using tools like VIM and shell scripting can significantly enhance your capabilities. This chapter delves into these topics, providing a comprehensive guide to mastering Linux essentials.

### Linux File System Structure

The Linux file system is hierarchical and organized in a tree-like structure. The root of this tree is denoted by `/`. Each directory and file within this structure has a specific role and function.

#### Directory Structure

- **/**: The root directory, containing all other directories and files.
- **/bin**: Contains essential user commands.
- **/boot**: Contains files needed to boot the system, including the kernel.
- **/dev**: Contains device files.
- **/etc**: Contains system-wide configuration files.
- **/home**: Contains user home directories.
- **/lib**: Contains shared libraries.
- **/media**: Mount point for removable media.
- **/mnt**: Temporary mount point for file systems.
- **/opt**: Optional application software packages.
- **/proc**: Virtual file system containing information about processes.
- **/root**: Home directory for the root user.
- **/sbin**: Contains system binaries.
- **/srv**: Data for services provided by this system.
- **/tmp**: Temporary files.
- **/usr**: Secondary hierarchy for read-only data.
- **/var**: Variable data, such as logs and spool files.

#### Example Directory Structure

```mermaid
graph TD
    A[Root (/)] --> B[bin]
    A --> C[boot]
    A --> D[dev]
    A --> E[etc]
    A --> F[home]
    A --> G[lib]
    A --> H[media]
    A --> I[mnt]
    A --> J[opt]
    A --> K[proc]
    A --> L[root]
    A --> M[sbin]
    A --> N[srv]
    A --> O[tmp]
    A --> P[usr]
    A --> Q[var]
```

### Essential Linux Commands

Mastering the Linux command line interface (CLI) is fundamental for any DevOps engineer. Here are some essential commands:

#### Basic Navigation

- `cd`: Change directory.
- `pwd`: Print working directory.
- `ls`: List directory contents.

Example:

```bash
$ cd /home/user
$ pwd
/home/user
$ ls
Documents Downloads Music Pictures Videos
```

#### File Manipulation

- `cp`: Copy files and directories.
- `mv`: Move or rename files and directories.
- `rm`: Remove files and directories.
- `mkdir`: Create directories.

Example:

```bash
$ cp Documents/report.txt Downloads/
$ mv Downloads/report.txt Downloads/final_report.txt
$ rm -r Pictures/old_photos
$ mkdir Documents/new_folder
```

#### File Permissions

- `chmod`: Change file mode bits.
- `chown`: Change file owner and group.

Example:

```bash
$ chmod 755 script.sh
$ chown user:group file.txt
```

### Installing Software on Linux

Installing software on Linux typically involves using package managers and software repositories. Understanding these tools is crucial for managing software installations effectively.

#### Package Managers

Package managers automate the process of installing, updating, and removing software packages. Common package managers include:

- **APT (Advanced Package Tool)**: Used in Debian-based distributions like Ubuntu.
- **YUM (Yellowdog Updater Modified)**: Used in Red Hat-based distributions like CentOS.
- **DNF (Dandified Yum)**: Successor to YUM, also used in Red Hat-based distributions.

#### Software Repositories

Software repositories are collections of software packages. They are categorized and indexed to facilitate easy installation and updates.

Example using APT:

```bash
$ sudo apt update
$ sudo apt install git
```

Example using DNF:

```bash
$ sudo dnf update
$ sudo dnf install git
```

### Hands-On Demos

#### Installing Git Using APT

```bash
$ sudo apt update
$ sudo apt install git
```

#### Installing Git Using DNF

```bash

$ sudo dnf update
$ sudo dnf install git
```

### VIM Editor

VIM is a highly configurable text editor built to enable efficient text editing. It is widely used in Linux environments due to its powerful features and efficiency.

#### Basic VIM Commands

- `i`: Enter insert mode.
- `Esc`: Exit insert mode.
- `:wq`: Write changes and quit.
- `:q!`: Quit without saving changes.
- `dd`: Delete a line.
- `yy`: Yank (copy) a line.
- `p`: Paste after cursor.
- `u`: Undo.
- `.`: Redo.

Example:

```vim
i
This is a new line.
Esc
:wq
```

### Users and Permissions

Managing users and permissions is critical for maintaining security and functionality in a Linux environment.

#### User Management

- `adduser`: Add a new user.
- `deluser`: Delete a user.
- `passwd`: Change a user's password.
- `usermod`: Modify a user's account.

Example:

```bash
$ sudo adduser newuser
$ sudo passwd newuser
$ sudo usermod -aG sudo newuser
```

#### Group Management

- `groupadd`: Add a new group.
- `groupdel`: Delete a group.
- `gpasswd`: Administer /etc/group and /etc/gshadow.
- `usermod`: Add or remove a user from a group.

Example:

```bash
$ sudo groupadd developers
$ sudo gpasswd -a newuser developers
```

#### File Ownership and Permissions

- `chown`: Change file owner and group.
- `chmod`: Change file mode bits.

Example:

```bash
$ sudo chown user:group file.txt
$ sudo chmod 755 file.txt
```

### Shell Scripting

Shell scripting is an essential skill for automating tasks and managing systems. Bash is one of the most commonly used shells.

#### Basic Bash Scripting

- `#!/bin/bash`: Shebang to specify the interpreter.
- `echo`: Print text to the console.
- `if`: Conditional statements.
- `for`: Loop through items.
- `function`: Define functions.

Example:

```bash
#!/bin/bash

# Print a welcome message
echo "Welcome to the script!"

# Check if a file exists
if [ -f "file.txt" ]; then
    echo "File exists!"
else
    echo "File does not exist."
fi

# Loop through numbers
for i in {1..5}; do
    echo "Number $i"
done

# Define a function
function greet {
    echo "Hello, $1!"
}

# Call the function
greet "World"
```

### How to Prevent / Defend

#### Secure Installation Practices

- Always use trusted repositories.
- Regularly update software to patch vulnerabilities.
- Use secure installation methods (e.g., verify checksums).

#### Secure User Management

- Limit user privileges.
- Use strong passwords.
- Regularly review user accounts and permissions.

#### Secure File Permissions

- Set appropriate file permissions.
- Use `chown` and `chmod` to control access.
- Regularly audit file permissions.

### Real-World Examples

#### CVE-2021-44228 (Log4j)

In December 2021, a critical vulnerability was discovered in Apache Log4j, a logging framework used in many applications. This vulnerability allowed attackers to execute arbitrary code on affected systems.

**Impact**: Many systems were compromised, leading to widespread security incidents.

**Prevention**: Ensure all software dependencies are up-to-date. Use package managers to automatically apply security patches.

#### Example of Secure Installation

```bash
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install --only-upgrade log4j
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers extensive labs on web security, including Linux fundamentals.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in applying the concepts learned in this chapter.

### Conclusion

Mastering Linux essentials is a foundational skill for any DevOps engineer. By understanding the Linux file system, mastering essential commands, learning to install software, using VIM, managing users and permissions, and scripting with Bash, you can become proficient in managing Linux environments. Regular practice and staying updated with security practices will further enhance your capabilities.

---
<!-- nav -->
[[02-Introduction to Operating Systems|Introduction to Operating Systems]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/01-Linux Essentials For DevOps Engineers/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/01-Linux Essentials For DevOps Engineers/04-Practice Questions & Answers|Practice Questions & Answers]]
