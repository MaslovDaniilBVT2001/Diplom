from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import register_user, check_existing_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Модель для ошибки регистрации
class RegistrationError(BaseModel):
    message: str

@router.post("/register/")
async def register(request: Request, 
                   first_name: str = Form(...), 
                   last_name: str = Form(...), 
                   username: str = Form(...), 
                   password: str = Form(...), 
                   email: str = Form(...), 
                   role: str = Form(...)):
    errors = []

    

    # Проверяем существующего пользователя с таким же логином или email
    if await check_existing_user(request.app.state.db_connection, username, email):
        errors.append("Пользователь с таким логином или email уже существует.")

    # Если есть ошибки, возвращаем JSON с сообщением об ошибке
    if errors:
        return JSONResponse(content={"message": "Произошла ошибка при регистрации", "errors": errors}, status_code=400)

    # Регистрируем нового пользователя
    await register_user(request.app.state.db_connection, first_name, last_name, username, password, email, role)

    # Выводим сообщение об успешной регистрации и перенаправляем на страницу входа
    return templates.TemplateResponse("registration_success.html", {"request": request})

@router.get("/register-form/", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register_slide.html", {"request": request})
