#!/usr/bin/env python3
"""Find available iPhone and iPad simulator names and IDs."""
import subprocess
import re

result = subprocess.run(
    ["xcrun", "simctl", "list", "devices", "available"],
    capture_output=True, text=True
)

iphone = None
ipad = None
for line in result.stdout.splitlines():
    if "(Booted)" in line or "(Shutdown)" in line or "(Shutting down)" in line or "(Booting)" in line:
        name = line.rsplit("(", 2)[0].strip()
        if "iPhone" in name and not iphone:
            iphone = name
        if "iPad" in name and not ipad:
            ipad = name

print(f"IPHONE={iphone or ''}")
print(f"IPAD={ipad or ''}")