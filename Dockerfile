FROM python:3.9-slim-buster

COPY . .

COPY requirements.txt .
COPY requirements_custom.txt .

RUN pip install -r requirements.txt
RUN pip install -r requirements_custom.txt

EXPOSE 9000

CMD ["python", "main.py"]




