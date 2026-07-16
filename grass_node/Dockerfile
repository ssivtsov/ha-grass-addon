ARG BUILD_FROM=mrcolorrain/grass-node:latest
FROM ${BUILD_FROM}

# jq reads /data/options.json in run.sh; chromium + chromium-driver may be
# missing in some arch variants of the base image and Selenium needs both.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# The stock script relies on Selenium Manager auto-discovery, which cannot
# find Debian's chromium/chromedriver; wire the paths in explicitly.
COPY patch-webdriver.py /tmp/patch-webdriver.py
RUN python3 /tmp/patch-webdriver.py && rm /tmp/patch-webdriver.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Keep the base image's tini as PID 1, but route startup through our
# options-reading script before handing off to the original entrypoint chain.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
