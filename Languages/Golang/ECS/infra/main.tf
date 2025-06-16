provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  name    = "my-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
}

resource "aws_db_instance" "postgres" {
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  name              = "mydb"
  username          = "dbuser"
  password          = "dbpassword"
  allocated_storage = 20
  db_subnet_group_name = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  skip_final_snapshot = true
}

resource "aws_s3_bucket" "flutter_frontend" {
  bucket = "my-flutter-frontend-bucket"
  acl    = "public-read"
  website {
    index_document = "index.html"
    error_document = "index.html"
  }
}

module "ecs" {
  source = "terraform-aws-modules/ecs/aws"
  cluster_name = "go-backend-cluster"
  # ... add cluster config
}

# ECS Fargate + Load Balancer + Service
module "ecs_service" {
  source = "terraform-aws-modules/ecs/aws//modules/service"
  name           = "go-backend-service"
  cluster_arn    = module.ecs.cluster_arn
  # ... configure Fargate task, container image, env vars, ALB, etc.
}

# Route53 record example
resource "aws_route53_record" "api" {
  zone_id = "<your_zone_id>"
  name    = "api.example.com"
  type    = "A"
  alias {
    name                   = module.ecs_service.lb_dns_name
    zone_id                = module.ecs_service.lb_zone_id
    evaluate_target_health = true
  }
}