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

# sitecustomize.py is imported by Python before any user script. It patches
# selenium.webdriver.Chrome to use explicit chromedriver/binary paths,
# bypassing Selenium Manager without needing to touch the upstream script.
COPY sitecustomize.py /usr/lib/python3/dist-packages/sitecustomize.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
