Contributing
==========================

.. highlight:: sh

This project was initially created with pyscaffold::

    putup --travis --tox --pre-commit mpl-tools

The *2nd git commit* includes the most important changes
I would include to any such project setup.

Pre-commit
--------------------------

::

    pip install pre-commit
    pre-commit install

To run them without committing::

    pre-commit run --all-files
    pre-commit run <name-of-hook>


Run tests
--------------------------
Tests are also run on Travis CI,
as configured in ``.travis.yml`` and ``tox.ini``,
but this will just update the "build passing/failing" badge.

Locally you do any one of::

    tox
    pytest
    python setup.py test
    coverage run -m pytest

To get the report again do one of::

  coverage report -m
  coverage html

Options to ``pytest`` are set in ``setup.cfg``.
Notably, it requires that you've done
``pip install coverage pytest-cov``.



Making a release
--------------------------
- Tag::

    git tag v0.1.6 # or whatever
    git push origin --tags

- Clean::

    rm -rf build/ dist *.egg-info .eggs

- Build::

    python setup.py dists

- Upload to PyPI::

    twine upload --repository pypi dist/*

- Upload to Test.PyPI::

    twine upload --repository testpypi dist/*

  where ``~/.pypirc`` contains::

    [distutils]
    index-servers=
                    pypi
                    testpypi

    [pypi]
    username: myuser
    password: mypass

    [testpypi]
    repository: https://test.pypi.org/legacy/
    username: myuser
    password: mypass


Test installation
--------------------------

- Install from Test.PyPI::

    pip install --extra-index-url https://test.pypi.org/simple/ mpl-tools

- Install from PyPI::

    pip install mpl-tools

  - Install into specific dir (includes all of the dependencies)::

      pip install mpl-tools -t MyDir

  - Install with options::

      pip install mpl-tools[testing]

- Install from local (makes installation accessible from everywhere)::

    pip install -e .
