---
tags: [web-exploitation, injection, vapt]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.23 Type Juggling"
---

# Type Juggling

## Introduction

Type juggling abuses **loose, dynamically-typed comparisons** — primarily PHP's `==` (and `switch`, `in_array` without strict mode) — where the language silently coerces operands to a common type before comparing. This produces surprising "equalities" (`0 == "abc"` was true pre-PHP 8; `"0e123" == "0e456"` is true as numbers) that attackers exploit to **bypass authentication, signature/HMAC checks, and password comparisons** without knowing the real value. The classic is the **magic hash**: a password whose hash is `0e...` (all digits) compares equal to any other `0e...` hash under `==`.

## Core Mechanics

PHP `==` coercion pitfalls (pre-8.0 especially; PHP 8 fixed string↔number but `0e`/numeric-string cases persist):
- `"0e12345" == "0e98765"` → **true** (both parsed as `0 * 10^n = 0`). → **magic hashes**.
- `0 == "abc"` → true in PHP < 8 (string→0). → loose checks against `0`.
- `null == false == 0 == ""` chains; `"1abc" == 1` (leading-numeric) in PHP < 8.
- `in_array($x, $arr)` / `switch($x)` use loose comparison by default.
- `strcmp(array, string)` returns `null` (==0) on type error → "equal".

## Mermaid: Auth Bypass via Magic Hash

```mermaid
flowchart TD
    A[App: md5(input) == stored_hash with ==] --> B{stored_hash is 0e... magic hash?}
    B -- Yes --> C[Send input whose md5 is also 0e...]
    C --> D[0e... == 0e... → both coerced to 0 → equal]
    D --> E[Auth/token check bypassed]
    A2[strcmp(secret, input) with input as array] --> F[strcmp returns NULL == 0 → 'match']
```

## Vulnerability 1: Magic-hash authentication bypass
```php
if (md5($_POST['password']) == $stored)   // loose ==
// if $stored is "0e830400451993494058024219903391" (a 0e-hash),
// supply a password whose md5 is also 0e... e.g. "240610708" (md5 = 0e462...)
```
Known magic-hash inputs exist for md5/sha1; brute-forceable for short ones.

## Vulnerability 2: Loose token / API key checks
```php
if ($_GET['token'] == $secret)   // attacker tries token=0 against a numeric/0e secret
if (strcmp($_GET['key'], $secret) == 0)   // attacker: ?key[]=  → strcmp(array,...) = NULL == 0
```

## Vulnerability 3: JSON-driven type confusion
APIs decoding JSON keep types: sending `{"password": true}` or `{"id": 0}` where the backend does loose `==`/`in_array` can satisfy comparisons or match the first array element.

## Methodology
1. Identify comparison-based security checks (login, token/HMAC verify, coupon/role checks) and the language/version (PHP < 8 is most affected).
2. Test loose-comparison payloads: `0`, `0e...` magic hashes, empty array `key[]=`, booleans via JSON, leading-numeric strings.
3. For hash checks, determine the hash algorithm + whether stored value is a `0e` magic hash; supply a known magic-hash preimage.
4. Confirm bypass (logged in / valid signature / accepted token).

## Remediation
1. Use **strict comparison `===`** (and `in_array($x,$a,true)`, strict `switch` alternatives) for all security checks; compare hashes with `hash_equals()` and verify passwords with `password_verify()`.
2. Validate/normalize input **types** before comparison (reject arrays where strings expected); enforce types at the API boundary (schemas).
3. Upgrade PHP (8+ changed string↔number coercion); never compare secrets with `==`/`strcmp`-as-equality.

## Chaining Opportunities
- Direct **authentication bypass** / signature bypass → account takeover (folder B-16 Authentication); accepted forged tokens → privilege escalation.
- JSON type confusion overlaps NoSQL injection operators (folder B-06).

## Related Notes
- Sibling injection/logic flaws in this folder; auth context: folder B-16; deserialization type issues: folder A-15.

## Tools
Magic-hash lists (`md5`/`sha1` `0e` preimages), `hashcat` (find magic hashes), BurpSuite, source review for `==`/`strcmp`.
