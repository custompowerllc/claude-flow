#!/usr/bin/env python3
"""Setup configuration for GEHC PHTC RS422 Test Application."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gehc-phtc-test",
    version="1.0.0",
    author="GEHC Development Team",
    author_email="development@gehc.com",
    description="GEHC PHTC RS422 Communication Protocol Test Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="gehc_phtc_test"),
    package_dir={"": "gehc_phtc_test"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gehc-phtc-test=gehc_phtc_test.src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json"],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/gehc/phtc-test/issues",
        "Source": "https://github.com/gehc/phtc-test",
    },
)