ARG BUILD_FROM=mrcolorrain/grass-node:latest
FROM ${BUILD_FROM}

# jq reads /data/options.json in run.sh.
# chromium + chromium-driver provide the browser and chromedriver that
# Selenium needs; without them Selenium Manager fails to locate a driver.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Wrapper that forwards to system Chromium with required container flags.
COPY google-chrome.sh /usr/local/bin/google-chrome
RUN chmod +x /usr/local/bin/google-chrome

# Patch grass-node_main.py to use explicit ChromeService path instead of
# Selenium Manager auto-discovery, which cannot find Debian's chromedriver.
COPY patch-webdriver.py /patch-webdriver.py
RUN python3 /patch-webdriver.py && rm /patch-webdriver.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
