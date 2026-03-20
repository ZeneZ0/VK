from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="backend/app/templates")

# Лендинг (для неавторизованных)
@router.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# Дашборд (главная панель для авторизованных)
@router.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/screenshots")
async def screenshots_page(request: Request):
    return templates.TemplateResponse("screenshots.html", {"request": request})

@router.get("/tokens")
async def tokens_page(request: Request):
    return templates.TemplateResponse("tokens.html", {"request": request})

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/posts")
async def posts_page(request: Request):
    return templates.TemplateResponse("posts.html", {"request": request})

@router.get("/reposts_wall")
async def reposts_wall_page(request: Request):
    return templates.TemplateResponse("reposts_wall.html", {"request": request})

@router.get("/reposts_dm")
async def reposts_dm_page(request: Request):
    return templates.TemplateResponse("reposts_dm.html", {"request": request})

@router.get("/comments")
async def comments_page(request: Request):
    return templates.TemplateResponse("comments.html", {"request": request})

@router.get("/likes")
async def likes_page(request: Request):
    return templates.TemplateResponse("likes.html", {"request": request})

@router.get("/subscribe_group")
async def subscribe_group_page(request: Request):
    return templates.TemplateResponse("subscribe_group.html", {"request": request})

@router.get("/statistics")
async def statistics_page(request: Request):
    return templates.TemplateResponse("statistics.html", {"request": request})

@router.get("/subscribe")
async def subscribe_page(request: Request):
    return templates.TemplateResponse("subscribe.html", {"request": request})

# Заглушки для будущих страни