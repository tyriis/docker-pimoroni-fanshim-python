FROM python:slim-bullseye AS build
RUN apt-get update

RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

ENV CFLAGS="-fcommon"

RUN pip3 install RPi.GPIO psutil prometheus-client python-json-logger fanshim

FROM python:slim-bullseye

COPY --from=build /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

ADD main.py .

CMD [ "main.py" ]

ENTRYPOINT [ "python3" ]
