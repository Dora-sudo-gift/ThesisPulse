
FROM python:3.12


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/docker/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries=5 -r requirements.txt


COPY . .