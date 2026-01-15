# NARRA_FORGE - Dockerfile
# Autonomiczny Wieloświatowy System Generowania Narracji

FROM python:3.11-slim

# Metadata
LABEL maintainer="NARRA_FORGE Team"
LABEL description="Autonomiczny system generowania narracji klasy absolutnej"
LABEL version="1.0.0"

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Katalog roboczy
WORKDIR /app

# Zainstaluj zależności systemowe (jeśli potrzebne)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements
COPY requirements.txt .

# Zainstaluj zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Stwórz katalogi dla danych
RUN mkdir -p /app/data /app/output /app/logs

# Ustaw uprawnienia
RUN chmod +x przyklad_uzycia_pl.py || true

# Domyślna komenda: uruchom test
CMD ["python", "-u", "test_docker.py"]
