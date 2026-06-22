---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Mapping the Application

The first step in testing for directory traversal vulnerabilities is to map the application. This involves visiting the URL of the application and exploring all the pages accessible within the user context. The goal is to identify all potential input vectors that could be used to retrieve data from the server's file system.

### Identifying Input Vectors

Input vectors are points in the application where user-supplied data is accepted and processed. These can include form fields, URL parameters, and API endpoints. When mapping the application, pay close attention to any parameters that might contain file names or directory paths.

#### Example: File Upload Form

Consider a file upload form where the user can specify a file name. This form might look like this:

```html
<form action="/upload" method="POST">
    <input type="file" name="file">
    <input type="text" name="filename">
    <button type="submit">Upload</button>
</form>
```

In this case, the `filename` parameter is a potential input vector for directory traversal attacks.

### Common Input Vectors

Some common input vectors to watch out for include:

- **File Upload Forms**: Parameters that accept file names or paths.
- **Download Links**: Parameters that specify file paths.
- **Configuration Settings**: Parameters that reference external files or directories.
- **API Endpoints**: Parameters that accept file names or paths.

---
<!-- nav -->
[[06-Directory Traversal|Directory Traversal]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[08-Testing for Directory Traversal Vulnerabilities|Testing for Directory Traversal Vulnerabilities]]
