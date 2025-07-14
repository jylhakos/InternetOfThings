

# Microservices Application with React and Node.js

A comprehensive microservices architecture implementation with React/Next.js frontend and Node.js backend services, deployed on AWS using Infrastructure as Code (CloudFormation).

## 🏗️ Architecture Overview

This project implements a modern microservices architecture with:

- **Frontend**: React + Next.js Single Page Application (SPA)
- **Backend**: Node.js + Express.js microservices
- **Database**: PostgreSQL on AWS RDS
- **API Gateway**: Single entry point for all services
- **Authentication**: JWT-based authentication service
- **Deployment**: AWS CloudFormation (Infrastructure as Code)
- **Security**: IAM roles, VPC, security groups, HTTPS/SSL
- **CDN**: CloudFront for static asset delivery

## 📁 Project Structure

```
├── backend/
│   ├── auth-service/          # JWT authentication microservice
│   ├── user-service/          # User management with PostgreSQL
│   ├── api-gateway/           # API gateway and routing
│   └── shared/                # Shared utilities and types
├── frontend/                  # React + Next.js SPA
├── infrastructure/            # CloudFormation templates
│   ├── 01-network.yaml        # VPC, subnets, security groups
│   ├── 02-database.yaml       # RDS PostgreSQL
│   ├── 03-ecs.yaml           # ECS cluster and services
│   └── 04-frontend.yaml       # S3, CloudFront, Route53
├── docker/                    # Docker configurations
├── scripts/                   # Deployment and setup scripts
└── docker-compose.yml         # Local development environment
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Docker and Docker Compose
- AWS CLI configured with appropriate permissions
- Git

### Local Development

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd microservices-project
   chmod +x scripts/*.sh
   ```

2. **Install dependencies and setup environment:**
   ```bash
   ./scripts/dev-setup.sh setup
   ```

3. **Start the development environment:**
   ```bash
   ./scripts/dev-setup.sh start
   ```

4. **Access the application:**
   - Frontend: http://localhost:3001
   - API Gateway: http://localhost:3000
   - PostgreSQL: localhost:5432

5. **View logs:**
   ```bash
   ./scripts/dev-setup.sh logs [service-name]
   ```

### AWS Production Deployment

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Deploy to AWS:**
   ```bash
   ./scripts/deploy.sh deploy
   ```

3. **Check deployment status:**
   ```bash
   ./scripts/deploy.sh status
   ```

4. **Destroy infrastructure:**
   ```bash
   ./scripts/deploy.sh destroy
   ```

## 🛠️ Services

### Auth Service (Port 3001)
- **Purpose**: JWT token generation and validation
- **Endpoints**: 
  - `POST /api/auth/signup` - User registration
  - `POST /api/auth/signin` - User login
  - `POST /api/auth/verify` - Token verification

### User Service (Port 3002)
- **Purpose**: User management with PostgreSQL database
- **Endpoints**:
  - `GET /api/users/profile` - Get user profile
  - `PUT /api/users/profile` - Update user profile
  - `GET /api/users` - List all users (demo)

### API Gateway (Port 3000)
- **Purpose**: Single entry point, request routing, load balancing
- **Features**: Rate limiting, CORS, proxy middleware

### Frontend (Port 3001 in dev)
- **Technology**: React + Next.js with TypeScript
- **Features**: 
  - Single Page Application (SPA)
  - Server-Side Rendering (SSR)
  - JWT authentication
  - Responsive design with Tailwind CSS

## 🔐 Security Features

- **Authentication**: JWT tokens with secure secret management
- **Network Security**: VPC with public/private subnets
- **Database Security**: RDS in private subnets with security groups
- **HTTPS**: SSL/TLS encryption with CloudFront
- **IAM**: Least privilege access with specific roles
- **Secrets**: AWS Secrets Manager for sensitive data

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🌐 AWS Infrastructure

### Network Layer
- VPC with public and private subnets across 2 AZs
- Internet Gateway and NAT Gateways
- Security Groups for ALB, ECS, and RDS

### Compute Layer
- ECS Fargate cluster for containerized services
- Application Load Balancer for traffic distribution
- Auto-scaling based on CPU and memory usage

### Storage Layer
- RDS PostgreSQL with encryption and backups
- S3 for static website hosting
- CloudFront CDN for global content delivery

### Security Layer
- IAM roles and policies
- Secrets Manager for credentials
- SSL certificates for HTTPS

## 🔧 Development Commands

```bash
# Local development
./scripts/dev-setup.sh start     # Start all services
./scripts/dev-setup.sh stop      # Stop all services
./scripts/dev-setup.sh logs      # View logs
./scripts/dev-setup.sh test      # Run tests
./scripts/dev-setup.sh clean     # Clean up containers

# AWS deployment
./scripts/deploy.sh deploy       # Deploy to AWS
./scripts/deploy.sh status       # Check stack status
./scripts/deploy.sh destroy      # Destroy infrastructure
```

## 🧪 Testing

### API Testing
```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:3001/health
curl http://localhost:3002/health

# User registration
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# User login
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 📊 Monitoring and Logging

- **CloudWatch**: Application and infrastructure metrics
- **ECS Logging**: Centralized logging for all services
- **Health Checks**: Automated health monitoring
- **Alarms**: Automated alerts for critical issues

## 🔄 CI/CD Pipeline

The project includes deployment scripts that can be integrated with:
- GitHub Actions
- AWS CodePipeline
- Jenkins
- GitLab CI/CD

## 📝 Environment Variables

### Backend Services
```env
NODE_ENV=production
JWT_SECRET=<secure-secret>
DB_HOST=<rds-endpoint>
DB_USER=<db-username>
DB_PASSWORD=<db-password>
```

### Frontend
```env
NEXT_PUBLIC_API_URL=<api-gateway-url>
```

## 🎯 Key Features

✅ **Microservices Architecture** - Loosely coupled, independently deployable services  
✅ **RESTful APIs** - Standard HTTP methods with JSON responses  
✅ **JWT Authentication** - Stateless authentication with secure tokens  
✅ **PostgreSQL Database** - Relational database with ACID compliance  
✅ **Docker Containerization** - Consistent deployment across environments  
✅ **AWS CloudFormation** - Infrastructure as Code for reproducible deployments  
✅ **SSL/HTTPS** - Secure communication with TLS encryption  
✅ **CDN Integration** - Fast global content delivery with CloudFront  
✅ **Auto-scaling** - Automatic scaling based on demand  
✅ **Monitoring** - Comprehensive logging and metrics  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## References

- [Deploy a React-based single-page application to Amazon S3 and CloudFront](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-a-react-based-single-page-application-to-amazon-s3-and-cloudfront.html)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/introduction.html)
- [Microservices Pattern](https://microservices.io/)
- [Next.js Documentation](https://nextjs.org/docs)