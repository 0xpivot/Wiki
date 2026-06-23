---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Generic Error Messages

### What are Generic Error Messages?

Generic error messages are consistent error messages displayed to users when they enter incorrect credentials during login. These messages do not differentiate between whether the username or password is incorrect, providing a uniform response.

### Why Use Generic Error Messages?

Using generic error messages helps prevent **credential enumeration** attacks. An attacker could otherwise use specific error messages to determine if a username exists in the system, narrowing down potential targets for further attacks.

### How Do Generic Error Messages Work?

Here’s an example of implementing generic error messages in a login form using PHP:

```php
<?php
session_start();
$servername = "localhost";
$username = "username";
$password = "password";
$dbname = "myDB";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $user = $_POST['username'];
    $pass = $_POST['password'];

    // Prepare SQL statement
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->bind_param("s", $user);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        if (password_verify($pass, $row['password'])) {
            $_SESSION['loggedin'] = true;
            $_SESSION['username'] = $user;
            echo "Login successful!";
        } else {
            echo "Invalid username or password.";
        }
    } else {
        echo "Invalid username or password.";
    }
}
?>
```

### Real-World Example: Equifax Breach (CVE-2017-11882)

In 2017, Equifax suffered a massive data breach affecting over 143 million users. One of the vulnerabilities exploited was a lack of proper error handling, allowing attackers to determine valid usernames through specific error messages. Using generic error messages could have made such attacks more difficult.

### How to Prevent / Defend

#### Secure Error Handling Practices

1. **Use Consistent Error Messages**: Always display the same error message regardless of whether the username or password is incorrect.
2. **Avoid Leaking Information**: Ensure that error messages do not reveal any information about the internal workings of the system.

---
<!-- nav -->
[[08-Default Credentials|Default Credentials]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/10-Hands-On Labs|Hands-On Labs]]
