---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Command Line Interface (CLI) Basics

### Introduction to CLI

The Command Line Interface (CLI) is a powerful tool used to interact with operating systems and applications through text-based commands. Unlike graphical user interfaces (GUIs), which rely on visual elements like buttons and menus, CLIs require users to enter specific commands to perform tasks. This method of interaction is particularly useful for system administrators, developers, and power users who need to perform complex operations quickly and efficiently.

### Command History in CLI

One of the key features of CLI environments is the ability to maintain a history of executed commands. This feature allows users to recall and reuse previous commands, which can save time and reduce errors. The command history is stored in a file, typically named `.bash_history` for Bash shells, and can be accessed and manipulated using various commands.

#### Viewing Command History

To view the command history, you can use the `history` command. This command displays a list of all the commands executed in the current session, along with their respective line numbers. Here is an example of how to use the `history` command:

```sh
$ history
```

This command will output a list similar to the following:

```plaintext
1  ls
2  cd Documents
3  mkdir new_folder
4  touch new_file.txt
5  cat new_file.txt
```

Each line number corresponds to a command executed in the session. This can be very useful for recalling commands that were executed earlier.

### Searching Command History

In addition to viewing the entire command history, you can also search for specific commands using the `Ctrl+R` key combination. This feature performs a reverse search through the command history, allowing you to find and execute commands based on keywords.

#### Using Reverse Search

To use the reverse search feature, press `Ctrl+R` in the terminal. This will bring up a prompt that looks like this:

```plaintext
(reverse-i-search)`':
```

You can then type a keyword or partial command to search for. For example, typing `ls` will search for the most recent command containing `ls`. Once you find the desired command, you can press `Enter` to execute it or `Ctrl+R` again to continue searching.

Here is an example of using reverse search:

```plaintext
(reverse-i-search)`ls': ls
```

Pressing `Enter` will execute the `ls` command.

### Stopping Command Execution

Sometimes, you may need to stop a command that is currently executing. This can be done using the `Ctrl+C` key combination. This sends an interrupt signal to the process, causing it to terminate.

#### Example of Interrupting a Command

Consider a scenario where you are running a long-running process, such as a `find` command that searches through a large directory structure. If you decide to stop the process, you can press `Ctrl+C`.

```sh
$ find / -name "example.txt"
```

If you press `Ctrl+C`, the process will be interrupted, and you will return to the command prompt.

### Practical Examples and Real-World Scenarios

#### Example 1: Recalling Previous Commands

Suppose you are working on a project and need to frequently switch between directories. You might use the `cd` command to navigate to different directories. If you forget the exact path, you can use the `history` command to recall the previous `cd` commands.

```sh
$ history | grep cd
```

This will display all the `cd` commands in your history.

#### Example 2: Using Reverse Search for Complex Commands

Imagine you are working on a script that requires a complex command involving multiple flags and arguments. You might have executed this command earlier but forgot the exact syntax. You can use the reverse search feature to find the command.

```plaintext
(reverse-i-search)`git commit': git commit -m "Add new feature"
```

By pressing `Enter`, you can execute the command again.

### Recent Real-World Examples

#### Example: CVE-2021-44228 (Log4Shell)

In December 2021, a critical vulnerability was discovered in the Apache Log4j library, known as Log4Shell (CVE-2021-44228). This vulnerability allowed attackers to execute arbitrary code on affected systems. One of the ways to mitigate this vulnerability was to monitor and control the commands executed on the system.

Using the command history and reverse search features, system administrators could quickly identify and review commands that might have been executed by attackers. This helped in detecting and responding to potential attacks more effectively.

### How to Prevent / Defend

#### Detecting and Preventing Unauthorized Command Execution

To prevent unauthorized command execution, it is essential to implement proper access controls and monitoring mechanisms. Here are some steps to ensure security:

1. **Limit Access**: Ensure that only authorized users have access to the command line interface. Use role-based access control (RBAC) to restrict permissions.
2. **Audit Logs**: Enable auditing of command executions. This helps in tracking and reviewing commands executed by users.
3. **Command Filtering**: Implement command filtering to block potentially harmful commands. This can be done using tools like `sudo` with restricted commands.
4. **Regular Monitoring**: Regularly review command history logs to detect any suspicious activity.

#### Secure Coding Practices

When writing scripts or automation tools, it is crucial to follow secure coding practices. Here is an example of a vulnerable script and its secure version:

**Vulnerable Script**

```sh
#!/bin/bash
echo "Running command: $1"
$1
```

This script takes a command as an argument and executes it. However, it is vulnerable to command injection attacks.

**Secure Script**

```sh
#!/bin/bash
# Validate input to prevent command injection
if [[ "$1" =~ ^[a-zA-Z0-9\._/-]+$ ]]; then
    echo "Running command: $1"
    $1
else
    echo "Invalid command"
fi
```

In the secure version, the script validates the input to ensure it only contains safe characters, preventing command injection.

### Hands-On Practice

For hands-on practice with CLI commands and command history, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover various aspects of web security, including command-line usage.
- **OWASP Juice Shop**: A deliberately insecure web application that includes challenges related to command-line interactions and security.

These labs provide real-world scenarios and challenges that help reinforce the concepts learned.

### Conclusion

Understanding and effectively using the command history and reverse search features in CLI environments can significantly enhance productivity and security. By following secure coding practices and implementing proper access controls, you can protect against unauthorized command execution and other security threats.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/11-Miscellaneous/10-GUI vs CLI File Management Commands/00-Overview|Overview]] | [[02-Introduction to GUI vs CLI File Management Commands|Introduction to GUI vs CLI File Management Commands]]
