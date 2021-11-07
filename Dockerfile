FROM python:slim-bullseye AS compile-image

RUN apt-get update

RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN export CFLAGS=-fcommon && pip3 install fanshim psutil RPi.GPIO prometheus-client python-json-logger

FROM python:slim-bullseye AS build-image

WORKDIR /app

COPY --from=compile-image /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

ADD main.py .

CMD [ "main.py" ]

ENTRYPOINT [ "python3" ]
