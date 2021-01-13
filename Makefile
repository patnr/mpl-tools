# Run `make` with no arguments to view possible actions.
#
# NB: This Makefile is mostly linux-only.
#
# Why this file ? (when you already use poetry/pyproject.toml)
# ----------------
# 	Poetry not only deals with dependency resolution.
# It also handles packaging/distribution. But, only for PyPI (pip).
# 	So how are "applications" (vs "libraries") to be packaged?
# Using pipx? Distributing as .deb package? What about MacOS? etc. Ref:
# https://docs.python-guide.org/shipping/freezing/#freezing-your-code-ref
# Remember, they need to create an isolated python environment,
# and download (or vendorize) dependencies.
# 	Similarly, how should it be installed from source (github),
# for the purpose of development?
# One alternative is to state that poetry is prerequisite.
# Another way is to provide this makefile, since (GNU) make
# is pretty universal. This makefile takes care of
# - Poetry installation
# - Venv activation (with poetry)
# - Task running (invoker), avoiding the necessity for
#   multiple small scripts for testing, cleaning, linting, publishing, etc.
#   Note that task execution might be handled by poetry in the future:
#   https://github.com/python-poetry/poetry-core/pull/40 .
# - Providing (fairly readable) recipies
#
# Makefile syntax:
# ----------------
# - cheatsheet: https://devhints.io/makefile
# - Must use tabs to prefix the action parts of rules!
# - .PHONY is used to declare targets that don't yield (epynomous) files.
#   For example, w/o this, the tests will not run if a `test` dir exists
#   Related note: targets without deps always run, unless they're shaded by a file/dir.
# - Directory timestamps don't change upon file changes => use `find`, e.g.:
#   hello: $(shell find $(SRC) -type f)
#   	@echo "Hello World" > hello

# Project-specific
SRC:=mpl_tools
TESTS:=tests

# - Some sensible defaults from https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# POETRY:=poetry
# Hack to avoid poetry using (and complaining about) python < 3
# https://github.com/python-poetry/poetry/issues/3288#issuecomment-717090078
POETRY:=python3 $(HOME)/.poetry/bin/poetry
POETRY_URL:=https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py

# Explained above
.PHONY: all clean help lint type test tests test-cov tox autoformat doc docs
.PHONY: venv poetry install install-dev

# w/o this, the topmost target is the default
.DEFAULT_GOAL := help

# Auto-doc makefile
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

get_poetry: # internal -- leave undoc'd
	@command -v poetry &> /dev/null || \
		{ echo "Installing poetry"; curl -sSL $(POETRY_URL) | python - ; }
	# - See also a more secure and detailed version at
	#   https://github.com/wrike/callisto/blob/master/Makefile
	# - Could also use `pip install poetry`, but that's not really recommended.
	# - Pipx is probably not a good idea either, ref:
	#   https://github.com/python-poetry/poetry/issues/677#issuecomment-443372910
	# - Approaches using venv:
	#   https://news.ycombinator.com/item?id=20677114
	#   https://stackoverflow.com/a/59335943/38281


define echo_install_success
	echo -e "\033[0;34m\n✔️ ✔️ ✔️ ✔️ ✔️ ✔️  You can now run scripts using:\033[0m"
	echo -e "poetry run the_example_script.py\n"
endef

install: get_poetry ## Install with dev. tools
	@echo "Installing $(SRC) with dev. tools"
	$(POETRY) install
	$(call echo_install_success)

install-no-dev: get_poetry ## Install without dev. tools
	@echo "Installing $(SRC)"
	$(POETRY) install --no-dev
	$(call echo_install_success)

#run: ## Run app
#    $(POETRY) run myapp.py

# If this line is active, then installation will re-run each time
# (although poetry is smart enough to avoid re-installing, it takes time).
#run test test tox lint: install

clean: ## Rm build/test/cache files
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +
	#@git clean -Xdf # DANGEROUS -- delete all files in .gitignore

tests: test ## Alias for test
test: ## Run tests
	@$(POETRY) run pytest
	#$(POETRY) run pytest $(TESTS)

tox: ## Run tests in all supported python versions
	@$(POETRY) run tox

# Provide output also in case of no issues.
lint: ## Run linter
	@$(POETRY) run flakehell lint $(SRC) $(TESTS) && \
	echo -e "Linter found no issues ✨ 🍰 ✨" || \
	echo -e "❌ Issues detected. See above."

autoformat:  ## Run autoformatter
	@echo "Autoformatting not supported at the moment."
	#@black .


docs: ## Build docs
	@$(POETRY) run pdoc ...

version_bump: ## Bump version
	:

publish: docs ## Publish to PyPI (pip)
	git add doc ; git commmit -m "Build doc"; git push
	git tag; git ta gpush
	poetry publish
