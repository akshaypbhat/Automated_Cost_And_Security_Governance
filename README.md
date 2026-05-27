# Automated AWS Cost & Security Guardrail Framework

[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/terraform-%235C4EE5.svg?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An enterprise-grade, cloud-native automated auditing framework designed to enforce security compliance and cost optimization governance across AWS infrastructure. Built using **Terraform** for reproducible Infrastructure as Code (IaC) and **Python (Boto3)** for event-driven serverless runtime orchestration.

This framework proactively scans AWS environments to detect critical security vulnerabilities (publicly exposed administrative ports) and cost/compliance leaks (unprotected public S3 buckets), delivering formatted real-time notifications to infrastructure teams via Amazon SNS and SES.

---

## 🏗️ System Architecture

The framework leverages a completely serverless design to eliminate operational overhead while maintaining a continuous compliance posture.

```
+------------------------------------------------------------------------+
|                              AWS Cloud                                 |
|                                                                        |
|   +-------------------+        +--------------------+                  |
|   |  EC2 Workloads    |        | S3 Storage Buckets |                  |
|   |  (Security Groups)|        | (Public Access)    |                  |
|   +---------+---------+        +---------+----------+                  |
|             |                            |                             |
|             +------------+  +------------+                             |
|                          |  |                                          |
|                          v  v                                          |
|                +-----------------------+                               |
|                |   AWS Lambda          | <--- State/Package managed    |
|                |   (Python / Boto3)    |      via Terraform            |
|                +-----------+-----------+                               |
|                            |                                           |
|                            v                                           |
|                +-----------------------+                               |
|                |   Amazon SNS / SES    |                               |
|                |   (Alert Dispatcher)  |                               |
|                +-----------+-----------+                               |
|                            |                                           |
+----------------------------|-------------------------------------------+
                             v
                  +---------------------+
                  |  SecOps Inbox       |
                  |  (HTML Report)      |
                  +---------------------+
```

### Key Architectural Components:
* **Infrastructure as Code (IaC):** Modular Terraform configuration enforcing automated ZIP packaging (`data.archive_file`), cryptographic state-hashing (`source_code_hash`), and strict IAM execution roles following the **Principle of Least Privilege**.
* **Serverless Execution Layer:** AWS Lambda runtime optimized on Python 3.11 utilizing highly decoupled Boto3 API client handlers.
* **Notification Engine:** Multi-target alert bus combining AWS SNS protocols and custom-styled AWS SES HTML transitional payloads for rapid human triage.

---

## ⚡ Core Capabilities & Guardrails

### 1. Network Perimeter Security Guardrail
* **The Risk:** Open ingress rules allowing unrestricted global traffic (`0.0.0.0/0`) to management ports expose infrastructure to automated brute-force attacks and malicious network scanning.
* **The Logic:** Evaluates all EC2 Security Groups dynamically. Isolates, flags, and records any rule permitting open internet ingress over administrative ports (specifically **Port 22 / SSH**).

### 2. S3 Storage Compliance Guardrail
* **The Risk:** Unconfigured or explicitly disabled public access blocks on S3 buckets represent one of the leading causes of corporate data leaks.
* **The Logic:** Programmatically queries the S3 API service fabric across the environment. Interrogates the target bucket's `PublicAccessBlockConfiguration` structure via `get_public_access_block`.
* **Compliance Evaluation Criteria:** Captures and reports buckets missing critical configurations:
    * `BlockPublicAcls`
    * `IgnorePublicAcls`
    * `BlockPublicPolicy`
    * `RestrictPublicBuckets`

### 3. Unified Executive Alert Delivery
* Consolidates findings into a single execution context to prevent alert fatigue.
* Compiles raw JSON security payloads into an intuitive, high-visibility HTML email summary containing structured tabular markdown of exposed Asset IDs, resource metadata, and explicit configuration vulnerabilities.

---

## 📁 Repository Structure

```text
Automated_Cost_Optimisation/
│
├── src/
│   ├── cost_governance/           # Extensible module for cost hooks
│   │   ├── emails.py
│   │   ├── instances.py
│   │   ├── lambda_function.py
│   │   ├── snapshots.py
│   │   └── volumes.py
│   │
│   └── security_guardrails/       # Operational Guardrail Subsystem
│       └── lambda_function.py     # Main Boto3 compliance evaluation script
│
├── Main.tf                        # Primary AWS resource mapping (Lambda, IAM, SNS)
├── Providers.tf                   # Terraform Provider constraints & AWS configurations
├── Variables.tf                   # Strong-typed input parameters
├── terraform.tfvars               # Deployment environments workspace variables
└── README.md                      # Professional technical documentation
```

---

## 🚀 Deployment & Installation

### Prerequisites
* [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) (v1.5.0+)
* [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate administrative execution credentials.
* Verified Sender Identity in **AWS SES** for both the target sender and recipient addresses.

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/automated-cost-security-guardrail.git
cd automated-cost-security-guardrail
```

### Step 2: Configure Environment Variables
Create or modify the `terraform.tfvars` file to supply the required deployment context parameters:
```hcl
sender_email    = "security-alerts@yourdomain.com"
recipient_email = "secops-triage@yourdomain.com"
aws_region      = "us-east-1"
```

### Step 3: Initialize Terraform Provider Plugins
Download provider plugins, construct local working state data, and ensure version constraints are lock-verified.
```bash
terraform init
```

### Step 4: Validate Configuration Integrity
Execute syntactic and structural checks across the custom HCL scripts.
```bash
terraform validate
```

### Step 5: Provision Infrastructure
Review the execution blueprint and apply changes to the live AWS provider instance.
```bash
terraform apply
```

---

## 🧪 Operational Testing & Verification

Once provisioned by Terraform, the compliance engine can be validated directly within the AWS Console or via AWS CLI:

1.  **Generate a Synthetic Breach Matrix:**
    * Create a temporary EC2 Security Group containing an ingress rule opening Port `22` to `0.0.0.0/0`.
    * Provision an S3 Bucket with public access blocks explicitly disabled or left unconfigured.
2.  **Execute the Auditor:** Trigger the Lambda function via a blank test payload (`{}`).
3.  **Verify Results:** Monitor your designated triage email inbox. The framework will instantly dispatch a formatted executive summary detailing the exact out-of-compliance resources:

```text
🚨 Security Guardrail Alert
The automated security scanner identified infrastructure resources exposed to the public internet.

🔒 Exposed EC2 Security Groups
------------------------------------------------------------
| Group ID              | Group Name       | Exposure     |
------------------------------------------------------------
| sg-017614162b0d10c3d  | launch-wizard-2  | Port 22 Open |
------------------------------------------------------------

🪣 Non-Compliant S3 Buckets
------------------------------------------------------------
| Bucket Name                           | Exposure        |
------------------------------------------------------------
| testingpurposebucketfordemopurpose    | PAB Disabled    |
------------------------------------------------------------
```

---

## 🛠️ Technical Implementation Highlights

* **State Integrity & Drift Prevention:** Utilizes `source_code_hash = data.archive_file.security_guardrail_zip.output_base64sha256` to ensure that any local changes made to Python business logic are mathematically matched, zipped, and forced updated on subsequent code applies.
* **Robust Exception Processing:** Built defensive exception structures around AWS API endpoints using specific `botocore.exceptions.ClientError` wrappers. This prevents script failures if individual resources are deleted mid-scan or when querying unconfigured API structures (such as S3 buckets completely lacking a PAB config block).
* **Clean Architecture:** Employs explicit separation of concerns by breaking down code spaces into functional configuration blocks (`Providers.tf`, `Variables.tf`, `Main.tf`) and separate application resource directories (`src/`).
