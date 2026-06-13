---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.07 Sliver Armory Installing Custom Extensions"
---

# 95.07 Sliver Armory Installing Custom Extensions

## Introduction to Sliver Armory

One of the defining features of mature C2 frameworks like Cobalt Strike is the ability to extend functionality dynamically without recompiling the main implant. Sliver implements this capability through the **Sliver Armory**. 

The Armory is a package manager and extension ecosystem that allows operators to seamlessly integrate third-party tools, Beacon Object Files (BOFs), .NET assemblies, and custom extensions directly into the Sliver client. This mechanism significantly reduces the size of the initial payload, as post-exploitation tooling is only downloaded and loaded into memory on an as-needed basis.

## Armory Architecture and Extension Flow

Below is an ASCII diagram illustrating how Armory interacts with the Sliver client, server, and the target implant.

```text
    [ GitHub / External Repo ]                 [ Operator's Sliver Client ]
              |                                             |
              | 1. 'armory install' fetches                 |
              |    extension manifest & binaries            |
              v                                             v
+-----------------------------+               +-----------------------------+
|    Sliver Armory Registry   |               |    Local Client Storage     |
| (JSON manifests, aliases)   | <-----------> |  (~/.sliver-client/aliases) |
+-----------------------------+               +-----------------------------+
                                                            |
                                                            | 2. Operator runs 
                                                            |    e.g., 'seatbelt'
                                                            v
                                              +-----------------------------+
                                              |     Sliver C2 Server        |
                                              |  (Handles routing, caching) |
                                              +-----------------------------+
                                                            |
                                                            | 3. Extension payload
                                                            |    sent via MTLS/WG
                                                            v
                                              +-----------------------------+
                                              |       Sliver Implant        |
                                              |       (Target System)       |
                                              |                             |
                                              |  +-----------------------+  |
                                              |  |  In-Memory Execution  |  |
                                              |  |  (.NET CLR / BOF Ldr) |  |
                                              |  +-----------------------+  |
                                              +-----------------------------+
```

## Installing Extensions via Armory

Sliver maintains an official repository of widely used Red Team tools that have been pre-packaged for the Armory. 

### Initializing the Armory
Before installing tools, you must update the package manifest from the remote repository.
```bash
sliver > armory update

[*] Updating armory index...
[*] Successfully updated armory index
```

### Searching for Packages
You can search the registry to see what tools are available.
```bash
sliver > armory search seatbelt

 Name      Version   Type        Description 
 ========  ========  ========    =========== 
 seatbelt  1.0.0     assembly    Seatbelt is a C# project that performs...
```

### Installing an Extension
Installing an extension downloads it to the client and configures the necessary aliases so you can call it directly from the interactive beacon/session prompt.
```bash
sliver > armory install seatbelt

[*] Installing 'seatbelt' (v1.0.0) ...
[*] Successfully installed 'seatbelt'
[*] Run `seatbelt --help` to see usage
```

## Types of Armory Extensions

Armory supports several extension formats, dictating how the implant executes the tool on the target:

1. **.NET Assemblies (`assembly`)**: The implant loads the CLR (Common Language Runtime) into its process space, reflects the .NET binary (e.g., Rubeus, Seatbelt) into memory, and executes it. This is powerful but can be noisy due to AMSI and ETW telemetry.
2. **Beacon Object Files (`bof`)**: Unlinked C code compiled to object files. The implant acts as the linker, resolving internal symbols and executing the code directly in memory. BOFs are extremely lightweight and OPSEC-safe compared to .NET.
3. **Shared Libraries (`extension`)**: Standard shared libraries (.dll or .so) that expose specific exported functions expected by the Sliver implant.

## Managing Aliases and Extensions

Extensions are primarily interacted with via command aliases. When you type `rubeus`, Sliver understands this is an alias for `execute-assembly` pointing to the downloaded Rubeus binary.

To view installed aliases:
```bash
sliver > aliases

 Alias        Command                   Description
 ===========  =======================   ===========================
 rubeus       execute-assembly rubeus   Rubeus is a C# toolset...
 seatbelt     execute-assembly seatbelt Seatbelt performs...
 nanodump     bof nanodump              A flexible tool to create...
```

### Air-Gapped Environments
In highly secure environments where the Sliver client does not have internet access to reach the Armory registry, you can manually install extensions:
1. Download the extension `.tar.gz` and `armory.json` manifest from an internet-connected machine.
2. Transfer them to the air-gapped client.
3. Use the `armory install /path/to/extension_folder` command to install locally.

## Custom Extension Development

To add custom, proprietary Red Team tools to your Armory:
1. Create a directory for your tool.
2. Create an `armory.json` file defining the command alias, argument parsing, OS compatibility, and binary path.
3. Package your tool (BOF or .NET assembly) in the directory.
4. Run `armory install .` locally.

### Example `armory.json` snippet
```json
{
  "name": "my_custom_bof",
  "version": "1.0.0",
  "command_name": "stealth_recon",
  "type": "bof",
  "files": [
    {
      "os": "windows",
      "arch": "amd64",
      "path": "bin/stealth_recon.x64.o"
    }
  ],
  "help": "Executes stealth reconnaissance via BOF."
}
```

## Real-World Attack Scenario

### Post-Exploitation and Reconnaissance
The Red Team has established a Sliver session on a target workstation but needs to map the Active Directory environment without triggering EDR alerts. Dropping `SharpHound.exe` to disk is out of the question.

1. The operator opens their Sliver console and runs `armory install bofhound`.
2. BofHound is a BOF implementation of BloodHound ingestors, making it vastly stealthier than the C# equivalent, as it does not require loading the .NET CLR or triggering AMSI.
3. The operator switches to the active session and executes the newly available alias: `bofhound --ldap`.
4. The Sliver implant requests the BOF payload from the server, receives it over the encrypted WG tunnel, allocates memory, resolves the Windows API imports, and executes the code block.
5. The AD enumeration results are streamed back to the C2 server in real-time, allowing the operator to plan lateral movement with zero disk artifacts and minimal memory footprint.

## Chaining Opportunities

- **AMSI/ETW Patching prior to .NET:** Use Armory to run a BOF that patches AMSI/ETW, and then immediately run an Armory `.NET` assembly extension securely.
- **Evasion Hooks:** Integrate custom unhooking BOFs via Armory before executing standard modules.
- **Lateral Movement:** Use Armory to load specialized BOFs for WMI or DCOM lateral movement, chaining with details from [[09 - Sliver Lateral Movement PsExec WMI]].

## Related Notes

- [[05 - Sliver Session Management and Post-Exploitation]]
- [[06 - Sliver Stagers and Shellcode Execution]]
- [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]
- [[10 - Integrating BOFs Beacon Object Files in Sliver]]
- [[12 - Advanced Active Directory Enumeration Techniques]]
