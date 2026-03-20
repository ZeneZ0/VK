from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.app.api import auth, pages, bots, publish, subscriptions
from backend.app.middleware.subscription_middleware import SubscriptionMiddleware
from backend.app.api import auth, pages, bots, publish, subscriptions, statistics

app = FastAPI(title="VK Manager")

# Подключаем middleware
app.add_middleware(SubscriptionMiddleware)

# Подключаем статику
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="backend/app/templates")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(bots.router)
app.include_router(publish.router)
app.include_router(subscriptions.router)
app.include_router(statistics.router)

@app.get("/")
def root():
    return templates.TemplateResponse("landing.html", {"request": {}})