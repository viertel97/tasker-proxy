FROM python:3.10-slim-bookworm
ARG PAT
RUN apt-get update &&  apt-get install -y git

COPY . .

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV IS_CONTAINER=True

EXPOSE 9000

CMD ["python", "main.py"]




