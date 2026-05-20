"""Browser cookie utilities."""

import json
import re
from pathlib import Path

from notebooklm_tools.core.exceptions import AuthenticationError
from notebooklm_tools.utils.config import get_base_url

# NotebookLM domain for cookie filtering
NOTEBOOKLM_DOMAIN = ".google.com"
NOTEBOOKLM_URL = get_base_url()


def parse_cookies_from_file(file_path: str | Path) -> dict[str, str]:
    """
    Parse cookies from a file.

    The file can contain:
    - Raw cookie header string (Cookie: name=value; name2=value2)
    - cURL command (copy as cURL from DevTools)
    - JSON object with cookies

    Args:
        file_path: Path to the file containing cookies.

    Returns:
        Dictionary of cookie name -> value.

    Raises:
        AuthenticationError: If file cannot be parsed.
    """
    path = Path(file_path).expanduser()

    if not path.exists():
        raise AuthenticationError(
            message=f"Cookie file not found: {path}",
            hint="Create the file with cookies copied from browser DevTools.",
        )

    content = path.read_text(encoding="utf-8").strip()

    # Try to parse as JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        if isinstance(data, list):
            # List of cookie objects
            cookies = {}
            for item in data:
                if isinstance(item, dict) and "name" in item and "value" in item:
                    cookies[item["name"]] = item["value"]
            if cookies:
                return cookies
    except json.JSONDecodeError:
        pass

    # Try to extract from cURL command
    curl_match = re.search(r"-H\s+['\"]Cookie:\s*([^'\"]+)['\"]", content, re.IGNORECASE)
    if curl_match:
        content = curl_match.group(1)

    # Try to extract Cookie header value
    if content.lower().startswith("cookie:"):
        content = content[7:].strip()

    # Parse cookie string (name=value; name2=value2)
    cookies: dict[str, str] = {}
    for part in content.split(";"):
        part = part.strip()
        if "=" in part:
            name, _, value = part.partition("=")
            name = name.strip()
            value = value.strip()
            if name and value:
                cookies[name] = value

    if not cookies:
        raise AuthenticationError(
            message="Could not parse cookies from file",
            hint="The file should contain a Cookie header value or cURL command.",
        )

    return cookies


def cookies_to_header(cookies: dict[str, str]) -> str:
    """Convert cookies dict to Cookie header value."""
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


def validate_notebooklm_cookies(cookies: dict[str, str]) -> bool:
    """
    Check if cookies appear to be valid for NotebookLM.

    This is a basic check - actual validation requires making an API call.
    """
    # Check for essential Google auth cookies
    essential_patterns = ["SID", "HSID", "SSID", "APISID", "SAPISID"]
    found = sum(1 for pattern in essential_patterns if any(pattern in name for name in cookies))
    return found >= 2  # At least 2 essential cookies should be present


def parse_cookies_from_curl(curl: str) -> dict[str, str]:
    """Extract cookies from a cURL command's Cookie header."""
    match = re.search(r"-H\s+['\"]Cookie:\s*([^'\"]+)['\"]", curl, re.IGNORECASE)
    if not match:
        raise AuthenticationError(
            message="No Cookie header found in cURL command",
            hint="Make sure you copied the full cURL command including -H 'Cookie: ...' headers.",
        )

    cookie_string = match.group(1)
    cookies: dict[str, str] = {}
    for part in cookie_string.split(";"):
        part = part.strip()
        if "=" in part:
            name, _, value = part.partition("=")
            name = name.strip()
            value = value.strip()
            if name and value:
                cookies[name] = value

    if not cookies:
        raise AuthenticationError(
            message="Could not parse cookies from cURL command",
            hint="Ensure the cURL command contains valid Cookie headers.",
        )

    return cookies


def extract_csrf_from_curl(curl: str) -> str:
    """Extract CSRF token (at= parameter) from cURL request body."""
    # The at= value is embedded in JSON within the --data-raw argument.
    # Shell escaping makes it hard to parse the data cleanly, so we just
    # search for the "at":"..." pattern directly.
    match = re.search(r'"at":"([^"]+)"', curl)
    if match:
        return match.group(1)
    return ""


def extract_session_id_from_curl(curl: str) -> str:
    """Extract session ID (f.sid= parameter) from cURL URL."""
    match = re.search(r"[?&]f\.sid=(\d+)", curl)
    if match:
        return match.group(1)
    return ""


def extract_build_label_from_curl(curl: str) -> str:
    """Extract build label (bl= parameter) from cURL URL."""
    match = re.search(r"[?&]bl=([^&'\"]+)", curl)
    if match:
        return match.group(1)
    return ""
