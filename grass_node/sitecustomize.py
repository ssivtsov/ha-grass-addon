"""
Patch selenium.webdriver.Chrome before any user script runs so that:
  - chromedriver is taken from /usr/bin/chromedriver (Debian package)
  - the Chrome binary is our wrapper at /usr/local/bin/google-chrome

This avoids Selenium Manager auto-discovery, which fails in HA containers
because Debian ships 'chromium'/'chromedriver', not 'google-chrome'.
"""
try:
    from selenium.webdriver.chrome.service import Service as _ChromeService
    import selenium.webdriver as _wd

    _orig_Chrome = _wd.Chrome

    class _PatchedChrome(_orig_Chrome):
        def __init__(self, *args, **kwargs):
            from selenium.webdriver.chrome.options import Options
            if "service" not in kwargs:
                kwargs["service"] = _ChromeService("/usr/bin/chromedriver")
            opts = kwargs.get("options") or (args[0] if args else None)
            if opts is None:
                opts = Options()
                kwargs["options"] = opts
            if not opts.binary_location:
                opts.binary_location = "/usr/local/bin/google-chrome"
            super().__init__(**{k: v for k, v in kwargs.items()})

    _wd.Chrome = _PatchedChrome
except Exception:
    pass
