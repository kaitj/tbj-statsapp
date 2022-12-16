# Stage: dev deploy
# TODO: Turn into a multistage build for prod deploy
# g++, libdatrie1 required for poetry
FROM python:3.10-slim-bullseye AS build
COPY ./poetry.lock ./pyproject.toml /
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
        g++=4:10.2.1-1 \
        libdatrie1=0.2.13-1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pip install --prefer-binary --no-cache-dir \
        poetry==1.2.2 \
    && poetry config virtualenvs.create false \
    && apt-get purge -y -q g++ \
    && apt-get --purge -y -qq autoremove
WORKDIR /apps/tbj-statsapp
COPY . .
RUN poetry install --without=dev
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
