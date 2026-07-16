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

# Prepend a monkeypatch to grass-node_main.py that:
#   1. Bypasses Selenium Manager by using explicit ChromeService path
#   2. Sets binary_location to our wrapper
#   3. Adds only the two GPU flags needed to prevent Chromium crashes in
#      containers — --no-zygote was causing renderer crashes, so it is
#      intentionally omitted here
RUN python3 - << 'PATCH'
patch = """\
from selenium.webdriver.chrome.service import Service as _ChromeService
import selenium.webdriver as _wd
_orig_chrome_init = _wd.Chrome.__init__
def _patched_chrome_init(self, options=None, service=None, keep_alive=True, **kwargs):
    if service is None:
        service = _ChromeService('/usr/bin/chromedriver')
    if options is not None:
        if not getattr(options, 'binary_location', ''):
            options.binary_location = '/usr/local/bin/google-chrome'
        for _flag in ['--disable-gpu', '--disable-software-rasterizer']:
            options.add_argument(_flag)
    _orig_chrome_init(self, options=options, service=service, keep_alive=keep_alive, **kwargs)
_wd.Chrome.__init__ = _patched_chrome_init
"""
target = '/app/custom_entrypoints_scripts/grass-node_main.py'
with open(target) as f:
    original = f.read()
with open(target, 'w') as f:
    f.write(patch + original)
print('patch prepended to', target)
PATCH

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
