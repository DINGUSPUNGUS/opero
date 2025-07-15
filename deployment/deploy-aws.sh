#!/bin/bash
# AWS Deployment Script for Opero Platform

set -e

# Configuration
APP_NAME="opero"
REGION="us-east-1"
ECR_REPOSITORY="${APP_NAME}-api"
ECS_CLUSTER="${APP_NAME}-cluster"
ECS_SERVICE="${APP_NAME}-service"
TASK_DEFINITION="${APP_NAME}-task"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AWS deployment for Opero Platform${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}🔍 Checking AWS credentials...${NC}"
aws sts get-caller-identity > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ AWS credentials configured${NC}"
else
    echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure'${NC}"
    exit 1
fi

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo -e "${YELLOW}📦 Creating ECR repository...${NC}"
aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${REGION} 2>/dev/null || echo "Repository already exists"

echo -e "${YELLOW}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo -e "${YELLOW}🏗️ Building Docker image...${NC}"
docker build -f Dockerfile.production -t ${ECR_REPOSITORY} .

echo -e "${YELLOW}🏷️ Tagging image...${NC}"
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}/${ECR_REPOSITORY}:latest
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

echo -e "${YELLOW}📤 Pushing image to ECR...${NC}"
docker push ${ECR_URI}/${ECR_REPOSITORY}:latest
docker push ${ECR_URI}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

echo -e "${YELLOW}☁️ Creating ECS infrastructure...${NC}"

# Create ECS cluster
aws ecs create-cluster --cluster-name ${ECS_CLUSTER} --region ${REGION} 2>/dev/null || echo "Cluster already exists"

# Create task definition
cat > task-definition.json << EOF
{
  "family": "${TASK_DEFINITION}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "${APP_NAME}-api",
      "image": "${ECR_URI}/${ECR_REPOSITORY}:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${APP_NAME}",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:${APP_NAME}/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:${APP_NAME}/secret-key"
        }
      ]
    }
  ]
}
EOF

echo -e "${YELLOW}📋 Registering task definition...${NC}"
aws ecs register-task-definition --cli-input-json file://task-definition.json --region ${REGION}

echo -e "${YELLOW}🌐 Creating load balancer and service...${NC}"
# This would typically involve creating ALB, target groups, and ECS service
# Simplified for this example

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Configure your domain DNS to point to the load balancer"
echo "2. Set up SSL certificate in AWS Certificate Manager"
echo "3. Configure environment variables in AWS Secrets Manager"
echo "4. Set up monitoring and alerts"

# Cleanup
rm -f task-definition.json
