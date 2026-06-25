---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Configuring a Local Python Development Environment

In this section, we will delve into the process of setting up a local Python development environment, focusing on the installation of Python itself and the configuration of a suitable code editor. We'll explore the importance of having a robust development environment, the differences between various versions of Python, and the benefits of using an integrated development environment (IDE) like PyCharm.

### Why Configure a Local Python Development Environment?

A local Python development environment allows developers to write, test, and debug Python code on their own computers. This setup is essential for several reasons:

1. **Isolation**: A local environment isolates the development process from the production environment, reducing the risk of accidental changes affecting live systems.
2. **Flexibility**: Developers can experiment with different configurations and libraries without impacting other projects.
3. **Consistency**: Ensures that the development environment mirrors the production environment as closely as possible, reducing the likelihood of environment-specific bugs.

### Differentiating Between Installed Python Versions

When setting up a Python development environment, it's crucial to understand the differences between the versions of Python installed on your system. Typically, most modern operating systems come with a pre-installed version of Python. However, this version might not be the latest, and it may lack certain features or security patches.

#### Checking Installed Python Versions

To check the installed Python versions on your system, you can use the following commands:

```bash
python --version
python3 --version
```

These commands will display the version numbers of the Python installations. If you have multiple versions installed, you might see something like `Python 2.7.x` and `Python 3.x.y`.

#### Installing a New Version of Python

If you need to install a newer version of Python, you can do so using package managers or by downloading the installer from the official Python website. Here’s how to install Python 3.10 on Ubuntu:

```bash
sudo apt update
sudo apt install python3.10
```

For macOS, you can use Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.10
```

### Setting Up a Code Editor for Python

Once Python is installed, the next step is to set up a code editor. While a simple text editor like Notepad or TextEdit can be used to write Python code, a dedicated code editor provides numerous advantages such as syntax highlighting, code completion, and debugging tools.

#### Best Python Code Editors

Among the many code editors available, PyCharm from JetBrains stands out as one of the best options for Python development. PyCharm offers both a Community Edition (free) and a Professional Edition (paid).

### Downloading and Installing PyCharm

To get started with PyCharm, follow these steps:

1. **Visit the PyCharm Download Page**:
   - Go to the [PyCharm download page](https://www.jetbrains.com/pycharm/download/) and select the appropriate version for your operating system (Windows, macOS, or Linux).

2. **Download the Installer**:
   - Click on the download link for the Community Edition. This version is free and includes most of the features needed for Python development.

3. **Install PyCharm**:
   - Once the installer is downloaded, run it to install PyCharm. Follow the on-screen instructions to complete the installation process.

4. **Launch PyCharm**:
   - After installation, launch PyCharm from your applications menu or desktop shortcut.

### Creating a New Project in PyCharm

Once PyCharm is installed, you can start creating a new project:

1. **Open PyCharm**:
   - Launch PyCharm and select "Create New Project".

2. **Configure Project Settings**:
   - In the project creation dialog, specify the project name and location. For example, you can name the project "My Python Project".
   - Choose the Python interpreter to use for the project. PyCharm will automatically detect the installed Python versions and allow you to select one.

3. **Project Structure**:
   - PyCharm creates a project structure with a default layout. The project folder will contain subdirectories for source code, tests, and other resources.

### Exploring PyCharm Features

PyCharm offers a wide range of features to enhance Python development:

- **Code Completion**: PyCharm provides intelligent code completion based on context.
- **Syntax Highlighting**: Highlights syntax errors and provides visual cues for different elements of the code.
- **Debugging Tools**: Allows you to set breakpoints, step through code, and inspect variables.
- **Version Control Integration**: Supports popular version control systems like Git, allowing you to manage your codebase effectively.

### Example: Creating a Simple Python Script

Let's create a simple Python script to demonstrate the usage of PyCharm:

1. **Create a New File**:
   - Right-click on the project folder in the Project Explorer and select "New" > "Python File". Name the file `hello.py`.

2. **Write the Code**:
   - Open the `hello.py` file and write the following code:

```python
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

3. **Run the Script**:
   - Right-click on the `hello.py` file and select "Run 'hello'". PyCharm will execute the script and display the output in the Run window.

### Common Pitfalls and How to Avoid Them

While setting up a Python development environment, several common pitfalls can occur:

- **Conflicting Python Versions**: Ensure that the correct Python version is selected for the project. Use virtual environments to isolate dependencies.
- **Missing Dependencies**: Install required packages using pip. Use a requirements file to manage dependencies.
- **Configuration Issues**: Double-check the configuration settings in PyCharm to ensure they match your project requirements.

### How to Prevent and Defend Against Common Issues

#### Virtual Environments

Virtual environments help manage dependencies and avoid conflicts between different projects. To create a virtual environment in PyCharm:

1. **Create a Virtual Environment**:
   - In the Project Interpreter settings, click on the gear icon and select "Add".
   - Choose "Virtualenv Environment" and specify the location and base interpreter.

2. **Activate the Virtual Environment**:
   - PyCharm will automatically activate the virtual environment when you run the project.

#### Secure Coding Practices

Secure coding practices are essential to prevent vulnerabilities in your Python applications. Here are some best practices:

- **Input Validation**: Always validate user input to prevent injection attacks.
- **Error Handling**: Implement proper error handling to avoid exposing sensitive information.
- **Use Libraries Safely**: Keep libraries up-to-date and review their security advisories.

### Real-World Examples and CVEs

Recent CVEs related to Python include:

- **CVE-2021-3177**: A vulnerability in the `pickle` module that could lead to arbitrary code execution.
- **CVE-2021-3179**: A vulnerability in the `subprocess` module that could allow attackers to execute arbitrary commands.

To mitigate these risks, ensure that your Python environment is up-to-date and follow secure coding practices.

### Conclusion

Setting up a local Python development environment with PyCharm provides a powerful and efficient way to write, test, and debug Python code. By understanding the differences between installed Python versions and leveraging the features of PyCharm, you can create a robust and secure development environment.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP-based web application with intentional vulnerabilities for educational purposes.

By completing these labs, you can gain practical experience in configuring and securing a Python development environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/03-Python & Scripting/08-Configuring Local Python Development Environment/00-Overview|Overview]] | [[02-Configuring Local Python Development Environment|Configuring Local Python Development Environment]]
