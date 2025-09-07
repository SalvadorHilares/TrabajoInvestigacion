output "alb_dns_name" {
  value       = aws_lb.api_alb.dns_name
  description = "URL del Load Balancer (HTTP/80)"
}

output "alb_url" {
  value       = "http://${aws_lb.api_alb.dns_name}"
  description = "URL completa de la aplicación"
}

output "ecr_repository_url" {
  value       = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${aws_ecr_repository.api_repo.name}"
  description = "URL para docker push"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.api_cluster.name
  description = "Nombre del cluster ECS"
}

output "ecs_service_name" {
  value       = aws_ecs_service.api_service.name
  description = "Nombre del servicio ECS"
}
