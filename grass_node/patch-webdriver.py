"""Build-time patch for the upstream grass-node_main.py.

The stock script calls webdriver.Chrome() without explicit paths and relies
on Selenium Manager auto-discovery, which fails against Debian's chromium /
chromium-driver packages ("Unable to obtain driver for chrome"). Wire the
binary and driver paths explicitly instead.
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
        "    driver_options = Options()",
        "    driver_options = Options()\n"
        "    driver_options.binary_location = os.getenv('CHROME_BIN', '/usr/bin/chromium')",
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
