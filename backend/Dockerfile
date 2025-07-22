# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# --- system deps (ffmpeg only) -------------------------
RUN apt-get update                                   \
 && apt-get install -y --no-install-recommends       \
      -o Acquire::Retries=3 --fix-missing            \
      ffmpeg                                         \
 && apt-get clean                                    \
 && rm -rf /var/lib/apt/lists/*

# --- project code -------------------------------------
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

