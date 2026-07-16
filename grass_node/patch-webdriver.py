#!/usr/bin/env python3
"""
Patch grass-node_main.py so Selenium uses system chromedriver/chromium
instead of Selenium Manager auto-discovery (which fails in HA containers).
"""
import re, sys

TARGET = "/app/custom_entrypoints_scripts/grass-node_main.py"

with open(TARGET) as f:
    src = f.read()

# 1. Add ChromeService import alongside existing webdriver import
src = re.sub(
    r"(from selenium import webdriver)",
    r"\1\nfrom selenium.webdriver.chrome.service import Service as ChromeService",
    src, count=1
)

# 2. Point Chrome binary at our wrapper
src = re.sub(
    r"(chrome_options\s*=\s*Options\(\))",
    r"\1\n    chrome_options.binary_location = '/usr/local/bin/google-chrome'",
    src, count=1
)

# 3. Use explicit ChromeService so Selenium Manager is bypassed entirely
src = re.sub(
    r"driver\s*=\s*webdriver\.Chrome\(options=chrome_options\)",
    "driver = webdriver.Chrome(service=ChromeService('/usr/bin/chromedriver'), options=chrome_options)",
    src, count=1
)

with open(TARGET, "w") as f:
    f.write(src)

print("patch-webdriver: patched", TARGET)
