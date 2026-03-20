from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.api import auth, pages  # добавили pages
from backend.app.api import auth, pages, bots
from backend.app.api import auth, pages, bots, publish

app = FastAPI(title="VK Manager")

# Подключаем статику
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(pages.router)  
app.include_router(bots.router)
app.include_router(publish.router)

@app.get("/")
def root():
    return {"message": "VK Manager запущен!"}