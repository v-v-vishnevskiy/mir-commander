import re

file_name_sanitize_re = re.compile(r"[^\w _\-]|(\s)(?=\1+)")


def sanitize_filename(value: str) -> str:
    value = value.strip().replace(".", "_").replace(" ", "_").replace("/", "_")
    value = re.sub(file_name_sanitize_re, "", value)
    return value
