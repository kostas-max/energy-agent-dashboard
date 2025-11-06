@echo off
echo ====================================
echo Energy Agent Dashboard (GR) v1_GR_Stable
echo ====================================
echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

pause
