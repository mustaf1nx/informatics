# backend_leaderboard_example.py
#
# Пример endpoint'ов для общего рейтинга (топа) по тестам EduCon.
# Рассчитан на твой стек: FastAPI + SQLAlchemy + PostgreSQL.
# Просто перенеси нужные куски в свой существующий backend (Zein Academy /
# любой другой FastAPI-проект) и подключи роутер.
#
# После того как поднимешь эндпоинт, впиши его базовый адрес в API_BASE
# внутри progress.js - и хаб-страница с рейтингом начнёт показывать
# результаты всех учеников, а не только локального устройства.

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from .database import Base, get_db  # замени на свои реальные импорты


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(30), nullable=False, index=True)
    test_id = Column(String(50), nullable=False, index=True)
    test_title = Column(String(200), nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeaderboardSubmit(BaseModel):
    nickname: str = Field(..., max_length=30)
    test_id: str = Field(..., max_length=50)
    test_title: str = Field(..., max_length=200)
    score: int
    total: int


router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.post("")
def submit_score(payload: LeaderboardSubmit, db: Session = Depends(get_db)):
    """
    Сохраняет результат. Если у ученика уже есть запись по этому тесту,
    обновляем только если новый результат лучше (чтобы не засорять топ
    старыми низкими попытками).
    """
    existing = (
        db.query(LeaderboardEntry)
        .filter(
            LeaderboardEntry.nickname == payload.nickname,
            LeaderboardEntry.test_id == payload.test_id,
        )
        .first()
    )

    if existing:
        if payload.score > existing.score:
            existing.score = payload.score
            existing.total = payload.total
            existing.created_at = datetime.utcnow()
            db.commit()
        return {"status": "updated" if payload.score > existing.score else "unchanged"}

    entry = LeaderboardEntry(
        nickname=payload.nickname,
        test_id=payload.test_id,
        test_title=payload.test_title,
        score=payload.score,
        total=payload.total,
    )
    db.add(entry)
    db.commit()
    return {"status": "created"}


@router.get("")
def get_leaderboard(test_id: str | None = None, db: Session = Depends(get_db)):
    """
    Возвращает топ. Если test_id не передан - агрегирует средний процент
    по всем тестам для каждого ученика (общий рейтинг для хаб-страницы).
    """
    query = db.query(LeaderboardEntry)
    if test_id:
        query = query.filter(LeaderboardEntry.test_id == test_id)

    rows = query.all()

    if test_id:
        result = [
            {
                "nickname": r.nickname,
                "test_id": r.test_id,
                "test_title": r.test_title,
                "score": r.score,
                "total": r.total,
                "pct": round(r.score / r.total * 100),
            }
            for r in rows
        ]
        result.sort(key=lambda x: x["pct"], reverse=True)
        return result[:50]

    # Общий рейтинг: средний процент по всем тестам, которые проходил ученик
    by_nick: dict[str, list[float]] = {}
    for r in rows:
        by_nick.setdefault(r.nickname, []).append(r.score / r.total * 100)

    overall = [
        {
            "nickname": nick,
            "tests_completed": len(pcts),
            "avg_pct": round(sum(pcts) / len(pcts)),
        }
        for nick, pcts in by_nick.items()
    ]
    overall.sort(key=lambda x: (x["avg_pct"], x["tests_completed"]), reverse=True)
    return overall[:50]


# В основном приложении:
# from .leaderboard import router as leaderboard_router
# app.include_router(leaderboard_router)
#
# Не забудь миграцию (alembic revision --autogenerate) для новой таблицы
# leaderboard_entries.
