FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV POSTGRES_USER=si5_sacc \
    POSTGRES_DB=td_1 \
    POSTGRES_HOST=my-postgresql \
    POSTGRES_PORT=5432 \
    REDIS_HOST=${REDIS_HOST} \
    REDIS_PORT=${REDIS_PORT}

COPY main.py app.py

EXPOSE 8080

CMD ["python", "app.py"]
