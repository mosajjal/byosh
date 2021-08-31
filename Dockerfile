FROM alpine:edge
LABEL maintainer="Ali Mosajjal <hi@n0p.me>"

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
    py3-pip \
    nginx \
    nginx-mod-stream \
    && sh -c 'mkdir -p /run/openrc/ && mkdir -p /run/nginx' \
    && pip3 install --no-cache-dir dnslib

COPY nginx.conf /etc/nginx/nginx.conf
COPY src/ /opt/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
