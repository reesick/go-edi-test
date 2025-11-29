@echo off
echo ========================================
echo  Algorithm Visualizer - Quick Start
echo ========================================
echo.

echo [1/3] Starting Python Backend (Port 8000)...
start cmd /k "cd backend-python && uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak > nul

echo [2/3] Starting Go Backend (Port 8080)...
start cmd /k "cd backend-go && go run ."
timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend (Port 5173)...
start cmd /k "cd frontend && npm run dev"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo  All services starting!
echo ========================================
echo.
echo Python Backend: http://localhost:8000
echo Go Backend:     http://localhost:8080
echo Frontend:       http://localhost:5173
echo.
echo Press any key to open browser...
pause > nul

start http://localhost:5173

echo.
echo ========================================
echo  To stop all servers, close the terminal windows
echo ========================================
