from html import escape


def escape_html(value: object) -> str:
    """Escape untrusted text before inserting it into Telegram HTML messages."""
    return escape(str(value), quote=True)
