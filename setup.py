from setuptools import setup, find_packages, Extension

native_extension = Extension(
    "core._airingdeck_native",
    sources=["src/core/_airingdeck_native.c"],
)

setup(
    name="airingdeck",
    version="3.3.0",
    description="Desktop anime airing tracker with AniList integration",
    license="GPL-3.0-or-later",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Microsoft :: Windows",
    ],
    ext_modules=[native_extension],
)
