#!/usr/bin/env python3
"""
Corrected Grass Desktop autologin entrypoint (ha-grass-addon).

Based on MRColorR/get-grass grass-desktop_main.py, with two fixes:

1. Credentials are now always typed with `xdotool type` (never `xdotool key`).
   The upstream heuristic used `xdotool key` for any string that was not
   purely alphanumeric, so an email like "user@gmail.com" was fed to
   `xdotool key` and rejected with "Invalid key sequence".

2. The login choreography follows Grass's current email-first flow:
   type email -> Continue (Return) -> "Use Password Instead" -> password
   -> Sign In, instead of the old single-screen email+Tab+password flow.

The number of Tab presses needed to reach the "Use Password Instead" link on
the code screen can vary; it is configurable via PASSWORD_LINK_TABS (default 7)
so it can be tuned without editing this file.
"""
import os
import sys
import time
import random
import logging
import subprocess
from typing import List, Optional, Tuple, Any

# --- Constants ---
GRASS_EXECUTABLE_PATH = "/usr/bin/grass"
GRASS_WINDOW_NAME = "Grass"
CONFIGURED_FLAG_FILE = "~/.grass-configured"

DEFAULT_MAX_RETRY_MULTIPLIER = 3
DEFAULT_TRY_AUTOLOGIN = "true"

INITIAL_X_SERVER_WAIT_FACTOR = 5
GRASS_LAUNCH_WAIT_FACTOR = 1
WINDOW_SEARCH_INITIAL_WAIT_FACTOR = 1
WINDOW_SEARCH_BACKOFF_MIN_FACTOR = 11
WINDOW_SEARCH_BACKOFF_MAX_FACTOR = 31
GRASS_INTERFACE_LOAD_WAIT_FACTOR = 5
POST_FOCUS_WAIT_FACTOR = 2
POST_LOGIN_STEP_WAIT_FACTOR = 2
POST_CREDENTIAL_ENTRY_WAIT_FACTOR = 1
POST_LOGIN_ATTEMPT_WAIT_FACTOR = 3
PROCESS_TERMINATE_TIMEOUT = 5

XDOTOOL_CMD = ["xdotool"]
XDOTOOL_TYPE_DELAY_MS = "125"

# Tab navigation counts (all tunable via env / add-on options).
DEFAULT_CONTINUE_TABS = 1       # email field -> CONTINUE button
DEFAULT_PASSWORD_LINK_TABS = 7  # code screen -> "Use Password Instead"
DEFAULT_SIGNIN_TABS = 1         # password field -> SIGN IN button


def _screenshots_enabled() -> bool:
    return os.getenv("DEBUG_SCREENSHOTS", "false").lower() == "true"


def _screenshot_dir() -> str:
    """
    Prefer /share/grass-debug (browsable via the File editor / Samba add-ons);
    fall back to /data if /share is not mapped.
    """
    base = "/share/grass-debug" if os.path.isdir("/share") else "/data"
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        base = "/data"
    return base


def capture(step: str) -> None:
    """Save a screenshot of the whole screen for debugging (if enabled)."""
    if not _screenshots_enabled():
        return
    path = os.path.join(_screenshot_dir(), f"grass-{step}.png")
    try:
        subprocess.run(["scrot", "-o", path], check=False)
        logging.info(f"Saved screenshot: {path}")
    except FileNotFoundError:
        logging.warning("scrot not installed; cannot save screenshot.")
    except Exception as e:  # noqa: BLE001
        logging.warning(f"Screenshot failed: {e}")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def _run_subprocess(cmd: List[str], check: bool = False, **kwargs: Any) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=check, universal_newlines=True, **kwargs)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{' '.join(cmd)}' failed with error: {e}")
        raise
    except FileNotFoundError:
        logging.error(f"Command '{cmd[0]}' not found. Ensure it is installed and in PATH.")
        raise


def press_key(key_sequence: str, retry_multiplier: int) -> bool:
    """Press a single key or key combo (e.g. 'Tab', 'Return', 'Escape')."""
    cmd = XDOTOOL_CMD + ["key", key_sequence]
    logging.info(f"Pressing key: '{key_sequence}'")
    try:
        result = _run_subprocess(cmd)
        time.sleep(retry_multiplier * 0.1)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def type_text(text: str, retry_multiplier: int, delay_ms: str = XDOTOOL_TYPE_DELAY_MS) -> bool:
    """
    Type an arbitrary string with xdotool. Uses '--' so leading dashes and
    special characters (@, ., -, etc.) are typed literally, not parsed as
    options or interpreted as key names.
    """
    cmd = XDOTOOL_CMD + ["type", "--delay", delay_ms, "--", text]
    logging.info(f"Typing string of length {len(text)}")
    try:
        result = _run_subprocess(cmd)
        time.sleep(retry_multiplier * 0.1)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def search_windows_by_name(window_name: str, max_attempts: int, retry_multiplier: int) -> Optional[List[str]]:
    time.sleep(retry_multiplier * WINDOW_SEARCH_INITIAL_WAIT_FACTOR)
    for attempt in range(max_attempts):
        try:
            cmd = XDOTOOL_CMD + [
                "search", "--sync", "--all", "--onlyvisible",
                "--classname", "--name", window_name,
            ]
            output = subprocess.check_output(cmd, universal_newlines=True).strip()
            windows = output.splitlines()
            if windows:
                logging.info(f"'{window_name}' window detected with IDs: {windows}")
                return windows
        except subprocess.CalledProcessError:
            pass
        except FileNotFoundError:
            logging.error("xdotool command not found.")
            return None

        if attempt < max_attempts - 1:
            logging.warning(
                f"'{window_name}' window not found (attempt {attempt + 1}/{max_attempts}). Retrying..."
            )
            backoff_time = (
                random.randint(WINDOW_SEARCH_BACKOFF_MIN_FACTOR, WINDOW_SEARCH_BACKOFF_MAX_FACTOR)
                * (attempt + 1) * retry_multiplier
            )
            logging.info(f"Backing off for {backoff_time:.2f} seconds before next attempt...")
            time.sleep(backoff_time)

    logging.error(f"Failed to find the '{window_name}' window after {max_attempts} attempts.")
    return None


def launch_grass_with_retries(max_attempts: int, retry_multiplier: int) -> Optional[subprocess.Popen]:
    wait_time_after_launch = retry_multiplier * GRASS_LAUNCH_WAIT_FACTOR
    for attempt in range(max_attempts):
        logging.info(f"Launching Grass desktop application... (Attempt {attempt + 1}/{max_attempts})")
        try:
            proc = subprocess.Popen([GRASS_EXECUTABLE_PATH])
        except FileNotFoundError:
            logging.error(f"Grass executable not found at '{GRASS_EXECUTABLE_PATH}'.")
            return None

        time.sleep(wait_time_after_launch)
        if proc.poll() is not None:
            logging.warning(
                f"Grass process ended prematurely on attempt {attempt + 1} with code {proc.returncode}."
            )
            if attempt < max_attempts - 1:
                logging.info("Retrying Grass launch...")
            else:
                logging.error(f"Failed to start Grass after {max_attempts} attempts.")
                return None
        else:
            logging.info("Grass application launched successfully.")
            return proc
    return None


def kill_process(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        logging.info(f"Terminating process {proc.pid}...")
        proc.terminate()
        try:
            proc.wait(timeout=PROCESS_TERMINATE_TIMEOUT)
            logging.info(f"Process {proc.pid} terminated gracefully.")
        except subprocess.TimeoutExpired:
            logging.warning(f"Process {proc.pid} did not terminate gracefully. Killing.")
            proc.kill()
            proc.wait()


def _get_credentials() -> Tuple[Optional[str], Optional[str]]:
    email_username = (
        os.getenv("USER_EMAIL")
        or os.getenv("GRASS_EMAIL")
        or os.getenv("GRASS_USER")
        or os.getenv("GRASS_USERNAME")
    )
    password = (
        os.getenv("USER_PASSWORD")
        or os.getenv("GRASS_PASSWORD")
        or os.getenv("GRASS_PASS")
    )
    return email_username, password


def _clear_field(retry_multiplier: int) -> None:
    """Select-all and delete, so a focused input starts empty before typing."""
    press_key("ctrl+a", retry_multiplier)
    press_key("Delete", retry_multiplier)


def _tab_to_and_activate(tabs: int, retry_multiplier: int) -> bool:
    """Press Tab `tabs` times to move focus onto a button/link, then activate it."""
    for _ in range(tabs):
        if not press_key("Tab", retry_multiplier):
            return False
    return press_key("Return", retry_multiplier)


def _perform_login_steps(email_username: str, password: str, retry_multiplier: int) -> bool:
    """
    Drive Grass's current email-first login flow with keyboard automation.

    IMPORTANT: this form does NOT submit on Enter — the CONTINUE / SIGN IN
    buttons must be focused (via Tab) and activated. Pressing Return while the
    email field is focused does nothing, which previously left the flow stuck
    on the email screen.

      email field (autofocused) -> type email -> Tab to CONTINUE -> Return
      -> Tab N times to "Use Password Instead" -> Return
      -> type password -> Tab to SIGN IN -> Return
    """
    continue_tabs = int(os.getenv("CONTINUE_TABS", str(DEFAULT_CONTINUE_TABS)))
    password_link_tabs = int(os.getenv("PASSWORD_LINK_TABS", str(DEFAULT_PASSWORD_LINK_TABS)))
    signin_tabs = int(os.getenv("SIGNIN_TABS", str(DEFAULT_SIGNIN_TABS)))

    logging.info("Login step 1/4: clearing and typing email into the email field...")
    _clear_field(retry_multiplier)
    if not type_text(email_username, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_CREDENTIAL_ENTRY_WAIT_FACTOR)
    capture("step1-email-typed")

    logging.info(f"Login step 2/4: Tab x{continue_tabs} to CONTINUE, then Return...")
    if not _tab_to_and_activate(continue_tabs, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_LOGIN_STEP_WAIT_FACTOR)
    capture("step2-after-continue")

    logging.info(
        f"Login step 3/4: Tab x{password_link_tabs} to 'Use Password Instead', then Return..."
    )
    if not _tab_to_and_activate(password_link_tabs, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_LOGIN_STEP_WAIT_FACTOR)
    capture("step3-after-use-password")

    logging.info(f"Login step 4/4: typing password, Tab x{signin_tabs} to SIGN IN, then Return...")
    _clear_field(retry_multiplier)
    if not type_text(password, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_CREDENTIAL_ENTRY_WAIT_FACTOR)
    capture("step4-password-typed")
    if not _tab_to_and_activate(signin_tabs, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_LOGIN_ATTEMPT_WAIT_FACTOR)
    capture("step5-after-signin")
    return True


def configure_grass(
    grass_proc_ref: subprocess.Popen,
    email_username: Optional[str],
    password: Optional[str],
    max_attempts: int,
    retry_multiplier: int,
) -> bool:
    configured_flag_path = os.path.expanduser(CONFIGURED_FLAG_FILE)
    if os.path.exists(configured_flag_path):
        logging.info(f"Grass already configured (flag found: {configured_flag_path}).")
        return True

    if not email_username or not password:
        logging.error("Credentials not provided to configure_grass. Cannot autologin.")
        return False

    current_grass_proc = grass_proc_ref

    for attempt in range(max_attempts):
        logging.info(f"Attempting Grass configuration (Attempt {attempt + 1}/{max_attempts})...")

        windows = search_windows_by_name(GRASS_WINDOW_NAME, max_attempts, retry_multiplier)
        if windows is None:
            if current_grass_proc.poll() is not None:
                logging.info("Grass process died. Attempting relaunch for configuration...")
                new_proc = launch_grass_with_retries(max_attempts, retry_multiplier)
                if new_proc:
                    current_grass_proc = new_proc
                else:
                    logging.error("Failed to relaunch Grass. Configuration aborted.")
                    return False
            continue

        time.sleep(retry_multiplier * GRASS_INTERFACE_LOAD_WAIT_FACTOR)

        windows = search_windows_by_name(GRASS_WINDOW_NAME, 1, 1)
        if not windows:
            logging.warning("Grass window disappeared before focusing. Retrying.")
            if current_grass_proc.poll() is not None:
                new_proc = launch_grass_with_retries(max_attempts, retry_multiplier)
                if new_proc:
                    current_grass_proc = new_proc
                else:
                    return False
            continue

        last_window_id = windows[-1]
        logging.info(f"Focusing the Grass main window (ID: {last_window_id})...")
        if _run_subprocess(XDOTOOL_CMD + ["windowfocus", "--sync", last_window_id]).returncode != 0:
            logging.warning("Failed to focus Grass window. Retrying.")
            if current_grass_proc.poll() is not None:
                new_proc = launch_grass_with_retries(max_attempts, retry_multiplier)
                if new_proc:
                    current_grass_proc = new_proc
                else:
                    return False
            continue

        time.sleep(retry_multiplier * POST_FOCUS_WAIT_FACTOR)

        logging.info("Performing login steps (email-first flow)...")
        if not _perform_login_steps(email_username, password, retry_multiplier):
            logging.warning("A login step failed. Retrying configuration attempt.")
            continue

        logging.info("Grass configuration steps completed.")
        try:
            with open(configured_flag_path, "w") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
            logging.info(f"Created configuration flag: {configured_flag_path}")
            return True
        except IOError as e:
            logging.error(f"Failed to write configuration flag file: {e}")
            return False

    logging.error(f"Failed to configure Grass after {max_attempts} attempts.")
    return False


def main() -> None:
    setup_logging()

    max_retry_multiplier_str = os.getenv("MAX_RETRY_MULTIPLIER", str(DEFAULT_MAX_RETRY_MULTIPLIER))
    try:
        max_retry_multiplier = int(max_retry_multiplier_str)
    except ValueError:
        logging.warning(f"Invalid MAX_RETRY_MULTIPLIER: '{max_retry_multiplier_str}'. Using default.")
        max_retry_multiplier = DEFAULT_MAX_RETRY_MULTIPLIER

    initial_wait = max_retry_multiplier * INITIAL_X_SERVER_WAIT_FACTOR
    logging.info(f"Initial wait of {initial_wait}s to allow X server to stabilize.")
    time.sleep(initial_wait)

    logging.info("Starting Grass Desktop script...")

    email_username, password = _get_credentials()
    try_autologin_env_str = os.getenv("TRY_AUTOLOGIN", DEFAULT_TRY_AUTOLOGIN)
    should_try_autologin = try_autologin_env_str.lower() == "true"

    if should_try_autologin and (not email_username or not password):
        logging.warning("Autologin enabled but credentials missing. Switching to manual mode.")
        should_try_autologin = False

    launch_configure_max_attempts = max_retry_multiplier
    grass_proc = launch_grass_with_retries(launch_configure_max_attempts, max_retry_multiplier)
    if grass_proc is None:
        logging.error("Grass application failed to launch. Exiting script.")
        sys.exit(1)

    if should_try_autologin:
        logging.info("Proceeding with automated Grass configuration (autologin)...")
        if configure_grass(grass_proc, email_username, password,
                           launch_configure_max_attempts, max_retry_multiplier):
            logging.info("Grass configuration (autologin) reported success.")
        else:
            logging.error(
                "Automated autologin failed. Switching to manual login mode. "
                "Grass will remain running; log in via the noVNC window."
            )
    else:
        logging.info("Autologin disabled or credentials missing. Waiting for manual interaction.")

    logging.info(f"Grass Desktop is now running (pid {grass_proc.pid}).")
    logging.info("Interact with the noVNC window for manual login if needed.")

    try:
        grass_proc.wait()
        logging.info(f"Grass process {grass_proc.pid} exited with code {grass_proc.returncode}.")
    except KeyboardInterrupt:
        logging.info("Script interrupted. Terminating Grass...")
        kill_process(grass_proc)
    sys.exit(grass_proc.returncode if grass_proc.returncode is not None else 0)


if __name__ == "__main__":
    main()
