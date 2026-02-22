# Third-Party Licenses

This project is distributed under `GPL-3.0-or-later`.

The following third-party components are used by AiringDeck and keep their
own licenses:

## Runtime dependencies

- `PySide6` (Qt for Python) - `LGPL-3.0-or-later` (or commercial)
- `requests` - `Apache-2.0`
- `python-dotenv` - `BSD-3-Clause`
- `keyring` - `MIT`
- `certifi` (transitive via requests) - `MPL-2.0`
- `urllib3` (transitive via requests) - permissive (see package metadata)
- `charset-normalizer` (transitive via requests) - `MIT`
- `idna` (transitive via requests) - permissive (see package metadata)

## Build/packaging dependencies

- `pyinstaller` - `GPL-2.0-or-later` with PyInstaller exception
- `setuptools` - `MIT`
- `wheel` - `MIT`

## QA/dev dependencies (not required at runtime)

- `pytest` - `MIT`
- `coverage` - `Apache-2.0`
- `ruff` - `MIT`
- `bandit` - `Apache-2.0`
- `hypothesis` - `MPL-2.0`
- `psutil` - `BSD-3-Clause`

## Notes

1. Each dependency remains under its own license terms.
2. For Qt/PySide6 licensing obligations, refer to:
   https://doc.qt.io/qtforpython-6/licenses.html
3. For PyInstaller exception details, refer to:
   https://pyinstaller.org/en/stable/license.html
4. End users and redistributors are responsible for complying with all
   applicable third-party license requirements.
