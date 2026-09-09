"""
App Launcher module for Virtual AI Mouse & Keyboard.
Handles safe launching of web applications and desktop tools mapped to recognized letters.
"""
import os
import subprocess
import webbrowser
from src import config


class AppLauncher:
    """
    Executes or opens applications and URLs based on recognized letters.
    """

    def __init__(self):
        self.mappings = config.APP_MAPPINGS
        self.chrome_path = self._find_chrome_executable()

    def _find_chrome_executable(self) -> str | None:
        """Searches standard Windows installation locations for chrome.exe."""
        for candidate in config.CHROME_CANDIDATE_PATHS:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def launch(self, letter: str) -> tuple[bool, str]:
        """
        Launches the target associated with the letter.
        Returns:
            (success: bool, status_message: str)
        """
        letter = letter.upper().strip()
        if letter not in self.mappings:
            msg = f"[WARNING] No application mapped to letter '{letter}'"
            print(msg)
            return False, msg

        app_info = self.mappings[letter]
        app_name = app_info["name"]
        app_type = app_info["type"]
        target = app_info["target"]

        try:
            if letter == "C":
                # Special handling for Google Chrome
                if self.chrome_path and os.path.exists(self.chrome_path):
                    subprocess.Popen([self.chrome_path])
                    msg = f"[LAUNCH] Opened {app_name} (Desktop App)"
                else:
                    webbrowser.open(target)
                    msg = f"[LAUNCH] Opened {app_name} in default browser"
                print(msg)
                return True, msg

            elif letter == "N":
                # Special handling for Windows Notepad
                subprocess.Popen(["notepad.exe"])
                msg = f"[LAUNCH] Opened {app_name}"
                print(msg)
                return True, msg

            elif app_type in ("url", "browser"):
                # Open Web URLs
                webbrowser.open(target)
                msg = f"[LAUNCH] Opened {app_name}"
                print(msg)
                return True, msg

            elif app_type == "app":
                # Desktop application execution
                subprocess.Popen([target])
                msg = f"[LAUNCH] Opened {app_name}"
                print(msg)
                return True, msg

        except Exception as e:
            # Fallback to web browser if app execution fails
            try:
                if target.startswith("http"):
                    webbrowser.open(target)
                else:
                    webbrowser.open("https://www.google.com")
                msg = f"[LAUNCH] Opened {app_name} (Fallback: {e})"
                print(msg)
                return True, msg
            except Exception as fallback_err:
                msg = f"[ERROR] Failed to launch {app_name}: {fallback_err}"
                print(msg)
                return False, msg

        return False, f"[ERROR] Unknown error launching {app_name}"
