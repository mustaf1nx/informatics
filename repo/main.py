"""
EduCon Hub — раздача статических тестов, хаба и PDF-конспектов.
Тот же подход, что и в Zein Academy: FastAPI + Railway.

Запуск локально:
    uvicorn main:app --reload

На Railway задаётся автоматически через Procfile / railway.toml.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="EduCon Hub")


@app.get("/health")
def health():
    return {"status": "ok"}


# Отдаём index.html на корне, а все остальные файлы (тесты, progress.js,
# pdfs/...) - как обычную статику по их прямым путям.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
