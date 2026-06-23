---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what Broken Object Level Authorization (BOLA) is and how it can lead to security vulnerabilities in APIs.**

Broken Object Level Authorization (BOLA) occurs when an application fails to properly enforce access controls at the object level, allowing unauthorized users to access or manipulate objects they should not have access to. In the context of APIs, this means that an attacker might be able to read or modify data belonging to another user if the API does not correctly verify the user's identity and permissions before processing requests. For instance, if an API endpoint allows fetching book details without checking whether the requesting user owns those books, an attacker could potentially retrieve sensitive information from other users.

**Q2. How would you exploit a BOLA vulnerability in an API that allows fetching book details by title?**

To exploit a BOLA vulnerability in an API that allows fetching book details by title, an attacker would need to craft a request that bypasses the lack of proper user-level authorization checks. The attacker would send a GET request to the endpoint responsible for retrieving book details, specifying a book title that belongs to another user. If the API does not validate that the requesting user is authorized to view the specified book, the attacker would receive the book details, which could include sensitive information such as the book's content or metadata.

For example, if the API endpoint is `/books/details`, the attacker would send a request like:

```http
GET /books/details?title=Secret%20Offensive%20API%20Penetration%20Testing HTTP/1.1
Authorization: Bearer <attacker's_token>
```

If the API does not check the ownership of the book, the response would contain the details of the book, even though it belongs to another user.

**Q3. What changes would you implement in the code to prevent BOLA vulnerabilities in an API that manages user books?**

To prevent BOLA vulnerabilities in an API that manages user books, the code should ensure that every request to access or modify a book includes a check to verify that the requesting user is authorized to perform the action. Here’s an example of how to modify the code to include user-level authorization:

```python
def get_book_details(book_title):
    # Fetch the current user from the authentication token
    current_user = get_current_user_from_token()

    # Query the database to find the book by title
    book = Book.query.filter_by(title=book_title).first()

    # Check if the book exists and if the current user is the owner
    if book and book.user_id == current_user.id:
        return book.details
    else:
        return "Unauthorized access"
```

In this code snippet, `get_current_user_from_token()` retrieves the user associated with the authentication token, and the query checks both the book title and the user ID to ensure that the requesting user is the owner of the book.

**Q4. How would you configure an API to ensure that only authorized users can add new books to their account?**

To ensure that only authorized users can add new books to their account, the API should require authentication and validate that the user is authorized to perform the action. Here’s an example of how to configure the API endpoint to handle adding new books:

```python
@app.route('/books', methods=['POST'])
@token_required
def add_book():
    # Extract the book details from the request
    book_data = request.json

    # Fetch the current user from the authentication token
    current_user = get_current_user_from_token()

    # Create a new book entry and associate it with the current user
    new_book = Book(title=book_data['title'], user_id=current_user.id)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'message': 'Book added successfully'})
```

In this example, the `@token_required` decorator ensures that the request is authenticated, and the `current_user` variable holds the user associated with the authentication token. The new book is created with the user ID of the current user, ensuring that the book is associated with the correct user.

**Q5. Referencing recent real-world examples, explain how BOLA vulnerabilities can impact an organization.**

BOLA vulnerabilities can significantly impact an organization by exposing sensitive data and compromising user privacy. A notable example is the Capital One data breach in 2019, where an attacker exploited a misconfigured web application firewall to gain unauthorized access to customer data. Although this specific breach was due to improper configuration rather than BOLA, similar vulnerabilities can arise from inadequate object-level authorization.

Another example is the Equifax data breach in 2017, where attackers exploited a vulnerability in the Apache Struts framework to gain access to sensitive personal information. While this breach involved a different type of vulnerability, it underscores the importance of robust access control mechanisms to protect user data.

In both cases, the breaches resulted in significant financial losses, reputational damage, and legal consequences for the organizations involved. To mitigate such risks, organizations must implement strict access control policies and regularly audit their systems to identify and fix potential BOLA vulnerabilities.

---
<!-- nav -->
[[04-Understanding Broken Object-Level Authorization (BOLA)|Understanding Broken Object-Level Authorization (BOLA)]] | [[API Security/06-Broken Object Level Authorization issues/02-BOLA Demonstration Live/00-Overview|Overview]]
