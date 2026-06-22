---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Main Method and Command Line Arguments

The main method is the entry point of a Python script. It handles the execution flow and processes command line arguments.

### What is the Main Method?

The main method is a function that is executed when the script is run. It typically contains the logic for processing command line arguments and executing the core functionality of the script.

### Why Define the Main Method?

Defining the main method ensures that the script behaves consistently whether it is imported as a module or executed directly. It also provides a clear structure for handling command line arguments.

### How to Define the Main Method

Here’s an example of defining the main method:

```python
import sys

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(-1)

    url = sys.argv[1]
    print(f"Processing URL: {url}")

if __name__ == "__main__":
    main()
```

### Real-World Example

Suppose you are developing a script to perform directory traversal attacks. The script takes a URL as a command line argument and attempts to access files outside the intended directory.

### Pitfalls

Failing to handle command line arguments correctly can lead to errors and unexpected behavior. It’s important to validate the input and provide clear usage instructions.

### How to Prevent / Defend

**Detection**: Use logging to track the execution flow and command line arguments.

**Prevention**: Always validate command line arguments and provide clear usage instructions.

**Secure Code Fix**:

```python
# Vulnerable code
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: script.py <URL>")
        sys.exit(-1)

    url = sys.argv[1]
    print(f"Processing URL: {url}")

if __name__ == "__main__":
    main()

# Secure code
import sys

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(-1)

    url = sys.argv[1]
    print(f"Processing URL: {url}")

if __name__ == "__main__":
    main()
```

### Conclusion

This section covered the essential steps for setting up a Python script for web security testing, including disabling insecure request warnings, setting proxy settings, and defining the main method to handle command line arguments. Each step was explained in detail, with real-world examples and secure coding practices provided.

---
<!-- nav -->
[[03-Disabling Insecure Request Warnings|Disabling Insecure Request Warnings]] | [[Web Security (PortSwigger)/11-Directory Traversal/04-Lab 3 File path traversal traversal sequences stripped non recursively/00-Overview|Overview]] | [[05-Setting Proxy Settings|Setting Proxy Settings]]
