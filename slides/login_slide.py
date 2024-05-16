from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from database import authenticate_user, connect_to_db, close_connection
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def get_db(request: Request):
    # Получаем соединение с базой данных
    if not hasattr(request.app.state, "db_connection") or request.app.state.db_connection is None:
        # Если соединение не установлено или закрыто, подключаемся к базе данных
        request.app.state.db_connection = await connect_to_db()
        # Запускаем отслеживание активности соединения
        asyncio.create_task(track_connection_activity(request.app.state.db_connection))
    # Возвращаем соединение
    return request.app.state.db_connection

async def track_connection_activity(conn):
    try:
        await asyncio.sleep(20)  # Ожидаем 20 секунд
        await close_connection(conn)
    except asyncio.CancelledError:
        pass  # Игнорируем отмену задачи отслеживания

@router.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        # Получаем соединение с базой данных
        conn = await get_db(request)
        
        # Проверка аутентификации пользователя
        if not await authenticate_user(conn, username, password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        return RedirectResponse(url="/login-success/")
    except Exception as e:
        # Если возникла ошибка, восстанавливаем соединение и повторно выполняем запрос
        request.app.state.db_connection = await connect_to_db()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/login-form/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_slide.html", {"request": request})

@router.get("/login-success/", response_class=HTMLResponse)
async def login_success(request: Request):
    return templates.TemplateResponse("login_success.html", {"request": request})
