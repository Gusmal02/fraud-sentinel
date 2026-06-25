# Fraud Sentinel — Infraestructura AWS
# DOCUMENTADO — no ejecutado en esta etapa

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "fraud_sentinel" {
  name = "fraud-sentinel-${var.environment}"
}

# ECR Repository para la imagen Docker
resource "aws_ecr_repository" "fraud_sentinel" {
  name                 = "fraud-sentinel"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true  # Escaneo de vulnerabilidades automático
  }
}

# Task Definition
resource "aws_ecs_task_definition" "fraud_sentinel" {
  family                   = "fraud-sentinel"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  container_definitions = jsonencode([{
    name  = "fraud-sentinel"
    image = "${aws_ecr_repository.fraud_sentinel.repository_url}:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "LLM_PROVIDER", value = "gemini" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/fraud-sentinel"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}