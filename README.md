# Myr (Pauperformance bot)

This repository hosts `Myr`, the bot required to manage the Pauperformance project.

Myr tirelessly takes care of different tasks.
The most important of them is keeping the [Academy](https://pauperformance.com/) up-to-date.

---
## Information

**Status**: `Actively developed`

**Type**: `Personal project`

**Development year(s)**: `2021+`

**Authors**: [ShadowTemplate](https://github.com/ShadowTemplate), [ThisIsMirquez](https://github.com/ThisIsMirquez), [Federico Maiorano](https://github.com/fedemaiorano), [Rikxvis](https://github.com/Rikxvis), [Marco Casari](https://github.com/mirasac)

---
## Getting Started

Make sure `Python 3.9` (or newer) is installed on your machine.
Instructions to download and install `Python` can be found in the [official page](https://www.python.org/downloads/).  
You can verify `Python` is working by running:
```
$ python3 --version
Python 3.9.12
```
Additionally, install [pip](https://pip.pypa.io/en/stable/installation/) and [venv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) modules.  
You can verify `pip` is working by running:
```
$ pip --version
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.9)
```

Make sure `git` is also installed on your machine.
Instructions to download and install `git` can be found in the [official page](https://git-scm.com/downloads).  
You can verify `git` is working by running:
```
$ git --version
git version 2.25.1
```

Now, you are ready to clone Pauperformance repositories (you will need both of them):
```
$ git clone https://github.com/Pauperformance/Pauperformance.github.io.git
$ git clone https://github.com/Pauperformance/pauperformance-bot.git
$ cd pauperformance-bot
```

### Prerequisites

Create and activate a virtual environment for `Myr`:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip setuptools wheel
```

### Installing

Upon installing `Myr` in your virtual environment, you can choose between 3 versions:
* `default`: sufficient to execute `Myr` tasks;
* `test`: required to run `Myr` tests, often used by autonomous agents (includes `default`);
* `dev`: required to develop new `Myr` functionalities (includes `default`).

You can install any of these versions by running, respectively:
```
$ pip install .        # default
$ pip install .[test]  # test
$ pip install .[dev]   # dev
```
You can verify `pauperformance-bot` is working by running:
```
$ myr test hello
Myr ready to serve you, Milord!
```

### Testing

Tests are executed with [tox](https://tox.wiki/):

```
$ tox
```
---

## Building tools

* [Python](https://www.python.org/) - Programming language
* [GitHub Pages](https://pages.github.com/) - Web host
* [Jinja](https://jinja.palletsprojects.com/) - Templating engine
* [Dropbox](https://www.dropbox.com/) - Storage service
* [pyquery](https://github.com/gawel/pyquery/) - Web pages parser

---
## Contributing

Any contribution is welcome.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests.

---
## License

This project is licensed under the GNU General Public License v3 (GPLv3) license.
Please refer to the [LICENSE.md](LICENSE.md) file for details.

---
*This README.md complies with [this project template](https://github.com/ShadowTemplate/project-template).
Feel free to adopt it and reuse it.*
