FROM alpine:latest

RUN apk update && \
		apk add python3 py3-pip

RUN pip3 install flask kubernetes requests

COPY ./pod-api-server.py .

ENV PYTHONUNBUFFERED=0
ENTRYPOINT ["/usr/bin/python3", "-u", "pod-api-server.py"]
