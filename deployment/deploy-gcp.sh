#!/bin/bash
# Google Cloud Platform Deployment Script for Opero Platform

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
APP_NAME="opero"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${APP_NAME}-api"
SERVICE_NAME="${APP_NAME}-api"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting GCP deployment for Opero Platform${NC}"

# Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not installed${NC}"
    exit 1
fi

# Authenticate and set project
echo -e "${YELLOW}🔐 Setting up GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
gcloud auth configure-docker

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Build and push image
echo -e "${YELLOW}🏗️ Building image with Cloud Build...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} --file Dockerfile.production .

# Create Cloud SQL instance
echo -e "${YELLOW}🗄️ Setting up Cloud SQL...${NC}"
gcloud sql instances create ${APP_NAME}-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=${REGION} \
    --root-password=your-secure-password \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-release-channel=production \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 || echo "Database already exists"

# Create database and user
gcloud sql databases create opero_db --instance=${APP_NAME}-db || echo "Database already exists"
gcloud sql users create opero_user --instance=${APP_NAME}-db --password=your-secure-user-password || echo "User already exists"

# Create secrets
echo -e "${YELLOW}🔐 Creating secrets...${NC}"
echo -n "postgresql+asyncpg://opero_user:your-secure-user-password@//cloudsql/${PROJECT_ID}:${REGION}:${APP_NAME}-db/opero_db" | \
    gcloud secrets create database-url --data-file=-

echo -n "your-super-secure-secret-key-32-chars-minimum" | \
    gcloud secrets create secret-key --data-file=-

echo -n "your-jwt-secret-key-32-chars-minimum" | \
    gcloud secrets create jwt-secret-key --data-file=-

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production \
    --set-secrets DATABASE_URL=database-url:latest \
    --set-secrets SECRET_KEY=secret-key:latest \
    --set-secrets JWT_SECRET_KEY=jwt-secret-key:latest \
    --add-cloudsql-instances ${PROJECT_ID}:${REGION}:${APP_NAME}-db

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${YELLOW}📋 API Docs: ${SERVICE_URL}/docs${NC}"
echo -e "${YELLOW}🎮 Dashboard: ${SERVICE_URL}/dashboard${NC}"
