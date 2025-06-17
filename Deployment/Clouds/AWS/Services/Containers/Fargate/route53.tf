# Hosted Zone (if you have a domain)
resource "aws_route53_zone" "main" {
  name = "yourdomain.com" # Replace with your domain
  
  tags = {
    Name = var.app_name
  }
}

# A Record pointing to ALB
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.yourdomain.com" # Replace with your subdomain
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}