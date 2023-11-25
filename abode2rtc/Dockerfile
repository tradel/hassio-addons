FROM alexxit/go2rtc

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY abode2rtc/*.py abode2rtc/*.j2 ./
RUN chmod a+x ./spawn.py ./stream.py

ENTRYPOINT ["/sbin/tini", "--"]
CMD [ "/app/spawn.py" ]

EXPOSE 1984/tcp
EXPOSE 8554/tcp
EXPOSE 8555/tcp
EXPOSE 8555/udp
