FROM python:3.7-slim-stretch

RUN pip install pipenv

ENV WORKDIR = "/sfwbot"

COPY Pipfile Pipfile.lock ${WORKDIR}/

WORKDIR ${WORKDIR}
RUN pipenv install --system --deploy

COPY quarantine.py ${WORKDIR}/

ENTRYPOINT [ "python", "quarantine.py" ]
