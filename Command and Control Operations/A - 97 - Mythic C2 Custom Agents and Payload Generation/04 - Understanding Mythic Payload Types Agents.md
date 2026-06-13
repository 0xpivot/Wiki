---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.04 Understanding Mythic Payload Types Agents"
---

# 97.04 Understanding Mythic Payload Types Agents

## 1. The Anatomy of a Mythic Payload Type

In the context of the Mythic framework, a "Payload Type" is synonymous with a specific "Agent" or "Implant." Agents are the actual malicious binaries, scripts, or shellcode executed on the target system (e.g., Apollo, Athena, Poseidon, Medusa).

Mythic’s architecture dictates a strict separation of logic: the core Mythic framework knows absolutely nothing about the internal workings, programming language, memory execution flow, or compilation process of any specific agent. Instead, all logic regarding how an agent is built, what commands it natively supports, and how to format those commands is encapsulated within a dedicated, isolated Docker container specific to that Payload Type.

### The Two Core Components of an Agent
1.  **The Translation Container (Backend Builder):** A Docker container running alongside the Mythic Server. It is typically written in Python (leveraging the official Mythic scripting library) and is responsible for defining the agent's capabilities to the Web UI, parsing operator input, and physically compiling the final binary using installed toolchains (like GCC, MinGW, or the .NET SDK).
2.  **The Implant Source Code (Frontend):** The actual source code (written in C#, Golang, C, Rust, or Python) that executes on the target system. The Translation Container modifies and compiles this code dynamically during the payload generation phase.

## 2. The Dynamic Payload Build Process

When an operator clicks "Generate Payload" in the Mythic React UI, a complex, highly automated, asynchronous workflow is triggered behind the scenes.

1.  **UI Configuration & Parameter Selection:** The operator selects the target OS, architecture, C2 Profile (e.g., HTTP), cryptographic keys, and specifically checks which commands they want compiled into the agent (allowing for modular, lightweight payloads).
2.  **Task Dispatch via AMQP:** The Mythic core takes this entire configuration as a JSON blob and publishes it to the RabbitMQ exchange specifically bound to that Payload Type.
3.  **Container Execution:** The Payload Type container picks up the request from the queue. Its internal Python `builder.py` script executes.
4.  **Source Code Modification & Compilation:** The `builder.py` script dynamically modifies the implant's raw source code on the fly. It injects the C2 profile settings (URIs, headers), hardcodes the AES encryption keys, and sets the sleep intervals directly into the source. It then invokes the relevant compiler (e.g., `dotnet publish -c Release -r win-x64` for a C# agent).
5.  **Return and Storage:** Once successfully compiled, the resulting binary (or generated shellcode) is passed back via RabbitMQ to the Mythic Server, which stores it securely and makes it available for download via the UI.

## 3. Payload Build Architecture and Compilation Diagram

```text
+---------------------+
|  Operator (Web UI)  |
| 1. Selects Options  |
| 2. Clicks "Build"   |
+---------+-----------+
          | (GraphQL Mutation / JSON config)
          v
+---------------------+
|  Mythic Core Server |
|  Records Request    |
+---------+-----------+
          | (Message Published to RabbitMQ)
          v
+-------------------------------------------------------------+
|               PAYLOAD TYPE CONTAINER (e.g., Apollo)         |
|                                                             |
|  +----------------+     +-------------------------------+   |
|  | builder.py     | --> | 1. Parse Operator JSON Config |   |
|  | (Python Core)  |     | 2. Modify C# Source Files     |   |
|  +----------------+     | 3. Inject Crypto/AES Keys     |   |
|                         | 4. Select Build Profile       |   |
|                         +---------------+---------------+   |
|                                         |                   |
|                                         v                   |
|                         +---------------+---------------+   |
|                         | .NET Core SDK / Compiler      |   |
|                         | `dotnet build /p:Obfuscate=1` |   |
|                         +---------------+---------------+   |
|                                         |                   |
|                                         v                   |
|  +----------------+     +-------------------------------+   |
|  | Result Payload | <-- | Output: apollo_artifact.exe   |   |
|  | (to RabbitMQ)  |     +-------------------------------+   |
+-------------------------------------------------------------+
          | (Compiled Binary sent back via RPC)
          v
+---------------------+
|  Mythic Core Server | (Available for Download / Hosting)
+---------------------+
```

## 4. Defining Commands and Strict Parameter Typing

A highly unique and powerful aspect of Mythic is how strictly it parses and validates commands before they ever leave the C2 server. Inside the Payload Type container, every single command the agent supports must have an associated Python class definition.

### Command Definition Example (Python snippet inside the Container)
```python
from mythic_container.MythicCommandBase import *

class ShellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command to execute via cmd.exe",
                parameter_group_info=[ParameterGroupInfo(ui_position=1)]
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise Exception("Require command to execute.")
        self.add_arg("command", self.command_line)

class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell [command]"
    description = "Execute a command via cmd.exe /c."
    version = 1
    author = "@redteamer"
    argument_class = ShellArguments
    attackmapping = ["T1059", "T1059.003"] # Direct MITRE Mapping

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        # This function formats the user input into exactly what the agent expects
        # E.g., packing it into a specific JSON struct or byte array
        return task
```

Because of this strict typing and explicit parameter definition, the Mythic Web UI can automatically generate visual forms for complex commands, perform rigorous input validation before sending tasking to the target (saving the agent from crashing due to bad input), and map operations directly to MITRE ATT&CK techniques automatically.

## 5. Cross-Platform vs. Native Agents

Mythic supports a wide, diverse ecosystem of agents developed by the community:
*   **Golang Agents (Poseidon, Athena):** Highly versatile as they can be cross-compiled extremely easily within the Docker container for Windows, Linux, and macOS. They are often heavier (larger file sizes) due to statically linked libraries, but offer unparalleled cross-platform consistency.
*   **.NET/C# Agents (Apollo):** Primarily target Windows environments. They leverage the deep, native integration of the CLR (Common Language Runtime) with the Windows OS, allowing for advanced evasion techniques like Assembly execution, BOFs, and in-memory module loading.
*   **JXA / Objective-C Agents (Apfell):** Specialized for macOS targeting, leveraging Apple's native scripting bridges and bypassing many standard macOS security controls.

## 6. Real-World Attack Scenario

### Customizing an Agent for Advanced AV/EDR Evasion

A red team is operating in an environment protected by a mature EDR solution (e.g., CrowdStrike Falcon) that heavily signatures standard, out-of-the-box Mythic agents based on strings and exported functions.

1.  **Source Code Modification:** Because the Payload Type runs locally in Docker and mounts its source code directly to the host filesystem, the operator can directly edit the agent's source code on the Mythic server host without needing complex development environments. They modify `Apollo`'s C# source to change class names, obfuscate hardcoded strings, and alter the execution flow of the main beaconing loop.
2.  **Custom Build Pipeline Injection:** The operator alters the Python `builder.py` script within the Apollo container to integrate a third-party obfuscator (like ConfuserEx or a custom LLVM obfuscation pass) immediately after the `.NET` compilation step, but before sending the final binary back to the Mythic Server.
3.  **On-the-Fly Obfuscated Generation:** The operator returns to the Mythic UI, selects their custom build profile, and clicks generate. The Docker container executes the customized build pipeline, resulting in a highly obfuscated, uniquely signatured binary that easily bypasses the target's static EDR analysis.

This ability to dynamically hot-wire the compilation process without touching the core C2 framework is a massive advantage in modern evasive operations.

## 7. Chaining Opportunities

*   Agents generated via this process must be logically paired with [[03 - Mythic C2 Profiles HTTP WebSocket SMB]] to establish a communication route.
*   Specific, deep-level capabilities of advanced agents, such as BOF execution and SOCKS proxying, are detailed in agent-specific notes like [[05 - Apollo Agent Advanced Windows C2]].
*   The modular build system can be chained with automated AV evasion pipelines described in [[88 - Automated Payload Obfuscation and CI-CD Pipelines]].

## 8. Related Notes

*   [[01 - Introduction to Mythic C2 Architecture and Docker]]
*   [[03 - Mythic C2 Profiles HTTP WebSocket SMB]]
*   [[05 - Apollo Agent Advanced Windows C2]]
*   [[61 - Evading EDR via Custom Payload Engineering]]
