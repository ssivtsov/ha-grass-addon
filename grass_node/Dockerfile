ARG BUILD_FROM=mrcolorrain/grass-node:latest
FROM ${BUILD_FROM}

# jq reads /data/options.json in run.sh.
# google-chrome.sh provides a "google-chrome" binary on PATH; it wraps the
# system Chromium with the flags required to run stably in a container.
# patch-webdriver.py wires that wrapper + the system chromedriver into the
# upstream script via ChromeService (Selenium cannot locate them automatically).
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY google-chrome.sh /usr/local/bin/google-chrome
RUN chmod +x /usr/local/bin/google-chrome

COPY patch-webdriver.py /tmp/patch-webdriver.py
RUN python3 /tmp/patch-webdriver.py && rm /tmp/patch-webdriver.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
