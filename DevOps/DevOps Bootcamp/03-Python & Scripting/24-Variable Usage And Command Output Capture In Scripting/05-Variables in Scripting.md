---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Variables in Scripting

### Introduction to Variables

Variables are fundamental constructs in scripting languages that allow you to store and manipulate data. They provide a way to hold values that can be referenced and modified throughout the script. This is particularly useful when you need to reuse a piece of information multiple times within your script.

#### Naming Conventions

When naming variables, it's important to follow certain conventions to ensure readability and maintainability of your code. Common conventions include:

- **Underscore Syntax**: Using underscores to separate words in variable names. For example, `file_name`.
- **Camel Case**: Capitalizing the first letter of each word except the first one. For example, `fileName`.

While these are common conventions, you can name your variables in any way you prefer, as long as it adheres to the syntax rules of the scripting language you are using.

```bash
# Example of variable assignment using underscore syntax
file_name="config.yaml"

# Example of variable assignment using camel case
fileName="config.yaml"
```

### Assigning Values to Variables

To assign a value to a variable, you use the equal sign (`=`). The left side of the equal sign is the variable name, and the right side is the value you want to assign to the variable.

```bash
# Assigning a string value to a variable
file_name="config.yaml"

# Assigning a numeric value to a variable
count=10
```

### Referencing Variables

Once a variable is assigned a value, you can reference it in your script using the `$` symbol followed by the variable name. This allows you to use the stored value in various operations and commands.

```bash
# Referencing a variable in an echo command
echo "The file name is $file_name"
```

### Command Output Capture

Another powerful feature of variables is their ability to capture the output of command executions. This is particularly useful when you need to process the results of a command in subsequent steps of your script.

For example, you might want to list the contents of a directory and store the result in a variable for further processing.

```bash
# Capturing the output of the ls command
files=$(ls config)

# Printing the captured output
echo "Files in the config directory: $files"
```

### Real-World Examples

#### Example 1: Configuring a File

Let's consider a scenario where you need to configure a file named `config.yaml`. You can store the file name in a variable and use it in multiple commands.

```bash
# Storing the file name in a variable
file_name="config.yaml"

# Using the variable in a command
echo "Configuring $file_name"
```

#### Example 2: Listing Directory Contents

Suppose you want to list the contents of a directory and store the result in a variable for further processing.

```bash
# Capturing the output of the ls command
files=$(ls config)

# Printing the captured output
echo "Files in the config directory: $files"
```

### Pitfalls and Best Practices

#### Common Mistakes

- **Forgetting the `$` Symbol**: One common mistake is forgetting to use the `$` symbol when referencing a variable. This will cause the script to treat the variable name as a literal string instead of substituting the stored value.

  ```bash
  # Incorrect usage
  echo "The file name is file_name"
  ```

- **Variable Scope**: Variables defined in a script are typically local to that script unless explicitly exported. Ensure that variables are properly scoped and accessible where needed.

  ```bash
  # Exporting a variable to make it available in subshells
  export file_name="config.yaml"
  ```

### How to Prevent / Defend

#### Detection

To detect issues related to variable usage, you can use static analysis tools that check your scripts for common errors such as missing `$` symbols or incorrect variable references.

#### Prevention

- **Use Linters**: Tools like ShellCheck can help identify potential issues in your shell scripts, including problems with variable usage.
- **Code Reviews**: Regular code reviews can catch mistakes and ensure adherence to best practices.
- **Testing**: Write tests to verify that your scripts behave as expected, especially when dealing with variable assignments and command outputs.

#### Secure Coding Fixes

Here’s an example of a vulnerable script and its secure counterpart:

**Vulnerable Script**

```bash
# Vulnerable script
file_name=config.yaml
echo "The file name is $file_name"
```

**Secure Script**

```bash
# Secure script
file_name="config.yaml"
echo "The file name is $file_name"
```

### Conclusion

Variables are essential in scripting for storing and reusing values. Understanding how to properly assign, reference, and capture command outputs using variables is crucial for writing efficient and maintainable scripts. By following best practices and using tools for detection and prevention, you can ensure that your scripts are robust and secure.

### Practice Labs

For hands-on practice with variable usage and command output capture in scripting, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover various aspects of web application security, including scripting.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which includes scenarios where scripting and variable handling are relevant.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities to practice exploiting and securing, including those involving scripting and variable management.

These labs will help you apply the concepts learned in a practical setting, reinforcing your understanding and skills.

---
<!-- nav -->
[[04-Variable Usage and Command Output Capture in Scripting|Variable Usage and Command Output Capture in Scripting]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/24-Variable Usage And Command Output Capture In Scripting/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/24-Variable Usage And Command Output Capture In Scripting/06-Practice Questions & Answers|Practice Questions & Answers]]
