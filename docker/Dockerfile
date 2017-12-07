# Base image with os requirements
# ===============================
FROM alpine:3.7 as base

ENV LANG=C.UTF-8
RUN apk update \
 && apk add python3 libffi openssl ca-certificates pcre wget sqlite \
 && ln -sf /usr/bin/python3.6 /usr/bin/python


# Build tools, dependencies and python packages
# =============================================
FROM base as deps

RUN apk add python3-dev libffi-dev openssl-dev pcre-dev build-base linux-headers
COPY ./requirements.txt /
RUN pip3 install --prefix=/pypkg -r requirements.txt


# Final image
# ===========
FROM base

ENV PATH=/pypkg/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHONPATH=/pypkg/lib/python3.6/site-packages
COPY --from=deps /pypkg /pypkg
