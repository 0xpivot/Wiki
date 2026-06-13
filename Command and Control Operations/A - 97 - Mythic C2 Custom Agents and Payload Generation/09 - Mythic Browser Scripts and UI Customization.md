---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.09 Mythic Browser Scripts and UI Customization"
---

# Mythic Browser Scripts and UI Customization

## Introduction
One of the most powerful quality-of-life and operational efficiency features of the Mythic C2 framework is its extensibility via Browser Scripts. During high-tempo Red Team engagements, reading raw JSON, heavily nested arrays, or massive text blobs from command outputs (like `ls`, `ps`, or BloodHound data) is inefficient and error-prone. 

Mythic Browser Scripts allow operators to use pure JavaScript/React to parse the raw data returned by an agent and render it into beautiful, interactive, and actionable UI components directly within the Mythic web interface.

## Core Capabilities
- **Data Parsing**: Convert raw string or JSON output into structured JavaScript objects.
- **Custom Tables**: Render sortable, filterable tables for processes, files, or network connections.
- **Interactive Buttons**: Embed action buttons (e.g., "Kill Process", "Download File") directly alongside the parsed data.
- **Color Coding**: Highlight specific data points (e.g., red for `root`/`SYSTEM` processes, green for active connections).
- **React Integration**: Leverage Mythic's underlying React framework to build complex UI modules seamlessly.

## Architecture and Execution Flow

Browser scripts run client-side in the operator's web browser, ensuring the Mythic server remains performant.

```text
+-------------------+      +-------------------+       +-----------------------+
|  Mythic Agent     |      |  Mythic Server    |       |  Operator Browser     |
|  (Target System)  |      |  (Database)       |       |  (UI Rendering)       |
+-------------------+      +-------------------+       +-----------------------+
         |                          |                               |
         | 1. Executes task         |                               |
         |    "ps"                  |                               |
         |                          |                               |
         | 2. Returns JSON array    |                               |
         |------------------------->| 3. Stores raw response        |
                                    |------------------------------>|
                                                                    | 4. Browser Script
                                                                    |    Intercepts Data
                                                                    |
                                                          +-------------------+
                                                          | UI Parsing Engine |
                                                          | (JavaScript)      |
                                                          +-------------------+
                                                                    | 5. Renders
                                                                    v
                                                          [ Interactive Table ]
```

## Anatomy of a Browser Script

A Mythic Browser Script is simply a JavaScript function registered to a specific command. Mythic provides the `response` object, and your script returns a React UI component or a formatted string.

### Basic JSON Parsing Example
If your agent returns a JSON string for a `ps` command:
`[{"pid": 1234, "name": "explorer.exe", "user": "DOMAIN\\User"}]`

The browser script processes this:
```javascript
function(task, responses){
    if(responses.length > 0){
        try{
            let data = JSON.parse(responses[0]);
            let output_table = [];
            for(let i = 0; i < data.length; i++){
                output_table.push({
                    "PID": {"plaintext": data[i]["pid"]},
                    "Name": {"plaintext": data[i]["name"]},
                    "User": {"plaintext": data[i]["user"]}
                });
            }
            return {
                "table": [
                    {
                        "headers": [
                            {"plaintext": "PID", "type": "number", "width": 100},
                            {"plaintext": "Name", "type": "string"},
                            {"plaintext": "User", "type": "string"}
                        ],
                        "rows": output_table,
                        "title": "Process List"
                    }
                ]
            };
        }catch(error){
            return responses[0]; // Fallback to raw text
        }
    }
    return "";
}
```

## Adding Interactive Actions

The true power of browser scripts is turning data into actionable intelligence. You can embed tasking buttons directly into the rows of your custom tables.

For instance, in a File Browser script, you can add a "Download" button:
```javascript
"Actions": {
    "button": {
        "name": "Download",
        "type": "task",
        "ui_feature": "file_browser:download",
        "parameters": JSON.stringify({
            "path": data[i]["full_path"]
        })
    }
}
```
When clicked, Mythic automatically tasks the agent to download that specific file.

## Operational Security (OPSEC) via UI

While Browser Scripts run client-side and don't interact with the target, they severely impact operator OPSEC:
- **Reduced Mistakes**: Clearly structured data prevents operators from accidentally killing critical infrastructure processes.
- **Contextual Awareness**: Scripts can automatically highlight processes associated with EDR (e.g., highlighting `csfalconservice.exe` in red), ensuring operators are aware of hostile software before attempting lateral movement.
- **Speed**: In assumed breach scenarios where time is limited, quickly parsing domain trust JSON files into visual links saves hours.

## Real-World Attack Scenario

### The Problem
During a large-scale Active Directory compromise, the Red Team executes a custom BOF (Beacon Object File) via their Mythic agent to query all Kerberos tickets in memory (similar to `Rubeus klist`). The output is a massive, unreadable blob of base64 and hex strings spanning thousands of lines.

### The Solution
The operator quickly writes a Mythic Browser Script. The script intercepts the raw BOF output, decodes the necessary JSON wrappers, and extracts the `Service Principal Name (SPN)`, `Client Name`, `End Time`, and the base64 `.kirbi` payload.

The script renders an interactive table. Crucially, it adds a "Pass-the-Ticket" button next to each row. 

### The Attack
Instead of manually copying base64 blobs, decoding them, and issuing separate inject commands, the operator simply scrolls through the neat table, finds a high-privileged `krbtgt` ticket, and clicks "Pass-the-Ticket". The UI automatically tasks the agent to inject that specific ticket into the current session, enabling immediate lateral movement.

## Development and Debugging Tips

- **Console Logs**: You can use `console.log()` in your browser scripts and view the output in your Chrome/Firefox Developer Tools (F12). This is critical for debugging complex JSON parsing.
- **Version Control**: Store your browser scripts in a Git repository. Mythic allows you to sync browser scripts directly from a URL or UI upload.
- **Handling Chunked Responses**: Remember that Mythic agents often send large data in chunks. Ensure your script iterates over all elements in the `responses` array before rendering the final table.

## Chaining Opportunities
- Use parsed output to inform lateral movement strategies: [[13 - Advanced Active Directory Exploitation]]
- Integrate browser scripts with custom agent capabilities: [[08 - Customizing Mythic Agent Builds and OPSEC]]

## Related Notes
- [[06 - Poseidon Agent macOS and Linux C2]]
- [[07 - Medusa Agent Cross-Platform Python C2]]
