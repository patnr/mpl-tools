# mpl-tools

[![Travis](https://travis-ci.org/patricknraanes/mpl-tools.svg?branch=master)](https://travis-ci.org/patricknraanes/mpl-tools)
[![Coveralls](https://coveralls.io/repos/github/patricknraanes/mpl-tools/badge.svg?branch=master)](https://coveralls.io/github/patricknraanes/mpl-tools?branch=master)
[![Hits.dwyl](http://hits.dwyl.com/patricknraanes/mpl-tools.svg)](http://hits.dwyl.com/patricknraanes/mpl-tools)
[![PyPI](https://badge.fury.io/py/mpl-tools.svg)](https://badge.fury.io/py/mpl-tools)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/mpl-tools)](https://pypi.org/project/mpl-tools/0.1.5/)

This package provides some tools to work with [Matplotlib](https://matplotlib.org/).

## Installation

#### Normal installation

```sh
pip install mpl-tools
```

#### For development

**On Linux**:
`git clone <this repo> ; make install`

**On Windows (or Linux)**:
Download & extract this repo.
Install [poetry](https://python-poetry.org/docs/#installation).
Run `poetry install`.

**Note**: The above will install *poetry*,
which then installs the source and its dependencies
into an isolated *virtual environment*.
To add packages, you should *not* use `pip install`,
but *poetry*, e.g. `poetry add --dev somepackage`.

<!-- markdownlint-disable-file header-increment -->
