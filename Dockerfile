FROM python:3.10-slim-buster
ARG PAT
RUN apt-get update &&  apt-get install -y git

COPY . .

COPY requirements.txt .

RUN pip install  --extra-index-url https://Quarter-Lib-Old:${PAT}@pkgs.dev.azure.com/viertel/Quarter-Lib-Old/_packaging/Quarter-Lib-Old/pypi/simple/ -r requirements.txt

ENV IS_CONTAINER=True

EXPOSE 9000

CMD ["python", "main.py"]




