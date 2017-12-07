# Base image with os requirements
FROM ubuntu:17.04 as base

ENV LANG=C.UTF-8

RUN apt-get update -y \
 && apt-get -y install --no-install-recommends \
        python3.6 libpython3.6 libffi6 openssl \
        ca-certificates libpcre3 wget tzdata \
 && ln -sf /usr/bin/python3.6 /usr/bin/python


# Build tools, dependencies and python packages
FROM base as deps

RUN apt-get -y install --no-install-recommends \
        python3.6-dev libffi-dev libssl-dev libpcre3-dev build-essential \
 && wget -q https://raw.githubusercontent.com/pypa/get-pip/430ba37776ae2ad89f794c7a43b90dc23bac334c/get-pip.py -O /get-pip.py \
 && echo '3b74f5cd0740a05802a23b019ce579a3  /get-pip.py' | md5sum -c

COPY ./requirements.txt /

RUN python /get-pip.py \
 && pip install -r requirements.txt


# Final image
FROM base
COPY --from=deps /usr/local /usr/local
