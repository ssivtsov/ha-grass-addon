"""Minimal build-time patch for the upstream grass-node_main.py.

Selenium Manager cannot locate chromedriver automatically in this
container environment. Three targeted changes are made:
  1. Import ChromeService.
  2. Point binary_location at the google-chrome wrapper (which adds the
     container stability flags via google-chrome.sh).
  3. Pass an explicit ChromeService so Selenium uses the system
     chromedriver directly instead of trying to download one.

Everything else in the upstream script is left untouched.
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
        "    driver_options.binary_location = '/usr/local/bin/google-chrome'",
    ),
    (
        "        driver = webdriver.Chrome(options=driver_options)",
        "        driver = webdriver.Chrome(\n"
        "            service=ChromeService('/usr/bin/chromedriver'),\n"
        "            options=driver_options,\n"
        "        )",
    ),
]

for old, new in REPLACEMENTS:
    if old not in src:
        sys.exit(f'ERROR: upstream script changed, pattern not found: {old!r}')
    src = src.replace(old, new, 1)

with open(PATH, 'w') as f:
    f.write(src)

print('grass-node_main.py patched: ChromeService + google-chrome wrapper path')
