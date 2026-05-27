variable "aws_region" {
  type = string
  description = "Region where to deploy resources into"
}

variable "sender_email" {
  type = string
  description = "Verified SES email to send the report"
}

variable "recipient_email" {
  type = string
  description = "Email recieving the report"
}

variable "alerts_email" {
  type = string
  description = "Enter emails for security guardrail alerts"
}