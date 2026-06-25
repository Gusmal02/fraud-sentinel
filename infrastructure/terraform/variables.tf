variable "aws_region" {
  description = "Región AWS"
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  default     = "dev"
}

variable "task_cpu" {
  description = "CPU para la tarea ECS (unidades)"
  default     = "1024"
}

variable "task_memory" {
  description = "Memoria para la tarea ECS (MB)"
  default     = "2048"
}