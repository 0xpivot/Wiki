---
tags: [web-exploitation, injection, vapt]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.22 External Variable Modification"
---

# External Variable Modification

## Introduction

External Variable Modification is a (mostly PHP) class of bug where user input is **imported into the application's variable scope**, letting an attacker **overwrite internal variables** the developer assumed were trusted. The usual culprits are `extract($_GET)`/`extract($_POST)`, `import_request_variables()`, `parse_str()` into the global scope, and the legacy `register_globals` behavior. Overwriting the right variable bypasses auth checks, flips feature flags, poisons file-include paths (→ LFI/RFI), or changes prices/roles. It's a quiet logic vuln that turns "the app trusts `$is_admin`" into "the attacker sets `$is_admin`."

## Core Mechanics

`extract($arr)` creates a variable for every key in `$arr`. If `$arr` is attacker-controlled (`$_GET`/`$_POST`/`$_REQUEST`) and runs **before** the variables it would overwrite are set (or without `EXTR_SKIP`), the request can define/overwrite **any** variable in scope:
- `?is_admin=1` ⇒ `$is_admin = 1`
- `?price=0` ⇒ overwrite a computed price
- `?template=/etc/passwd` ⇒ poison a later `include $template;`
Similar with `parse_str($_SERVER['QUERY_STRING']);` (no result array → writes to locals) and `import_request_variables('gpc')`.

## Mermaid: Overwrite Flow

```mermaid
flowchart TD
    A[User input: $_GET/$_POST] --> B[extract() / parse_str() / import_request_variables()]
    B --> C[Attacker keys become in-scope variables]
    C --> D{Overwritten variable used for...}
    D -- Auth flag --> E[$is_admin/$authenticated bypass]
    D -- Include path --> F[include $tpl → LFI/RFI]
    D -- Business value --> G[price/role/quantity tampering]
```

## Vulnerability 1: Auth/flag overwrite
```php
$is_admin = false;
extract($_GET);                 // attacker: ?is_admin=1
if ($is_admin) { /* admin panel */ }   // bypassed
```

## Vulnerability 2: Poisoning file inclusion
```php
extract($_REQUEST);
include($page . '.php');        // attacker: ?page=php://filter/.../etc/passwd or RFI URL
```
Combine with wrappers for LFI→RCE (see Path Traversal / File Inclusion notes).

## Vulnerability 3: Global variable injection / uninitialized vars
Code relying on uninitialized variables being empty breaks when the attacker pre-sets them (`?config[debug]=1`, `?db_host=attacker`), enabling SSRF/debug exposure/logic changes.

## Methodology
1. Grep source for `extract(`, `import_request_variables`, `parse_str(` (single-arg), and uninitialized variables used in security decisions.
2. Identify variables that, if set, change behavior (auth flags, include paths, prices, host/config values).
3. Send those names as GET/POST params; confirm the overwrite and the resulting bypass/LFI/logic change.

## Remediation
1. **Never** `extract()` untrusted arrays; if unavoidable, use `EXTR_SKIP` and an explicit allowlist of keys.
2. Always **initialize** variables before use; access request data explicitly (`$_GET['x']`) with validation; use `parse_str($s, $out)` with the second arg.
3. Keep `register_globals` off (removed in modern PHP); enforce typed config objects instead of loose globals.

## Chaining Opportunities
- Poisoned include → LFI/RFI (folder I-23 Path Traversal) and RCE; auth-flag overwrite → access control bypass (folder B-21); config overwrite → SSRF (folder I-13).

## Related Notes
- [[21 - Email Header Injection and Address Spoofing]] and other injection siblings in this folder; LFI: folder I-23 Path Traversal; logic impact: folder I-25 Business Logic.

## Tools
Source review (grep `extract`/`parse_str`), BurpSuite param fuzzing, `Arjun`/`ParamMiner` for hidden params.
