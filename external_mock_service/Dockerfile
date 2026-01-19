FROM python:3.11-slim

WORKDIR /app

RUN pip install Flask==3.0.0

COPY app.py .

EXPOSE 5001

CMD ["python", "app.py"]
