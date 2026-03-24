import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export class LLMInferenceServerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create VPC
    const vpc = new ec2.Vpc(this, 'LLMInferenceVPC', {
      maxAzs: 2,
      natGateways: 1,
    });

    // Create ECS Cluster
    const cluster = new ecs.Cluster(this, 'LLMInferenceCluster', {
      vpc,
      containerInsights: true,
    });

    // Add EC2 capacity with GPU support
    cluster.addCapacity('GPUCapacity', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.G4DN, ec2.InstanceSize.XLARGE),
      minCapacity: 1,
      maxCapacity: 3,
      userData: ec2.UserData.forLinux(),
    });

    // Create secrets for sensitive data
    const secrets = new secretsmanager.Secret(this, 'LLMInferenceSecrets', {
      secretName: 'llm-inference-secrets',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          JWT_SECRET: '',
          OPENAI_API_KEY: '',
          HUGGINGFACE_API_KEY: '',
        }),
        generateStringKey: 'JWT_SECRET',
        excludeCharacters: '"@/\\',
      },
    });

    // Create CloudWatch log group
    const logGroup = new logs.LogGroup(this, 'LLMInferenceLogGroup', {
      logGroupName: '/aws/ecs/llm-inference-server',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create task definition
    const taskDefinition = new ecs.Ec2TaskDefinition(this, 'LLMInferenceTaskDef', {
      memoryLimitMiB: 8192,
    });

    // Add IAM permissions for the task
    taskDefinition.addToTaskRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'secretsmanager:GetSecretValue',
          'logs:CreateLogStream',
          'logs:PutLogEvents',
        ],
        resources: [secrets.secretArn, logGroup.logGroupArn],
      })
    );

    // Add container to task definition
    const container = taskDefinition.addContainer('LLMInferenceContainer', {
      image: ecs.ContainerImage.fromRegistry('your-account.dkr.ecr.region.amazonaws.com/llm-inference-server:latest'),
      memoryLimitMiB: 7168,
      cpu: 2048,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'llm-inference',
        logGroup,
      }),
      environment: {
        NODE_ENV: 'production',
        PORT: '3000',
        LLM_MODEL_NAME: 'meta-llama/Llama-3.1-8B-Instruct',
        USE_QUANTIZED_MODEL: 'true',
        QUANTIZATION_BITS: '4',
        GPU_MEMORY_FRACTION: '0.8',
      },
      secrets: {
        JWT_SECRET: ecs.Secret.fromSecretsManager(secrets, 'JWT_SECRET'),
        OPENAI_API_KEY: ecs.Secret.fromSecretsManager(secrets, 'OPENAI_API_KEY'),
        HUGGINGFACE_API_KEY: ecs.Secret.fromSecretsManager(secrets, 'HUGGINGFACE_API_KEY'),
      },
    });

    // Add GPU resources
    container.addUlimits({
      name: ecs.UlimitName.MEMLOCK,
      softLimit: -1,
      hardLimit: -1,
    });

    // Map container port
    container.addPortMappings({
      containerPort: 3000,
      protocol: ecs.Protocol.TCP,
    });

    // Create Application Load Balanced Fargate Service
    const service = new ecsPatterns.ApplicationLoadBalancedEc2Service(this, 'LLMInferenceService', {
      cluster,
      taskDefinition,
      publicLoadBalancer: true,
      desiredCount: 1,
      listenerPort: 443,
      protocol: ecsPatterns.ApplicationProtocol.HTTPS,
      domainName: 'your-domain.com', // Replace with your domain
      domainZone: undefined, // Add your hosted zone if you have one
    });

    // Configure health check
    service.targetGroup.configureHealthCheck({
      path: '/api/health',
      healthyHttpCodes: '200',
      interval: cdk.Duration.seconds(30),
      timeout: cdk.Duration.seconds(5),
      healthyThresholdCount: 2,
      unhealthyThresholdCount: 3,
    });

    // Auto scaling configuration
    const scaling = service.service.autoScaleTaskCount({
      minCapacity: 1,
      maxCapacity: 5,
    });

    scaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });

    scaling.scaleOnMemoryUtilization('MemoryScaling', {
      targetUtilizationPercent: 80,
      scaleInCooldown: cdk.Duration.seconds(300),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });

    // Output the load balancer DNS name
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: service.loadBalancer.loadBalancerDnsName,
      description: 'DNS name of the load balancer',
    });

    // Output the service URL
    new cdk.CfnOutput(this, 'ServiceURL', {
      value: `https://${service.loadBalancer.loadBalancerDnsName}`,
      description: 'URL of the LLM Inference Service',
    });
  }
}
