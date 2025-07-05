# Spring Boot 

Spring Boot accelerates application development.

## Deploying Spring Boot application on AWS

Deploying a Spring Boot (Java) application on AWS can be achieved through the following ways, each offering different levels of control and management.

1. AWS Elastic Beanstalk

AWS Elastic Beanstalk is a popular option for ease of use. You package your Spring Boot application as a JAR file and upload it to Elastic Beanstalk.

Elastic Beanstalk handles the provisioning of infrastructure (EC2 instances, load balancers, etc.), deployment, scaling, and monitoring, simplifying the process.

Steps

Create an Elastic Beanstalk application in the AWS console.

Select "Java" as the platform and "Upload your code."

Upload your Spring Boot JAR file.

Configure environment variables, service access, and other settings as needed.

2. AWS EC2

You launch an EC2 instance, install Java, and manually deploy your Spring Boot JAR file.

AWS EC2 offers the most control over the server environment.

Steps

Launch an EC2 instance.

Connect to the instance and install Java.

Upload your Spring Boot JAR file to the instance (e.g., via SCP or S3).

Run your application using java -jar your-app.jar.

Configure security groups to allow necessary inbound traffic (e.g., HTTP/HTTPS).

3. AWS Lambda (Serverless)

For serverless deployments, you can package your Spring Boot application to run as an AWS Lambda function, often using tools like AWS SAM or the aws-serverless-java-container library.

The serverless deployments requires adapting your Spring Boot application to the Lambda execution model and handling API Gateway integration for web requests.

4. AWS ECS/EKS (Containerization)

Containerize your Spring Boot application using Docker, then deploy it to Amazon Elastic Container Service (ECS) or Amazon Elastic Kubernetes Service (EKS).

### Example: Spring Boot for RESTful web services on AWS

Building a full-stack application with a Java Spring Boot backend, PostgreSQL database, Docker containerization, and AWS deployment using Terraform involves several steps.

1. Configure Spring Initializr

Configure Spring Initializr to generate a Gradle project with the specified dependencies either using Spring Initializr Web or Spring Boot CLI.

A. Spring Initializr Web

Navigate to Spring Initializr

Go to https://start.spring.io/

Configure project settings

```

	Project: Select Groovy or Gradle
	Language: Select Java or Kotlin
	Spring Boot: Choose latest stable version (e.g., 3.2.x)
	Project Metadata:
	Group: com.example
	Artifact: demo
	Name: demo
	Package name: com.example.demo
	Packaging: Jar
	Java: 17 or 21

```

Add dependencies

```

	Spring Web - Build web, including RESTful applications
	Spring Data JPA - Persist data in SQL stores with Java Persistence API
	PostgreSQL Driver - A JDBC and R2DBC driver for PostgreSQL

```

B. Spring Boot CLI

```

	spring init \
	  --dependencies=web,data-jpa,postgresql \
	  --build=gradle \
	  --java-version=17 \
	  --group-id=com.example \
	  --artifact-id=demo \
	  --name=demo \
	  --package-name=com.example.demo \
	  demo-project

```

The generated build.gradle file will include plugins, group, dependencies etc. variables.

After generation

Import the project into your preferred IDE and configure database connection.

Edit src/main/resources/application.properties file.

2. Spring Boot RESTful API for CRUD operations

Setup

Use Spring Initializr to generate a new Gradle project with dependencies like Spring Web, Spring Data JPA, PostgreSQL Driver, and Lombok.

Spring Boot configures JPA based on application.properties file.

###  Entity layer (data model)

Create Java classes representing your database tables, annotated with @Entity, @Id, @GeneratedValue, etc.

```

	@Entity
	@Table(name = "users")
	public class User {
	    @Id
	    @GeneratedValue(strategy = GenerationType.IDENTITY)
	    private Long id;
	    
	    @Column(nullable = false)
	    private String name;
	    
	    @Column(nullable = false, unique = true)
	    private String email;
	    
	    // constructors, getters, setters
	}

```
The User entity defines the database table structure with JPA persistence.

```

	@Entity

```

Marks class as JPA entity

```

	@Table(name = "users")

```

Maps to database table

```

	@Column

```
Column constraints (nullable, unique, etc.)

### Repository layer (data access)

Define interfaces extending JpaRepository for each entity to handle basic CRUD operations.

```

	@Repository
	public interface UserRepository extends JpaRepository<User, Long> {
	    
	    // Custom query methods
	    Optional<User> findByEmail(String email);
	    
	    List<User> findByNameContainingIgnoreCase(String name);
	    
	    @Query("SELECT u FROM User u WHERE u.email = ?1")
	    Optional<User> findUserByEmail(String email);
	    
	    @Modifying
	    @Query("UPDATE User u SET u.name = ?1 WHERE u.id = ?2")
	    int updateUserName(String name, Long id);
	}

```

The UserRepository provides database CRUD operations.

```

	save(entity)

```

Insert/Update

```

	findById(id)

```

Find by primary key

```

	findAll()

```

Get all records

```

deleteById(id)

```

Delete by primary key

### Service layer (logic)

Implement service classes that encapsulate business logic and interact with the repositories.

Consider a UserService that depends on a UserRepository to perform database operations.

UserService is not directly tied to the concrete implementation of UserRepository.

```
	@Service
	@Transactional
	public class UserService {
	    
	    @Autowired
	    private UserRepository userRepository;
	    
	    public List<User> getAllUsers() {
	        return userRepository.findAll();
	    }
	    
	    public Optional<User> getUserById(Long id) {
	        return userRepository.findById(id);
	    }
	    
	    public User createUser(User user) {
	        // Validation logic
	        if (userRepository.findByEmail(user.getEmail()).isPresent()) {
	            throw new RuntimeException("Email already exists");
	        }
	        return userRepository.save(user);
	    }
	    
	    public User updateUser(Long id, User userDetails) {
	        User user = userRepository.findById(id)
	            .orElseThrow(() -> new RuntimeException("User not found"));
	        
	        user.setName(userDetails.getName());
	        user.setEmail(userDetails.getEmail());
	        
	        return userRepository.save(user); // JPA automatically updates
	    }
	    
	    public void deleteUser(Long id) {
	        if (!userRepository.existsById(id)) {
	            throw new RuntimeException("User not found");
	        }
	        userRepository.deleteById(id);
	    }
	}

```
UserService is a service class, annotated with @Service, making it another Spring component.

UserRepository is an interface defining data access operations.

UserRepositoryImpl is a concrete implementation of UserRepository, annotated with @Repository to make it a Spring component (a bean).

The @Autowired annotation tells Spring that "When creating an instance of UserService, find a bean of type UserRepository in the application context and inject it into this constructor."

The @Service annotation is Spring service component.

The @Transactional annotation is database transaction management and ensures ACID properties.

### Controller layer

The UserController handles HTTP requests.

Create REST controllers using @RestController and @RequestMapping to expose endpoints for CRUD operations, handling HTTP requests (GET, POST, PUT, DELETE) and mapping them to service methods.

```

	@RestController
	@RequestMapping("/api/users")
	@CrossOrigin(origins = "*")
	public class UserController {
	    
	    @Autowired
	    private UserService userService;
	    
	    @GetMapping
	    public ResponseEntity<List<User>> getAllUsers() {
	        List<User> users = userService.getAllUsers();
	        return ResponseEntity.ok(users);
	    }
	    
	    @PostMapping
	    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
	        try {
	            User createdUser = userService.createUser(user);
	            return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
	        } catch (RuntimeException e) {
	            return ResponseEntity.badRequest().build();
	        }
	    }
	    
	    @PutMapping("/{id}")
	    public ResponseEntity<User> updateUser(@PathVariable Long id, 
	                                         @Valid @RequestBody User userDetails) {
	        try {
	            User updatedUser = userService.updateUser(id, userDetails);
	            return ResponseEntity.ok(updatedUser);
	        } catch (RuntimeException e) {
	            return ResponseEntity.notFound().build();
	        }
	    }
	}

```
The annotations in UserController.java file

```

	@RestController

```

Combines @Controller and @ResponseBody

Marks this class as a REST API controller

```

	@RequestMapping("/api/users")

```

Sets the base URL path for all endpoints in this controller

```

	@CrossOrigin(origins = "*")

```
Enables Cross-Origin Resource Sharing (CORS)

Allows requests from any domain (* means all origins)

Essential for frontend applications running on different ports/domains

All methods will be accessible under /api/users

Dependency Injection (DI)

Spring "injects" those dependencies into the class.

When applied @Autowired annotation to a field, constructor, or setter method, Spring Boot instructs the Spring IoC container to automatically find a matching bean (an object managed by Spring) of the required type and inject it into the annotated component. 

```

	@Autowired
	private UserService userService;

```
Enables Spring's dependency injection

Automatically injects an instance of UserService

ResponseEntity Class

ResponseEntity provides complete control over the HTTP response:

```

	ResponseEntity<T>

```
T is the response body type

Includes status code, headers, and body

The controller follows REST conventions and provides a complete CRUD API for user management, working in conjunction with the UserService and UserRepository layers.

Database initialization

Configure application.properties or application.yml to connect to your PostgreSQL database.

Data flows

Saving data with PUT/POST operations

```

	HTTP Request → Controller → Service → Repository → JPA → Database

```
Controller receives JSON data
Service validates business rules
Repository calls JPA methods
JPA/Hibernate generates SQL
Database stores data

Retrieving data with GET operations

```

	Database → JPA → Repository → Service → Controller → HTTP Response

```
Database returns raw data
JPA/Hibernate maps to entities
Repository returns Java objects
Service applies business logic
Controller converts to JSON response


Project

```

	src/
	├── main/
	│   ├── java/
	│   │   └── com/example/demo/
	│   │       ├── DemoApplication.java
	│   │       ├── controller/
	│   │       │   └── UserController.java
	│   │       ├── entity/
	│   │       │   └── User.java
	│   │       ├── repository/
	│   │       │   └── UserRepository.java
	│   │       └── service/
	│   │           └── UserService.java
	│   └── resources/
	│       └── application.yml
	└── test/

```

3. Dockerization

Dockerfile for Java application

Use a base image with Java (e.g., openjdk:17-jdk-slim).

Copy your built Spring Boot JAR file into the container.

Expose the application's port.

Define the entry point to run the JAR.

```

    FROM openjdk:17-jdk-slim
    ARG JAR_FILE=build/libs/*.jar
    COPY ${JAR_FILE} app.jar
    EXPOSE 8080
    ENTRYPOINT ["java", "-jar", "/app.jar"]

```

Dockerfile for PostgreSQL

Use the official postgres Docker image.

Docker Compose (Optional)

Create a docker-compose.yml to define and link your Java application and PostgreSQL containers for local development and testing.

4. Deployment on AWS with Terraform

IAM Roles

Create specific IAM roles with necessary permissions for your web service (e.g., EC2 permissions for running instances, EKS permissions for cluster management, S3 permissions for storing Docker images).

ECR (Elastic Container Registry)

Build your Docker images and push them to ECR, which acts as a private Docker registry on AWS.

Terraform configuration

Provider configuration

Configure the AWS provider in your Terraform files.

EC2 deployment

Define aws_instance resources for your EC2 instances.

Configure user data to pull Docker images from ECR and run containers (Java app, Nginx).

Set up security groups to control network access.

EKS Deployment (for container orchestration)

Define aws_eks_cluster and aws_eks_node_group resources.

Configure Kubernetes deployments and services to manage your application containers.

Database 

Use aws_db_instance for managed PostgreSQL with RDS, or deploy PostgreSQL in a container on EC2/EKS.

Networking

Configure VPCs, subnets, and route tables as needed.

Nginx Configuration (if used as a reverse proxy)

Create a nginx.conf file to proxy requests to your Spring Boot application.

Include this configuration in your Nginx Docker image or mount it as a volume.

4. Running on Docker containers

Local

Use docker-compose up to run your application and database locally.

AWS

Terraform will provision the necessary AWS resources and either directly run containers on EC2 or deploy them within an EKS cluster. Nginx, if used, will be configured to serve as a reverse proxy for your Java application.

References

Building an Application with Spring Boot

https://spring.io/guides/gs/spring-boot

Accessing Data with JPA

https://spring.io/guides/gs/accessing-data-jpa