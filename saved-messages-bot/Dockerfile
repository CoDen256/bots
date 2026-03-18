FROM coden256/core-bots:latest

COPY requirements.txt /app
COPY main.py /app
COPY cfg.py /app
WORKDIR /app

RUN python3 -m pip install -r ./requirements.txt

ENTRYPOINT ["python3", "./main.py" ]