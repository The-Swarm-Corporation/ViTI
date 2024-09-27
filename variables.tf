variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "swarms-platform"
}


variable "region" {
  description = "The region where GKE resources will be deployed"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The zone where GKE nodes will be created"
  type        = string
  default     = "us-central1-a"
}