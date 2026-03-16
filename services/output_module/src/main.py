import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from src.presentation.api.v1.routes.post.api import router as post_router

# Импортируй свой провайдер (где ты прописала репозиторий и сервис)
from src.infrastructure.di import MyProvider 

def create_app() -> FastAPI:
    app = FastAPI(
        title="PulseSight Output Module",
        description="API для вывода новостей и анализа рисков",
        version="1.0.0",
        docs_url="/docs"
    )

    # 1. Настройка CORS (чтобы фронтенд мог достучаться)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # В продакшене замени на конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Подключение роутеров
    app.include_router(post_router, prefix="/api/v1")

    # 3. Инициализация Dishka (Dependency Injection)
    container = make_async_container(MyProvider())
    setup_dishka(container, app)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)