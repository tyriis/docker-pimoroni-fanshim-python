FROM balenalib/raspberrypi4-64-debian-python

RUN apt-get update && apt-get -y install build-essential

WORKDIR /app

RUN export CFLAGS=-fcommon && pip3 install fanshim psutil RPi.GPIO prometheus-client python-json-logger

RUN apt purge git build-essential && apt clean && apt autoremove --yes

ADD main.py .

CMD [ "main.py" ]

ENTRYPOINT [ "python3" ]
