FROM alpine:latest

RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3

# Install Python dependencies
COPY requirements.txt /tmp
RUN python3 -m pip install \
        --no-cache-dir \
        -r /tmp/requirements.txt

ADD src/ .

ENV PYTHONUNBUFFERED=0
ENTRYPOINT ["/usr/bin/python3", "-u", "app.py"]
