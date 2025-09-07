variable "region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region"
}

variable "account_id" {
  type        = string
  description = "Tu AWS Account ID (ej. 478701513931)"
}

variable "iam_role_arn" {
  type        = string
  description = "ARN del rol IAM a usar (LabRole), ej: arn:aws:iam::<account_id>:role/LabRole"
}

variable "repo_name" {
  type        = string
  default     = "fastapi-ecs"
}

variable "image_tag" {
  type        = string
  default     = "v1"
}

variable "app_port" {
  type        = number
  default     = 8080
}
