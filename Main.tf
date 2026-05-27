# 1. Package the Python Code Automatically from the Source Directory
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src/cost_governance"
  output_path = "${path.module}/cost_governance_payload.zip"
}

data "archive_file" "security_guardrail_zip"{
  type = "zip"
  source_dir = "${path.module}/src/security_guardrails"
  output_path = "${path.module}/security_guardrail_payload.zip"
}
 
# 2. IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_role" {
  name = "ebs_cost_governance_role"
 
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}
 
# 3. IAM Policy for Least-Privilege Access (EC2, Snapshots, CloudWatch, and SES)
resource "aws_iam_policy" "lambda_policy" {
  name = "ebs_cost_governance_policy"
 
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:DescribeInstances"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
 
# 4. Attach Policy to Role
resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
 
# 5. AWS Lambda Function Definition
resource "aws_lambda_function" "ebs_scaler" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "ebs_cost_governance_validator"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.11"
  timeout          = 300 # 5 minutes execution window
 
  environment {
    variables = {
      SENDER_EMAIL    = var.sender_email
      RECIPIENT_EMAIL = var.recipient_email
    }
  }
}
 
# 6. EventBridge Weekly Schedule Trigger (Runs every 7 days)
resource "aws_cloudwatch_event_rule" "weekly_check" {
  name                = "weekly-ebs-cost-rule"
  schedule_expression = "rate(7 days)"
}
 
# 7. EventBridge Target to Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly_check.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.ebs_scaler.arn
}
 
# 8. Grant EventBridge Permission to Invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ebs_scaler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_check.arn
}

# --- SNS Notification Infrastructure ---
resource "aws_sns_topic" "security_alerts" {
  name = "security-guardrail-alerts"
}
 
resource "aws_sns_topic_subscription" "security_alerts_email" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alerts_email
}
 
# --- IAM Execution Role for Lambda ---
resource "aws_iam_role" "security_lambda_role" {
  name = "security_guardrail_lambda_role"
 
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}
 
resource "aws_iam_policy" "lambda_security_policy" {
  name        = "security_guardrail_policy"
  description = "Permissions for Lambda to inspect EC2/S3 and alert via SNS"
 
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:DescribeInstances"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "sns:Publish"
        Resource = aws_sns_topic.security_alerts.arn
      },
      {
        Effect   = "Allow"
        Action   = [
          "cloudwatch:GetMetricStatistics"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "ses:SendEmail"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:GetBucketPublicAccessBlock"
        ]
        Resource = "*"
      }
    ]
  })
}
 
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.security_lambda_role.name
  policy_arn = aws_iam_policy.lambda_security_policy.arn
}
 
# --- Lambda Function ---
resource "aws_lambda_function" "security_guardrail" {
  filename      = "security_guardrail_payload.zip"
  function_name = "security_guardrail_validator"
  role          = aws_iam_role.security_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  source_code_hash = data.archive_file.security_guardrail_zip.output_base64sha256
  timeout = 300
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.security_alerts.arn
      SENDER_EMAIL = var.sender_email
      RECIPIENT_EMAIL = var.recipient_email
    }
  }
}
 
resource "aws_iam_role" "states_role" {
  name = "security_guardrail_states_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "states.amazonaws.com"}
    }]
  })
}

resource "aws_iam_role_policy" "states_lambda_policy" {
  name = "states_lambda_invoke_policy"
  role = aws_iam_role.states_role.id
 
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.security_guardrail.arn
    }]
  })
}

# --- Step Functions State Machine ---
resource "aws_sfn_state_machine" "security_guardrail_sfn" {
  name     = "security-guardrail-workflow"
  role_arn = aws_iam_role.states_role.arn
 
  definition = jsonencode({
    Comment = "Guardrail waiting workflow"
    StartAt = "Wait One Hour"
    States = {
      "Wait One Hour" = {
        Type    = "Wait"
        Seconds = 120 #needs to change
        Next    = "Trigger Security Lambda"
      }
      "Trigger Security Lambda" = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = aws_lambda_function.security_guardrail.arn
          "Payload.$"  = "$"
        }
        End = true
      }
    }
  })
}