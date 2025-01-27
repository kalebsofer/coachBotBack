FROM python:3.12-slim

WORKDIR /app

COPY src/frontend/ /app/frontend/

RUN pip install -r /app/frontend/requirements.txt

WORKDIR /app/frontend

CMD ["streamlit", "run", "app.py"] 