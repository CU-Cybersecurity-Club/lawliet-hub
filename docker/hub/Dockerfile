FROM alpine:latest

RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3

RUN python3 -m pip install \
        --no-cache-dir \
        flask \
        kubernetes \
        requests

COPY src/pod-api-server.py .

ENV PYTHONUNBUFFERED=0
ENTRYPOINT ["/usr/bin/python3", "-u", "pod-api-server.py"]
