Run backend:
cd backend
.venv/Scripts/Activate
uvicorn app.main:app --reload

alembic revision --autogenerate -m "create ----- table"
alembic upgrade head