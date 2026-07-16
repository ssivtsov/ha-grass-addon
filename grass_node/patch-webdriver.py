"""Build-time patch for the upstream grass-node_main.py.

Fixes two issues:
1. The stock script calls webdriver.Chrome() with no explicit paths and
   relies on Selenium Manager auto-discovery, which fails against Debian's
   chromium/chromium-driver packages. Wire the binary and driver paths.
2. Chromium crashes during page navigation in containerised environments
   (empty WebDriver error + raw stacktrace) because GPU hardware
   acceleration is unavailable. Add --disable-gpu and
   --disable-software-rasterizer to prevent the crash.
"""
import sys

PATH = '/app/custom_entrypoints_scripts/grass-node_main.py'

with open(PATH) as f:
    src = f.read()

if 'ChromeService' in src:
    print('grass-node_main.py already patched')
    sys.exit(0)

REPLACEMENTS = [
    (
        "from selenium.webdriver.chrome.options import Options",
        "from selenium.webdriver.chrome.options import Options\n"
        "from selenium.webdriver.chrome.service import Service as ChromeService",
    ),
    (
        "    driver_options = Options()\n"
        "    driver_options.add_argument('--no-sandbox')",
        "    driver_options = Options()\n"
        "    driver_options.binary_location = os.getenv('CHROME_BIN', '/usr/bin/chromium')\n"
        "    driver_options.add_argument('--disable-gpu')  # required in containers: no GPU available\n"
        "    driver_options.add_argument('--disable-software-rasterizer')  # avoids GPU-fallback crash\n"
        "    driver_options.add_argument('--no-sandbox')",
    ),
    (
        "        driver = webdriver.Chrome(options=driver_options)",
        "        driver = webdriver.Chrome(\n"
        "            service=ChromeService(os.getenv('CHROMEDRIVER_BIN', '/usr/bin/chromedriver')),\n"
        "            options=driver_options,\n"
        "        )",
    ),
]

for old, new in REPLACEMENTS:
    if old not in src:
        sys.exit(f'ERROR: pattern not found (upstream script changed?): {old!r}')
    src = src.replace(old, new, 1)

with open(PATH, 'w') as f:
    f.write(src)

print('grass-node_main.py patched: explicit chromium/chromedriver paths')
