---
tags: [blockchain, account-abstraction, erc-4337, pentesting]
difficulty: advanced
module: "52 - Blockchain and Smart Contract Security"
topic: "52.07 ERC-4337 Account Abstraction Security"
---

# ERC-4337 Account Abstraction Security

## Introduction
**ERC-4337 (Account Abstraction)** lets smart contracts act as user accounts ("smart accounts") without changing the Ethereum protocol, enabling features like gas sponsorship, social recovery, batched transactions, session keys, and custom validation logic. Instead of a normal transaction signed by an EOA, users submit **UserOperations** that flow through a new pipeline (bundlers, an EntryPoint contract, paymasters, and the smart account's own `validateUserOp`). This rich machinery introduces **account-abstraction-specific attack surface** — flaws in account validation, paymaster abuse, and the UserOp lifecycle. This note covers the model and its pitfalls.

## The ERC-4337 Pipeline
```text
+---------------------------------------------------------------+
|                    ERC-4337 FLOW                             |
+---------------------------------------------------------------+
|  User -> signs a UserOperation (intent + signature)           |
|     | sent to an alt-mempool                                  |
|     v                                                         |
|  Bundler  collects UserOps -> calls ENTRYPOINT contract       |
|     |                                                         |
|     v                                                         |
|  EntryPoint -> calls the SMART ACCOUNT's validateUserOp()     |
|             -> (optional) PAYMASTER validates/pays gas        |
|             -> executes the account's call                    |
+---------------------------------------------------------------+
```
Compared to a normal tx, validation is **custom code** in the account and paymaster — so bugs there are bugs in "who is allowed to act / who pays."

## Attack / Pitfall Classes
### 1. Account validation flaws (`validateUserOp`)
The smart account decides whether a UserOp is authorized. Mistakes = unauthorized control of the account:
- Weak/incorrect **signature validation** (replay across chains/accounts if nonce/chainId/EntryPoint not bound; signature malleability).
- **Session keys / module permissions** scoped too broadly (a session key meant for one dApp can drain the account).
- Validation that can be tricked into approving an attacker's UserOp.

### 2. Paymaster abuse
**Paymasters** sponsor gas. Flaws let attackers **drain the paymaster's deposit** (free gas / griefing) or bypass its intended conditions:
- Paymaster validation that doesn't correctly bind to the sponsored operation, enabling abuse of sponsored gas.
- Failing to account for the validation/execution split, letting an op pass validation but grief during execution.

### 3. Storage/opcode rule violations & DoS
ERC-4337 restricts what validation may access (to keep bundlers safe from mass invalidation). Accounts/paymasters that depend on banned opcodes or external mutable state can be **griefed** — attackers invalidate many pending UserOps, or cause bundler DoS.

### 4. Initialization / factory issues
Smart accounts are often **counterfactually deployed** (address known before deployment) via a factory; flaws in the factory or first-time initialization (`initCode`) can let an attacker deploy/initialize an account to their advantage — an account-abstraction twist on the proxy-initialization bug ([[04 - Proxy and Delegatecall Vulnerabilities]]).

### 5. Delegatecall/module takeover
Smart accounts frequently use modules/plugins and delegatecall; a malicious module or delegatecall path can take over the account ([[04]], [[08 - Web3 Signing and Wallet Workflow Compromise]]).

## Testing Workflow
```text
1. Review the smart account's validateUserOp: signature scheme bound to
   nonce + chainId + EntryPoint? session-key/module scopes correct?
2. Review the paymaster: can its deposit be drained or its conditions
   bypassed? validation vs execution handled safely?
3. Check init/factory: can an attacker influence counterfactual deploy
   or initialization?
4. Look for banned-opcode/external-state reliance -> griefing/DoS.
5. Inspect modules/delegatecall for takeover paths ([[04]]).
6. Test on a fork against a real EntryPoint deployment.
```

## Why It Matters
Account abstraction is a major direction for Ethereum UX and is being adopted by wallets and L2s, putting user funds behind **custom validation logic** rather than a single battle-tested signature check. New machinery means new bugs — and a flaw in account validation or a paymaster is a direct path to draining accounts or sponsor funds. It's an emerging, high-value audit area.

## Defensive Notes
- Bind signatures to **nonce + chainId + EntryPoint address**; scope session keys/modules narrowly; use audited account implementations (e.g. established AA wallet kits).
- Design paymasters to correctly validate and bound what they sponsor; account for the validate/execute split; protect the deposit.
- Follow ERC-4337 **storage/opcode rules** to avoid griefing/DoS; secure factory init (disable re-init); vet modules and delegatecall targets ([[04]]).
- Audit + fuzz the AA-specific paths ([[09]]).

## Related Notes
- [[04 - Proxy and Delegatecall Vulnerabilities]]
- [[08 - Web3 Signing and Wallet Workflow Compromise]]
- [[03 - Common Solidity Vulnerabilities]]
- [[09 - Smart Contract Auditing Tools and Methodology]]
