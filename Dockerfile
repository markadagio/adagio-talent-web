FROM python:3.13-slim

WORKDIR /app
COPY index.html serve.py ./

EXPOSE 8080

CMD ["python3", "serve.py"]
