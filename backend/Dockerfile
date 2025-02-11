FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y libpq-dev gcc gettext make && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

ENV WORKDIR=/app
ENV PYTHONPATH=$WORKDIR/src
# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файлы для зависимостей перед их установкой (ускоряет билд)
COPY pyproject.toml poetry.lock $WORKDIR/

# Install dependencies
COPY Makefile $WORKDIR/
RUN poetry update
COPY src $WORKDIR/src

#RUN make setup
ENTRYPOINT ["make", "start-prod"]