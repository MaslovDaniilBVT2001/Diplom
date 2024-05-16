# main.py
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from slides.register_slide import router as register_router
from slides.login_slide import router as login_router
from database import connect_to_db, close_connection, create_user_table
import asyncio
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

app = FastAPI(debug=True)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры слайдов
app.include_router(register_router)
app.include_router(login_router)

# Устанавливаем соединение с базой данных при запуске приложения
@app.on_event("startup")
async def startup_event():
    try:
        app.state.db_connection = await connect_to_db()
    except Exception as e:
        logging.error("Failed to connect to the database: %s", e)
        raise

# Закрываем соединение с базой данных при остановке приложения
@app.on_event("shutdown")
async def shutdown_event():
    await close_connection(app.state.db_connection)

# Функция для получения соединения с базой данных в качестве зависимости
async def get_db():
    return app.state.db_connection

# Подключаем зависимость к роутерам, чтобы использовать соединение с базой данных
app.include_router(
    register_router,
    dependencies=[Depends(get_db)]
)
app.include_router(
    login_router,
    dependencies=[Depends(get_db)]
)






@app.post("/registration-success/")
async def registration_success():
    return {"message": "Registration successful!"}

@app.post("/login-success/")
async def login_success():
    return {"message": "Login successful!"}

# Обработчики ошибок

@app.exception_handler(Exception)
async def error_handler(request, exc):
    logging.error("Internal server error: %s", str(exc))
    return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})