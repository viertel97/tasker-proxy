FROM python:3.9-slim-buster
ARG PAT

COPY . .
COPY requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg flac && rm -rf /var/lib/apt/lists/*

RUN pip install --extra-index-url https://Quarter-Lib-Old:${PAT}@pkgs.dev.azure.com/viertel/Quarter-Lib-Old/_packaging/Quarter-Lib-Old/pypi/simple/ -r requirements.txt

ENV IS_CONTAINER=True

EXPOSE 9000

CMD ["python", "main.py"]
