 # build stage
FROM python:3.8-buster as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt update && apt install -y vim ffmpeg sox

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

