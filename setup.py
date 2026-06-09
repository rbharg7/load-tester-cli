from setuptools import setup, find_packages

setup(
    name="loadtest",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "aiohttp",
        "rich",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "loadtest=loadtest.cli:main",
        ],
    },
)