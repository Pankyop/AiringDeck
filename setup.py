from setuptools import setup, find_packages

setup(
    name="anime-calendar-qt",
    version="1.0.0",
    description="Desktop anime calendar with AniList integration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.7.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "keyring>=24.3.0",
    ],
    entry_points={
        "console_scripts": [
            "anime-calendar=main:main",
        ],
    },
)
