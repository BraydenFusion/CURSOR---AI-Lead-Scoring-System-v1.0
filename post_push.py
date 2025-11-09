# Run this script from your local terminal, not inside Cursor.
# Requires a valid .env file and local network access.

import os
from datetime import datetime

import requests

LOG_FILE = "deploy.log"


def load_environment() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        load_dotenv = None  # type: ignore

    if load_dotenv:
        load_dotenv()


def format_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log(message: str, success: bool = True) -> None:
    status = "✅" if success else "❌"
    line = f"[{format_timestamp()}] {status} {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{line}\n")


def main() -> None:
    try:
        load_environment()

        api_endpoint = os.getenv("API_ENDPOINT")
        api_key = os.getenv("API_KEY")

        if not api_endpoint:
            write_log("API_ENDPOINT not set—skipping post-push notification")
            return

        if not api_key:
            write_log("API_KEY not set—skipping post-push notification")
            return

        payload = {
            "event": "deploy_triggered",
            "timestamp": datetime.utcnow().isoformat(),
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()

        write_log(f"Python post-push SUCCESS ({response.status_code})")
    except Exception as exc:
        write_log(f"Python post-push FAILURE - {exc}", success=False)
        raise


if __name__ == "__main__":
    main()

