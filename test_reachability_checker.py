"""Basic tests for reachability_checker.py that don't require network access."""

import csv
import tempfile
import unittest
from pathlib import Path

from reachability_checker import load_inventory, Result


class TestLoadInventory(unittest.TestCase):
    def test_loads_valid_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "host", "port"])
            writer.writerow(["example", "example.com", "443"])
            path = f.name

        try:
            rows = load_inventory(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "example")
            self.assertEqual(rows[0]["host"], "example.com")
            self.assertEqual(rows[0]["port"], "443")
        finally:
            Path(path).unlink()

    def test_missing_column_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "host"])  # missing "port"
            writer.writerow(["example", "example.com"])
            path = f.name

        try:
            with self.assertRaises(ValueError):
                load_inventory(path)
        finally:
            Path(path).unlink()


class TestResult(unittest.TestCase):
    def test_result_fields(self):
        r = Result("example", "example.com", 443, True, 12.3, "")
        self.assertTrue(r.reachable)
        self.assertEqual(r.port, 443)


if __name__ == "__main__":
    unittest.main()
