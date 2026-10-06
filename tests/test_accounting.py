import copy
import json
from pathlib import Path
import unittest
from benchmark import validate_accounting, validate_receipt_metrics


class AccountingTests(unittest.TestCase):
    def test_owner_baseline_cannot_gain_credit_by_hiding_work_or_inventing_measurement(self):
        baseline = json.loads((Path(__file__).resolve().parents[1] / 'autonomy-baseline.json').read_text())
        validate_accounting(baseline)
        for change in [lambda x: x.update(assistant_percent=90, factory_percent=10),
                       lambda x: x['work_units'].pop(), lambda x: x.update(tokens=0)]:
            altered = copy.deepcopy(baseline); change(altered)
            with self.assertRaises(ValueError): validate_accounting(altered)

    def test_receipt_does_not_promote_literal_zeros_to_measurements(self):
        receipt = {'declared_run_constraints': {'source': 'declared_constraint', 'paid_api_calls_allowed': 0, 'paid_provisioning_allowed': False},
                   'manual_output_patches': None,
                   'run_observation': {'assistant_interventions_during_command': None, 'manual_output_edits': None}}
        validate_receipt_metrics(receipt)
        for change in [lambda x: x.update(manual_output_patches=0),
                       lambda x: x['run_observation'].update(assistant_interventions_during_command=0),
                       lambda x: x['run_observation'].update(manual_output_edits=0),
                       lambda x: x.update(paid_api_calls=0), lambda x: x.update(paid_provisioning=False),
                       lambda x: x['declared_run_constraints'].update(source='measured'),
                       lambda x: x.update(executor_report={'source': 'measured', 'manual_output_edits': 0})]:
            altered = copy.deepcopy(receipt); change(altered)
            with self.assertRaises(ValueError): validate_receipt_metrics(altered)
        receipt['executor_report'] = {'source': 'executor_report', 'manual_output_edits': 0}
        validate_receipt_metrics(receipt)
