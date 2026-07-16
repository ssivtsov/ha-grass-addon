ARG BUILD_FROM=mrcolorrain/grass-node:latest
FROM ${BUILD_FROM}

RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Keep the base image's tini as PID 1, but route startup through our
# options-reading script before handing off to the original entrypoint chain.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
