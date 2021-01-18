"""Developer guide.

## Why is patlib not in develop mode?
Because even though I made it an "extras",
it appears to still be registered in the lockfile.
Anyways, when doing `poetry install` on Travis,
it cannot find this local path (of course), and the installation fails.

I tried adding it in the poetry environment
(without adding it to `pyproject.toml` or `poetry.lock`)
by doing `poetry run pip install -e ../patlib`
but that fails due to issues in this lengthy thread:
https://github.com/python-poetry/poetry/issues/34
I could still hack my way around it, with inspiration from that thread,
beacuse `pip install` will install the dependencies before failing,
and path to patlib can be provided by inserting a `.pth` file
in the site-packages of the poetry venv.
But that's just too dirty.

Still, I don't want to copy-paste all the dependencies from patlib,
so I include patlib in the project dependencies.
TODO: Make a pre-commit hook to remove patlib?


## Why use `make publish` instead of just `poetry publish`?
As opposed to `poetry publish`, this accomplishes

- Builds docs.
- Bumps version with `poetry`, and tags `git` with the result,
  thus synchronizing these versions
  (note that `__init__.py` gets its `__version__` independently).
  `Travis` then gets triggered, and since the commit includes a tag,
  it will deploy to `PyPI.` Of course, Travis is slow,
  but it means that only successfully tested builds are published.

## Want tests to run on any level (`pytest`, `tox`, `travis`)
Note that Travis ain't really a level above tox
(although it's true that with travis you can even test on different
OS and platform versions), as explained under `Why not tox?`.

## Why a makefile (when you already use `poetry/pyproject.toml`) ?
Poetry not only deals with dependency resolution.
It also handles packaging/distribution. But, only for PyPI (`pip`).

So how are "applications" (vs "libraries") to be packaged?
Using pipx? Distributing as .deb package? What about MacOS? etc.
[Ref](https://docs.python-guide.org/shipping/freezing/#freezing-your-code-ref)
Remember, they need to create an isolated python environment,
and download (or vendorize) dependencies.

Similarly, how should it be installed from source (github),
for the purpose of development?
One alternative is to state that poetry is prerequisite.
Another way is to provide this makefile, since (GNU) make
is pretty (awful, but) universal. This makefile takes care of
the poetry installation, together with the venv activation,
package and pre-commit installation (with poetry).

The makefile is also useful as a task runner (invoker),
avoiding the necessity for multiple small scripts
for testing, cleaning, linting.
Some of the tasks are simple enough that it might be better
just to read the recipe and do them yourself.
Indeed this makefile hardly takes advantage of the main pros
of `make` (DAG of dependencies combined with mtime;
support for incremental and parallel builds).
Nevertheless, the makefile still serves as a reminder of
which tasks "exist", as shown by running `make` without arguments.
Note that task execution could
[maybe](https://github.com/python-poetry/poetry-core/pull/40)
be handled by poetry in the future.

#### Is the makefile using the best way to get poetry?
It's using the "official" way. Whether it's the best,
for our purposes, I don't know. Other alternatives:
- See also a more secure and detailed version at
  https://github.com/wrike/callisto/blob/master/Makefile
- Could also use `pip install poetry`, but that's not really recommended.
- Pipx is probably not a good idea either, ref:
  https://github.com/python-poetry/poetry/issues/677#issuecomment-443372910
- Approaches using venv:
  https://news.ycombinator.com/item?id=20677114
  https://stackoverflow.com/a/59335943/38281


### Items
Screw cookiecutter and pyscaffold. Use this skeleton
coc-settings
Poetry/pyproject

Linting

- Editor: useful
- Precommit: useful. Maybe not markdownlint though?
- Travis: for PRs
- As part of pytest - maybe for heavier (eg pylint) linting.
- As part of tox - nah. This is one overlap too many

Why doesn't makefile use `pre-commit`
(e.g. `@$(POETRY) run pre-commit flakehell -a`) for linting?
Vice-versa, why does travis use pre-commit for linting?
Pre-commit's flakehell plugin deps are manually kept in sync
(pre-commit will likely never support pyproject.toml)
with pyproject.toml. So they might get out-of-sync,
which is a slight disadvantage.
Other than that, there's not really any good reason.
I just had to chose something.

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
Tox installs in its own venv, while `coverage` is pointed to the repo
(from its config in pyproject.toml).
Therefore there will be `0%` coverage.
Refs:

- [1](https://stackoverflow.com/a/59072005/38281)
- [2](https://pytest-cov.readthedocs.io/en/latest/tox.html).

It is possible to get coverage reports ALSO from within tox runs,
but it requires that pytest be configured via tox,
which is a bit uglier, requiring that you set
`tool.tox.legacy_tox_ini` to the following:

    ```ini
    [tox]
    envlist = clean,py3{8,9}
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

## Travis-CI

#### Why pip3 ?
[Ref](https://docs.travis-ci.com/user/languages/python/#running-python-tests-on-multiple-operating-systems)

    all three OSes agree about 'pip3'
    'python' points to Python 2.7 on macOS but points to Python 3.8 on Linux and Windows
    'python3' is a 'command not found' error on Windows but 'py' works on Windows only

#### Why only 1 python version of MacOS?
Coz that's pretty much all Travis supports.
[Ref](https://docs.travis-ci.com/user/languages/python/#running-python-tests-on-multiple-operating-systems)

- Potentially another
  [way](https://docs.travis-ci.com/user/multi-os/#python-example-unsupported-languages)
- Potentially another
  [way](https://github.com/travis-ci/travis-ci/issues/9929#issuecomment-505232416)

#### Why stages?
Jobs run in parallel. But some things should only run
after others have succeeded (eg. "deploy")
=> [Stages](https://docs.travis-ci.com/user/build-stages/#what-are-build-stages)
The top-level `stages` key just serves to specify their order.

#### Can the deploy stage be moved outside of `jobs.include`
Yes, it can be moved to the top level, as seen in many travis doc examples.
You can then remove the `stage` and the `script` keys.
You might need some checks (something similar to
`condition: $TRAVIS_BUILD_STAGE_NAME = Deploy`) to ensure
it won't deploy for each job.

#### Why not makefile?
It would probably be possible to replace some of the instructions
in `.travis.yml` with `make blah`,
but there are also quite a few differences,
so we don't bother to try with that.
Also, the makefile is supposed to be for linux only,
while Travis can test other platforms.

#### Why not tox?
Checkout `3a7750` for a working Travis/Tox version.
AFAICT, the primary benefit of running tox on travis
(including the use of the `tox-travis` package to
only use the python version currently configured by Travis)
is that it reads your `tox` configuration. This
[example](https://github.com/python-poetry/poetry/issues/366#issuecomment-634666677)
seems case-in-point.
However, I have configured pytest in `[tool.pytest.ini_options]`,
i.e. outside of `[tool.tox]`
So I might as well just run `pytest` directly.

#### Why not `poetry publish` (merely `poetry build`)?
Because then we can use
[Travis' encryption mechanism](https://docs.travis-ci.com/user/deployment/pypi/)
to store my encrypted pypi-global API token in `.travis.yml`
instead of relying on Github or Travis secrets
(which requires manual configuration for each new project).
Now, the build log does complain
`python: can't open file
'/home/travis/build/patricknraanes/mpl-tools/setup.py':
[Errno 2] No such file or directory`
but nevertheless proceeds with the upload (built by poetry).
Checkout `75ba468` for the previous ("secrets") version.

## Starting a new project
Start by copying over `pyproject.toml`, and making appropriate changes.
This should be enough to get you going.
It's better to copy over the rest of the files if you need them,
rather than eliminating them later.
Use grep to search for `mpl-tools` and `mpl_tools`

You might choose not to copy over the makefile,
as its use is mainly for developers,
and developers should be able to get poetry on their own.

Turn on Travis and Coveralls through their web interface
"""
