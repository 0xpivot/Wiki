---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.15 Mythic Scripting API Automating Operations"
---

# 97.15 Mythic Scripting API Automating Operations

## 1. Introduction to Mythic API and Automation

Red Team operations, especially at scale, require executing repetitive tasks across dozens or hundreds of compromised hosts. Manually issuing situational awareness commands (`whoami`, `ipconfig`, `netstat`) upon every new callback is inefficient and prone to operator error. 

Mythic provides a comprehensive GraphQL and REST API layer, designed heavily for automation. The official `mythic` PyPI package provides Python wrappers that allow operators to interact programmatically with the C2 server, script complex workflows, automate payload generation, and stream events to external systems.

## 2. Scripting API Mechanics

Mythic's API uses standard API tokens for authentication. Operations can be scripted externally using Python. The `mythic` library leverages asynchronous programming (`asyncio`) to handle the heavy websocket connections required for GraphQL subscriptions.

### 2.1 Generating API Tokens
To authenticate, an operator must generate an API token from the Mythic UI (Profile -> API Tokens). These tokens inherit the RBAC permissions of the operator who generated them.

### 2.2 ASCII Diagram: Scripting API Automation Loop

```text
+--------------------------------------------------------------------------------+
|                        Mythic Scripting Architecture                           |
|                                                                                |
|  +------------------+         GraphQL Subscriptions          +--------------+  |
|  |                  | <------------------------------------- |              |  |
|  |  Mythic Server   |                                        |  Python Bot  |  |
|  |  (GraphQL API)   | -------------------------------------> |  (mythic)    |  |
|  +------------------+          Event Feed Stream             +--------------+  |
+---------+------------------------------------------------------------+---------+
          |                                                            |
          | (1) New Apollo Agent checks in                             |
          |                                                            |
          v                                                            |
     Registers Agent                                                   |
          |                                                            |
          +---------------------(2) Broadcasts New Callback------------>
                                                                       |
                                         (3) Script detects callback   |
                                         (4) Script logic triggers     |
                                                                       |
          <---------------------(5) API Request: issue `whoami`--------+
          |
          v
     Tasks Apollo Agent
          |
          +---------------------(6) Output returns to Script----------->
                                                                       |
                                         (7) Script parses output      |
                                         (8) Script pushes to Splunk   |
```

## 3. Automating Tasking upon New Callbacks

One of the most powerful use cases for the scripting API is "Situational Awareness Automation." When a new payload executes, an automated script can immediately profile the host without operator intervention.

### 3.1 Python Script Example: Auto-Tasking
Below is a robust example utilizing the `mythic` Python library to listen for new callbacks and automatically issue commands.

```python
import asyncio
from mythic import mythic_rest
from mythic import mythic_graphql

MYTHIC_IP = "127.0.0.1"
MYTHIC_PORT = 7443
API_TOKEN = "your_api_token_here"

async def handle_new_callback(mythic, callback_data):
    print(f"[*] New callback detected! UUID: {callback_data['agent_callback_id']}")
    
    # Extract agent ID
    agent_id = callback_data["id"]
    
    # Define tasks to run automatically
    tasks_to_run = [
        {"command": "whoami", "params": ""},
        {"command": "ipconfig", "params": ""},
        {"command": "shell", "params": "netstat -anp tcp"}
    ]

    for task in tasks_to_run:
        print(f"[*] Issuing task: {task['command']}")
        # Submit the task via GraphQL mutation
        resp = await mythic.execute_custom_query(
            mythic_graphql.create_task_mutation,
            variables={
                "callback_id": agent_id,
                "command": task["command"],
                "params": task["params"]
            }
        )
        if resp:
            print(f"[+] Task {task['command']} queued successfully.")

async def listen_for_callbacks():
    print("[*] Connecting to Mythic API...")
    # Initialize connection
    mythic = await mythic_rest.login_with_apitoken(
        server_ip=MYTHIC_IP,
        server_port=MYTHIC_PORT,
        apitoken=API_TOKEN,
        ssl=True
    )
    
    print("[*] Listening for new callbacks...")
    # Subscribe to new callback events via GraphQL websockets
    async for callback in mythic.subscribe_new_callbacks():
        # Dispatch handler asynchronously
        asyncio.create_task(handle_new_callback(mythic, callback))

if __name__ == "__main__":
    asyncio.run(listen_for_callbacks())
```

## 4. Automating Payload Generation

During a large campaign, Red Teams often need payloads configured with unique URLs or specific obfuscation parameters to rotate through heavily filtered environments. 

Instead of manually clicking through the UI, the API allows for dynamic payload generation. A script can pull a list of 50 new, categorized domain names, iterate through them, and instruct Mythic to generate 50 unique payload binaries pointing to each domain, downloading them to a staging server automatically.

## 5. Data Extraction and Integration (BloodHound / SIEM)

The scripting API is heavily used for data extraction. 
- **BloodHound Integration:** Scripts can monitor for the completion of specific BOFs (like `ldap_enum`), intercept the JSON output, and pipe it directly into a Neo4j database, building a live BloodHound graph as the operation progresses without ever dropping files to disk.
- **Reporting & SIEM:** Red Teams can synchronize Mythic's command execution logs directly into the Blue Team's SIEM (like Splunk or ELK) during purple team exercises, providing a unified view of attacker actions mapped directly to telemetry.

## 6. Real-World Attack Scenario

**The Environment:** A massive internal network with thousands of subnets. The Red Team has established a foothold but needs to map internal domain trusts and pivot aggressively before defensive teams notice the beaconing.

**The Execution:**
1. The Team Lead runs a Python automation script against the Mythic API.
2. An operator compromises an IT admin's workstation and executes an Apollo payload.
3. The script instantly detects the new high-privilege callback.
4. Without human intervention, the script tasks the agent to load and execute the `bof_run ad_enum` command.
5. The BOF output returns. The script parses the domain trust relationships from the JSON output and identifies a high-value trusted domain.
6. The script automatically generates a new SMB named-pipe payload configured specifically for lateral movement into that trusted domain.
7. The operator returns from a coffee break to find the network mapped and a custom payload ready for deployment, saving critical operational hours.

## 7. Chaining Opportunities

- **[[11 - Integrating BOFs in Mythic]]**: Automate the execution of BOFs for stealthy situational awareness. The script issues BOFs instead of native agent commands to preserve OpSec.
- **[[13 - Mythic Event Feed and Team Collaboration]]**: Use the API to inject custom alert messages into the Mythic Event feed (e.g., "Script successfully mapped Bloodhound data for Callback 42").
- **[[14 - Evading Signatures with Unique Mythic Payloads]]**: Automate the mass generation of highly obfuscated payloads, rotating C2 profiles and sleep timers automatically.

## 8. Related Notes
- [[11 - Integrating BOFs in Mythic]]
- [[13 - Mythic Event Feed and Team Collaboration]]
- [[14 - Evading Signatures with Unique Mythic Payloads]]
- [[88 - Automated BloodHound Ingestion]]
- [[92 - Purple Team SIEM Integrations]]
