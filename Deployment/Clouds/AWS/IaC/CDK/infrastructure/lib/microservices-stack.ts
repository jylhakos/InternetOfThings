import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

interface MicroservicesStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
  ecsSecurityGroup: ec2.SecurityGroup;
  albSecurityGroup: ec2.SecurityGroup;
  database: rds.DatabaseInstance;
}

export class MicroservicesStack extends cdk.Stack {
  public readonly cluster: ecs.Cluster;
  public readonly loadBalancer: elbv2.ApplicationLoadBalancer;
  public readonly cloudFrontDistribution: cloudfront.Distribution;

  constructor(scope: Construct, id: string, props: MicroservicesStackProps) {
    super(scope, id, props);

    const { vpc, ecsSecurityGroup, albSecurityGroup, database } = props;

    // Create ECS Cluster
    this.cluster = new ecs.Cluster(this, 'MicroservicesCluster', {
      vpc,
      clusterName: 'microservices-cluster',
      containerInsights: true,
    });

    // Create Application Load Balancer
    this.loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'MicroservicesALB', {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
      loadBalancerName: 'microservices-alb',
    });

    // Create S3 bucket for frontend static assets
    const frontendBucket = new s3.Bucket(this, 'FrontendBucket', {
      bucketName: `microservices-frontend-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'error.html',
      publicReadAccess: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ACLS,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // CloudFront distribution for frontend
    this.cloudFrontDistribution = new cloudfront.Distribution(this, 'FrontendDistribution', {
      defaultBehavior: {
        origin: new cloudfront.S3Origin(frontendBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      additionalBehaviors: {
        '/api/*': {
          origin: new cloudfront.HttpOrigin(this.loadBalancer.loadBalancerDnsName, {
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY,
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        },
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });

    // Create task execution role
    const executionRole = new iam.Role(this, 'TaskExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
    });

    // Grant access to database secret
    database.secret?.grantRead(executionRole);

    // Create task role
    const taskRole = new iam.Role(this, 'TaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      inlinePolicies: {
        DatabaseAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'rds:DescribeDBInstances',
                'rds:DescribeDBClusters',
              ],
              resources: ['*'],
            }),
          ],
        }),
      },
    });

    // Create log groups
    const authServiceLogGroup = new logs.LogGroup(this, 'AuthServiceLogGroup', {
      logGroupName: '/ecs/auth-service',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const userServiceLogGroup = new logs.LogGroup(this, 'UserServiceLogGroup', {
      logGroupName: '/ecs/user-service',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const apiGatewayLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: '/ecs/api-gateway',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Auth Service Task Definition
    const authServiceTaskDef = new ecs.FargateTaskDefinition(this, 'AuthServiceTaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
      executionRole,
      taskRole,
    });

    authServiceTaskDef.addContainer('AuthServiceContainer', {
      image: ecs.ContainerImage.fromRegistry('your-ecr-repo/auth-service:latest'),
      environment: {
        NODE_ENV: 'production',
        PORT: '3001',
        DB_HOST: database.instanceEndpoint.hostname,
        DB_PORT: database.instanceEndpoint.port.toString(),
        DB_NAME: 'userdb',
      },
      secrets: {
        DB_USER: ecs.Secret.fromSecretsManager(database.secret!, 'username'),
        DB_PASSWORD: ecs.Secret.fromSecretsManager(database.secret!, 'password'),
        JWT_SECRET: ecs.Secret.fromSecretsManager(database.secret!, 'password'), // Use a dedicated secret in production
      },
      logging: ecs.LogDriver.awsLogs({
        logGroup: authServiceLogGroup,
        streamPrefix: 'auth-service',
      }),
      portMappings: [
        {
          containerPort: 3001,
          protocol: ecs.Protocol.TCP,
        },
      ],
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:3001/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    // User Service Task Definition
    const userServiceTaskDef = new ecs.FargateTaskDefinition(this, 'UserServiceTaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
      executionRole,
      taskRole,
    });

    userServiceTaskDef.addContainer('UserServiceContainer', {
      image: ecs.ContainerImage.fromRegistry('your-ecr-repo/user-service:latest'),
      environment: {
        NODE_ENV: 'production',
        PORT: '3002',
        DB_HOST: database.instanceEndpoint.hostname,
        DB_PORT: database.instanceEndpoint.port.toString(),
        DB_NAME: 'userdb',
        AUTH_SERVICE_URL: 'http://auth-service.microservices.local:3001',
      },
      secrets: {
        DB_USER: ecs.Secret.fromSecretsManager(database.secret!, 'username'),
        DB_PASSWORD: ecs.Secret.fromSecretsManager(database.secret!, 'password'),
      },
      logging: ecs.LogDriver.awsLogs({
        logGroup: userServiceLogGroup,
        streamPrefix: 'user-service',
      }),
      portMappings: [
        {
          containerPort: 3002,
          protocol: ecs.Protocol.TCP,
        },
      ],
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:3002/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    // API Gateway Task Definition
    const apiGatewayTaskDef = new ecs.FargateTaskDefinition(this, 'ApiGatewayTaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
      executionRole,
      taskRole,
    });

    apiGatewayTaskDef.addContainer('ApiGatewayContainer', {
      image: ecs.ContainerImage.fromRegistry('your-ecr-repo/api-gateway:latest'),
      environment: {
        NODE_ENV: 'production',
        PORT: '3000',
        AUTH_SERVICE_URL: 'http://auth-service.microservices.local:3001',
        USER_SERVICE_URL: 'http://user-service.microservices.local:3002',
      },
      logging: ecs.LogDriver.awsLogs({
        logGroup: apiGatewayLogGroup,
        streamPrefix: 'api-gateway',
      }),
      portMappings: [
        {
          containerPort: 3000,
          protocol: ecs.Protocol.TCP,
        },
      ],
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:3000/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    // Create ECS Services
    const authService = new ecs.FargateService(this, 'AuthService', {
      cluster: this.cluster,
      taskDefinition: authServiceTaskDef,
      desiredCount: 2,
      securityGroups: [ecsSecurityGroup],
      serviceName: 'auth-service',
      cloudMapOptions: {
        cloudMapNamespace: this.cluster.addDefaultCloudMapNamespace({
          name: 'microservices.local',
        }),
        name: 'auth-service',
      },
    });

    const userService = new ecs.FargateService(this, 'UserService', {
      cluster: this.cluster,
      taskDefinition: userServiceTaskDef,
      desiredCount: 2,
      securityGroups: [ecsSecurityGroup],
      serviceName: 'user-service',
      cloudMapOptions: {
        name: 'user-service',
      },
    });

    const apiGatewayService = new ecs.FargateService(this, 'ApiGatewayService', {
      cluster: this.cluster,
      taskDefinition: apiGatewayTaskDef,
      desiredCount: 2,
      securityGroups: [ecsSecurityGroup],
      serviceName: 'api-gateway',
      cloudMapOptions: {
        name: 'api-gateway',
      },
    });

    // Create target groups
    const apiGatewayTargetGroup = new elbv2.ApplicationTargetGroup(this, 'ApiGatewayTargetGroup', {
      vpc,
      port: 3000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        path: '/health',
        healthyHttpCodes: '200',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 3,
      },
    });

    // Register ECS service with target group
    apiGatewayService.attachToApplicationTargetGroup(apiGatewayTargetGroup);

    // Create ALB listener
    const listener = this.loadBalancer.addListener('PublicListener', {
      port: 80,
      open: true,
      defaultTargetGroups: [apiGatewayTargetGroup],
    });

    // Add HTTPS listener (you'll need to provide a certificate)
    // const httpsListener = this.loadBalancer.addListener('HttpsListener', {
    //   port: 443,
    //   certificates: [certificate],
    //   defaultTargetGroups: [apiGatewayTargetGroup],
    // });

    // Auto Scaling
    const authServiceScaling = authService.autoScaleTaskCount({
      minCapacity: 1,
      maxCapacity: 10,
    });

    authServiceScaling.scaleOnCpuUtilization('AuthServiceCpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(300),
    });

    const userServiceScaling = userService.autoScaleTaskCount({
      minCapacity: 1,
      maxCapacity: 10,
    });

    userServiceScaling.scaleOnCpuUtilization('UserServiceCpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(300),
    });

    const apiGatewayScaling = apiGatewayService.autoScaleTaskCount({
      minCapacity: 1,
      maxCapacity: 10,
    });

    apiGatewayScaling.scaleOnCpuUtilization('ApiGatewayScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(300),
    });

    // Outputs
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: this.loadBalancer.loadBalancerDnsName,
      description: 'Application Load Balancer DNS name',
      exportName: `${cdk.Stack.of(this).stackName}-LoadBalancerDNS`,
    });

    new cdk.CfnOutput(this, 'CloudFrontURL', {
      value: this.cloudFrontDistribution.distributionDomainName,
      description: 'CloudFront distribution URL',
      exportName: `${cdk.Stack.of(this).stackName}-CloudFrontURL`,
    });

    new cdk.CfnOutput(this, 'FrontendBucketName', {
      value: frontendBucket.bucketName,
      description: 'S3 bucket name for frontend',
      exportName: `${cdk.Stack.of(this).stackName}-FrontendBucket`,
    });
  }
}
