ARG BUILD_FROM=mrcolorrain/grass-desktop:latest
FROM ${BUILD_FROM}

# Debian base; jq reads /data/options.json in run.sh.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
