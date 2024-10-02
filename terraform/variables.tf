variable "region" {
  description = "The AWS region where resources will be created"
  default     = "us-west-2"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  default     = "api-club"
}

