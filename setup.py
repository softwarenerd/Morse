from setuptools import setup, find_packages

setup(
    name="morse",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "morse = morse.cli:main",
        ]
    },
    install_requires=[],
    python_requires=">=3.7",
)