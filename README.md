# ICare4School — Система обращений о коррупционных рисках

## Запуск проекта

### 1. Установить зависимости (один раз)

```
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart "python-jose[cryptography]" bcrypt "qrcode[pil]" Pillow
```

### 2. Запустить сервер

```
cd backend
uvicorn main:app --reload --port 8000
```

Дождаться строки `Application startup complete`.

### 3. Открыть в браузере

| Страница | Адрес |
|---|---|
| Форма подачи обращения | http://localhost:8000/app/index.html |
| Проверка статуса / Мои обращения | http://localhost:8000/app/status.html |
| Панель администратора | http://localhost:8000/app/admin.html |

Логин в админку: `admin` / `admin123`

---

## Доступ с телефона (через ngrok)

Если нужно открыть приложение на телефоне или с другого устройства:

### 1. Установить ngrok (один раз)

```
winget install ngrok.ngrok --accept-source-agreements
ngrok update
```

Зарегистрироваться на [ngrok.com](https://ngrok.com) и добавить токен:

```
ngrok config add-authtoken ВАШ_ТОКЕН
```

### 2. Запустить туннель (пока работает сервер)

```
ngrok http 8000
```

Ngrok выдаст адрес вида `https://xxxx.ngrok-free.app`.

### 3. Открыть на телефоне

```
https://xxxx.ngrok-free.app/app/index.html
```

### 4. QR-код для формы

Зайти в админку через ngrok-адрес → нажать **QR-код** в боковом меню → отсканировать телефоном.

---

## Структура проекта

```
ICare4School/
├── backend/
│   ├── main.py          # FastAPI — все эндпоинты
│   ├── models.py        # Модели базы данных
│   ├── schemas.py       # Pydantic-схемы
│   ├── auth.py          # JWT-аутентификация
│   └── requirements.txt
├── index.html           # Форма подачи обращения
├── status.html          # Мои обращения / статус
└── admin.html           # Панель администратора
```
