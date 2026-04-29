#!/bin/bash
# AWS DeepEval Deployment Script
# Deploy BERT evaluation to Amazon EC2

# 1. Create EC2 instance
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t3.large \
    --key-name your-key-pair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --user-data file://deepeval-userdata.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=BERT-DeepEval-Evaluator}]'

# 2. User data script (deepeval-userdata.sh)
cat > deepeval-userdata.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Install dependencies
pip3 install deepeval torch transformers

# Clone repository
git clone https://github.com/your-repo/bert-evaluation.git
cd bert-evaluation

# Run evaluation
python3 evaluation_examples/deepeval_example.py

# Upload results to S3
aws s3 cp deepeval_results.json s3://your-bucket/evaluation-results/
EOF

# 3. Create CloudFormation template for automated deployment
cat > deepeval-cloudformation.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'BERT DeepEval Evaluation Infrastructure'

Resources:
  BERTEvaluationInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890
      InstanceType: t3.large
      IamInstanceProfile: !Ref InstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          pip3 install deepeval torch transformers
          python3 /path/to/deepeval_example.py
          aws s3 cp results.json s3://your-results-bucket/
      Tags:
        - Key: Name
          Value: BERT-DeepEval-Evaluator

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles: [!Ref EC2Role]

  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: assume-role
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3FullAccess

  ResultsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: bert-deepeval-results
EOF

echo "📁 AWS deployment scripts created"
echo "🚀 Deploy with: aws cloudformation create-stack --stack-name bert-deepeval --template-body file://deepeval-cloudformation.yaml"
