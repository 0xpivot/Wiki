---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Using Compliance Code Examples from Microsoft Azure

### Azure Policy Definition

Azure Policy is a service that enables organizations to create, assign, and manage policies that enforce organizational standards and regulatory compliance. Azure Policy definitions define the conditions and actions that should be taken when a policy is evaluated.

### Example Configuration: Azure Policy Definition

```json
{
  "mode": "All",
  "policyRule": {
    "if": {
      "allOf": [
        {
          "field": "type",
          "equals": "Microsoft.Compute/virtualMachines"
        },
        {
          "field": "Microsoft.Compute/virtualMachines/extensions/type",
          "notEquals": "CustomScriptExtension"
        }
      ]
    },
    "then": {
      "effect": "deny"
    }
  }
}
```

### Azure Blueprints

Azure Blueprints is a service that enables organizations to create and manage reusable blueprints for deploying consistent and compliant environments. Blueprints can include policies, role assignments, and resource groups.

### Example Configuration: Azure Blueprint

```json
{
  "name": "my-blueprint",
  "description": "Blueprint for deploying a compliant environment",
  "resourceGroups": [
    {
      "name": "my-resource-group",
      "location": "East US"
    }
  ],
  "policyAssignments": [
    {
      "name": "my-policy-assignment",
      "policyDefinitionId": "/subscriptions/{subscription-id}/providers/Microsoft.Authorization/policyDefinitions/my-policy-definition"
    }
  ]
}
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/10-Using Compliance Code Examples from AWS|Using Compliance Code Examples from AWS]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/12-Practice Questions & Answers|Practice Questions & Answers]]
