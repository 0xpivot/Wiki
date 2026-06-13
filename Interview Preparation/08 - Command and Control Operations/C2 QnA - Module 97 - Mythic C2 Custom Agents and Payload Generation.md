---
tags: [interview, c2, red-team, qna, scenario]
difficulty: expert
module: "Interview Prep - Command and Control Operations"
topic: "QnA - C2 Module 97"
---

# Mythic C2 Custom Agents and Payload Generation QnA

```text
    [ Red Team Operations ]
              | (Web GUI / GraphQL API / Python scripting)
              V
    +---------------------------------------------------+
    |                   Mythic Core                     |
    |            (Team Server / UI / DB)                |
    +---------------------------------------------------+
       |               |                 |
       V               V                 V
  +---------+     +---------+      +-----------+
  | HTTP    |     | WebSock |      | SMB Pipe  | <-- C2 Profiles
  | Profile |     | Profile |      | Profile   |     (Docker)
  +---------+     +---------+      +-----------+
       |               |                 |
  =============================================       
                   INTERNET                           
  =============================================       
       |               |                 |
  +---------+     +---------+      +-----------+
  | Apollo  |     | Athena  |      | Poseidon  | <-- Payload Types
  | (Win/C#)|     | (.NET)  |      | (macOS)   |     (Docker)
  +---------+     +---------+      +-----------+
```

## Real-World Attack Scenario

A highly specialized Red Team is tasked with compromising a mixed-OS
environment utilizing macOS for executive workstations and hardened Linux
servers for database hosting. Traditional C2 frameworks heavily focused on
Windows are inadequate. The team deploys Mythic C2 due to its modular,
Docker-based architecture. They spin up custom C2 profiles utilizing
WebSockets for real-time interactive control, bypassing strict HTTP request-
response filtering. For the macOS targets, they generate custom `Poseidon`
(Golang) agents tailored specifically for the ARM64 architecture, leveraging
native macOS API calls to evade XProtect and Jamf telemetry. For the Linux
servers, they utilize `Apollo` payloads modified to execute purely in memory
via `memfd_create`. The operators control the entire cross-platform
engagement through Mythic's centralized GraphQL API, automating tasking and
payload generation via custom Python scripts directly integrated with the
Mythic server, heavily utilizing Translation Containers to custom-encrypt
their network streams.

## Formal Technical Questions

### Q1: Describe the architectural design of Mythic C2. How does its use of Docker containers for "Payload Types" and "C2 Profiles" differ from monolithic frameworks?
**Expert Answer:**
Mythic architecture is fundamentally microservice-based and decoupled,
unlike monolithic frameworks like Cobalt Strike or older versions of
Metasploit.
The core of Mythic is just a management interface and database handling
routing, tasking, and the UI via a GraphQL API. It does not natively know
how to build a payload or speak a specific C2 protocol.
Instead, **Payload Types** (e.g., Apollo, Athena, Poseidon) and **C2
Profiles** (e.g., HTTP, WebSockets, SMB) are entirely independent Docker
containers. When an operator requests a new agent, the Mythic core sends the
configuration data to the specific Payload Type container via RabbitMQ. That
container independently compiles the code, embeds the C2 profile logic, and
returns the finished binary to the core.
This means developers can write a completely new C2 agent in Rust, Python,
or Nim, wrap it in a Docker container conforming to Mythic's API, and
instantly integrate it into the framework without modifying the core server
code. This extreme modularity allows Red Teams to constantly swap out
detected agents or protocols with zero downtime or complex server
reconfigurations.

### Q2: What is the significance of the "Translation Container" within the Mythic framework, particularly concerning custom encryption and malleable traffic?
**Expert Answer:**
The Translation Container is a critical component for extending Mythic's
evasive capabilities. While a C2 Profile handles the transport mechanism
(e.g., getting data from point A to B over HTTP), the Translation Container
dictates how the actual payload messages are formatted and encrypted
*before* they are handed to the transport layer.
For example, if an operator writes a custom agent that communicates using a
proprietary, non-standard encryption scheme or utilizes a heavily customized
binary serialization format to evade deep packet inspection, the Mythic core
natively cannot understand these responses.
The operator creates a custom Translation Container that sits between the C2
Profile and the Mythic Core. The agent sends the custom encrypted blob over
HTTP; the HTTP Profile receives it and passes it to the Translation
Container. The Translation Container decrypts and deserializes the custom
format into the standard JSON format that the Mythic Core understands. This
allows absolute freedom in developing bizarre, unrecognizable cryptographic
channels while maintaining full compatibility with the Mythic UI.

### Q3: Explain how Mythic leverages GraphQL. How does this benefit Red Team operators in terms of automation and complex tasking?
**Expert Answer:**
Mythic replaces traditional REST APIs with a comprehensive GraphQL API.
GraphQL allows clients to request exactly the data they need and nothing
more, in a single query.
For Red Team automation, this is immensely powerful. Using the
`mythic_scripting` Python package, operators can script complex workflows.
For example, a script can query the GraphQL endpoint to find all active
agents, filter only those running as `SYSTEM` on Windows, and automatically
issue a command to dump credentials, while simultaneously requesting the
output of those tasks as soon as they complete.
Furthermore, because the entire UI is built on top of this GraphQL API,
anything an operator can click in the browser can be perfectly scripted.
This facilitates rapid deployment of infrastructure, automated payload
generation integrated with CI/CD pipelines, and dynamic, programmatic
responses to events (e.g., if an agent detects an EDR process starting, a
script instantly tasks the agent to terminate its session to prevent
exposure).

### Q4: Detail the process of creating a custom Payload Type in Mythic. What are the essential components required within the Docker container?
**Expert Answer:**
Creating a custom Payload Type requires constructing a Docker container that
interacts with Mythic's RabbitMQ message broker.
The core components include:
1. **The Builder Script:** A Python script (usually extending the
`PayloadType` class from Mythic's libraries) that receives the build
parameters from the UI (e.g., target OS, architecture, chosen C2 profile)
and executes the actual compilation process (like invoking `gcc` or `go
build`).
2. **Command Definitions:** Python classes defining every command the agent
supports (e.g., `ls`, `shell`, `download`). These dictate what arguments the
command takes and how it is rendered in the UI.
3. **The Agent Code:** The actual source code of the malware implant (in
C++, Rust, Nim, etc.), designed to parse the configuration block injected by
the builder and communicate using the defined C2 profile format.
Once these are bundled in a Docker container and registered with the Mythic
core, the new agent becomes instantly available for generation via the GUI.

### Q5: How does Mythic handle "Dynamic Compilation" and what OPSEC advantages does this provide over pre-compiled binaries?
**Expert Answer:**
Dynamic Compilation means the Mythic Payload Type container compiles the
agent from source code *every single time* a payload is requested, rather
than distributing a pre-compiled binary.
During generation, the builder script dynamically injects the specific C2
profile settings, sleep times, AES encryption keys, and custom operator
configurations directly into the source code before invoking the compiler.
The OPSEC advantage is enormous. Every single generated payload has a unique
file hash, unique compilation timestamps, and unique embedded cryptographic
material. If the Blue Team captures one agent and reverses it to extract the
AES key, that key is utterly useless against any other agent deployed during
the operation, as the dynamic compilation process generated a unique key for
the other payloads. It inherently defeats static hash-based IOC sharing.

## Scenario-Based Questions

### Q1: You are targeting an enterprise environment where all traditional HTTP/HTTPS outbound traffic is strictly whitelisted and heavily scrutinized by an advanced proxy. However, Slack and Microsoft Teams are permitted. How can you utilize Mythic's modularity to establish a C2 channel?
**Expert Answer:**
This scenario requires abandoning traditional HTTP profiles entirely.
Mythic's architecture is perfectly suited for this via Third-Party C2
(External C2).
I would deploy or develop a specific C2 Profile Docker container designed
for third-party API integration (e.g., a Slack C2 profile).
When the payload is generated, it is compiled to communicate exclusively via
the Slack API. The agent posts base64 encoded messages to a private Slack
channel acting as the intermediary.
Simultaneously, the Slack C2 Profile container running on the Mythic server
polls the same Slack API. It reads the messages, forwards them to the Mythic
core for processing, and posts the responses back to the Slack channel for
the agent to retrieve. The internal network defenders only see legitimate,
heavily encrypted HTTPS traffic directed to `api.slack.com`, completely
bypassing the proxy whitelisting and HTTP inspection heuristics, as the
traffic appears entirely legitimate.

### Q2: You are leading an operation against a heavy Linux-based infrastructure (e.g., a Kubernetes cluster). Traditional Windows payloads are useless. How do you leverage Mythic's diverse payload types to establish robust access, and how do you achieve memory execution on Linux?
**Expert Answer:**
I would utilize Mythic's specialized cross-platform or Linux-specific
agents, such as `Poseidon` (written in Golang) or a custom Python agent.
For initial access, I might deploy a Python agent as a lightweight stager
since Python is almost universally installed on Linux servers.
To elevate to a robust, fully-featured agent while evading disk forensics, I
would utilize Linux-specific in-memory execution techniques. I would task
the initial agent to download the `Poseidon` binary and execute it via
`memfd_create`.
`memfd_create` allows a process to create an anonymous file in RAM that
behaves like a normal file but is not backed by the physical filesystem. The
agent writes the `Poseidon` ELF binary into this memory region and executes
it directly via `fexecve`. This ensures the primary C2 implant never touches
the disk, evading standard AV file scans and significantly complicating
forensic timelines.

### Q3: During a prolonged engagement, the Blue Team manages to reverse engineer your primary payload and writes YARA signatures that instantly flag any new payloads generated by your current Mythic configuration. How do you rapidly pivot and continue the operation without losing momentum?
**Expert Answer:**
The modularity of Mythic allows for rapid, drastic pivots.
First, I do not need to rebuild my entire infrastructure. The Mythic Core
and my C2 Profiles (the network transport) might still be viable.
The signature is likely targeting the specific Payload Type (e.g., Apollo)
or its compilation artifacts.
To pivot, I would immediately switch to an entirely different Payload Type
available in my Mythic instance (e.g., switching from the C# Apollo agent to
the .NET Athena agent, or a completely custom Nim agent I have prepared in a
standby container). Because these agents use fundamentally different
codebases, compilers, and dependencies, the Blue Team's specific YARA
signatures for the previous agent will fail completely. I can generate the
new payload type using the exact same C2 profile and instantly resume
operations, rendering their reverse engineering efforts temporarily moot.

### Q4: You need to execute highly privileged actions on a Windows domain controller, but deploying a heavy, feature-rich agent like Apollo is too risky. How do you utilize Mythic's capability for specialized, minimal agents?
**Expert Answer:**
In high-risk scenarios, I avoid deploying a massive, noisy agent. Instead, I
utilize a minimalist, specialized Payload Type or write one custom for the
task.
Mythic's microservice architecture allows me to deploy a completely custom,
minimal agent written in C or Assembly that has exactly one command: execute
shellcode.
I would generate this tiny, invisible agent and inject it into a benign
process on the DC. Then, I use Mythic to issue instructions to this minimal
agent. It receives the task, executes the necessary BOF or shellcode to
perform the privileged action (e.g., DCSync), returns the result, and
terminates. By keeping the footprint of the resident agent as close to zero
as possible and moving the operational logic into ephemeral memory
injections, I drastically reduce the risk of detection by aggressive EDRs
scanning the DC.

## Deep-Dive Defensive Questions

### Q1: You are a SOC analyst investigating a suspected compromise. You identify anomalous HTTP traffic, but the structure doesn't match standard Cobalt Strike or Metasploit profiles. How would you attempt to footprint or fingerprint a custom Mythic C2 server exposed to the internet?
**Expert Answer:**
Fingerprinting Mythic requires looking past standard payload signatures and
focusing on the infrastructure and management ports.
1. **Default Port Scans:** By default, the Mythic UI operates on port 7443.
While operators should change this, identifying an unexpected web interface
on 7443 presenting a specific React-based login portal is a strong
indicator.
2. **GraphQL Endpoint Enumeration:** Mythic relies heavily on its GraphQL
API endpoint (usually `/graphql`). Fuzzing suspect servers for exposed
GraphQL endpoints and attempting introspection queries (if not disabled by
the operator) can reveal the underlying schema, instantly confirming the
presence of the Mythic framework.
3. **JARM / JA3 Fingerprinting:** While custom C2 profiles can obfuscate
HTTP headers, the underlying web server (often a reverse proxy or the native
Go/Python server handling the specific profile) will have a distinct TLS
fingerprint. Matching JARM signatures of suspected redirectors against known
default Mythic C2 profile server configurations can help cluster the
infrastructure.

### Q2: A Red Team is using a custom Mythic payload developed in Rust, wrapped in a unique Translation Container employing a custom encryption algorithm. The traffic is perfectly blended into legitimate HTTPS. What advanced endpoint telemetry must defenders rely on to detect this highly customized threat?
**Expert Answer:**
When the network channel is completely dark and the binary is fully custom,
detection must rely entirely on **Endpoint Behavioral Telemetry and
Heuristics**.
1. **Process Lineage and Anomalous Execution:** The initial execution vector
is often the weakest link. Hunting for abnormal process trees—such as
`winword.exe` spawning `powershell.exe` which then executes an unknown
binary, or `w3wp.exe` (IIS) spawning `cmd.exe`—remains highly effective
regardless of the payload's source language.
2. **API Hooking and Telemetry (ETW-TI):** Even a custom Rust payload must
utilize standard OS APIs to interact with the system (e.g., reading files,
enumerating processes, injecting code). Advanced EDR utilizing ETW-TI can
monitor for aggressive or malicious API usage patterns. For instance, a
process rapidly querying the LSA secrets or calling `MiniDumpWriteDump` on
`lsass.exe` is malicious behavior, regardless of the binary's hash or custom
encryption.
3. **Memory Scanning (Unbacked Executable Memory):** If the Rust payload
uses process injection to hide within a legitimate process (like
`explorer.exe`), defenders must utilize memory scanners to identify
executable memory regions (PAGE_EXECUTE_READWRITE or PAGE_EXECUTE_READ) that
are not backed by a valid file on disk. This reveals the injected agent
running in memory.

### Q3: Explain the concept of "Bring Your Own Agent" (BYOA) in the context of Mythic. How does this capability significantly challenge traditional Threat Intelligence (TI) feeds that rely on tracking known malware families?
**Expert Answer:**
"Bring Your Own Agent" (BYOA) refers to the capability of frameworks like
Mythic to allow operators to develop, integrate, and deploy entirely unique,
custom-written malware implants on the fly, rather than relying on off-the-
shelf, publicly analyzed agents like Cobalt Strike's Beacon.
This severely undermines traditional Threat Intelligence. TI feeds primarily
distribute IOCs (Indicators of Compromise) such as file hashes, specific IP
addresses, and known malware signatures (YARA rules).
When an operator utilizes BYOA, the agent is essentially a "zero-day"
implant. It has never been seen in the wild, its hash is unique, its strings
are unknown, and its behavioral patterns might be highly customized.
Consequently, TI feeds are blind to it. Defenders cannot rely on vendor-
provided signatures to stop the payload; they must possess mature,
behavioral-based detection engineering teams capable of identifying the
anomalous actions the custom agent performs on the endpoint, rather than
relying on knowing what the agent looks like statically.

### Q4: How does the GraphQL API in Mythic pose a unique risk if the Red Team fails to secure their own C2 infrastructure?
**Expert Answer:**
The GraphQL API is the heart of Mythic's command and control logic. If an
operator exposes the Mythic server (or fails to secure the API tokens), it
presents a massive risk.
Because GraphQL allows complex, nested querying, an attacker (or a Blue Team
conducting active defense) who gains access to the GraphQL endpoint can
immediately query the entire database. They can pull down the exact
configurations of every active agent, the encryption keys used for C2
profiles, the IP addresses of all compromised targets, and even the full
logs of every command executed by the Red Team.
Unlike a traditional REST API where enumeration requires brute-forcing
endpoints, a single well-crafted introspection query against an unsecured
Mythic instance hands over the entire operational blueprint. This
underscores the necessity of Red Teams applying rigorous OPSEC and access
controls to their own infrastructure.

## Chaining Opportunities
- **Cross-Platform Lateral Movement:** Mythic's diverse payload types allow
seamless pivoting. A compromised Windows workstation (Apollo agent) can be
used to proxy traffic and deploy a macOS agent (Poseidon) into a different
segment of the network.
- **CI/CD Pipeline Integration:** Leveraging the GraphQL API, payload
generation can be integrated into offensive CI/CD pipelines, automatically
recompiling and obfuscating custom agents nightly to evade static signatures
continuously.
- **Dynamic Infrastructure Scaling:** Scripting Mythic to automatically
deploy new Docker-based C2 profiles directly to cloud providers when
existing profiles are flagged by defenders.

## Related Notes
- [[08 - Command and Control Operations]]
- [[Custom Malware Development]]
- [[GraphQL API Security and Exploitation]]
- [[Cross-Platform Exploitation and Lateral Movement]]
- [[Advanced Container Security]]
