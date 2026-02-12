import re

def download_mode_status_mapper(output: str) -> str:
    return (
        "Download Mode detected"
        if not output.startswith("ERROR")
        else "Download Mode not detected"
    )


def adb_status_mapper(output: str) -> str:
    return (
        "ADB detected"
        if bool(re.search(r'[1-9]', output))
        else "ADB not detected"
    )
