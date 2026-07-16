ARG BUILD_FROM=autonomylabxyz/grass:latest
FROM ${BUILD_FROM}

# Alpine base; jq reads /data/options.json in run.sh.
RUN apk add --no-cache jq

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
