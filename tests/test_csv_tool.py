import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CsvToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        cls.executable = cls.temp_path / ("csv-tool.exe" if os.name == "nt" else "csv-tool")
        flags = shlex.split((ROOT / "compile_flags.txt").read_text())
        build = subprocess.run(
            ["clang", *flags, "src/csvTool.c", "-o", str(cls.executable)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if build.returncode != 0:
            raise RuntimeError(f"Clang build failed:\n{build.stderr}")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def run_filter(self, contents, minimum_age="18"):
        input_path = self.temp_path / "input.csv"
        input_path.write_text(contents)
        return subprocess.run(
            [str(self.executable), minimum_age, str(input_path)],
            capture_output=True,
            text=True,
        )

    def test_single_character_row_does_not_crash(self):
        result = self.run_filter("A")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Age missing", result.stderr)

    def test_row_with_missing_age_is_skipped(self):
        result = self.run_filter("Alice,")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Age missing", result.stderr)

    def test_rows_are_filtered_by_minimum_age(self):
        result = self.run_filter("Alice,17\nBob,18\nCara,25\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Bob, 18\nCara, 25\n")

    def test_accepts_alternate_delimiters_and_keeps_comma_output(self):
        contents = "Alice,17\nBob;18\nCara\t19\nDrew|20\n"

        result = self.run_filter(contents)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Bob, 18\nCara, 19\nDrew, 20\n")

    def test_accepts_mixed_delimiters_in_one_row(self):
        result = self.run_filter("Evan;21|ignored\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Evan, 21\n")


if __name__ == "__main__":
    unittest.main()