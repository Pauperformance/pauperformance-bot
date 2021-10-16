#!/usr/bin/env python3
import os

from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install

HERE = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS_DIR = "requirements"
RESOURCES_DIR = "resources"
README_FILE = "README.md"
VERSION_FILE = "VERSION"
PAUPERFORMANCE_BOT_DIR = Path().joinpath(
    Path.home().as_posix(), ".pauperformance"
).as_posix()
CACHE_DIR = Path().joinpath(PAUPERFORMANCE_BOT_DIR, "cache").as_posix()
STORAGE_DIR = Path().joinpath(PAUPERFORMANCE_BOT_DIR, "storage").as_posix()
DECKS_PATH = Path().joinpath(STORAGE_DIR, "decks").as_posix()
DECKSTATS_DECKS_PATH = Path().joinpath(DECKS_PATH, "deckstats").as_posix()
MTGGOLDFISH_DECKS_PATH = Path().joinpath(DECKS_PATH, "mtggoldfish").as_posix()


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


def read_resources(resources_dir):
    resources = []
    for root, _, files in os.walk(resources_dir):
        resources.append((f"{root}/", [f"{root}/{file}" for file in files]))
    return resources


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        os.makedirs(PAUPERFORMANCE_BOT_DIR, exist_ok=True)
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(STORAGE_DIR, exist_ok=True)
        os.makedirs(DECKS_PATH, exist_ok=True)
        os.makedirs(DECKSTATS_DECKS_PATH, exist_ok=True)
        os.makedirs(MTGGOLDFISH_DECKS_PATH, exist_ok=True)


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
    data_files=read_resources(RESOURCES_DIR),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'myr = pauperformance_bot.cli.main:main',
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
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
)
