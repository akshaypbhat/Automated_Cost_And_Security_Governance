# AWS Enterprise Cloud Governance & Security Guardrail Framework

[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/terraform-%235C4EE5.svg?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A production-grade, dual-engine automation framework designed to enforce strict **FinOps Cost Optimization** and **SecOps Security Guardrails** across AWS cloud environments. Engineered using **Terraform** for reproducible Infrastructure as Code (IaC) and **Python (Boto3)** for event-driven, serverless execution.

This framework actively mitigates corporate cloud risks by simultaneously eliminating silent billing leaks (orphaned volumes, unattached snapshots, idle instances) and shutting down dangerous perimeter vulnerabilities (publicly open administrative ports, unshielded S3 storage buckets). Real-time, formatted tabular executive alerts are delivered straight to infrastructure teams via Amazon SNS and SES.

---

## 🏗️ System Architecture

The dual-engine framework operates entirely via a serverless topology, optimizing runtime execution costs while maintaining an active continuous governance posture across multi-module storage and network layers.

```
+-----------------------------------------------------------------------------------+
|                                     AWS Cloud                                     |
|                                                                                   |
|   +---------------------------------------+   +-------------------------------+   |
|   |         FINOPS COST GOVERNANCE        |   |    SECOPS SECURITY GUARDRAIL  |   |
|   |  • Idle EC2   • Unattached EBS Volumes |   |  • Open SSH/22  • Public S3   |   |
|   |  • Stale EBS Snapshots                |   |  • Missing Public Access Block|   |
|   +-------------------+-------------------+   +---------------+---------------+   |
|                       |                                       |                   |
|                       +-------------------+-------------------+                   |
|                                           |                                       |
|                                           v                                       |
|                               +-----------------------+                           |
|                               |   AWS Lambda Runtime  | <--- Stateful Packages    |
|                               |    (Python / Boto3)   |      via Terraform Engine |
|                               +-----------+-----------+                           |
|                                           |                                       |
|                                           v                                       |
|                               +-----------------------+                           |
|                               |   Amazon SNS / SES    |                           |
|                               |   (Alert Dispatcher)  |                           |
|                               +-----------+-----------+                           |
|                                           |                                       |
+-------------------------------------------|---------------------------------------+
                                            v
                               +-------------------------+
                               | Dual SecOps & FinOps    |
                               | Combined HTML Report    |
                               +-------------------------+
```

### Key Architectural Highlights:
* **Infrastructure as Code (IaC):** Modular Terraform codebase implementing advanced automation mechanisms like `data.archive_file` blocks for runtime zipping and `source_code_hash` mapping for secure, drift-free deployment updates.
* **Serverless Execution Engine:** Decoupled Python 3.11 Lambda handlers optimized to consume minimal compute footprints while performing deep multi-service API interrogation via `boto3`.
* **Enterprise Alerting Fabric:** Configured using multi-protocol Amazon SNS alerting backed by highly customized, executive-ready HTML transaction rendering via Amazon SES.

---

## ⚡ Core Engines Breakdown

### 💰 Engine A: FinOps Cost Governance
Corporate cloud waste typically accumulates from orphaned storage elements. This engine programmatically executes systemic cleanups by interrogating the `ec2` and `ebs` block-storage virtualization layers:
* **Unattached EBS Volumes:** Traces volumes lingering in an `available` state rather than `in-use`, mapping idle assets bleeding daily provisioned storage costs.
* **Orphaned EBS Snapshots:** Cross-references active volume architectures against older snapshots to flag detached backup allocations that no longer map to running company hardware.
* **Idle EC2 Workloads:** Evaluates instance states to track unutilized instances that consume budget without processing live application traffic.

### 🔒 Engine B: SecOps Security Guardrails
Perimeter security is non-negotiable. This engine acts as an automated perimeter firewall auditor by continuously evaluating resource exposure profiles:
* **Network Perimeter Ingress Guardrail:** Targets critical infrastructure vulnerabilities by identifying any EC2 Security Group permitting open ingress traffic (`0.0.0.0/0`) over management channels, specifically focusing on **Port 22 (SSH)** to block brute-force vectors.
* **S3 Data Leak Prevention Guardrail:** Scans environment storage buckets via the S3 client API fabric. It directly interrogates the `PublicAccessBlockConfiguration` structure via the `get_public_access_block` endpoint, flagging any bucket with deactivated or missing safety attributes (`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`).

---

## 📁 Repository Structure

```text
Automated_Cost_Optimisation/
│
├── src/
│   ├── cost_governance/           # ENGINE A: Cost Architecture Subsystem
│   │   ├── emails.py              # FinOps custom report formatting
│   │   ├── instances.py           # EC2 idle metrics processor
│   │   ├── lambda_function.py     # Cost core logic coordinator
│   │   ├── snapshots.py           # Orphaned snapshot mapping engine
│   │   └── volumes.py             # Idle EBS volume identifier
│   │
│   └── security_guardrails/       # ENGINE B: Security Guardrails Subsystem
│       └── lambda_function.py     # SecOps S3 and Security Group compliance scanning
│
├── Main.tf                        # Unified Infrastructure mapping (Lambda, IAM, SNS, SES)
├── Providers.tf                   # Version-locked Cloud Provider rules
├── Variables.tf                   # Strictly-typed global workspace inputs
├── terraform.tfvars               # Production deployment context parameters
└── README.md                      # High-impact documentation storefront
```

---

## 🚀 Deployment & Installation

### Prerequisites
* **Terraform CLI** (v1.5.0+) installed and path-configured.
* **AWS CLI** authenticated with administrative IAM workspace permissions.
* Verified Identities established within the **Amazon SES** dashboard for secure transmission.

### Provisioning Pipeline
```bash
# 1. Clone the project workspace
git clone https://github.com/your-username/automated-cost-security-guardrail.git
cd automated-cost-security-guardrail

# 2. Initialize provider frameworks and cache lock profiles
terraform init

# 3. Validate codebase syntax and configuration schema
terraform validate

# 4. Generate deployment blueprint and provision live resources
terraform apply
```

---

## 🧪 Verification & Executive Report Mock

When executed, the system consolidates compliance checks into a clean, easy-to-read executive dashboard layout:

```text
========================================================================
📊 CLOUD GOVERNANCE & SECURITY AUDIT SUMMARY
========================================================================

💰 FINOPS COST GOVERNANCE FINDINGS
------------------------------------------------------------------------
| Resource Type | Resource ID           | Size/State  | Financial Risk |
------------------------------------------------------------------------
| EBS Volume    | vol-0a12b34567cd89ef0 | 100 GiB     | Idle Waste     |
| EBS Snapshot  | snap-0987654321fedcba | Stale       | Orphaned Leak  |
------------------------------------------------------------------------

🔒 SECOPS SECURITY GUARDRAIL BREACHES
------------------------------------------------------------------------
| Resource Type | Resource ID           | Vulnerability| Threat Level  |
------------------------------------------------------------------------
| Security Group| sg-017614162b0d10c3d  | Port 22 Open | CRITICAL      |
| S3 Bucket     | demobucket-production | PAB Disabled | HIGH RISK     |
------------------------------------------------------------------------

Action Required: Please remediate flagged configurations via the AWS Console immediately.
```

---

## 🛠️ Engineering Implementation Highlights

* **Cryptographic State Integrity:** Configured with `source_code_hash = data.archive_file.security_guardrail_zip.output_base64sha256` to force immediate code upgrades anytime a local Python file is updated, completely removing structural drift.
* **Defensive Exception Engineering:** Implements strict try-except closures wrapped in `botocore.exceptions.ClientError` signatures to prevent execution thread crashes when evaluating buckets lacking explicit configurations.
* **Decoupled Structural Design:** Enforces strict compliance with enterprise separation patterns, splitting state declarations (`Main.tf`) cleanly away from pure functional computational logic units (`src/`).
