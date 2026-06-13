---
tags: [tools, recon, vapt, osint, recon-ng]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.05 Recon-ng Modular OSINT Framework"
---

# Recon-ng: The Modular OSINT Framework

Recon-ng is to Open Source Intelligence (OSINT) what Metasploit is to exploitation. Written in Python, it provides a powerful environment with an interactive command prompt, independent modules, API key management, and a centralized database. 

Instead of running a dozen disparate command-line tools and managing messy text files, Recon-ng allows an analyst to conduct comprehensive recon campaigns within a single, persistent workspace. Data flows seamlessly from one module to the next—for instance, discovering a company name populates the `companies` table, which a subsequent module uses to find root domains, populating the `domains` table, which another module uses to find subdomains, and so on.

## Core Architecture and Database Schema

At the heart of Recon-ng is a strictly defined SQLite database schema. Understanding this schema is the key to mastering the framework.

```ascii
+-------------------------------------------------------------------------------------+
|                              RECON-NG DATA FLOW ARCHITECTURE                        |
+-------------------------------------------------------------------------------------+
|                                                                                     |
|   +-----------------------------------------------------------------------------+   |
|   |                           WORKSPACE DATABASE                                |   |
|   |                                                                             |   |
|   |  [Companies] ---> [Domains] ---> [Hosts] ---> [Ports/Vulnerabilities]       |   |
|   |                     |              |                                        |   |
|   |                     v              v                                        |   |
|   |                 [Contacts]     [Credentials]                                |   |
|   +-----------------------------------------------------------------------------+   |
|          ^                  |                   ^                   |               |
|          | (Reads)          | (Writes)          | (Reads)           | (Writes)      |
|          |                  v                   |                   v               |
|   +---------------------------------+   +---------------------------------------+   |
|   |       RECON MODULES             |   |        DISCOVERY MODULES              |   |
|   | (e.g., recon/domains-hosts/...) |   |  (e.g., discovery/info_disclosure/..) |   |
|   +---------------------------------+   +---------------------------------------+   |
|                                                                                     |
|   +-----------------------------------------------------------------------------+   |
|   |                           REPORTING MODULES                                 |   |
|   |                    (HTML, CSV, JSON, Maltego CSV)                           |   |
|   +-----------------------------------------------------------------------------+   |
|                                                                                     |
+-------------------------------------------------------------------------------------+
```

The workflow is inherently chained. You seed the database with an initial piece of information (like a domain), and execute modules that consume that data to generate new types of data.

## Workspace Management

When you launch Recon-ng, you should immediately create a workspace for your specific target. This isolates the SQLite database so data from different engagements doesn't mix.

```bash
recon-ng
```

Inside the interactive prompt:
```text
[recon-ng][default] > workspaces create tesla_corp
[recon-ng][tesla_corp] > workspaces list
```

## The Marketplace and Modules

By default, a fresh installation of Recon-ng comes with almost no modules. You must install them from the central marketplace. This design keeps the core framework light and allows community developers to update modules independently.

To view available modules:
```text
[recon-ng][tesla_corp] > marketplace search
```

To install all modules (recommended for thick-client setups with plenty of API keys):
```text
[recon-ng][tesla_corp] > marketplace install all
```

Modules are categorized into branches:
- **recon/**: Transforms one piece of data into another (e.g., `recon/domains-hosts/bing_domain_web`).
- **discovery/**: Actively queries targets for misconfigurations.
- **reporting/**: Formats the database contents into usable reports.

## Configuration and API Keys

Recon-ng's true power is unlocked via APIs. The framework centralizes API key management via the `keys` command.

To see which installed modules require API keys, and which keys are currently missing:
```text
[recon-ng][tesla_corp] > keys list
```

To add an API key (e.g., for Shodan):
```text
[recon-ng][tesla_corp] > keys add shodan_api YOUR_SHODAN_KEY
```
*The key is securely stored in the global configuration and is available across all workspaces.*

## A Complete OSINT Workflow Walkthrough

Here is a step-by-step methodology for executing a campaign from scratch inside Recon-ng.

### Step 1: Seeding the Database
You must give Recon-ng a starting point. Let's add a domain.
```text
[recon-ng][tesla_corp] > db insert domains
domain (text): tesla.com
notes (text): Primary target domain
```

### Step 2: Running a Recon Module
Now, we want to transform that domain into hostnames (subdomains). We will load the Hackertarget module.
```text
[recon-ng][tesla_corp] > modules load recon/domains-hosts/hackertarget
[recon-ng][tesla_corp][hackertarget] > info
[recon-ng][tesla_corp][hackertarget] > run
```
*The module reads `tesla.com` from the `domains` table, queries Hackertarget, and automatically inserts the discovered subdomains into the `hosts` table.*

### Step 3: Verifying the Data
Check what the module discovered.
```text
[recon-ng][tesla_corp][hackertarget] > show hosts
```

### Step 4: Resolving Hosts to IP Addresses
The `hosts` table now has subdomains, but no IP addresses. Let's use another module to resolve them.
```text
[recon-ng][tesla_corp][hackertarget] > modules load recon/hosts-hosts/resolve
[recon-ng][tesla_corp][resolve] > run
```
*This reads the `hosts` table, performs DNS resolution, updates the IP column in the `hosts` table, and potentially adds new subnets to the `netblocks` table.*

### Step 5: Discovering Contacts/Emails
We can pivot from the `domains` table to the `contacts` table.
```text
[recon-ng][tesla_corp][resolve] > modules load recon/domains-contacts/hunter_io
[recon-ng][tesla_corp][hunter_io] > run
[recon-ng][tesla_corp][hunter_io] > show contacts
```

## Automation with Resource Files (`.rc`)

Running modules manually is tedious for repeatable engagements. Recon-ng supports resource files, which are simply text files containing a sequence of Recon-ng commands (exactly like Metasploit `.rc` files).

Create a file named `standard_recon.rc`:
```text
workspaces select tesla_corp
modules load recon/domains-hosts/hackertarget
run
modules load recon/domains-hosts/bing_domain_web
run
modules load recon/hosts-hosts/resolve
run
modules load reporting/html
options set CREATOR Antigravity
options set CUSTOMER Tesla
options set FILENAME /home/user/reports/tesla_report.html
run
exit
```

Execute the resource file from your bash terminal:
```bash
recon-ng -r standard_recon.rc
```
This enables fully headless, automated OSINT gathering pipelines powered by a robust database.

## Reporting and Exporting

The reporting modules are essential for extracting data out of Recon-ng's SQLite database to feed into other tools.

### CSV Export for Other Tools
```text
[recon-ng][tesla_corp] > modules load reporting/csv
[recon-ng][tesla_corp][csv] > options set TABLE hosts
[recon-ng][tesla_corp][csv] > options set FILENAME /tmp/tesla_hosts.csv
[recon-ng][tesla_corp][csv] > run
```

### HTML Reporting
The HTML reporting module generates highly professional, interactive dashboards displaying graphs and tables of all the data gathered across all tables (contacts, hosts, credentials, vulnerabilities).

## Limitations

- **Speed:** Because Recon-ng updates a SQLite database row-by-row and runs modules sequentially via Python, it is significantly slower than asynchronous Go binaries like Subfinder or Assetfinder.
- **Maintenance:** Modules frequently break when third-party websites change their HTML structure, as community updates can sometimes lag behind. Always favor API-based modules over scraping-based modules.

## Chaining Opportunities

- **Recon-ng -> CSV -> Nmap**: Export the `hosts` table to a CSV, extract the IP column, and pass it directly to Nmap for active port scanning.
- **Recon-ng -> JSON -> Custom Scripts**: Export the `contacts` table to JSON to build customized Active Directory username wordlists based on discovered employee names.
- **Amass -> Recon-ng**: Run Amass for heavy DNS brute-forcing, format the output, and use `db insert hosts` or a custom script to inject Amass's findings into Recon-ng's database for unified reporting.

## Related Notes
- [[01 - Amass Full Config and Usage]]
- [[02 - Subfinder Config Sources API Keys]]
- [[04 - theHarvester Full Usage Guide]]
- [[12 - Email Enumeration and Verification]]
- [[16 - Open Source Intelligence (OSINT) Fundamentals]]
