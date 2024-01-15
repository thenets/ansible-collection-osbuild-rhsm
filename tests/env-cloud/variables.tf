variable "project_id" {
  type        = string
  description = "Project ID"
}

variable "region" {
  type        = string
  description = "Region for this infrastructure"
  default     = "us-east1"
}

variable "name" {
  type        = string
  description = "Name for this infrastructure"
  default     = "osbuild-envs"
}
