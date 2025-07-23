FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app


RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
EXPOSE 8501

CMD streamlit run ui/streamlit_app.py --server.port 8501 & uvicorn main:app --host 0.0.0.0 --port 8000