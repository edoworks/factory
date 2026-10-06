import copy
import json
from pathlib import Path
import unittest
from benchmark import validate_accounting


class AccountingTests(unittest.TestCase):
    def test_owner_baseline_cannot_gain_credit_by_hiding_work_or_inventing_measurement(self):
        baseline = json.loads((Path(__file__).resolve().parents[1] / 'autonomy-baseline.json').read_text())
        validate_accounting(baseline)
        for change in [lambda x: x.update(assistant_percent=90, factory_percent=10),
                       lambda x: x['work_units'].pop(), lambda x: x.update(tokens=0)]:
            altered = copy.deepcopy(baseline); change(altered)
            with self.assertRaises(ValueError): validate_accounting(altered)
