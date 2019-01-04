FROM python:3.7-alpine3.8 as base

FROM base as builder

RUN mkdir /build
WORKDIR /build
RUN apk update && apk upgrade && \
    apk add bash git openssh
RUN apk add --virtual .pynacl_deps build-base python3-dev libffi-dev

COPY requirements.txt /

RUN pip install --prefix=/build -r /requirements.txt

FROM base

COPY --from=builder /build /usr/local
COPY --from=builder /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY . /app
WORKDIR /app

# ENTRYPOINT [ "tail", "-f", "/dev/null" ]
ENTRYPOINT [ "python", "run.py" ]