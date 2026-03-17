from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["pages"])
templates = Jinja2Templates(directory="backend/app/templates")

@router.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse(
        "profile_container.html",
        {"request": request}
    )
@router.get("/screenshots")
async def screenshots_page(request: Request):
    return templates.TemplateResponse(
        "screenshots.html",
        {"request": request}
    )