# 🚀 Opero Platform - Windows Deployment Script
# PowerShell version for Windows users

param(
    [string]$Action = "menu"
)

# Colors for PowerShell
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# ASCII Art Banner
Write-Host @"
   ____                       
  / __ \____  ___  __________ 
 / / / / __ \/ _ \/ ___/ __ \
/ /_/ / /_/ /  __/ /  / /_/ /
\____/ .___/\___/_/   \____/ 
    /_/                      

AI-Powered Business Automation Platform
"@ -ForegroundColor $Blue

Write-Host "🚀 Welcome to Opero Platform Deployment!" -ForegroundColor $Green
Write-Host "This script will help you deploy your platform step by step." -ForegroundColor $Yellow
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor $Blue

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor $Red
    exit 1
}
Write-Host "✅ Docker is installed" -ForegroundColor $Green

# Check Docker Compose
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor $Red
    exit 1
}
Write-Host "✅ Docker Compose is installed" -ForegroundColor $Green

function Show-Menu {
    Write-Host ""
    Write-Host "📋 What would you like to do?" -ForegroundColor $Yellow
    Write-Host "1. 🔧 Set up development environment"
    Write-Host "2. 🏗️ Build for production"
    Write-Host "3. 🚀 Deploy to production"
    Write-Host "4. 📊 Start monitoring stack"
    Write-Host "5. 🔐 Set up SSL certificates"
    Write-Host "6. 📖 View deployment guide"
    Write-Host "7. 🧹 Clean up containers"
    Write-Host "8. 🚪 Exit"
    Write-Host ""
}

function Setup-Development {
    Write-Host "🔧 Setting up development environment..." -ForegroundColor $Blue
    
    # Create development .env if it doesn't exist
    if (!(Test-Path .env)) {
        Write-Host "Creating development .env file..." -ForegroundColor $Yellow
        @"
DB_PASSWORD=devpassword
REDIS_PASSWORD=
GRAFANA_PASSWORD=admin
"@ | Out-File -FilePath .env -Encoding UTF8
    }
    
    # Start development stack
    docker-compose -f docker-compose.dev.yml up -d
    
    Write-Host "✅ Development environment started!" -ForegroundColor $Green
    Write-Host "🌐 Access your application at:" -ForegroundColor $Yellow
    Write-Host "   • API: http://localhost:8000"
    Write-Host "   • Docs: http://localhost:8000/docs"
    Write-Host "   • Dashboard: http://localhost:8000/dashboard"
    Write-Host "   • Database: localhost:5432"
    Write-Host "   • Redis: localhost:6379"
}

function Build-Production {
    Write-Host "🏗️ Building for production..." -ForegroundColor $Blue
    
    # Check if .env.production exists
    if (!(Test-Path .env.production)) {
        Write-Host "⚠️ .env.production not found. Creating from template..." -ForegroundColor $Yellow
        Copy-Item .env.production.example .env.production
        Write-Host "⚠️ Please edit .env.production with your actual values before deploying!" -ForegroundColor $Red
        Write-Host "Press any key to continue after editing..." -ForegroundColor $Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
    # Build production images
    docker-compose -f docker-compose.production.yml build
    
    Write-Host "✅ Production images built successfully!" -ForegroundColor $Green
}

function Deploy-Production {
    Write-Host "🚀 Deploying to production..." -ForegroundColor $Blue
    
    # Check if production env exists
    if (!(Test-Path .env.production)) {
        Write-Host "❌ .env.production not found. Please create it first (option 2)." -ForegroundColor $Red
        return
    }
    
    # Create production .env for docker-compose
    if (!(Test-Path .env)) {
        Write-Host "Creating production .env for Docker Compose..." -ForegroundColor $Yellow
        $dbPass = Read-Host "Enter database password" -AsSecureString
        $dbPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPass))
        
        $redisPass = Read-Host "Enter Redis password" -AsSecureString
        $redisPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($redisPass))
        
        $grafanaPass = Read-Host "Enter Grafana admin password" -AsSecureString
        $grafanaPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($grafanaPass))
        
        @"
DB_PASSWORD=$dbPassPlain
REDIS_PASSWORD=$redisPassPlain
GRAFANA_PASSWORD=$grafanaPassPlain
"@ | Out-File -FilePath .env -Encoding UTF8
    }
    
    # Start production stack
    docker-compose -f docker-compose.production.yml up -d
    
    Write-Host "✅ Production deployment started!" -ForegroundColor $Green
    Write-Host "🌐 Your application should be available at:" -ForegroundColor $Yellow
    Write-Host "   • API: http://your-domain:8000"
    Write-Host "   • Nginx: http://your-domain"
}

function Start-Monitoring {
    Write-Host "📊 Starting monitoring stack..." -ForegroundColor $Blue
    
    # Start monitoring profile
    docker-compose -f docker-compose.production.yml --profile monitoring up -d
    
    Write-Host "✅ Monitoring stack started!" -ForegroundColor $Green
    Write-Host "📊 Access monitoring at:" -ForegroundColor $Yellow
    Write-Host "   • Prometheus: http://your-domain:9090"
    Write-Host "   • Grafana: http://your-domain:3000"
}

function Setup-SSL {
    Write-Host "🔐 SSL Certificate Setup" -ForegroundColor $Blue
    Write-Host "Choose SSL setup method:" -ForegroundColor $Yellow
    Write-Host "1. Let's Encrypt (Linux/WSL required)"
    Write-Host "2. Custom certificates (manual)"
    $sslChoice = Read-Host "Enter choice (1-2)"
    
    switch ($sslChoice) {
        "1" {
            Write-Host "⚠️ Let's Encrypt requires Linux/WSL environment" -ForegroundColor $Yellow
            Write-Host "Please run the deployment/setup-ssl.sh script in WSL or Linux" -ForegroundColor $Yellow
        }
        "2" {
            Write-Host "📋 Manual SSL Certificate Setup:" -ForegroundColor $Yellow
            Write-Host "1. Copy your certificate files to nginx/ssl/"
            Write-Host "2. Ensure files are named: fullchain.pem and privkey.pem"
            Write-Host "3. Restart nginx: docker-compose restart nginx"
        }
    }
}

function Show-Guide {
    Write-Host "📖 Opening deployment guide..." -ForegroundColor $Blue
    if (Test-Path DEPLOYMENT_GUIDE.md) {
        Start-Process notepad DEPLOYMENT_GUIDE.md
    } else {
        Write-Host "❌ Deployment guide not found" -ForegroundColor $Red
    }
}

function Clean-Containers {
    Write-Host "🧹 Cleaning up containers..." -ForegroundColor $Blue
    Write-Host "This will stop and remove all Opero containers and volumes." -ForegroundColor $Yellow
    $confirm = Read-Host "Are you sure? (y/N)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        docker-compose -f docker-compose.dev.yml down -v
        docker-compose -f docker-compose.production.yml down -v
        docker system prune -f
        Write-Host "✅ Cleanup completed!" -ForegroundColor $Green
    }
}

# Main menu loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-8)"
    
    switch ($choice) {
        "1" { Setup-Development }
        "2" { Build-Production }
        "3" { Deploy-Production }
        "4" { Start-Monitoring }
        "5" { Setup-SSL }
        "6" { Show-Guide }
        "7" { Clean-Containers }
        "8" {
            Write-Host "👋 Thank you for using Opero Platform!" -ForegroundColor $Green
            Write-Host "🌟 Visit the dashboard to start automating your business!" -ForegroundColor $Yellow
            exit 0
        }
        default {
            Write-Host "❌ Invalid choice. Please enter 1-8." -ForegroundColor $Red
        }
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor $Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
} while ($true)
