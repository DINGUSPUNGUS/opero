#!/bin/bash
# 🚀 Opero Platform - Quick Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
   ____                       
  / __ \____  ___  __________ 
 / / / / __ \/ _ \/ ___/ __ \
/ /_/ / /_/ /  __/ /  / /_/ /
\____/ .___/\___/_/   \____/ 
    /_/                      

AI-Powered Business Automation Platform
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Welcome to Opero Platform Deployment!${NC}"
echo -e "${YELLOW}This script will help you deploy your platform step by step.${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Main menu
while true; do
    echo ""
    echo -e "${YELLOW}📋 What would you like to do?${NC}"
    echo "1. 🔧 Set up development environment"
    echo "2. 🏗️ Build for production"
    echo "3. 🚀 Deploy to production"
    echo "4. 📊 Start monitoring stack"
    echo "5. 🔐 Set up SSL certificates"
    echo "6. 📖 View deployment guide"
    echo "7. 🚪 Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice

    case $choice in
        1)
            echo -e "${BLUE}🔧 Setting up development environment...${NC}"
            
            # Create development .env if it doesn't exist
            if [ ! -f .env ]; then
                echo -e "${YELLOW}Creating development .env file...${NC}"
                cat > .env << EOL
DB_PASSWORD=devpassword
REDIS_PASSWORD=
GRAFANA_PASSWORD=admin
EOL
            fi
            
            # Start development stack
            docker-compose -f docker-compose.dev.yml up -d
            
            echo -e "${GREEN}✅ Development environment started!${NC}"
            echo -e "${YELLOW}🌐 Access your application at:${NC}"
            echo "   • API: http://localhost:8000"
            echo "   • Docs: http://localhost:8000/docs"
            echo "   • Dashboard: http://localhost:8000/dashboard"
            echo "   • Database: localhost:5432"
            echo "   • Redis: localhost:6379"
            ;;
            
        2)
            echo -e "${BLUE}🏗️ Building for production...${NC}"
            
            # Check if .env.production exists
            if [ ! -f .env.production ]; then
                echo -e "${YELLOW}⚠️ .env.production not found. Creating from template...${NC}"
                cp .env.production.example .env.production
                echo -e "${RED}⚠️ Please edit .env.production with your actual values before deploying!${NC}"
                echo -e "${YELLOW}Press any key to continue after editing...${NC}"
                read -n 1
            fi
            
            # Build production images
            docker-compose -f docker-compose.production.yml build
            
            echo -e "${GREEN}✅ Production images built successfully!${NC}"
            ;;
            
        3)
            echo -e "${BLUE}🚀 Deploying to production...${NC}"
            
            # Check if production env exists
            if [ ! -f .env.production ]; then
                echo -e "${RED}❌ .env.production not found. Please create it first (option 2).${NC}"
                continue
            fi
            
            # Create production .env for docker-compose
            if [ ! -f .env ]; then
                echo -e "${YELLOW}Creating production .env for Docker Compose...${NC}"
                read -s -p "Enter database password: " db_pass
                echo ""
                read -s -p "Enter Redis password: " redis_pass
                echo ""
                read -s -p "Enter Grafana admin password: " grafana_pass
                echo ""
                
                cat > .env << EOL
DB_PASSWORD=${db_pass}
REDIS_PASSWORD=${redis_pass}
GRAFANA_PASSWORD=${grafana_pass}
EOL
            fi
            
            # Start production stack
            docker-compose -f docker-compose.production.yml up -d
            
            echo -e "${GREEN}✅ Production deployment started!${NC}"
            echo -e "${YELLOW}🌐 Your application should be available at:${NC}"
            echo "   • API: http://your-domain:8000"
            echo "   • Nginx: http://your-domain"
            ;;
            
        4)
            echo -e "${BLUE}📊 Starting monitoring stack...${NC}"
            
            # Start monitoring profile
            docker-compose -f docker-compose.production.yml --profile monitoring up -d
            
            echo -e "${GREEN}✅ Monitoring stack started!${NC}"
            echo -e "${YELLOW}📊 Access monitoring at:${NC}"
            echo "   • Prometheus: http://your-domain:9090"
            echo "   • Grafana: http://your-domain:3000"
            ;;
            
        5)
            echo -e "${BLUE}🔐 SSL Certificate Setup${NC}"
            echo -e "${YELLOW}Choose SSL setup method:${NC}"
            echo "1. Let's Encrypt (automatic)"
            echo "2. Custom certificates (manual)"
            read -p "Enter choice (1-2): " ssl_choice
            
            case $ssl_choice in
                1)
                    if [ -f deployment/setup-ssl.sh ]; then
                        echo -e "${YELLOW}⚠️ Please edit deployment/setup-ssl.sh with your domain and email first${NC}"
                        echo -e "${YELLOW}Press any key to continue...${NC}"
                        read -n 1
                        chmod +x deployment/setup-ssl.sh
                        sudo deployment/setup-ssl.sh
                    else
                        echo -e "${RED}❌ SSL setup script not found${NC}"
                    fi
                    ;;
                2)
                    echo -e "${YELLOW}📋 Manual SSL Certificate Setup:${NC}"
                    echo "1. Copy your certificate files to nginx/ssl/"
                    echo "2. Ensure files are named: fullchain.pem and privkey.pem"
                    echo "3. Restart nginx: docker-compose restart nginx"
                    ;;
            esac
            ;;
            
        6)
            echo -e "${BLUE}📖 Opening deployment guide...${NC}"
            if [ -f DEPLOYMENT_GUIDE.md ]; then
                if command -v less &> /dev/null; then
                    less DEPLOYMENT_GUIDE.md
                else
                    cat DEPLOYMENT_GUIDE.md
                fi
            else
                echo -e "${RED}❌ Deployment guide not found${NC}"
            fi
            ;;
            
        7)
            echo -e "${GREEN}👋 Thank you for using Opero Platform!${NC}"
            echo -e "${YELLOW}🌟 Visit the dashboard to start automating your business!${NC}"
            exit 0
            ;;
            
        *)
            echo -e "${RED}❌ Invalid choice. Please enter 1-7.${NC}"
            ;;
    esac
done
