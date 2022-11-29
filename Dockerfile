FROM python:3.9-slim-buster

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt \
    && rm -rf /root/.cache

COPY . .

EXPOSE 9000

CMD ["python", "main.py"]
