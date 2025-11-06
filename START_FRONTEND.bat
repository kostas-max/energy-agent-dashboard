@echo off
echo ============================================================
echo Energy Agent Dashboard - Frontend Server
echo ============================================================
echo.
echo Starting HTTP server on http://localhost:8080
echo.
echo Press CTRL+C to stop
echo.

cd frontend
python -m http.server 8080
