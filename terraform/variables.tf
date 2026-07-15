variable "project_id" {
  description = "Your GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "europe-west3"
}

variable "environment" {
  description = "Environment name: dev, uat, or prod"
  type        = string
  default     = "dev"
}