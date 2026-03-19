FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV APP_NAME="forwarder-bot"

WORKDIR /app
COPY pyproject.toml uv.lock /app/
COPY core-bots/ /app/core-bots/
COPY $APP_NAME/ /app/$APP_NAME/
RUN uv sync --package $APP_NAME --no-dev --frozen

CMD .venv/bin/python $APP_NAME/main.py