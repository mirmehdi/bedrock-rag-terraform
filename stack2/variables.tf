variable "aurora_arn" {
  description = "Aurora cluster ARN (stack1 output: aurora_arn)"
  type        = string
}

variable "aurora_endpoint" {
  description = "Aurora cluster endpoint (stack1 output: aurora_endpoint)"
  type        = string
}

variable "aurora_secret_arn" {
  description = "Secrets Manager ARN with the DB credentials (stack1 output: rds_secret_arn)"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the document bucket (stack1 output: s3_bucket_name, which returns the ARN)"
  type        = string
}
