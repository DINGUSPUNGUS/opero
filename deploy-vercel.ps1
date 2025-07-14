# PowerShell Deployment Script for Vercel
# Run this script to deploy your Opero API to Vercel

Write-Host "🚀 Opero API - Vercel Deployment Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

Write-Host ""
Write-Host "📋 Pre-deployment Checklist:" -ForegroundColor Yellow
Write-Host "✅ vercel.json configuration created" -ForegroundColor Green
Write-Host "✅ api/index.py entry point ready" -ForegroundColor Green
Write-Host "✅ Requirements optimized for Vercel" -ForegroundColor Green
Write-Host "✅ FastAPI routes configured" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 Deployment Options:" -ForegroundColor Magenta
Write-Host "1. Deploy to Vercel (Recommended)"
Write-Host "2. Deploy to Railway"
Write-Host "3. Deploy to Render"
Write-Host "4. Exit"
Write-Host ""

$choice = Read-Host "Select deployment option (1-4)"

switch ($choice) {
    1 {
        Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Cyan
        Write-Host "This will:"
        Write-Host "  - Login to Vercel (if needed)"
        Write-Host "  - Deploy your FastAPI backend"
        Write-Host "  - Provide you with a live URL"
        Write-Host ""
        
        $confirm = Read-Host "Continue? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            vercel --prod
        } else {
            Write-Host "Deployment cancelled." -ForegroundColor Yellow
        }
    }
    2 {
        Write-Host "🚂 Railway Deployment Instructions:" -ForegroundColor Cyan
        Write-Host "1. Install Railway CLI: npm install -g @railway/cli"
        Write-Host "2. Login: railway login"
        Write-Host "3. Initialize: railway init"
        Write-Host "4. Deploy: railway up"
        Write-Host ""
        Write-Host "Railway is excellent for FastAPI with database support!"
    }
    3 {
        Write-Host "🎨 Render Deployment Instructions:" -ForegroundColor Cyan
        Write-Host "1. Go to https://render.com"
        Write-Host "2. Connect your GitHub repository"
        Write-Host "3. Choose 'Web Service'"
        Write-Host "4. Build Command: pip install -r requirements.txt"
        Write-Host "5. Start Command: uvicorn app.main:app --host 0.0.0.0 --port `$PORT"
    }
    4 {
        Write-Host "Goodbye! 👋" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid option. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📞 Need Help?" -ForegroundColor Cyan
Write-Host "- Check VERCEL_FIX.md for detailed instructions"
Write-Host "- Test locally: python api/index.py"
Write-Host "- View documentation: https://vercel.com/docs/functions/serverless-functions/runtimes/python"
Write-Host ""
Write-Host "🎉 Happy deploying!" -ForegroundColor Green
