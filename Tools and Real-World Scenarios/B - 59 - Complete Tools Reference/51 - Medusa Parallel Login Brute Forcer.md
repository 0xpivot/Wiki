---
tags: [tools, brute-force, password-cracking, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.51 Medusa Parallel Login Brute Forcer"
---

# 59.51 Medusa Parallel Login Brute Forcer

## Overview and Core Mechanics

Medusa is a speedy, massively parallel, modular, login brute-forcer for network services. Designed to be a robust alternative to Hydra, Medusa is specifically tailored to perform rapid password guessing attacks against an array of protocols. The core architecture of Medusa is entirely thread-based (pthreads), which allows it to maintain high efficiency and concurrency when testing multiple credentials across multiple hosts.

Medusa stands out because of its modular design. Each protocol to be tested is represented by a separate module (`.mod` file), meaning developers can easily create new modules to support custom or obscure protocols without altering the core engine. This modularity extends to how Medusa handles connection timeouts, parallel connections, and error handling, making it highly reliable in volatile network environments common in penetration testing.

Unlike some brute-force tools that may crash or hang when encountering unexpected server responses or slow connections, Medusa handles thread pooling and timeout management robustly. It will aggressively attempt to authenticate while gracefully managing connection drops, limiting false negatives that can occur when brute-forcing under heavy network load.

### Key Features
*   **Thread-based Parallelism:** Uses POSIX threads for massive concurrency.
*   **Modular Architecture:** Protocol support is handled via dynamically loaded modules.
*   **Flexible Target Selection:** Can brute-force a single host, or multiple hosts specified in a file.
*   **Flexible Credential Input:** Supports single username/password, dictionary files, and combined credential files (e.g., `user:pass` format).
*   **Service Probing:** Built-in ability to verify if a service is actually running before attacking.
*   **Resume Capability:** Ability to resume an aborted brute-force session.

## Visual Architecture: Medusa Attack Flow

```text
+-------------------+       +----------------------+       +-----------------------+
|   Attacker Node   |       |   Medusa Engine      |       |    Target Network     |
|                   |       |                      |       |                       |
| +---------------+ | Input | +------------------+ |       | +-------------------+ |
| | User/Pass List| |------>| | Input Parser &   | |       | | Host: 192.168.1.10| |
| +---------------+ |       | | Target Validator | |       | | Service: SSH (22) | |
|                   |       | +------------------+ |       | +-------------------+ |
| +---------------+ |       |          |           |       |           ^           |
| | Target List   | |------>|          v           |       |           |           |
| +---------------+ |       | +------------------+ |       |           |           |
|                   |       | | Thread Pool Mgr  | |       |           |           |
| +---------------+ |       | | (pthreads)       | |===================+           |
| | Module (SSH)  | |------>| +------------------+ |       | Parallel Logins       |
| +---------------+ |       |          |           |       |                       |
|                   |       |          v           |       |                       |
|                   |       | +------------------+ |       | +-------------------+ |
|                   |       | | Protocol Module  | |       | | Host: 192.168.1.11| |
|                   |       | | (ssh2.mod)       | |==================>| Service: FTP (21) | |
|                   |       | +------------------+ |       | +-------------------+ |
|                   |       |          |           |       |                       |
|                   |       |          v           |       |                       |
|                   |       | +------------------+ |       |                       |
|                   |       | | Result Output    | |       |                       |
+-------------------+       +----------------------+       +-----------------------+
```

## Detailed Installation and Configuration

Medusa is pre-installed on most penetration testing distributions like Kali Linux and Parrot OS. However, understanding its installation from source is vital when you need to compile it on custom attack boxes, especially to resolve module dependencies.

### Installation via Package Manager
On Debian-based systems:
```bash
sudo apt update
sudo apt install medusa
```

On RedHat-based systems:
```bash
sudo dnf install medusa
```

### Installation from Source
Compiling from source allows you to ensure all necessary libraries are included for specific modules (like `libssh2` for SSH, `libpq` for PostgreSQL, etc.).

```bash
# Install dependencies
sudo apt-get install libssl-dev libssh2-1-dev libpq-dev libpcre3-dev svn

# Clone the repository
git clone https://github.com/jmk-foofus/medusa.git
cd medusa

# Configure and make
./configure
make
sudo make install
```

When you run `./configure`, watch the output closely. It will summarize which modules will be compiled based on the development libraries present on your system. If a module says `no` next to it, you need to install the corresponding `*-dev` library and run `./configure` again.

## Syntax and Core Arguments

Medusa's syntax relies heavily on command-line flags. Understanding these flags is crucial for optimizing your brute-force attacks to balance speed and accuracy without triggering account lockouts unnecessarily.

### Basic Syntax
```bash
medusa [-h host|-H file] [-u username|-U file] [-p password|-P file] [-C file] -M module [OPTIONS]
```

### Essential Flags
*   **Target Options:**
    *   `-h [IP/Hostname]` : Test a single target host.
    *   `-H [File]` : Test multiple hosts listed in a file.
*   **Credential Options:**
    *   `-u [Username]` : Test a single username.
    *   `-U [File]` : Test a list of usernames from a file.
    *   `-p [Password]` : Test a single password.
    *   `-P [File]` : Test a list of passwords from a file.
    *   `-C [File]` : Test a combo file containing entries in the format `username:password`.
*   **Module Options:**
    *   `-M [Module]` : Specify the module to execute (e.g., `ssh`, `ftp`, `http`, `smbnt`). Use `medusa -d` to see available modules.
*   **Execution Modifiers:**
    *   `-O [File]` : Output results to a file.
    *   `-e [n/s/ns]` : Additional password checks. `n` = No password, `s` = Password same as username.
    *   `-F` : Stop brute-forcing on the first valid credential found (per host). Highly recommended to prevent unnecessary noise and account lockouts.
    *   `-b` : Suppress the banner.
*   **Performance Tuning:**
    *   `-t [Number]` : Total number of logins to be tested concurrently. Defaults to 16.
    *   `-r [Seconds]` : Sleep time between retries. Useful for bypassing rate limiting.
    *   `-T [Number]` : Number of hosts to test concurrently. Defaults to 1.
*   **Module Specific:**
    *   `-m [Option]` : Pass parameters specific to the chosen module. Example for HTTP: `-m DIR:/admin`.

## Comprehensive Use Cases

### Scenario 1: SSH Brute-Forcing with Dictionary
The most common use case is attacking an SSH service where you have enumerated a valid username and want to test a password list.

```bash
medusa -h 10.10.10.50 -u root -P /usr/share/wordlists/rockyou.txt -M ssh -F
```
*Analysis:* We target `10.10.10.50` (`-h`), targeting the `root` user (`-u`), using the `rockyou.txt` dictionary (`-P`). The `-M ssh` specifies the SSH protocol. The `-F` flag is critical here; it tells Medusa to stop as soon as it finds the valid password, saving time and reducing log entries on the target.

### Scenario 2: SMB Brute-Forcing Across a Subnet
You have a list of IPs and want to check if a specific local administrator credential works across the entire subnet (Password Spraying/Credential Stuffing).

```bash
medusa -H targets.txt -u Administrator -p 'Winter2024!' -M smbnt
```
*Analysis:* We use `-H targets.txt` to pass a list of hosts. The `-M smbnt` module is used for Windows SMB authentication. This is an effective way to perform lateral movement if you've recovered a credential and want to find where else it is valid.

### Scenario 3: HTTP Basic Authentication
Attacking an administrative portal protected by HTTP Basic Auth.

```bash
medusa -h 192.168.1.100 -U users.txt -P passwords.txt -M http -m DIR:/admin -F
```
*Analysis:* The `-M http` module requires us to specify the directory being protected using the `-m DIR:/path` option. Here, Medusa will try combinations from `users.txt` and `passwords.txt` against `http://192.168.1.100/admin`.

### Scenario 4: Using Combo Files
Often, after a data breach, you have a list of compromised credentials in `username:password` format. Medusa handles this elegantly.

```bash
medusa -h 10.0.0.5 -C compromised_creds.txt -M ftp
```
*Analysis:* The `-C` flag tells Medusa to read the file and split each line at the colon, using the left side as the username and the right side as the password. This is much faster than running a full Cartesian product of a user list against a password list.

### Scenario 5: Brute-Forcing PostgreSQL
Testing default credentials against a database instance.

```bash
medusa -h 172.16.5.50 -U db_users.txt -p 'postgres' -M postgres -F
```
*Analysis:* Uses the `postgres` module to authenticate against the database. Note that the PostgreSQL module must be compiled in your Medusa binary.

## Advanced Techniques and Optimization

### Tuning Concurrency and Timing
Aggressive brute-forcing can cause network congestion, resource exhaustion on the target server, or trigger Intrusion Detection Systems (IDS) and Fail2Ban.

*   **Evading Rate Limiting:** If a server limits login attempts to 3 per minute, you must slow Medusa down.
    ```bash
    medusa -h 10.10.10.50 -u admin -P pass.txt -M ssh -t 1 -r 25
    ```
    This sets concurrency to 1 thread (`-t 1`) and sleeps for 25 seconds between attempts (`-r 25`), effectively keeping the attempt rate below the threshold.

*   **Maximizing Speed on Local Networks:** On a high-bandwidth, low-latency network (like a local lab or internal segment), you can increase threads.
    ```bash
    medusa -h 10.10.10.50 -u admin -P huge_wordlist.txt -M ftp -t 64
    ```

### Password Variations
The `-e` flag allows you to test common password variations without adding them to your wordlist.
*   `-e ns` will test:
    1.  A blank password (`n`).
    2.  A password that is exactly the same as the username (`s`).

```bash
medusa -h 10.10.10.50 -U users.txt -P passwords.txt -M telnet -e ns -F
```

### Detailed Debugging
When Medusa isn't behaving as expected (e.g., getting all false positives or false negatives), the debugging output is invaluable.
Use `-v [1-6]` to increase verbosity. A level of 4 or 5 is usually sufficient to see the raw protocol exchanges.
```bash
medusa -h 10.10.10.50 -u admin -p password -M ssh -v 5
```
This will show you exactly what the SSH module is sending and receiving, helping you identify if the server is dropping the connection immediately or if a protocol mismatch is occurring.

## Defensive Evasion and Considerations

1.  **Account Lockout Awareness:** Always be aware of the target's account lockout policy. In Active Directory environments, brute-forcing with a large password list against a single user (`-U one_user.txt -P many_passwords.txt`) will almost certainly lock the account. Instead, use Password Spraying (`-U many_users.txt -p one_password`).
2.  **Log Noise:** Brute-forcing is inherently noisy. It generates massive amounts of authentication failure logs (Event ID 4625 in Windows, auth.log entries in Linux). Use this tool only when stealth is not a primary concern or when you are intentionally trying to create a diversion.
3.  **Source IP Rotation:** Medusa itself does not support proxy rotation natively. To brute-force through a proxy network (like Tor or a pool of proxies), you must wrap Medusa with a tool like `proxychains`.
    ```bash
    proxychains medusa -h 10.10.10.50 -u root -P rockyou.txt -M ssh
    ```

## Troubleshooting Common Issues

*   **Error: "Module not found" or `medusa -d` shows a short list:** This means Medusa was compiled without the necessary development libraries. Refer to the installation section and ensure `libssh2-1-dev`, `libpq-dev`, etc., are installed before compiling.
*   **Error: "Connection timed out" constantly:** The target might be down, firewalled, or heavily rate-limiting your IP. Verify the service is accessible manually (e.g., using Netcat) and consider slowing down the attack using `-t 1 -r [seconds]`.
*   **False Positives on HTTP:** The HTTP module relies on server response codes. If a server responds with `200 OK` for every login attempt (even failed ones, relying on body content to indicate failure), Medusa will register false positives. In such cases, Medusa might not be the best tool, and a tool capable of grep-matching the response body (like Hydra or Burp Suite Intruder) is preferable.

## Chaining Opportunities

Medusa is rarely used in isolation. It is typically chained with enumeration and post-exploitation tools.

1.  **[[02 - Nmap Network Mapper]] -> Medusa:** Use Nmap to identify open ports and running services, then pipe the findings to Medusa to test default or enumerated credentials.
2.  **[[15 - Enum4linux]] -> Medusa:** Enumerate valid usernames via SMB using Enum4linux, save them to a file, and use Medusa to perform a password spray attack.
3.  **Medusa -> [[52 - Netcat nc ncat Swiss Army Knife]] / [[53 - Socat Advanced Netcat Replacement]]:** Once Medusa recovers a valid credential (e.g., for SSH), log in and use Netcat or Socat to establish a reverse shell or establish further persistence.
4.  **[[21 - Hydra Network Logon Cracker]] vs Medusa:** Compare results. Sometimes one tool handles a specific edge-case implementation of a protocol better than the other. If Medusa fails due to weird HTTP redirects, try Hydra.

## Related Notes
*   [[21 - Hydra Network Logon Cracker]]
*   [[25 - Hashcat Advanced Password Recovery]]
*   [[26 - John the Ripper Password Cracker]]
*   [[02 - Nmap Network Mapper]]
*   [[41 - Password Spraying Techniques]]
