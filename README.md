# EduCon Hub

Тесты и конспекты по информатике 11 класс (подготовка к ЕНТ). 10 тем + итоговый
тест + шпаргалка. Статика раздаётся через FastAPI, деплой на Railway.

## Структура

```
main.py                          # FastAPI-сервер, раздаёт static/ как статику
requirements.txt
Procfile                         # команда запуска для Railway
railway.json                     # доп. конфиг Railway (на всякий случай)
backend_leaderboard_example.py   # референс: как поднять общий топ (см. ниже)
static/
  index.html                     # хаб: список тем, прогресс, топ, ссылки на PDF
  final_test.html                # итоговый тест, 40 вопросов по всем темам
  progress.js                    # сохранение прогресса + логика топа
  test_temaN_*.html               # 10 тестов по темам
  pdfs/
    tema1-ustroystva-kompyutera.pdf
    ...
    shpargalka-vse-temy.pdf
```

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Открыть http://127.0.0.1:8000

## Деплой на Railway

1. Запушить этот репозиторий в GitHub.
2. В Railway: New Project -> Deploy from GitHub repo -> выбрать репозиторий.
3. Railway сам подхватит `Procfile` / `railway.json` и `requirements.txt`
   (Nixpacks + Python), задавать ничего вручную не нужно.
4. После деплоя Railway выдаст публичный URL - это и есть адрес хаба.

## Прогресс и топ учеников

Прогресс каждого ученика (`progress.js`) по умолчанию хранится только в
localStorage его браузера - работает сразу после деплоя, без настройки.

Чтобы топ на хаб-странице был общим для всех учеников (а не только для
одного устройства), нужен backend-эндпоинт:

1. Перенести код из `backend_leaderboard_example.py` в реальный backend
   (например, в существующий Zein Academy backend на FastAPI + PostgreSQL,
   или прямо в этот репозиторий, добавив подключение к БД).
2. Подключить роутер в `main.py`:
   ```python
   from leaderboard import router as leaderboard_router
   app.include_router(leaderboard_router)
   ```
3. В `static/progress.js` найти строку:
   ```js
   const API_BASE = '';
   ```
   и вписать туда адрес своего backend (например, `https://zeinacademy.up.railway.app`).

После этого хаб-страница начнёт показывать реальный общий рейтинг
(GET `/api/leaderboard`), а результаты тестов будут отправляться на сервер
(POST `/api/leaderboard`) при каждой попытке.

## Важно

Все материалы написаны заново (не скопированы из книги EduCon дословно) -
конспекты и тестовые вопросы авторские, на основе программы ЕНТ по
информатике.
