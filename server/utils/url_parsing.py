import re

__all__ = ["extract_http_url_from_js"]


def extract_http_url_from_js(s: str) -> str:
    """
    javascript:fnEventView('https://...'); 또는 onclick="fnEventView('https://...')"
    같은 문자열에서 따옴표 안의 http(s) URL만 깔끔히 추출.
    없으면 빈 문자열 반환.
    """

    if not s:
        return ""

    try:
        m = re.search(r"['\"](https?://[^'\"()]+)['\"]", s)
        return m.group(1) if m else ""

    except Exception:
        return ""
