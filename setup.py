from setuptools import setup, find_packages, Extension

native_extension = Extension(
    "core._airingdeck_native",
    sources=["src/core/_airingdeck_native.c"],
)

setup(
    name="airingdeck",
    version="3.2.2",
    description="Desktop anime airing tracker with AniList integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    python_requires=">=3.10",
    ext_modules=[native_extension],
)
