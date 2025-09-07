output "alb_dns_name" {
  value       = aws_lb.api_alb.dns_name
  description = "URL del Load Balancer (HTTP/80)"
}

output "ecr_repository_url" {
  value       = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${aws_ecr_repository.api_repo.name}"
  description = "URL para docker push"
}
