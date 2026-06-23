---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Introduction to Mass Assignment Attack

Mass assignment, also known as overposting, is a common security vulnerability found in web applications, particularly those built using frameworks like Ruby on Rails, Laravel, and Django. This vulnerability occurs when an application allows unfiltered input data to be assigned to model attributes, potentially leading to unauthorized modifications of sensitive fields such as `admin` status, `password`, or `email`.

### What is Mass Assignment?

Mass assignment is a feature in many web frameworks that allows developers to update multiple attributes of a model at once. This is typically done through a single HTTP request, often a POST or PUT request, which contains a JSON object or form data. The framework automatically maps the incoming data to the corresponding model attributes, updating them accordingly.

#### Why Does Mass Assignment Matter?

Mass assignment matters because it can lead to serious security vulnerabilities. If an attacker can manipulate the input data to include additional attributes that should not be writable by the user, they can potentially escalate their privileges or modify critical information. For instance, an attacker might set the `admin` flag to `true` for a regular user account, thereby gaining administrative access to the system.

### How Does Mass Assignment Work Under the Hood?

To understand how mass assignment works, let's consider a simple example using a hypothetical web application built with a framework like Ruby on Rails. Suppose we have a `User` model with attributes such as `name`, `email`, and `admin`. A typical mass assignment scenario might look like this:

```ruby
class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])
    if @user.update(user_params)
      redirect_to @user, notice: 'User was successfully updated.'
    else
      render :edit
    end
  end

  private

  def user_params
    params.require(:user).permit(:name, :email)
  end
end
```

In this example, the `update` action finds a user by their ID and attempts to update their attributes based on the `params` passed in the request. The `user_params` method uses strong parameters to permit only the `name` and `email` attributes to be updated.

However, if the developer mistakenly permits all attributes without filtering, an attacker could send a request like this:

```json
{
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "admin": true
  }
}
```

If the `admin` attribute is not properly filtered, the attacker could set the `admin` flag to `true`, effectively elevating their privileges.

### Real-World Examples of Mass Assignment Attacks

Mass assignment attacks have been observed in several high-profile breaches and vulnerabilities. Here are a few recent examples:

1. **CVE-2021-21974**: This vulnerability affected the popular Ruby on Rails framework. An attacker could exploit this flaw to perform mass assignment attacks by manipulating the `params` hash. This allowed unauthorized modification of sensitive attributes, such as setting the `admin` flag to `true`.

2. **CVE-2020-14182**: This vulnerability was found in the Laravel framework. Similar to the Ruby on Rails issue, an attacker could exploit this flaw to perform mass assignment attacks, leading to unauthorized privilege escalation.

### Detailed Example of a Mass Assignment Attack

Let's walk through a detailed example of how a mass assignment attack might occur in a real-world scenario. Consider a web application with a `User` model that includes attributes such as `name`, `email`, and `admin`. The application uses a RESTful API to manage user data.

#### Vulnerable Code Example

Here is a simplified version of the vulnerable code:

```ruby
class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])
    if @user.update(params.require(:user))
      redirect_to @user, notice: 'User was successfully updated.'
    else
      render :edit
    end
  end
end
```

In this example, the `update` action uses `params.require(:user)` to fetch the user data from the request. However, it does not filter out any attributes, allowing an attacker to manipulate the `admin` flag.

#### Exploitation Scenario

An attacker could craft a request like this:

```http
PUT /users/1 HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "admin": true
  }
}
```

This request would update the user with ID `1`, setting their `admin` flag to `true`. If the application does not properly filter the input, the attacker would gain administrative privileges.

### How to Prevent / Defend Against Mass Assignment Attacks

Preventing mass assignment attacks requires careful handling of input data and strict validation of attributes. Here are some best practices and techniques to defend against these attacks:

#### Strong Parameter Filtering

One of the most effective ways to prevent mass assignment attacks is to use strong parameter filtering. This involves explicitly specifying which attributes can be updated through user input.

##### Secure Code Example

Here is the corrected version of the code with strong parameter filtering:

```ruby
class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])
    if @user.update(user_params)
      redirect_to @user, notice: 'User was successfully updated.'
    else
      render :edit
    end
  end

  private

  def user_params
    params.require(:user).permit(:name, :email)
  end
end
```

In this example, the `user_params` method explicitly permits only the `name` and `email` attributes, preventing an attacker from modifying the `admin` flag.

#### Input Validation

Another important defense mechanism is to validate user input thoroughly. This includes checking for the presence of required fields, ensuring that certain fields are within acceptable ranges, and verifying that sensitive fields are not being manipulated.

##### Example of Input Validation

```ruby
class User < ApplicationRecord
  validates :name, presence: true
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :admin, inclusion: { in: [false] }, unless: :super_admin?
end
```

In this example, the `User` model includes validations to ensure that the `name` and `email` fields are present and formatted correctly. Additionally, the `admin` field is validated to ensure it is not set to `true` unless the user is a super admin.

#### Role-Based Access Control (RBAC)

Implementing role-based access control (RBAC) can further enhance security by restricting access to sensitive operations based on user roles. This ensures that even if an attacker manages to manipulate certain attributes, they cannot perform actions that require higher privileges.

##### Example of RBAC Implementation

```ruby
class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  before_action :authorize_user!

  private

  def authenticate_user!
    unless current_user
      redirect_to login_path, alert: 'You must be logged in to access this page.'
    end
  end

  def authorize_user!
    unless current_user.admin?
      redirect_to root_path, alert: 'You do not have permission to access this page.'
    end
  end
end
```

In this example, the `ApplicationController` includes before-action filters to authenticate and authorize users. Only users with the `admin` flag set to `true` can access certain pages or perform specific actions.

### Detection and Monitoring

Detecting and monitoring for mass assignment attacks involves implementing logging and auditing mechanisms to track changes made to sensitive attributes. This can help identify suspicious activity and potential security breaches.

#### Logging and Auditing

Logging and auditing mechanisms can be implemented to track changes made to sensitive attributes. This includes logging the user who made the change, the timestamp of the change, and the previous and new values of the attribute.

##### Example of Logging Mechanism

```ruby
class User < ApplicationRecord
  after_update :log_changes

  private

  def log_changes
    if admin_changed?
      Rails.logger.info("Admin flag changed for user #{id} from #{admin_was} to #{admin}")
    end
  end
end
```

In this example, the `User` model includes an `after_update` callback to log changes made to the `admin` flag. This can help identify any unauthorized modifications to sensitive attributes.

### Hands-On Labs for Practice

To practice and reinforce your understanding of mass assignment attacks, consider the following hands-on labs:

1. **PortSwigger Web Security Academy**: This platform offers a series of labs that cover various web security topics, including mass assignment attacks. You can practice identifying and exploiting mass assignment vulnerabilities in a controlled environment.

2. **OWASP Juice Shop**: This is an intentionally vulnerable web application that simulates a modern e-commerce platform. It includes several mass assignment vulnerabilities that you can explore and exploit.

3. **DVWA (Damn Vulnerable Web Application)**: This is another intentionally vulnerable web application that includes several mass assignment vulnerabilities. You can practice identifying and exploiting these vulnerabilities to improve your skills.

By practicing in these environments, you can gain hands-on experience with mass assignment attacks and learn how to effectively defend against them.

### Conclusion

Mass assignment attacks are a significant security concern for web applications. By understanding how these attacks work, recognizing real-world examples, and implementing best practices for prevention and detection, you can significantly reduce the risk of such vulnerabilities in your applications. Always remember to filter input data carefully, validate user input thoroughly, and implement robust access control mechanisms to protect sensitive attributes and operations.

---
<!-- nav -->
[[API Security/10-Mass Assignment Attack/01-Mass Assignment Demonstration 2/00-Overview|Overview]] | [[API Security/10-Mass Assignment Attack/01-Mass Assignment Demonstration 2/02-Practice Questions & Answers|Practice Questions & Answers]]
