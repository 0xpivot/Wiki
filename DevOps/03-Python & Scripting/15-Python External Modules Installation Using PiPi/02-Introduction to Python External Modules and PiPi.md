---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Python External Modules and PiPi

When you first install Python, it comes with a set of built-in modules that are essential for basic programming tasks. These built-in modules provide fundamental functionalities such as file handling, mathematical operations, and string manipulations. However, Python's ecosystem extends far beyond these core modules through external modules, which are developed by third parties to address specific use cases such as web development, data science, machine learning, and more.

### Built-In vs. External Modules

**Built-In Modules**: These are pre-installed with Python and are available for immediate use. Examples include `os`, `sys`, `math`, and `datetime`. They are included because they cover a wide range of general-purpose functionalities that most Python programs might require.

**External Modules**: These are not included in the default Python installation but can be installed as needed. They extend Python's capabilities by providing specialized functionalities. Examples include `Django` for web development, `NumPy` for numerical computations, and `TensorFlow` for machine learning.

### Why Use External Modules?

Using external modules allows developers to leverage existing libraries and frameworks, saving time and effort in building complex functionalities from scratch. This modular approach promotes code reusability and maintainability, making development processes more efficient.

### The PiPi Repository

The Python Package Index (PiPi) is a repository where external Python modules are hosted. It serves as a central hub for discovering, installing, and managing Python packages. PiPi is crucial because it provides a standardized way to distribute and manage Python packages, ensuring consistency and reliability across different environments.

### Searching for Packages on PiPi

To find and install a package, you can visit the PiPi website (https://pypi.org/) and search for the desired package. For instance, if you need to install `Django` for web development, you can search for it on PiPi and find detailed information about the package, including its version history, documentation, and download statistics.

### Difference Between Package and Module

In Python, the terms "package" and "module" are often used interchangeably, but they have distinct meanings:

- **Module**: A single Python file containing functions, classes, and variables. For example, `math.py` is a module.
- **Package**: A directory containing multiple modules and possibly sub-packages. It typically includes an `__init__.py` file to mark it as a package. For example, `numpy` is a package that contains multiple modules.

### Installing Packages Using pip

`pip` is the package installer for Python, which simplifies the process of installing and managing external packages. To install a package using `pip`, you can run the following command in your terminal:

```sh
pip install <package_name>
```

For example, to install `Django`, you would run:

```sh
pip install django
```

### Example: Installing Django

Let's walk through the process of installing `Django` using `pip`.

#### Step 1: Open Terminal

Open your terminal or command prompt.

#### Step 2: Install Django

Run the following command:

```sh
pip install django
```

This command will download and install the latest version of `Django` along with its dependencies.

#### Step 3: Verify Installation

To verify that `Django` has been installed correctly, you can check its version by running:

```python
import django
print(django.get_version())
```

### Common Pitfalls and How to Prevent Them

#### Dependency Conflicts

One common issue when working with external modules is dependency conflicts. Different packages may require different versions of the same dependency, leading to conflicts.

**How to Prevent**: Use virtual environments to isolate project dependencies. Virtual environments allow you to create isolated Python environments for each project, preventing conflicts between dependencies.

```sh
# Create a virtual environment
python -m venv myenv

# Activate the virtual environment
# On Windows
myenv\Scripts\activate
# On Unix or MacOS
source myenv/bin/activate

# Install packages within the virtual environment
pip install django
```

#### Outdated Packages

Using outdated packages can expose your application to vulnerabilities and bugs.

**How to Prevent**: Regularly update your packages to the latest versions. You can use the following command to upgrade a package:

```sh
pip install --upgrade <package_name>
```

### Real-World Example: CVE-2021-3177

CVE-2021-3177 is a critical vulnerability found in the `Django` framework. This vulnerability allowed attackers to execute arbitrary code by exploiting a flaw in the `django.contrib.auth.forms.UserCreationForm` class.

**Impact**: An attacker could potentially gain unauthorized access to the system and execute arbitrary code.

**Detection**: To detect if your `Django` installation is vulnerable, check the version of `Django` you are using. Versions prior to 3.2.4 and 3.1.12 are affected.

**Prevention**: Upgrade to the latest version of `Django` to mitigate this vulnerability.

```sh
pip install --upgrade django
```

### Secure Coding Practices

When working with external modules, it's important to follow secure coding practices to minimize the risk of vulnerabilities.

#### Example: Secure Configuration of Django

Here’s an example of a secure configuration for a `Django` project:

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your_secret_key'
```

#### Vulnerable vs. Secure Code

**Vulnerable Code**:

```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'not_a_secure_key'
```

**Secure Code**:

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your_secret_key'
```

### Conclusion

Understanding how to install and manage external Python modules using PiPi is essential for effective Python development. By leveraging external modules, you can enhance your applications with specialized functionalities. However, it's crucial to be aware of potential pitfalls and to follow secure coding practices to ensure the robustness and security of your applications.

### Hands-On Practice

For hands-on practice with Python external modules and PiPi, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including Python-based exercises.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Django Girls Tutorial**: A beginner-friendly tutorial for setting up and deploying a `Django` application.

These resources will help you gain practical experience in installing and using external Python modules effectively.

---
<!-- nav -->
[[01-Introduction to Python External Modules Installation Using Pip|Introduction to Python External Modules Installation Using Pip]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/15-Python External Modules Installation Using PiPi/00-Overview|Overview]] | [[03-Introduction to Python External Modules and PyPI|Introduction to Python External Modules and PyPI]]
