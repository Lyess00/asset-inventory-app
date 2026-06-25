variable "aws_region" {
  description = "Région AWS"
  default     = "eu-west-3"
}

variable "account_id" {
  description = "ID du compte AWS"
  default     = "256748318700"
}

variable "app_name" {
  description = "Nom de l'application"
  default     = "asset-inventory-app"
}

variable "container_port" {
  description = "Port du conteneur"
  default     = 8000
}
