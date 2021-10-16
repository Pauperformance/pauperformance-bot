#!/usr/bin/env python3
import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS_DIR = "requirements"
README_FILE = "README.md"
VERSION_FILE = "VERSION"


def read_requirements(file_name):
    reqs = []
    with open(os.path.join(HERE, file_name)) as in_f:
        for line in in_f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("    #") \
                    or line.startswith("-r"):
                continue
            reqs.append(line)
    return reqs


with open(os.path.join(HERE, README_FILE)) as f:
    readme = f.read()

with open(os.path.join(HERE, VERSION_FILE)) as f:
    version = f.read()


setup(
    name="pauperformance-bot",
    version=version,
    url="https://github.com/Pauperformance/pauperformance-bot",
    author="Pauperformance Team",
    author_email=" pauperformance@gmail.com",
    license_files=('LICENSE.txt',),
    description="Myr",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests"]),
    install_requires=read_requirements(f"{REQUIREMENTS_DIR}/requirements.txt"),
    extras_require={
        "test": read_requirements(f"{REQUIREMENTS_DIR}/requirements-test.txt"),
        "dev": read_requirements(f"{REQUIREMENTS_DIR}/requirements-dev.txt"),
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.repo"]
    },
    entry_points={
        'console_scripts': [
            'myr = pauperformance_bot.cli_shit:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        # "Typing :: Typed",
    ]
)
