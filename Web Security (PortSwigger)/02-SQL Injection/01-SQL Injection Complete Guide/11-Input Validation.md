---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Input Validation

Input validation is the process of ensuring that user-supplied input meets specific criteria before it is processed. This can help prevent SQL Injection by rejecting invalid input.

### Example of Input Validation

Consider the following PHP code snippet with input validation:

```php
<?php
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

$user_input = $_GET['id']; // User-supplied input
if (!is_numeric($user_input)) {
    die("Invalid input");
}

$sql = "SELECT * FROM users WHERE id = '$user_input'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Output data of each row
    while($row = $result->fetch_assoc()) {
        echo "id: " . $row["id"]. " - Name: ". $row["name"]. "<br>";
    }
} else {
    echo "0 results";
}
$conn->close();
?>
```

In this example, the `is_numeric()` function ensures that the `$user_input` is a numeric value, preventing non-numeric input from being processed.

### Pitfalls of Input Validation

While input validation is a good practice, it is not foolproof. Attackers can sometimes bypass validation by encoding their input or using other evasion techniques. Therefore, input validation should be combined with other security measures.

---
<!-- nav -->
[[10-Error-Based SQL Injection|Error-Based SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[12-Mapping the Application An Underrated but Critical Step|Mapping the Application An Underrated but Critical Step]]
