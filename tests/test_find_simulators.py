import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "find-simulators.py"
SPEC = importlib.util.spec_from_file_location("find_simulators", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
select_devices = MODULE.select_devices


class SimulatorSelectionTests(unittest.TestCase):
    def test_duplicate_names_are_disambiguated_by_udid(self):
        payload = {
            "devices": {
                "com.apple.CoreSimulator.SimRuntime.iOS-25-0": [
                    {"name": "iPhone 17 Pro", "udid": "shutdown-phone", "state": "Shutdown", "isAvailable": True},
                    {"name": "iPhone 17 Pro", "udid": "booted-phone", "state": "Booted", "isAvailable": True},
                    {"name": "iPad Pro", "udid": "tablet", "state": "Shutdown", "isAvailable": True},
                ],
                "com.apple.CoreSimulator.SimRuntime.iOS-26-0": [
                    {"name": "iPhone 18 Pro", "udid": "newest-phone", "state": "Shutdown", "isAvailable": True},
                    {"name": "iPad Pro", "udid": "newest-tablet", "state": "Shutdown", "isAvailable": True},
                ],
            }
        }
        iphone, ipad = select_devices(payload)
        self.assertEqual(iphone["udid"], "newest-phone")
        self.assertEqual(ipad["udid"], "newest-tablet")
        self.assertEqual(iphone["runtimeIdentifier"], "com.apple.CoreSimulator.SimRuntime.iOS-26-0")

    def test_unavailable_devices_are_not_selected(self):
        payload = {
            "devices": {
                "runtime": [
                    {"name": "iPhone 17", "udid": "unavailable", "state": "Shutdown", "isAvailable": False}
                ]
            }
        }
        self.assertEqual(select_devices(payload), (None, None))


if __name__ == "__main__":
    unittest.main()
