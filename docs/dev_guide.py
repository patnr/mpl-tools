"""
# Dev guide

## Want tests to run on any level (pytest, tox, travis)

### Items
Screw cookiecutter and pyscaffold
coc-settings
Poetry/pyproject
Linting
 - Editor: useful
 - Precommit: useful
 - Travis: for PRs
 - As part of pytest - maybe for heavier (eg pylint) linting.
 - As part of tox - nah. This is one overlap too many

Flakehell
Unlike flake8, flakehell
- may be configured in pyproject.toml
- has prettier formatting
- does not use installed plugins that are not listed below
One interesting option not explored yet is to
inherit from remote config (or local if you want), e.g.:
`base = "https://raw.githubusercontent.com/life4/flakehell/master/pyproject.toml"`

Flakehell also enables intricate plugin configuration.
Examples follow.
NB: remember to comment-out the corresponding lines above

    pyflakes = ["+*", "-F401"] # ignore F401
    pycodestyle = ["+*", "-E722"] # ignore E722
    flake8-docstrings = ["-*"] # explicitly disable plugin
    flake8-bandit = ["+*", "-S322"]
    flake8-bandit = ["-*", "+S1??"] # enable only codes from S100 to S199

    # Exceptions:
    # [tool.flakehell.exceptions."tests/"]
    # pycodestyle = ["-F401"]     # disable a check
    # pyflakes = ["-*"]           # disable a plugin
    # [tool.flakehell.exceptions."tests/test_example.py"]
    # pyflakes = ["+*"]           # enable a plugin

Installation and tasks with Makefile

Pytest
- Using mpl image comparison

Tox requires that the python versions exist on your system.
=> pyenv

Travis-CI

    # AFAIK, the main reason to use tox on travis-ci (as well as locally)
    # is just to avoid repeating ourselves.


Deploy when git tag is pushed

## Tox/poetry

Poetry/tox integration is subject to rapid change, ref:
- <https://tox.readthedocs.io/en/latest/example/package.html#poetry>
- <https://tox.readthedocs.io/en/latest/example/basic.html\
#pyproject-toml-tox-legacy-ini>
- <https://python-poetry.org/docs/faq/#is-tox-supported>
- <https://github.com/python-poetry/poetry/issues/1941>
- <https://github.com/python-poetry/poetry/issues/1745>

Remember,
- `envlist` lists the tests run by default.
  Use CLI option `-e` to only run particular ones.
  Tests can be detailed using [testenv:myname] sections.
- `toxworkdir={homedir}/.tox` puts the tox envs in HOME,
  to avoid Dropbox syncing them.
- `isolated_build = True` is required with poetry
- `install_dev_deps` comes with `tox-poetry-installer` and is used to install the
  - dev-dependencies already specified in pyproject.toml
    (avoids repeating ourselves)
  - from the lockfile (for reproducibility)

## Tox/Coverage
It appears that `[tool.pytest.ini_options]`
does not apply when pytest is run through tox?
Example of how to generate COVERAGE reports WITHIN TOX runs,
[ref](https://pytest-cov.readthedocs.io/en/latest/tox.html).
Set `tool.tox.legacy_tox_ini` to the following:

    ```ini
    [tox]
    envlist = clean,py3{7,8,9}
    isolated_build = True

    [testenv]
    install_dev_deps = true

    # Pytest explanations
    # * envsitepackagesdir : https://stackoverflow.com/a/59072005
    # * cov-append         : https://pytest-cov.readthedocs.io/en/latest/tox.html
    # * term-missing       : List lines not covered
    # * {posargs}          : arguments forwarded from tox command
    commands =
        pytest \
        --cov {envsitepackagesdir}/mpl_tools \
        --cov-append \
        --cov-report=term-missing \
        {posargs}

    [testenv:clean]
    install_dev_deps = false
    deps = coverage
    skip_install = true
    commands = coverage erase
    ```
"""
