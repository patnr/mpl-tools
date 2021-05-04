# Run `make` with no arguments to view possible actions.
#
# NB: This Makefile is mostly linux-only.
# On MacOSX, must use homebrew's gmake!
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

define echo_install_success
	echo -e "\033[0;34m\n✔️ ✔️ ✔️ ✔️ ✔️ ✔️  You can now run scripts using:\033[0m"
	echo -e "poetry run the_example_script.py\n"
endef

install: get_poetry ## Install with dev. tools
	@echo "Installing $(SRC) with dev. tools"
	$(POETRY) install
	$(POETRY) run pre-commit install
	$(call echo_install_success)

install-no-dev: get_poetry ## Install without dev. tools
	@echo "Installing $(SRC)"
	$(POETRY) install --no-dev
	$(POETRY) run pre-commit install
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

test: ## Run tests
	@$(POETRY) run pytest
	#$(POETRY) run pytest $(TESTS)
tests: test ## Alias for test

tox: ## Run tests in all supported python versions (using existing pyenv's)
	@$(POETRY) run tox

# Provide output also in case of no issues.
# NB: Including sources means that you might forget others
#     => Let them be discovered instead.
lint: ## Run linter
	@$(POETRY) run flakehell lint && \
	echo -e "Linter found no issues ✨ 🍰 ✨" || \
	echo -e "❌ Issues detected. See above."

autoformat:  ## Run autoformatter
	@echo "Autoformatting not supported at the moment."
	#@black .

doc: ## Build docs (preview in ./docs/index.html)
	@echo -e "\033[0;34m" "Generating docs" "\033[0m"
	@$(POETRY) run pdoc \
		--force --html \
		--template-dir docs/templates \
		-o ./docs \
		$(SRC) docs/dev_guide.py
docs: doc ## Alias for doc

publish: docs ## Publish new version to PyPI (for pip). Via Travis-CI => Slow.
	@echo
	@echo -e "\033[0;34m" "Committing updated docs" "\033[0m"
	git add docs
	git commit -m "Build doc" 1>/dev/null || true
	@echo
	@echo -e "\033[0;34m" "Bumping package version" "\033[0m"
	VERSION=$(shell poetry version patch | rev | cut -f1 -d" " | rev)
	echo "New version" $$VERSION
	@echo
	@echo -e "\033[0;34m" "Pushing updated package" \
		"which will be deployed to PyPI in due time" \
		"after running tests on Travis-CI" "\033[0m"
	git add pyproject.toml
	git commit -m "Bump version"
	git tag v$$VERSION
	git push
	git push origin --tags
