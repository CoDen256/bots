FROM coden256/bot-parent:1.0

COPY requirements.txt /app
RUN python3 -m pip install -r ./requirements.txt

COPY main.py /app/main.py

ENTRYPOINT ["python3", "./main.py"]