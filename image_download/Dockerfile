FROM python:3.7-slim-stretch

RUN pip install pipenv

ENV SRC_DIR "/image_download"
ENV WORK_DIR "/sfwbot"

COPY Pipfile Pipfile.lock ${SRC_DIR}/

WORKDIR ${SRC_DIR}
RUN pipenv install --system --deploy

COPY image_download.py ${SRC_DIR}/

WORKDIR ${WORK_DIR}

ENTRYPOINT [ "python", "/image_download/image_download.py" ]
