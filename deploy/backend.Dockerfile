# Backend: FastAPI + librería LR(1) instalada en editable
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema mínimas (ajusta si tu backend necesita compilar algo)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# 1) Instala requirements del backend
COPY lr1_app/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 2) Instala la librería LR(1) desde el código del repo
#    (editable no aplica en Docker; se instala como paquete normal)
COPY lr1_project/ /tmp/lr1_project/
RUN pip install --no-cache-dir /tmp/lr1_project

# 3) Copia el backend
COPY lr1_app/backend/ /app/

EXPOSE 8000

# Producción: varios workers
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips="*"
