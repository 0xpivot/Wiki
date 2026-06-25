---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## File Ownership and Permissions in Unix Systems

In Unix-based systems, including Linux and macOS, files and directories have specific ownership and permissions associated with them. These permissions determine who can read, write, or execute a file. Understanding these concepts is crucial for effective DevOps automation using Bash scripting.

### Ownership

When a file is created, the user who creates it becomes the owner of that file. This is true by default unless explicitly changed. Ownership is important because the owner has certain privileges over the file, such as changing its permissions or deleting it.

#### Example

Let's create a simple file named `setup.sh`:

```bash
touch setup.sh
```

By default, the current user will be the owner of this file. We can verify this using the `ls -l` command:

```bash
ls -l setup.sh
```

The output might look like this:

```
-rw-r--r-- 1 username groupname 0 Jan 1 12:00 setup.sh
```

Here, `username` is the owner of the file.

### Permissions

Permissions in Unix systems are divided into three categories: owner, group, and others. Each category can have read (`r`), write (`w`), and execute (`x`) permissions.

#### Execute Permission

For a file to be executable, it must have the execute (`x`) permission set. Without this permission, attempting to run the file will result in an error.

#### Adding Execute Permission

To add the execute permission for the owner of the file, we use the `chmod` command. The `chmod` command changes the file mode bits, which control access permissions.

```bash
chmod u+x setup.sh
```

This command adds the execute permission (`+x`) for the user (`u`). After running this command, the file permissions should look like this:

```bash
ls -l setup.sh
```

Output:

```
-rwxr--r-- 1 username groupname 0 Jan 1 12:00 setup.sh
```

Notice the `x` in the first position after the `-rw-`, indicating that the owner now has execute permission.

### Executing the Script

Now that the file has execute permission, we can run it. There are two primary ways to execute a Bash script:

1. **Using the filename directly**:
    ```bash
    ./setup.sh
    ```

2. **Using the `bash` command**:
    ```bash
    bash setup.sh
    ```

Both methods will work as long as the file has the appropriate shebang line at the top, which specifies the interpreter to use. For a Bash script, this would typically be:

```bash
#!/bin/bash
```

### Full Example

Let's create a simple Bash script and walk through the process of making it executable and running it.

#### Creating the Script

First, create the `setup.sh` file with some basic content:

```bash
echo '#!/bin/bash' > setup.sh
echo 'echo "Hello, World!"' >> setup.sh
```

#### Making the Script Executable

Next, add the execute permission for the owner:

```bash
chmod u+x setup.sh
```

#### Running the Script

Now, run the script using both methods:

1. Using the filename directly:

    ```bash
    ./setup.sh
    ```

    Output:

    ```
    Hello, World!
    ```

2. Using the `bash` command:

    ```bash
    bash setup.sh
    ```

    Output:

    ```
    Hello, World!
    ```

### Universal Execution Method

The method of executing a script using `./scriptname` is universal across different types of shell scripts. This method works regardless of the specific shell syntax used within the script.

However, for Bash scripts specifically, using `bash scriptname` is also valid and sometimes preferred, especially when the script may contain non-standard features or when you want to ensure that the script is interpreted by Bash even if the shebang line is missing or incorrect.

### Pitfalls and Best Practices

#### Common Mistakes

1. **Missing Shebang Line**: If the shebang line is missing or incorrect, the script may not run as expected.
2. **Incorrect Permissions**: If the execute permission is not set, the script cannot be run directly.
3. **Ambiguous File Extensions**: While `.sh` is commonly used for shell scripts, it is not strictly necessary. Ensure the script is correctly identified by its shebang line.

#### How to Prevent / Defend

1. **Ensure Correct Shebang Line**: Always include the correct shebang line at the top of your script.
2. **Set Proper Permissions**: Use `chmod` to set the correct permissions for your script.
3. **Use Absolute Paths**: Use absolute paths for commands and files within the script to avoid issues with environment variables.
4. **Validate Input**: Validate any input to the script to prevent injection attacks.

### Real-World Examples

#### CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) demonstrated the importance of proper script execution and validation. In this case, a Java logging library was exploited due to improper handling of user input. Ensuring that scripts properly validate input and execute with the correct permissions can help mitigate such vulnerabilities.

### Conclusion

Understanding file ownership and permissions is essential for effective DevOps automation. By ensuring that scripts have the correct permissions and are executed properly, you can avoid common pitfalls and enhance the security of your automated processes.

### Practice Labs

For hands-on practice with Bash scripting and file permissions, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including sections on server-side scripting and file permissions.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web hacking techniques, including server-side scripting and file management.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning about web security, including file permissions and script execution.

These labs provide practical experience in managing file permissions and executing scripts securely.

---
<!-- nav -->
[[04-Introduction to Shell and Bash|Introduction to Shell and Bash]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/01-Bash Scripting Basics For DevOps Automation/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/01-Bash Scripting Basics For DevOps Automation/06-Practice Questions & Answers|Practice Questions & Answers]]
