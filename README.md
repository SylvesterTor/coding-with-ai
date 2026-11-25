# C template for multiple main files

For https://c-programming.aydos.de

Select a C main file and press <kbd>F5</kbd> to start your program. There are two examples for testing: `hello.c` and `pi-estimator.c`.

## Running the tests

The tests require Python 3 and Clang to be available on `PATH`. From the repository root, run:

```powershell
python -m unittest discover -s tests -v
```

The test suite compiles `src/hello.c` using `compile_flags.txt` into a temporary directory, then checks that short or incomplete CSV rows do not crash the filter and that the minimum-age filtering still works. The temporary executable and test data are removed after the tests finish.