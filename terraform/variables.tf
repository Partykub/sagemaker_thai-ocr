variable "project_id" {
  description = "Unique project identifier"
  type        = string
  default     = "paddleocr"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "owner" {
  description = "Project owner"
  type        = string
  default     = "partykub"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "ml-research"
}
