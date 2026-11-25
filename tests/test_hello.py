import shlex
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HelloFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)
        cls.executable = cls.temp_path / ("hello-filter.exe" if os.name == "nt" else "hello-filter")
        flags = shlex.split((ROOT / "compile_flags.txt").read_text())
        build = subprocess.run(
            ["clang", *flags, "src/hello.c", "-o", str(cls.executable)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if build.returncode != 0:
            raise RuntimeError(f"Clang build failed:\n{build.stderr}")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def run_filter(self, contents, *arguments):
        input_path = self.temp_path / "input.csv"
        input_path.write_text(contents)
        return subprocess.run(
            [str(self.executable), *map(str, arguments), str(input_path)],
            capture_output=True,
            text=True,
        )

    def test_single_character_row_does_not_crash(self):
        result = self.run_filter("A", "18")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Age missing", result.stderr)

    def test_row_with_missing_age_is_skipped(self):
        result = self.run_filter("Alice,", "18")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Age missing", result.stderr)

    def test_rows_are_filtered_by_minimum_age(self):
        result = self.run_filter("Alice,17\nBob,18\nCara,25\n", "18")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Bob, 18\nCara, 25\n")


if __name__ == "__main__":
    unittest.main()
