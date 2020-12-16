FROM python:3.7-alpine3.8 as base

FROM base as builder

# Builder Image setup
RUN mkdir /build
WORKDIR /build
RUN apk update && apk upgrade && \
    apk add bash git openssh
RUN apk add --virtual .pynacl_deps build-base python3-dev libffi-dev

# Install all requirements
COPY requirements.txt /
RUN pip install --prefix=/build -r /requirements.txt

# Production image
FROM base

# This is actually just for the version + commit hash
# Honestly worth the extra 30mb until I figure out a better solution
RUN apk add git

# Copy necessary files from builder image
COPY --from=builder /build /usr/local
COPY --from=builder /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY . /app
WORKDIR /app

ENTRYPOINT [ "python", "run.py" ]