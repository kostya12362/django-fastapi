FROM python:3.12-slim

# Installing system dependencies
RUN apt-get update && apt-get install -y libpq-dev make && rm -rf /var/lib/apt/lists/*

# Installing Poetry
RUN pip install poetry

ENV WORKDIR=/app
ENV PYTHONPATH=$WORKDIR/src
# Set the working directory
WORKDIR /app

# Copy only files for dependencies before installing them (speeds up the build)
COPY pyproject.toml poetry.lock $WORKDIR/

# Install dependencies
COPY Makefile $WORKDIR/
RUN poetry update
COPY src $WORKDIR/src

#RUN make setup
ENTRYPOINT ["make", "start"]