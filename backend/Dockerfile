FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fastapi_ai_email_assistant.py .
CMD ["uvicorn", "fastapi_ai_email_assistant:app", "--host", "0.0.0.0", "--port", "8000"]
