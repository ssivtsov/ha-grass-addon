ARG BUILD_FROM=mrcolorrain/grass-node:latest
FROM ${BUILD_FROM}

# jq reads /data/options.json in run.sh.
# chromium + chromium-driver are matched Debian packages so chromedriver
# finds the right browser binary without needing binary_location.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Prepend a monkeypatch that:
#   1. Provides explicit ChromeService so Selenium Manager is bypassed
#   2. Adds --disable-gpu/--disable-software-rasterizer via ChromeOptions
#   No binary_location — chromedriver finds /usr/bin/chromium itself since
#   they are from the same Debian package.
RUN python3 - << 'PATCH'
patch = """\
from selenium.webdriver.chrome.service import Service as _ChromeService
import selenium.webdriver as _wd
_orig_chrome_init = _wd.Chrome.__init__
def _patched_chrome_init(self, options=None, service=None, keep_alive=True, **kwargs):
    if service is None:
        service = _ChromeService('/usr/bin/chromedriver')
    if options is not None:
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
