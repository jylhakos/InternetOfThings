# Quick start

## Overview

This project implements microservices and uses Infrastructure as code (IaC) with AWS Cloud Development Kit.

- **Backend**: Node.js microservices (Auth, User, API Gateway)
- **Frontend**: React + Next.js with TypeScript
- **Database**: PostgreSQL on AWS RDS
- **Infrastructure**: AWS CDK for Infrastructure as Code (IaC)
- **Deployment**: Docker containers on AWS ECS/Fargate

## Local development

Install prerequisites to implement Node.js microservices with React frontend and use AWS CDK for deployment on AWS.

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- AWS CLI (for AWS deployment)
- AWS CDK CLI (for AWS deployment)

### 1. Clone and setup
```bash
# Install all dependencies and start local development
./deploy.sh dev
```

This single command will:
- Install all dependencies
- Build all services
- Start Docker Compose with all services
- Create database tables automatically

### 2. Access to applications
- **Frontend**: http://localhost:3003
- **API Gateway**: http://localhost:3000
- **Authorization**: http://localhost:3001
- **User**: http://localhost:3002

### 3. Test the APIs

#### Create user account
```bash
curl -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phoneNumber": "+1234567890",
    "password": "password123"
  }'
```

#### Sign In
```bash
curl -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Get user profile (replace TOKEN with JWT from signin)
```bash
curl -X GET http://localhost:3000/users/profile \
  -H "Authorization: Bearer TOKEN"
```

## AWS deployment

### 1. Setup AWS credentials
```bash
aws configure
```

### 2. Install AWS CDK
```bash
npm install -g aws-cdk
```

### 3. Deploy to AWS
```bash
./deploy.sh deploy
```

1. Build all services
2. Create Docker images (you'll need to push to ECR)
3. Deploy infrastructure using CDK
4. Set up VPC, RDS, ECS, CloudFront, etc.

## Architecture

### Microservices
1. **Authorization** (Port 3001)
   - User registration and login
   - JWT token generation and validation
   - Password hashing with bcrypt

2. **User** (Port 3002)
   - User profile management
   - CRUD operations
   - Database interactions

3. **API Gateway** (Port 3000)
   - Single entry point for all services
   - Request routing and proxy
   - Rate limiting and CORS

### Frontend
- Server-side rendering with Next.js
- TypeScript for type safety
- Responsive design with Tailwind CSS
- JWT-based authentication
- Protected routes and state management

### AWS Infrastructure
- **ECS Fargate**: Serverless container orchestration
- **RDS PostgreSQL**: Managed database
- **Application Load Balancer**: Traffic distribution
- **CloudFront**: CDN for frontend assets
- **S3**: Static asset storage
- **VPC**: Network isolation and security

## Security
- JWT-based authentication
- Password hashing with bcrypt
- Security groups and VPC isolation
- HTTPS encryption (in production)
- Rate limiting
- Input validation
- SQL injection prevention

## Scaling and monitoring
- Auto-scaling based on CPU utilization
- CloudWatch logging for all services
- Health checks for all containers
- Performance insights for database
- Application Load Balancer health checks

## Development workflow

### Local development
```bash
# Start services
./deploy.sh dev

# View logs
docker-compose logs -f

# Stop services
./deploy.sh stop
```

### Building and testing
```bash
# Install dependencies
./deploy.sh install

# Build all services
./deploy.sh build

# Run tests (when implemented)
npm test
```

### Cleanup
```bash
# Clean all build artifacts
./deploy.sh clean
```

## Environment variables

### Backend
- `DB_HOST`: Database host
- `DB_PORT`: Database port (5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `JWT_SECRET`: Secret key for JWT signing
- `NODE_ENV`: Environment (development/production)

### Frontend
- `NEXT_PUBLIC_API_URL`: API Gateway URL

## Production

1. **Security**
   - Use AWS Secrets Manager for sensitive data
   - Enable HTTPS with SSL certificates
   - Configure proper CORS origins
   - Set up AWS WAF for additional protection

2. **Scaling**
   - Configure auto-scaling policies
   - Set up multi-AZ deployment
   - Use Application Load Balancer health checks
   - Monitor with CloudWatch

3. **Database**
   - Enable Multi-AZ for RDS
   - Configure automated backups
   - Set up read replicas if needed
   - Monitor performance insights

4. **Monitoring**
   - Set up CloudWatch alarms
   - Configure log aggregation
   - Use AWS X-Ray for tracing
   - Monitor application metrics

## Troubleshooting

### Issues
1. **Services not starting**: Check Docker logs
2. **Database connection**: Verify credentials and network
3. **API not responding**: Check service health endpoints
4. **Frontend not loading**: Verify environment variables

### Debug commands
```bash
# Check service health
curl http://localhost:3000/health
curl http://localhost:3001/health
curl http://localhost:3002/health

# View Docker logs
docker-compose logs auth-service
docker-compose logs user-service
docker-compose logs api-gateway

# Check database connection
docker-compose exec postgres psql -U postgres -d userdb
```
