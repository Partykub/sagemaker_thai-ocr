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

# Training Configuration Variables
variable "training_instance_type" {
  description = "SageMaker training instance type"
  type        = string
  default     = "ml.m5.large"
}

variable "training_epochs" {
  description = "Number of training epochs"
  type        = number
  default     = 100
}

variable "training_batch_size" {
  description = "Training batch size"
  type        = number
  default     = 128
}

variable "training_learning_rate" {
  description = "Learning rate for training"
  type        = number
  default     = 0.001
}

variable "max_training_time" {
  description = "Maximum training time in seconds"
  type        = number
  default     = 86400  # 24 hours
}

variable "use_gpu" {
  description = "Use GPU for training"
  type        = bool
  default     = true
}
