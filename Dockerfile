FROM tiangolo/uvicorn-gunicorn:python3.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PORT=8083
EXPOSE 8083
RUN mkdir app

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.0.* && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

