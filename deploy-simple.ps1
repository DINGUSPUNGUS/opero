# Simple Vercel Deployment Script
Write-Host "Opero API - Vercel Deployment" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check Vercel CLI
try {
    $vercelVersion = vercel --version
    Write-Host "Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

Write-Host ""
Write-Host "Deployment Options:" -ForegroundColor Yellow
Write-Host "1. Deploy to Vercel"
Write-Host "2. Deploy to Railway"  
Write-Host "3. Deploy to Render"
Write-Host "4. Exit"
Write-Host ""

$choice = Read-Host "Select option (1-4)"

switch ($choice) {
    1 {
        Write-Host "Deploying to Vercel..." -ForegroundColor Green
        Write-Host "This will deploy your FastAPI backend to Vercel" -ForegroundColor White
        $confirm = Read-Host "Continue? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            vercel --prod
        } else {
            Write-Host "Deployment cancelled." -ForegroundColor Yellow
        }
    }
    2 {
        Write-Host "Railway Instructions:" -ForegroundColor Green
        Write-Host "1. npm install -g @railway/cli" -ForegroundColor White
        Write-Host "2. railway login" -ForegroundColor White
        Write-Host "3. railway init" -ForegroundColor White
        Write-Host "4. railway up" -ForegroundColor White
    }
    3 {
        Write-Host "Render Instructions:" -ForegroundColor Green
        Write-Host "1. Go to https://render.com" -ForegroundColor White
        Write-Host "2. Connect your GitHub repo" -ForegroundColor White
        Write-Host "3. Build: pip install -r requirements.txt" -ForegroundColor White
        Write-Host "4. Start: uvicorn app.main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor White
    }
    4 {
        Write-Host "Goodbye!" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid option." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Files ready for deployment:" -ForegroundColor Cyan
Write-Host "- vercel.json (configuration)" -ForegroundColor White
Write-Host "- api/index.py (entry point)" -ForegroundColor White
Write-Host "- requirements.txt (dependencies)" -ForegroundColor White
Write-Host ""
Write-Host "Happy deploying!" -ForegroundColor Green
