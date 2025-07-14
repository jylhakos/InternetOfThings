# Microservices on Amazon AWS

This project implements microservices and uses Infrastructure as code (IaC) with AWS Cloud Development Kit.

## Overview

- **Backend**: Node.js microservices with Express.js
- **Frontend**: React + Next.js with TypeScript
- **Database**: PostgreSQL on AWS RDS
- **Authentication**: JWT-based auth service
- **Infrastructure**: AWS CDK for Infrastructure as Code (IaC)
- **Deployment**: Docker containers on AWS ECS/Fargate
- **API Gateway**: Single entry point for all services
- **CDN**: CloudFront for static assets

## Project

```

├── backend/
│   ├── auth-service/          # Authentication microservice
│   ├── user-service/          # User management microservice
│   ├── api-gateway/           # API Gateway service
│   └── shared/                # Shared utilities and models
├── frontend/                  # React + Next.js application
├── infrastructure/            # AWS CDK code
└── docker-compose.yml         # Local development

```

## Services

### Backend (Node.js + Express, PostgreSQL)

1. **Authorization** (Port 3001)
   - User signup/signin
   - JWT token generation and validation
   - Password hashing and verification

2. **User** (Port 3002)
   - User CRUD operations
   - Profile management
   - Database interactions

3. **API Gateway** (Port 3000)
   - Routes requests to appropriate services
   - Authentication middleware
   - Rate limiting and logging

### Frontend (React + Next.js)

- **Next.js** with TypeScript
- **React** components for UI
- **Server-side rendering** for better SEO
- **Static asset optimization** for CloudFront

## AWS Infrastructure

- **ECS/Fargate**: Container orchestration
- **RDS PostgreSQL**: Database
- **API Gateway**: External API access
- **CloudFront**: CDN for frontend
- **IAM Roles**: Secure service communication
- **VPC**: Network isolation
- **Load Balancer**: Traffic distribution

What is the AWS CDK?

The AWS Cloud Development Kit (AWS CDK) lets you define your cloud application resources.

The AWS CDK integrates with Amazon ECS (for containerized applications).

The AWS CDK supports JavaScript, TypeScript, Python, Java, C#, and Go.

Use the AWS CDK CLI to create, manage, and deploy your AWS CDK projects.

## Getting Started

### Prerequisites

- Node.js 18+
- Docker
- AWS CLI configured
- AWS CDK CLI

### Installation

```bash
npm run install:all
```

### Local development

```bash
# Start all services
docker-compose up

# Or run individually
npm run dev:backend
npm run dev:frontend
```

### Deployment

```bash
# Build and deploy to AWS
npm run build
npm run deploy
```

## Environment variables

Create `.env` files in each service directory:

### Backend services
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=userdb
DB_USER=postgres
DB_PASSWORD=password
JWT_SECRET=your-secret-key
NODE_ENV=development
```

### Frontend
```
NEXT_PUBLIC_API_URL=http://localhost:3000
```
## API Endpoints

React application communicates with Node.js microservices through the defined API (REST or GraphQL) Endpoints.

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/signin` - User login

### User management
- `GET /users/profile` - Get user profile (authenticated)
- `POST /users/profile` - Update user profile (authenticated)
- `GET /users/:id` - Get user by ID (authenticated)

## Docker images

Use Docker to containerize each microservice.

Consider Kubernetes for orchestration and managing your containers.

- `microservices/auth-service`
- `microservices/user-service`
- `microservices/api-gateway`
- `microservices/frontend`

## AWS resources

- ECS Cluster
- Fargate Services
- Application Load Balancer (ALB)
- RDS PostgreSQL Instance
- CloudFront distribution
- S3 Bucket for static assets
- IAM roles and policies
- VPC with public/private subnets
- Security groups

### Deployment of microservices and defining AWS resources with AWS Cloud Development Kit (CDK)

Organize your CDK project

Structure your CDK project into logical modules or stacks based on your application's architecture. 

Define AWS resources with constructs

Use AWS CDK constructs to define your AWS resources, such as API Gateway endpoints, DynamoDB tables, and S3 buckets for hosting your React application.

API Gateway setup

Create an API Gateway to act as a single entry point for client requests, routing them to the appropriate microservices. 

You can define the gateway and its resources and methods using CDK constructs.

Serverless deployment (Lambda & API Gateway)

When using AWS Lambda for your Node.js microservices, your CDK code will define the Lambda functions, create deployment packages (ZIP archives or container images) for your code and its dependencies, and configure API Gateway endpoints to trigger your Lambda functions via HTTP requests.

Containerized Deployment (ECS/Fargate/EKS & ALB)

If you're using containers, your CDK code will define your container images, create Amazon Elastic Container Service (ECS) clusters, or Amazon Elastic Kubernetes Service (EKS) clusters, and define Elastic Load Balancers (ALBs) to distribute traffic to your containerized microservices.

Frontend Deployment (S3 & CloudFront)

Deploy your React frontend to an Amazon S3 bucket and use Amazon CloudFront for content delivery and caching, improving performance and scalability.

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

### References

AWS Cloud Development Kit

https://aws.amazon.com/cdk/

Using the AWS CDK as an IaC tool

https://docs.aws.amazon.com/prescriptive-guidance/latest/choose-iac-tool/aws-cdk.html

