# Native Optimization Notes

This project ships a CPython extension module for hot-path filtering:

- Module name: `core._airingdeck_native`
- Source: `src/core/_airingdeck_native.c`
- Python wrapper/fallback: `src/core/native_accel.py`

## Why this exists

Filtering anime entries by title is invoked frequently while typing in the search box.
The native module runs the contains-check loop in C and returns matching indices.

## Safety model

- The native call is optional.
- If import or execution fails, Python fallback is used automatically.
- Runtime behavior remains identical from the UI perspective.

## Build flow

`scripts/build_windows.py` performs:

1. Optional CPU profile flags (`baseline`, `avx2`, `avx512`) via `CL`.
2. Native extension build: `python setup.py build_ext --inplace`.
3. PyInstaller packaging into `dist/AiringDeck.exe`.

Use `--require-native` if you want the build to fail when the C extension cannot be compiled.
