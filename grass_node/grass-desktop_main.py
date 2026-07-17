#!/usr/bin/env python3
"""
Corrected Grass Desktop autologin entrypoint (ha-grass-addon).

Fixes over the upstream MRColorR/get-grass entrypoint:

1. Credentials are typed with `xdotool type` (never `xdotool key`), so an
   email like "user@gmail.com" is entered correctly instead of being rejected
   with "Invalid key sequence".

2. The login choreography follows Grass's current email-first flow:
   type email -> CONTINUE -> "Use Password Instead" -> password -> SIGN IN.

3. Buttons and input fields are clicked at known window-relative coordinates
   (tunable via env vars / add-on options without a rebuild).
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

# Click targets — window-relative "x,y" offsets for the default 1280x720 layout.
# All tunable via env vars / add-on options so they can be corrected from debug
# screenshots without a rebuild.
DEFAULT_EMAIL_XY = "175,225"     # email input on the Sign In screen
DEFAULT_CONTINUE_XY = "175,296"  # CONTINUE button
DEFAULT_USEPASS_XY = "175,475"   # "Use Password Instead" link on the code screen
DEFAULT_PASSWORD_XY = "175,225"  # password input on the password screen
DEFAULT_SIGNIN_XY = "175,340"    # SIGN IN button on the password screen


def _parse_xy(env_name: str, default: str) -> Tuple[int, int]:
    raw = os.getenv(env_name, default) or default
    try:
        x_str, y_str = raw.split(",")
        return int(x_str.strip()), int(y_str.strip())
    except (ValueError, AttributeError):
        x_str, y_str = default.split(",")
        return int(x_str), int(y_str)


def _window_origin(window_id: str) -> Tuple[int, int]:
    """Return the (X, Y) screen coordinates of a window's top-left corner."""
    try:
        out = subprocess.check_output(
            XDOTOOL_CMD + ["getwindowgeometry", "--shell", window_id],
            universal_newlines=True,
        )
        geo = {}
        for line in out.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                geo[key.strip()] = val.strip()
        return int(geo.get("X", "0")), int(geo.get("Y", "0"))
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return 0, 0


def click_window_rel(window_id: str, rel_x: int, rel_y: int, retry_multiplier: int) -> bool:
    """Move the mouse to a window-relative offset and left-click there."""
    origin_x, origin_y = _window_origin(window_id)
    x, y = origin_x + rel_x, origin_y + rel_y
    logging.info("Clicking window-relative (%d,%d) -> screen (%d,%d)", rel_x, rel_y, x, y)
    try:
        result = _run_subprocess(
            XDOTOOL_CMD + ["mousemove", "--sync", str(x), str(y), "click", "1"]
        )
        time.sleep(retry_multiplier * 0.2)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _screenshots_enabled() -> bool:
    return os.getenv("DEBUG_SCREENSHOTS", "false").lower() == "true"


def _screenshot_dir() -> str:
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
        logging.info("Saved screenshot: %s", path)
    except FileNotFoundError:
        logging.warning("scrot not installed; cannot save screenshot.")
    except Exception as e:
        logging.warning("Screenshot failed: %s", e)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def _run_subprocess(cmd: List[str], check: bool = False, **kwargs: Any) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=check, universal_newlines=True, **kwargs)
    except subprocess.CalledProcessError as e:
        logging.error("Command '%s' failed: %s", " ".join(cmd), e)
        raise
    except FileNotFoundError:
        logging.error("Command '%s' not found.", cmd[0])
        raise


def press_key(key_sequence: str, retry_multiplier: int) -> bool:
    cmd = XDOTOOL_CMD + ["key", key_sequence]
    logging.info("Pressing key: '%s'", key_sequence)
    try:
        result = _run_subprocess(cmd)
        time.sleep(retry_multiplier * 0.1)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def type_text(text: str, retry_multiplier: int, delay_ms: str = XDOTOOL_TYPE_DELAY_MS) -> bool:
    """
    Type an arbitrary string with xdotool.  Uses '--' so leading dashes and
    special characters (@, ., -, etc.) are typed literally.
    """
    cmd = XDOTOOL_CMD + ["type", "--delay", delay_ms, "--", text]
    logging.info("Typing string of length %d", len(text))
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
                logging.info("'%s' window detected with IDs: %s", window_name, windows)
                return windows
        except subprocess.CalledProcessError:
            pass
        except FileNotFoundError:
            logging.error("xdotool not found.")
            return None

        if attempt < max_attempts - 1:
            logging.warning(
                "'%s' window not found (attempt %d/%d). Retrying...",
                window_name, attempt + 1, max_attempts,
            )
            backoff = (
                random.randint(WINDOW_SEARCH_BACKOFF_MIN_FACTOR, WINDOW_SEARCH_BACKOFF_MAX_FACTOR)
                * (attempt + 1) * retry_multiplier
            )
            logging.info("Backing off for %.0fs...", backoff)
            time.sleep(backoff)

    logging.error("Failed to find '%s' window after %d attempts.", window_name, max_attempts)
    return None


def launch_grass_with_retries(max_attempts: int, retry_multiplier: int) -> Optional[subprocess.Popen]:
    wait_time_after_launch = retry_multiplier * GRASS_LAUNCH_WAIT_FACTOR
    for attempt in range(max_attempts):
        logging.info("Launching Grass desktop application... (attempt %d/%d)", attempt + 1, max_attempts)
        try:
            proc = subprocess.Popen([GRASS_EXECUTABLE_PATH])
        except FileNotFoundError:
            logging.error("Grass executable not found at '%s'.", GRASS_EXECUTABLE_PATH)
            return None

        time.sleep(wait_time_after_launch)
        if proc.poll() is not None:
            logging.warning(
                "Grass process ended prematurely on attempt %d (code %s).",
                attempt + 1, proc.returncode,
            )
            if attempt < max_attempts - 1:
                logging.info("Retrying Grass launch...")
            else:
                logging.error("Failed to start Grass after %d attempts.", max_attempts)
                return None
        else:
            logging.info("Grass application launched successfully.")
            return proc
    return None


def kill_process(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        logging.info("Terminating process %d...", proc.pid)
        proc.terminate()
        try:
            proc.wait(timeout=PROCESS_TERMINATE_TIMEOUT)
            logging.info("Process %d terminated.", proc.pid)
        except subprocess.TimeoutExpired:
            logging.warning("Process %d did not terminate; killing.", proc.pid)
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
    """Select-all and delete the currently focused input."""
    press_key("ctrl+a", retry_multiplier)
    press_key("Delete", retry_multiplier)


def _perform_login_steps(window_id: str, email_username: str, password: str, retry_multiplier: int) -> bool:
    """
    Drive Grass's email-first login flow by clicking fields and buttons at
    known window-relative coordinates.

      click email field -> clear -> type email
      -> click CONTINUE
      -> click "Use Password Instead"
      -> click password field -> clear -> type password
      -> click SIGN IN
    """
    email_xy = _parse_xy("EMAIL_XY", DEFAULT_EMAIL_XY)
    continue_xy = _parse_xy("CONTINUE_XY", DEFAULT_CONTINUE_XY)
    usepass_xy = _parse_xy("USEPASS_XY", DEFAULT_USEPASS_XY)
    password_xy = _parse_xy("PASSWORD_XY", DEFAULT_PASSWORD_XY)
    signin_xy = _parse_xy("SIGNIN_XY", DEFAULT_SIGNIN_XY)

    logging.info("Login step 1/5: clicking email field and typing email...")
    if not click_window_rel(window_id, *email_xy, retry_multiplier):
        return False
    _clear_field(retry_multiplier)
    if not type_text(email_username, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_CREDENTIAL_ENTRY_WAIT_FACTOR)
    capture("step1-email-typed")

    logging.info("Login step 2/5: clicking CONTINUE...")
    if not click_window_rel(window_id, *continue_xy, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_LOGIN_STEP_WAIT_FACTOR)
    capture("step2-after-continue")

    logging.info("Login step 3/5: clicking 'Use Password Instead'...")
    if not click_window_rel(window_id, *usepass_xy, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_LOGIN_STEP_WAIT_FACTOR)
    capture("step3-after-use-password")

    logging.info("Login step 4/5: clicking password field and typing password...")
    if not click_window_rel(window_id, *password_xy, retry_multiplier):
        return False
    _clear_field(retry_multiplier)
    if not type_text(password, retry_multiplier):
        return False
    time.sleep(retry_multiplier * POST_CREDENTIAL_ENTRY_WAIT_FACTOR)
    capture("step4-password-typed")

    logging.info("Login step 5/5: clicking SIGN IN...")
    if not click_window_rel(window_id, *signin_xy, retry_multiplier):
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
        logging.info("Grass already configured (flag found: %s).", configured_flag_path)
        return True

    if not email_username or not password:
        logging.error("Credentials not provided. Cannot autologin.")
        return False

    current_grass_proc = grass_proc_ref

    for attempt in range(max_attempts):
        logging.info("Attempting Grass configuration (attempt %d/%d)...", attempt + 1, max_attempts)

        windows = search_windows_by_name(GRASS_WINDOW_NAME, max_attempts, retry_multiplier)
        if windows is None:
            if current_grass_proc.poll() is not None:
                logging.info("Grass process died. Relaunching...")
                new_proc = launch_grass_with_retries(max_attempts, retry_multiplier)
                if new_proc:
                    current_grass_proc = new_proc
                else:
                    logging.error("Relaunch failed. Aborting.")
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
        logging.info("Focusing Grass window (ID: %s)...", last_window_id)
        if _run_subprocess(XDOTOOL_CMD + ["windowfocus", "--sync", last_window_id]).returncode != 0:
            logging.warning("Failed to focus window. Retrying.")
            if current_grass_proc.poll() is not None:
                new_proc = launch_grass_with_retries(max_attempts, retry_multiplier)
                if new_proc:
                    current_grass_proc = new_proc
                else:
                    return False
            continue

        time.sleep(retry_multiplier * POST_FOCUS_WAIT_FACTOR)

        logging.info("Performing login steps...")
        if not _perform_login_steps(last_window_id, email_username, password, retry_multiplier):
            logging.warning("A login step failed. Retrying.")
            continue

        logging.info("Grass login steps completed.")
        try:
            with open(configured_flag_path, "w") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
            logging.info("Created configuration flag: %s", configured_flag_path)
            return True
        except IOError as e:
            logging.error("Failed to write configuration flag: %s", e)
            return False

    logging.error("Failed to configure Grass after %d attempts.", max_attempts)
    return False


def main() -> None:
    setup_logging()

    max_retry_multiplier_str = os.getenv("MAX_RETRY_MULTIPLIER", str(DEFAULT_MAX_RETRY_MULTIPLIER))
    try:
        max_retry_multiplier = int(max_retry_multiplier_str)
    except ValueError:
        logging.warning("Invalid MAX_RETRY_MULTIPLIER '%s'. Using default.", max_retry_multiplier_str)
        max_retry_multiplier = DEFAULT_MAX_RETRY_MULTIPLIER

    initial_wait = max_retry_multiplier * INITIAL_X_SERVER_WAIT_FACTOR
    logging.info("Waiting %ds for X server to stabilise...", initial_wait)
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
        logging.error("Grass application failed to launch. Exiting.")
        sys.exit(1)

    if should_try_autologin:
        logging.info("Proceeding with automated login...")
        if configure_grass(grass_proc, email_username, password,
                           launch_configure_max_attempts, max_retry_multiplier):
            logging.info("Autologin reported success.")
        else:
            logging.error(
                "Autologin failed. Grass is still running — log in manually via noVNC (port 6080)."
            )
    else:
        logging.info("Autologin disabled or credentials missing. Waiting for manual login via noVNC.")

    logging.info("Grass Desktop is running (pid %d).", grass_proc.pid)

    try:
        grass_proc.wait()
        logging.info("Grass process %d exited (code %s).", grass_proc.pid, grass_proc.returncode)
    except KeyboardInterrupt:
        logging.info("Interrupted. Terminating Grass...")
        kill_process(grass_proc)
    sys.exit(grass_proc.returncode if grass_proc.returncode is not None else 0)


if __name__ == "__main__":
    main()
