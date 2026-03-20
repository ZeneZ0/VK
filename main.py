from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.api import auth, pages  # добавили pages
from backend.app.api import auth, pages, bots

app = FastAPI(title="VK Manager")

# Подключаем статику
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(pages.router)  # добавили роутер страниц
app.include_router(bots.router)

@app.get("/")
def root():
    return {"message": "VK Manager запущен!"}