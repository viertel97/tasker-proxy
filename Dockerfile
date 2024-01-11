# Stage 1: Build dependencies
FROM python:3.9-slim AS builder
ARG PAT

COPY . .

COPY requirements.txt .

RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg flac && rm -rf /var/lib/apt/lists/*

RUN pip install --extra-index-url https://Quarter-Lib-Old:${PAT}@pkgs.dev.azure.com/viertel/Quarter-Lib-Old/_packaging/Quarter-Lib-Old/pypi/simple/ -r requirements.txt

# Stage 2: Create the final lightweight image
FROM python:3.9-slim-buster

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg flac && rm -rf /var/lib/apt/lists/*

ENV IS_CONTAINER=True

EXPOSE 9000

CMD ["python", "main.py"]
