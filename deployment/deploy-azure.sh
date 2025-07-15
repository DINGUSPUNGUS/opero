#!/bin/bash
# Azure Deployment Script for Opero Platform

set -e

# Configuration
RESOURCE_GROUP="opero-rg"
APP_NAME="opero"
LOCATION="eastus"
ACR_NAME="${APP_NAME}acr"
APP_SERVICE_PLAN="${APP_NAME}-plan"
WEB_APP="${APP_NAME}-api"
SQL_SERVER="${APP_NAME}-sql"
SQL_DATABASE="opero_db"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Azure deployment for Opero Platform${NC}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not installed${NC}"
    exit 1
fi

# Login to Azure
echo -e "${YELLOW}🔐 Checking Azure login...${NC}"
az account show > /dev/null || az login

# Create resource group
echo -e "${YELLOW}📦 Creating resource group...${NC}"
az group create --name ${RESOURCE_GROUP} --location ${LOCATION}

# Create Azure Container Registry
echo -e "${YELLOW}🏗️ Creating Azure Container Registry...${NC}"
az acr create --resource-group ${RESOURCE_GROUP} \
    --name ${ACR_NAME} \
    --sku Basic \
    --admin-enabled true

# Build and push image
echo -e "${YELLOW}📤 Building and pushing image...${NC}"
az acr build --registry ${ACR_NAME} \
    --image ${APP_NAME}-api:latest \
    --file Dockerfile.production .

# Create SQL Server
echo -e "${YELLOW}🗄️ Creating SQL Database...${NC}"
az sql server create \
    --name ${SQL_SERVER} \
    --resource-group ${RESOURCE_GROUP} \
    --location ${LOCATION} \
    --admin-user opero_admin \
    --admin-password "SecureP@ssw0rd123!"

# Create SQL Database
az sql db create \
    --resource-group ${RESOURCE_GROUP} \
    --server ${SQL_SERVER} \
    --name ${SQL_DATABASE} \
    --service-objective Basic

# Configure firewall
az sql server firewall-rule create \
    --resource-group ${RESOURCE_GROUP} \
    --server ${SQL_SERVER} \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Create App Service Plan
echo -e "${YELLOW}☁️ Creating App Service Plan...${NC}"
az appservice plan create \
    --name ${APP_SERVICE_PLAN} \
    --resource-group ${RESOURCE_GROUP} \
    --location ${LOCATION} \
    --sku B1 \
    --is-linux

# Create Web App
echo -e "${YELLOW}🌐 Creating Web App...${NC}"
az webapp create \
    --resource-group ${RESOURCE_GROUP} \
    --plan ${APP_SERVICE_PLAN} \
    --name ${WEB_APP} \
    --deployment-container-image-name ${ACR_NAME}.azurecr.io/${APP_NAME}-api:latest

# Configure Web App
az webapp config appsettings set \
    --resource-group ${RESOURCE_GROUP} \
    --name ${WEB_APP} \
    --settings \
        ENVIRONMENT=production \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
        WEBSITES_PORT=8000 \
        DATABASE_URL="postgresql+asyncpg://opero_admin:SecureP@ssw0rd123!@${SQL_SERVER}.database.windows.net:1433/${SQL_DATABASE}"

# Configure container registry
ACR_PASSWORD=$(az acr credential show --name ${ACR_NAME} --query passwords[0].value --output tsv)
az webapp config container set \
    --resource-group ${RESOURCE_GROUP} \
    --name ${WEB_APP} \
    --docker-custom-image-name ${ACR_NAME}.azurecr.io/${APP_NAME}-api:latest \
    --docker-registry-server-url https://${ACR_NAME}.azurecr.io \
    --docker-registry-server-user ${ACR_NAME} \
    --docker-registry-server-password ${ACR_PASSWORD}

# Get Web App URL
WEB_APP_URL="https://${WEB_APP}.azurewebsites.net"

echo -e "${GREEN}✅ Azure deployment completed!${NC}"
echo -e "${YELLOW}🌐 Web App URL: ${WEB_APP_URL}${NC}"
echo -e "${YELLOW}📋 API Docs: ${WEB_APP_URL}/docs${NC}"
echo -e "${YELLOW}🎮 Dashboard: ${WEB_APP_URL}/dashboard${NC}"
