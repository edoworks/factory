#!/usr/bin/env python3
"""Find unique available iPhone and iPad simulator destinations."""

from __future__ import annotations

import json
import re
import subprocess
import sys


def runtime_version(identifier: str) -> tuple[int, ...]:
    match = re.search(r"\.iOS-([0-9-]+)$", identifier)
    return tuple(int(part) for part in match.group(1).split("-")) if match else ()


def select_devices(payload: dict) -> tuple[dict | None, dict | None]:
    devices = [
        {**device, "runtimeIdentifier": runtime}
        for runtime, runtime_devices in payload.get("devices", {}).items()
        for device in runtime_devices
        if device.get("isAvailable", True)
    ]
    devices.sort(
        key=lambda device: runtime_version(device.get("runtimeIdentifier", "")),
        reverse=True,
    )
    iphone = next((device for device in devices if "iPhone" in device.get("name", "")), None)
    ipad = next((device for device in devices if "iPad" in device.get("name", "")), None)
    return iphone, ipad


def main() -> int:
    result = subprocess.run(
        ["xcrun", "simctl", "list", "devices", "available", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("IPHONE=")
        print("IPAD=")
        return result.returncode
    iphone, ipad = select_devices(json.loads(result.stdout))
    print(f"IPHONE={iphone.get('udid', '') if iphone else ''}")
    print(f"IPHONE_NAME={iphone.get('name', '') if iphone else ''}")
    print(f"IPHONE_TYPE={iphone.get('deviceTypeIdentifier', '') if iphone else ''}")
    print(f"IPHONE_RUNTIME={iphone.get('runtimeIdentifier', '') if iphone else ''}")
    print(f"IPAD={ipad.get('udid', '') if ipad else ''}")
    print(f"IPAD_NAME={ipad.get('name', '') if ipad else ''}")
    print(f"IPAD_TYPE={ipad.get('deviceTypeIdentifier', '') if ipad else ''}")
    print(f"IPAD_RUNTIME={ipad.get('runtimeIdentifier', '') if ipad else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
