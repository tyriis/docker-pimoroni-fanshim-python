FROM python:alpine3.14 AS build

# thanks to https://github.com/woahbase/alpine-rpigpio for the list of dependencies
RUN apk add --no-cache -Uu --virtual .build-dependencies python3-dev libffi-dev openssl-dev build-base musl-dev

# set CFLAGS for RPi.GPIO compilation
ENV CFLAGS="-fcommon"

# enable virtualenv
RUN python -m venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install RPi.GPIO psutil prometheus-client python-json-logger fanshim

FROM python:alpine3.14

# for space and security reasons delete apk we dont need it
# RUN apk --purge del apk-tools

COPY --from=build /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

ADD main.py .

CMD [ "main.py" ]

ENTRYPOINT [ "python3" ]
