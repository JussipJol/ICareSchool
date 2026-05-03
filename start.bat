@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  ==========================================
echo   ICareSchool — Система обращений
echo  ==========================================
echo.

:: Создаём виртуальное окружение при первом запуске
if not exist "venv\Scripts\activate.bat" (
    echo  [1/2] Первый запуск — создаём окружение и ставим пакеты...
    python -m venv venv
    if errorlevel 1 (
        echo  ОШИБКА: Python не найден. Установите Python 3.10+ с python.org
        pause
        exit /b 1
    )
    venv\Scripts\pip install -r backend\requirements.txt --quiet
    echo  [1/2] Готово!
) else (
    echo  [OK] Окружение уже готово.
)

:: Открываем браузер через 3 секунды (фоновый процесс)
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8000/app/index.html"

echo.
echo  Сервер: http://localhost:8000/app/index.html
echo  Админка: http://localhost:8000/app/admin.html
echo  Остановить: Ctrl+C
echo.

:: Запуск сервера
cd backend
..\venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
