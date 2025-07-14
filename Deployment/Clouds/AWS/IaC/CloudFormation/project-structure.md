# Microservices

## Overview
This project implements a microservices architecture with:
- Backend: Node.js + Express.js microservices
- Frontend: React + Next.js SPA
- Database: PostgreSQL on AWS RDS
- Deployment: AWS CloudFormation (IaC)
- Security: JWT authentication, IAM roles
- CDN: CloudFront for static assets

## Project
```
├── backend/
│   ├── auth-service/          # Authentication microservice
│   ├── user-service/          # User management microservice
│   ├── api-gateway/           # API Gateway service
│   └── shared/                # Shared utilities
├── frontend/                  # React + Next.js SPA
├── infrastructure/            # CloudFormation templates
├── docker/                    # Docker configurations
└── scripts/                   # Deployment scripts
```

## Services
1. **Auth Service**: JWT token generation/validation
2. **User Service**: User CRUD operations with PostgreSQL
3. **API Gateway**: Single entry point for frontend
4. **Frontend**: React SPA with Next.js SSR

## AWS resources
- EC2/ECS for backend services
- RDS PostgreSQL for database
- S3 + CloudFront for frontend
- API Gateway for routing
- IAM roles for security
- SSL certificates for HTTPS
