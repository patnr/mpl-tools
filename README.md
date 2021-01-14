# mpl-tools

[![Travis](https://travis-ci.org/patricknraanes/mpl-tools.svg?branch=master)](https://travis-ci.org/patricknraanes/mpl-tools)
[![Coveralls](https://coveralls.io/repos/github/patricknraanes/mpl-tools/badge.svg?branch=master)](https://coveralls.io/github/patricknraanes/mpl-tools?branch=master)
[![Hits.dwyl](http://hits.dwyl.com/patricknraanes/mpl-tools.svg)](http://hits.dwyl.com/patricknraanes/mpl-tools)
[![PyPI](https://badge.fury.io/py/mpl-tools.svg)](https://badge.fury.io/py/mpl-tools)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/mpl-tools)](https://pypi.org/project/mpl-tools/0.1.5/)

This package provides some tools to work with [Matplotlib](https://matplotlib.org/).

- `freshfig`
- `anchor_axes`, with auxiliaries:
  - `align_ax_with`
  - `set_ax_size`
  - `get_legend_bbox`
- `add_log_toggler`
  - `toggle_scale`

## Installation

#### Normal installation

```sh
pip install mpl-tools
```

#### For development

##### Linux

```sh
git clone <this repo>
make
```

##### Windows (or Linux)

- Install [poetry](https://python-poetry.org/docs/#installation)
- Download and extract this git repository
- Run `poetry install` in your shell (terminal)

<!-- markdownlint-configure-file
{
  "no-multiple-blanks": false,
  "header-increment": false
}
-->
