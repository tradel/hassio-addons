FROM alexxit/go2rtc:master-hardware

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r --break-system-packages requirements.txt
# RUN pip3 install jsonpath

COPY abode2rtc/*.py abode2rtc/*.j2 ./
RUN chmod a+x ./spawn.py ./stream.py

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD [ "/app/spawn.py" ]

EXPOSE 1984/tcp
EXPOSE 8554/tcp
EXPOSE 8555/tcp
EXPOSE 8555/udp
