FROM python:3.7-slim-stretch

RUN pip install pipenv

WORKDIR /image_download

COPY image_download.py Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

WORKDIR /nsfwdetectbot

ENTRYPOINT [ "python", "/image_download/image_download.py" ]
