---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Chaining Commands with Input Output Redirection

In the realm of DevOps and system administration, the ability to efficiently manipulate and process data through command-line interfaces is crucial. Two fundamental concepts that enable this efficiency are **command chaining** and **input/output redirection**. These techniques allow you to combine multiple commands and direct their outputs to different destinations, streamlining your workflow and making complex tasks more manageable.

### Command Chaining

Command chaining involves linking multiple commands together so that the output of one command serves as the input to the next. This is typically achieved using the `|` (pipe) symbol. Let's explore this concept in detail.

#### What is Command Chaining?

Command chaining allows you to create a pipeline where the output of one command is fed into the next command. This is particularly useful when you need to process large amounts of data or perform multiple operations sequentially.

#### Why Use Command Chaining?

Command chaining is essential because it enables you to perform complex tasks with a single command line. Instead of manually handling intermediate results, you can automate the entire process, reducing the chance of human error and saving time.

#### How Does Command Chaining Work?

When you chain commands using pipes (`|`), the shell executes the first command and passes its standard output to the second command as standard input. This process continues down the pipeline until the final command is executed.

#### Example: Filtering Files in `/usr/bin`

Let's consider an example where you want to filter files in the `/usr/bin` directory to find a specific program, such as `java`.

```bash
ls /usr/bin | grep java
```

Here, `ls /usr/bin` lists all files in the `/usr/bin` directory. The output of `ls` is then piped (`|`) to `grep`, which searches for lines containing the string `java`. This command will return all files in `/usr/bin` that contain `java` in their names.

#### Multiple Filters

You can chain multiple filters to refine your search further. For instance, if you want to find all files related to `python` and then filter those that contain `3`:

```bash
ls /usr/bin | grep python | grep 3
```

This command first lists all files in `/usr/bin`, then filters those containing `python`, and finally filters those containing `3`.

### Input/Output Redirection

Input/output redirection allows you to control where the input and output of a command come from and go to. This is achieved using symbols like `<`, `>`, `>>`, and `<<`.

#### What is Input/Output Redirection?

Redirection lets you specify alternative sources and destinations for a command's input and output. You can read from a file instead of the keyboard, write to a file instead of the screen, or append to a file instead of overwriting it.

#### Why Use Input/Output Redirection?

Redirection is powerful because it allows you to automate data processing and logging. By directing output to a file, you can save results for later analysis or use them as input for other processes.

#### How Does Input/Output Redirection Work?

- **Standard Input (`<`)**: Redirects the contents of a file to a command.
- **Standard Output (`>`)**: Redirects the output of a command to a file, overwriting the file if it already exists.
- **Append Output (`>>`)**: Appends the output of a command to a file.
- **Here Document (`<<`)**: Allows you to pass multiple lines of input to a command.

#### Example: Redirecting Output to a File

Suppose you want to list all files in `/usr/bin` and save the output to a file named `bin_files.txt`.

```bash
ls /usr/bin > bin_files.txt
```

This command redirects the output of `ls /usr/bin` to `bin_files.txt`. If `bin_files.txt` already exists, its contents will be overwritten.

#### Appending Output

If you want to append the output to an existing file instead of overwriting it:

```bash
ls /usr/bin >> bin_files.txt
```

This command appends the output of `ls /usr/bin` to `bin_files.txt`.

### Combining Command Chaining and Redirection

You can combine command chaining and redirection to perform complex operations efficiently. For example, you might want to filter a large YAML file for specific port numbers and save the results to a file.

#### Example: Filtering YAML Content

Consider a large YAML file named `config.yaml` that contains various configurations. You want to find all occurrences of the string `port` and save the results to `ports.txt`.

```bash
cat config.yaml | grep port > ports.txt
```

This command reads the contents of `config.yaml`, filters lines containing `port`, and saves the filtered output to `ports.txt`.

### Real-World Examples and Security Implications

#### Recent CVEs and Breaches

Redirection and command chaining can be exploited in various ways, leading to security vulnerabilities. For example, in the context of a web application, an attacker might use command injection to execute arbitrary commands on the server.

##### CVE-2021-2109
A recent example is CVE-2021-2109, where a vulnerability in the Jenkins Pipeline plugin allowed attackers to inject malicious commands. By manipulating environment variables, attackers could execute arbitrary commands on the server, potentially gaining unauthorized access.

#### Secure Coding Practices

To prevent such vulnerabilities, follow these secure coding practices:

1. **Validate and Sanitize Inputs**: Ensure that all inputs are validated and sanitized to prevent command injection attacks.
2. **Use Parameterized Queries**: When executing commands, use parameterized queries or safe APIs to avoid injecting user input directly into command strings.
3. **Least Privilege Principle**: Run commands with the least privilege necessary to minimize potential damage in case of a breach.

#### Vulnerable vs. Secure Code

Here’s an example of insecure code and its secure counterpart:

**Vulnerable Code:**

```bash
# Insecure code
command="ls $user_input"
eval "$command"
```

**Secure Code:**

```bash
# Secure code
user_input=$(echo "$user_input" | sed 's/[;&|]/ /g')  # Sanitize input
command="ls $user_input"
eval "$command"
```

### Practical Labs

To practice these concepts, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities to practice exploiting and securing.

### Conclusion

Command chaining and input/output redirection are powerful tools in the DevOps toolkit. They enable efficient data processing and automation, but they must be used carefully to avoid security vulnerabilities. By understanding how these concepts work and following secure coding practices, you can leverage them effectively while maintaining the security of your systems.

---
<!-- nav -->
[[04-Introduction to `grep` Command|Introduction to `grep` Command]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/03-Chaining Commands with Input Output Redirection/00-Overview|Overview]] | [[06-Chaining Commands with InputOutput Redirection|Chaining Commands with InputOutput Redirection]]
