from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="backend/app/templates")

@router.get("/")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/screenshots")
async def screenshots_page(request: Request):
    return templates.TemplateResponse("screenshots.html", {"request": request})

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Заглушки для будущих страниц (чтобы не было 404)
@router.get("/tokens")
async def tokens_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Управление VK токенами"})

@router.get("/posts")
async def posts_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Создание постов"})

@router.get("/reposts_wall")
async def reposts_wall_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Создание репостов (на стену)"})

@router.get("/reposts_dm")
async def reposts_dm_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Создание репостов (в лс)"})

@router.get("/comments")
async def comments_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Создание комментариев"})

@router.get("/likes")
async def likes_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Поставить лайки"})

@router.get("/subscribe_group")
async def subscribe_group_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Подписаться на группу"})

@router.get("/statistics")
async def statistics_page(request: Request):
    return templates.TemplateResponse("coming_soon.html", {"request": request, "page_name": "Статистика"})