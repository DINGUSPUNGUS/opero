@echo off
echo.
echo ============================================
echo    Opero API - Quick Vercel Deployment
echo ============================================
echo.
echo Checking Vercel CLI...
vercel --version
if %ERRORLEVEL% NEQ 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
)
echo.
echo Ready to deploy your FastAPI backend!
echo.
set /p deploy="Deploy to Vercel now? (y/N): "
if /I "%deploy%"=="y" (
    echo.
    echo Deploying to production...
    vercel --prod
) else (
    echo.
    echo Deployment cancelled. Run 'vercel --prod' when ready.
)
echo.
echo Files configured for deployment:
echo - vercel.json (Vercel configuration)
echo - api/index.py (FastAPI entry point) 
echo - requirements.txt (Python dependencies)
echo.
pause
