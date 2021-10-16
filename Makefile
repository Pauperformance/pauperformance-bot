include ./Makefile.vars

.DEFAULT_GOAL := default

default: clean install

clean:
	rm -rf .pytest_cache/ .tox/ build/ coverage_html/ dist/ pauperformance_bot.egg-info/ .coverage coverage.xml
.PHONY: clean

uninstall:
	pip uninstall pauperformance-bot
.PHONY: install

install:
	pip install .
.PHONY: install

install-dev:
	pip install .[${PY_EXTRA_DEV}]
.PHONY: install-dev

install-test:
	pip install .[${PY_EXTRA_TEST}]
.PHONY: install-test

test: install-test
	tox -- -n 16
.PHONY: test

autocomplete-bash:
	echo "eval \"\$$(register-python-argcomplete myr)\"" >> ~/.bashrc
	echo "Start a new shell to start receiving tab completion."
.PHONY: autocomplete-bash

