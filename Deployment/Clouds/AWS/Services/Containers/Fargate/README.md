# Fargate

Fargate is a serverless, pay-as-you-go compute engine.

## Example: Go application with RESTful APIs operates within a Docker container deployed on AWS using ECS and Fargate.

Follow this step-by-step approach to deploy your Go application on AWS.

1. Prepare your Go application

Ensure your Go application includes necessary packages like net/http for handling HTTP requests and responses, and potentially a routing library (like gorilla/mux) for managing API endpoints.

Create a Go application that implements RESTful APIs for CRUD operations.

Use a PostgreSQL driver (e.g., github.com/lib/pq) to connect to the database.

Create a .env file to store environment variables like database credentials, allowing secure configuration.

```

package main

import (
    "database/sql"
    "encoding/json"
    "log"
    "net/http"
    "os"

    "github.com/gorilla/mux"
    _ "github.com/lib/pq"
)

type App struct {
    DB *sql.DB
}

func main() {
    app := &App{}
    app.Initialize()
    app.Run(":8080")
}

func (a *App) Initialize() {
    dbHost := os.Getenv("DB_HOST")
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    
    connectionString := fmt.Sprintf("host=%s user=%s password=%s dbname=%s sslmode=require", 
        dbHost, dbUser, dbPassword, dbName)
    
    var err error
    a.DB, err = sql.Open("postgres", connectionString)
    if err != nil {
        log.Fatal(err)
    }
}

func (a *App) Run(addr string) {
    router := mux.NewRouter()
    // Add your API routes here
    router.HandleFunc("/health", a.healthCheck).Methods("GET")
    
    log.Printf("Server starting on %s", addr)
    log.Fatal(http.ListenAndServe(addr, router))
}

func (a *App) healthCheck(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

```

[main.go](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/main.go)

First, containerize your Go application with Docker.

```

    # Use an official Go runtime as a parent image
    FROM golang:latest
    
    # Set the working directory in the container
    WORKDIR /app
    
    # Copy the source code into the container
    COPY . .
    
    # Download all the dependencies.
    RUN go mod download
    
    # Build the Go application
    RUN go build -o main .
    
    # Expose port 8080 to the outside world
    EXPOSE 8080
    
    # Command to run the executable
    CMD ["/app/main"]


```

Build the Docker image:

Use the docker build command to build your Docker image locally. 

For example: docker build -t my-go-app .

Test the Docker image locally:

Run your Docker image locally using docker run -p 8080:8080 my-go-app and test your API endpoints.

Push the Docker image to a container registry:

You'll need to push your Docker image to a container registry like Amazon Elastic Container Registry (ECR) or Docker Hub.

[Dockerfile](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/Dockerfile)

Build and push Docker image:

```

	$ docker build -t my-go-app .


```
Build the Docker image locally

Tag the Docker image:

```

	$ docker tag my-go-app:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-go-app:latest

```

Push the image to Amazon Elastic Container Registry (ECR):

```


	$ aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com

	$ docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-go-app:latest

```

Then, set up your AWS infrastructure, including ECS, Fargate, RDS, IAM roles, Route53, and VPC. 

2. Set up your AWS infrastructure

Infrastructure as Code (IaC) with Terraform

Set Up Terraform for AWS

Install Terraform:

Download and install [Terraform](https://www.terraform.io/downloads) from its official site.

Define resources

Create Terraform files for resources:

Create a Virtual Private Cloud (VPC):

Define a VPC with public and private subnets, internet gateways, and route tables to isolate your application and database.

Set up Route 53:

Configure a hosted zone and record sets to map your domain name to your application's endpoint.

Create an RDS PostgreSQL instance:

Provision a PostgreSQL database instance within your VPC, ensuring it's not publicly accessible.

[Terraform for RDS](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/rds.tf)

Set up IAM roles:

Define IAM roles for ECS tasks and ECS execution to grant permissions for accessing other AWS resources, like RDS and ECR.

```

	resource "aws_iam_role" "ecs_task_execution_role" {
	  name = "ecsTaskExecutionRole"

	  assume_role_policy = jsonencode({
	    Version = "2012-10-17"
	    Statement = [{
	      Action = "sts:AssumeRole"
	      Effect = "Allow"
	      Principal = {
	        Service = "ecs-tasks.amazonaws.com"
	      }
	    }]
	  })

	  managed_policy_arns = [
	    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
	  ]
	}

```
ECR repository:

```

	resource "aws_ecr_repository" "go_app_repo" {
  		name = "my-go-app"
	}

```

Create an ECS cluster:

Create an ECS cluster, which will be the environment where your application runs.

```

	resource "aws_ecs_cluster" "go_app_cluster" {
	  name = "go-app-cluster"
	}

```
Create a Fargate profile:

Define a Fargate profile to specify the VPC and subnets where your Fargate tasks will run, ensuring they are within your VPC. 

[Terraform for AWS](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/main.tf)

```

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "14.5"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  username             = "admin"
  password             = "securepassword"
  publicly_accessible  = false
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}

```
Task

```


	resource "aws_ecs_task_definition" "go_app" {
	  family                   = "go-app-task"
	  container_definitions    = jsonencode([{
	    name        = "go-app-container"
	    image       = "<aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-go-app:latest"
	    memory      = 512
	    cpu         = 256
	    portMappings = [{
	      containerPort = 8080
	      hostPort      = 8080
	    }]
	    environment = [{
	      name  = "DATABASE_URL"
	      value = "postgres://admin:securepassword@<rds_endpoint>:5432/mydb"
	    }]
	  }])
	  requires_compatibilities = ["FARGATE"]
	  network_mode             = "awsvpc"
	  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
	  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn
	  memory                   = "512"
	  cpu                      = "256"
	}


```

Fargate Service

```

resource "aws_ecs_service" "go_app_service" {
  name            = "go-app-service"
  cluster         = aws_ecs_cluster.go_app_cluster.id
  task_definition = aws_ecs_task_definition.go_app.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.app_subnets[*].id
    security_groups  = [aws_security_group.app_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.go_app_target_group.arn
    container_name   = "go-app-container"
    container_port   = 8080
  }
}

```
3. Set up PostgreSQL on AWS RDS

Create an RDS Instance:

Go to AWS RDS service and create a PostgreSQL instance.

Configure VPC, security groups, availability zones, and subnets.

Set the username, password, and database name.

Allow Connections:

Add security group rules to allow incoming connections from the application (e.g., ECS tasks).

Store Credentials Securely:

Use AWS Secrets Manager or SSM Parameter Store to store database credentials.

4. Configure ECS and deploy with Fargate

Create a task definition:

This definition specifies the Docker image to use, the resources (CPU and memory) required, the port mappings, and the IAM role for the task.

Define a service:

Create an ECS service, which manages the desired number of tasks and ensures they are running correctly. You can use Fargate as the launch type for your service.

[ECS Cluster and Task](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/ecs.tf)

Configure service discovery (optional):

You can use AWS Cloud Map or Application Load Balancer for service discovery, allowing other services to easily find your Go application.

Deploy your application:

Deploy your ECS service. 

ECS and Fargate will handle the deployment, scaling, and management of your Go application within your VPC. 

Application Load Balancer (ALB)

```

	resource "aws_lb" "go_app_alb" {
	  name               = "go-app-alb"
	  internal           = false
	  load_balancer_type = "application"
	  security_groups    = [aws_security_group.alb_sg.id]
	  subnets            = aws_subnet.app_subnets[*].id
	}

	resource "aws_lb_target_group" "go_app_target_group" {
	  name        = "go-app-tg"
	  port        = 8080
	  protocol    = "HTTP"
	  vpc_id      = aws_vpc.main.id
	  target_type = "ip"
	}

	resource "aws_lb_listener" "http" {
	  load_balancer_arn = aws_lb.go_app_alb.arn
	  port              = 80
	  protocol          = "HTTP"

	  default_action {
	    type             = "forward"
	    target_group_arn = aws_lb_target_group.go_app_target_group.arn
	  }
	}

```
[ALB](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/alb.tf)

Route53 for Domain

```

	resource "aws_route53_record" "go_app_record" {
	  zone_id = aws_route53_zone.main.zone_id
	  name    = "myapp.example.com"
	  type    = "A"
	  alias {
	    name                   = aws_lb.go_app_alb.dns_name
	    zone_id                = aws_lb.go_app_alb.zone_id
	    evaluate_target_health = true
	  }
	}

```

[Route53](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/route53.tf)

5. Deployment

Initialize Terraform:

```

	$ terraform init
```

Plan:

```

	$ terraform plan

```

Apply changes:

```
	
	$ terraform apply

```

Alternatively run Bash script to deploy

```

	$ chmod +x deploy.sh

	$ ./deploy.sh

```
Update DNS: 

Configure your domain's nameservers to point to the Route53 hosted zone.

SSL/TLS:

Enable SSL/TLS with AWS Certificate Manager for HTTPS.

[bash](https://github.com/jylhakos/InternetOfThings/blob/main/Deployment/Clouds/AWS/Services/Containers/Fargate/deploy.sh)

References

What is Amazon Elastic Container Service (ECS)?

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html

Get started with Amazon ECS on Fargate

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started-fargate.html

Deploy Java microservices on Amazon ECS using AWS Fargate

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/deploy-java-microservices-on-amazon-ecs-using-aws-fargate.html

Access container applications privately on Amazon ECS by using AWS Fargate, AWS PrivateLink, and a Network Load Balancer

https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/access-container-applications-privately-on-amazon-ecs-by-using-aws-fargate-aws-privatelink-and-a-network-load-balancer.html

Getting started with Amazon Relational Database Service

https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/what-is-rds.html
