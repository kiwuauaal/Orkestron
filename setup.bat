@echo off
echo =====================================
echo Orkestron - Setup Script
echo =====================================
echo.

echo [1/6] Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [2/6] Installing Next.js dashboard dependencies...
cd frontend\dashboard
call npm install
cd ..\..

echo.
echo [3/6] Installing Vue monitor dependencies...
cd frontend\vue-monitor
call npm install
cd ..\..

echo.
echo [4/6] Creating logs directory...
if not exist logs mkdir logs

echo.
echo [5/6] Setting up environment file...
if not exist .env copy .env.example .env
echo Please edit .env and add your OPENAI_API_KEY

echo.
echo [6/6] Starting infrastructure with Docker...
docker-compose up -d redis rabbitmq

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Next steps:
echo 1. Edit .env and add your OPENAI_API_KEY
echo 2. Run: python main.py
echo 3. Access dashboard at: http://localhost:3000
echo 4. Access monitor at: http://localhost:3001
echo.
echo Welcome to Orkestron!
echo.
pause
