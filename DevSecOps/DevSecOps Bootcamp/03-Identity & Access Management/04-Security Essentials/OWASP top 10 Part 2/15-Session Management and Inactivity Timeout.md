---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Session Management and Inactivity Timeout

### Importance of Inactivity Timeout

Session management is a critical aspect of web application security. One of the most important features of session management is the implementation of an inactivity timeout. This feature ensures that a user's session is automatically terminated after a certain period of inactivity, thereby reducing the risk of unauthorized access.

#### What is Inactivity Timeout?

An inactivity timeout is a mechanism that automatically logs out a user after a specified period of inactivity. This period can vary depending on the application's requirements, but a common standard is around 30 minutes to 1 hour. The primary goal of this feature is to mitigate the risk of an attacker gaining access to a user's session if the user forgets to log out.

#### Why Implement Inactivity Timeout?

Implementing an inactivity timeout is crucial because it addresses the scenario where a user might leave their device unattended while still logged into an application. Without an inactivity timeout, an attacker could potentially gain access to the user's session and perform actions on behalf of the user. This is particularly dangerous in applications that handle sensitive information, such as financial transactions or personal data.

#### How Does Inactivity Timeout Work?

The inactivity timeout mechanism typically works by tracking the time between user interactions. Each interaction (such as clicking a button or navigating to a new page) resets the timer. Once the timer reaches the specified inactivity period, the session is terminated, and the user is logged out.

Here’s a simplified example of how this might be implemented in a web application:

```python
# Example Python Flask application with inactivity timeout

from flask import Flask, session, redirect, url_for, request
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.before_request
def check_inactivity():
    if 'last_activity' in session:
        last_activity = session['last_activity']
        current_time = datetime.datetime.now()
        if (current_time - last_activity).total_seconds() > 3600:  # 1 hour
            session.clear()
            return redirect(url_for('login'))
    session['last_activity'] = datetime.datetime.now()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform authentication logic here
        session['user_id'] = 'some_user_id'
        return redirect(url_for('home'))
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/')
def home():
    return 'Welcome to the Home Page!'

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the `check_inactivity` function runs before each request and checks if the session has been inactive for more than 1 hour. If so, it clears the session and redirects the user to the login page.

### Hard-Coded Credentials

Another critical aspect of application security is ensuring that credentials are not hard-coded within the application code. Hard-coded credentials can lead to severe security vulnerabilities if the code is exposed or leaked.

#### What Are Hard-Coded Credentials?

Hard-coded credentials refer to usernames, passwords, API keys, or other sensitive information that are embedded directly into the source code of an application. This practice is highly discouraged because it makes it easy for attackers to extract these credentials if they gain access to the source code.

#### Why Avoid Hard-Coded Credentials?

Hard-coding credentials is a significant security risk because it exposes sensitive information to anyone who has access to the source code. This includes developers, testers, and even potential attackers who might gain access to the code through various means, such as a data breach or a misconfigured repository.

#### Real-World Examples

One notable example of the consequences of hard-coded credentials is the Equifax data breach in 2017. The breach was partly attributed to the use of default credentials for an Apache Struts server, which were not changed from their default values. This allowed attackers to exploit a known vulnerability in the server software.

Another example is the Capital One data breach in 2019, where an attacker gained access to sensitive customer data by exploiting a misconfigured web application firewall. The attacker was able to access the source code of the application, which contained hard-coded credentials for accessing internal systems.

#### How to Prevent Hard-Coded Credentials

To prevent the use of hard-coded credentials, developers should follow best practices for managing sensitive information:

1. **Use Environment Variables**: Store sensitive information in environment variables rather than hard-coding them in the source code. This allows the credentials to be managed separately from the codebase.

2. **Configuration Files**: Use configuration files to store sensitive information, and ensure these files are not included in version control systems.

3. **Secret Management Tools**: Utilize secret management tools such as HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault to securely store and manage credentials.

4. **Code Reviews**: Conduct regular code reviews to identify and remove any instances of hard-coded credentials.

Here’s an example of how to use environment variables to manage credentials in a Python application:

```python
import os

# Load credentials from environment variables
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

# Use the credentials to connect to a database
# db_connection = DatabaseConnection(username, password)
```

In this example, the credentials are stored in environment variables (`DB_USERNAME` and `DB_PASSWORD`) rather than being hard-coded in the source code.

### Authentication and Session Management

Proper authentication and session management are essential for securing web applications. These mechanisms ensure that users are correctly identified and that their sessions are managed securely.

#### What is Authentication?

Authentication is the process of verifying the identity of a user. This typically involves validating a username and password combination, but can also include other forms of authentication such as multi-factor authentication (MFA).

#### What is Session Management?

Session management refers to the mechanisms used to maintain a user's state across multiple requests. This typically involves generating a session identifier (session ID) that is used to track the user's session.

#### How to Properly Manage Sessions

To properly manage sessions, developers should follow these best practices:

1. **Use Secure Cookies**: Ensure that session cookies are marked as `HttpOnly` and `Secure`. This prevents client-side scripts from accessing the cookie and ensures that the cookie is only sent over HTTPS.

2. **Regenerate Session IDs**: Regenerate the session ID after successful authentication to prevent session fixation attacks.

3. **Implement Inactivity Timeout**: As discussed earlier, implement an inactivity timeout to automatically log out users after a period of inactivity.

4. **Use Strong Encryption**: Ensure that all communication between the client and server is encrypted using strong encryption protocols such as TLS 1.2 or higher.

5. **Store Session Data Securely**: Store session data securely on the server side, and avoid storing sensitive information in client-side storage such as local storage or cookies.

Here’s an example of how to implement secure session management in a Node.js application using Express and Passport:

```javascript
const express = require('express');
const passport = require('passport');
const session = require('express-session');

const app = express();

// Configure session middleware
app.use(session({
  secret: 'your_secret_key',
  resave: false,
  saveUninitialized: true,
  cookie: {
    httpOnly: true,
    secure: true,
    maxAge: 3600000 // 1 hour
  }
}));

// Configure Passport
app.use(passport.initialize());
app.use(passport.session());

// Define routes
app.get('/', (req, res) => {
  res.send('Welcome to the Home Page!');
});

app.get('/login', (req, res) => {
  res.send('''
    <form method="post" action="/login">
      <input type="text" name="username" placeholder="Username">
      <input type="password" name="password" placeholder="Password">
      <input type="submit" value="Login">
    </form>
  ''');
});

app.post('/login', passport.authenticate('local', { failureRedirect: '/login' }), (req, res) => {
  res.redirect('/');
});

// Start the server
app.listen(3000, () => {
  console.log('Server started on port 3000');
});
```

In this example, the session middleware is configured to use a secret key, mark the session cookie as `HttpOnly` and `Secure`, and set a maximum age of 1 hour. The Passport middleware is used to handle authentication.

### How to Prevent / Defend Against Authentication-Related Attacks

To defend against authentication-related attacks, developers should implement the following measures:

1. **Use Strong Password Policies**: Enforce strong password policies that require users to create complex passwords and change them regularly.

2. **Implement Multi-Factor Authentication (MFA)**: Require users to provide additional forms of authentication, such as a one-time code sent to their phone or email.

3. **Monitor for Suspicious Activity**: Monitor user activity for signs of suspicious behavior, such as multiple failed login attempts or unusual access patterns.

4. **Use CAPTCHA**: Implement CAPTCHA to prevent automated bots from performing brute-force attacks.

5. **Regularly Update and Patch**: Keep all software and dependencies up to date to protect against known vulnerabilities.

Here’s an example of how to implement MFA using Google Authenticator in a Node.js application:

```javascript
const express = require('express');
const passport = require('passport');
const session = require('express-session');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

const app = express();

// Configure session middleware
app.use(session({
  secret: 'your_secret_key',
  resave: false,
  saveUninitialized: true,
  cookie: {
    httpOnly: true,
    secure: true,
    maxAge: 3600000 // 1 hour
  }
}));

// Configure Passport
app.use(passport.initialize());
app.use(passport.session());

passport.use(new GoogleStrategy({
  clientID: 'your_client_id',
  clientSecret: 'your_client_secret',
  callbackURL: 'http://localhost:3000/auth/google/callback'
}, (accessToken, refreshToken, profile, done) => {
  // Save the user's profile in the session
  done(null, profile);
}));

// Define routes
app.get('/', (req, res) => {
  res.send('Welcome to the Home Page!');
});

app.get('/login', (req, res) => {
  res.send('''
    <form method="get" action="/auth/google">
      <input type="submit" value="Login with Google">
    </form>
  ''');
});

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/auth/google/callback', passport.authenticate('google', { failureRedirect: '/login' }), (req, res) => {
  res.redirect('/');
});

// Start the server
app.listen(3000, () => {
  console.log('Server started on port 3000');
});
```

In this example, the Google OAuth 2.0 strategy is used to authenticate users via Google. This provides an additional layer of security by leveraging Google's authentication mechanisms.

### Conclusion

Proper session management and the avoidance of hard-coded credentials are critical components of web application security. By implementing inactivity timeouts, using secure session management techniques, and avoiding hard-coded credentials, developers can significantly reduce the risk of authentication-related attacks. Regular monitoring, strong password policies, and the use of multi-factor authentication further enhance the security of web applications.

### Practice Labs

For hands-on experience with these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on session management and authentication.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide practical experience in identifying and mitigating security vulnerabilities related to session management and authentication.

---
<!-- nav -->
[[14-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 2/00-Overview|Overview]] | [[16-Software Supply Chain Security|Software Supply Chain Security]]
