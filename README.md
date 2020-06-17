# urbanroute
Urban routing algorithms

## Installation

Create a conda environment first. We are using python 3.8, but 3.6 and above should be supported too.

```bash
conda create -n urbanroute python=3.8
conda activate urbanroute
```

### Install urbanroute

The `urbanroute` package is intended to create graphs of urban networks with variables
on the edges and vertices that are extracted from urban datasets.

We recommend installing `osmnx` with conda before installing the remaining dependencies:

```bash
conda install -c conda-forge osmnx
```

You can use pip to do the rest:

```bash
pip install -r requirements.txt     # developer tools
pip install -e urbanroute
```

### Install routex

The `routex` package consists of the routing algorithms themselves. Install with pip:

```bash
pip install -e routex
```

## Developer guide

### Style guide

For keeping our code tidy & professional.

#### Writing Documentation
Before being accepted into master all code should have well writen documentation. 

**Please use [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)**

We will be using [type hints](https://docs.python.org/3.7/library/typing.html) so you may optionally add types to your code. In which case you do not need to include types in your google style docstrings. 

Adding and updating existing documentation is highly encouraged.

#### Gitmoji
We like [gitmoji](https://gitmoji.carloscuesta.me/) for an emoji guide to our commit messages. You might consider (entirly optional) to use the [gitmoji-cli](https://github.com/carloscuesta/gitmoji-cli) as a hook when writing commit messages. 

#### Working on an issue

The general workflow for contributing to the project is to first choose and issue (or create one) to work on and assign yourself to the issues. 

You can find issues that need work on by searching by the `Needs assignment` label. If you decide to move onto something else or wonder what you've got yourself into please unassign yourself, leave a comment about why you dropped the issue (e.g. got bored, blocked by something etc) and re-add the `Needs assignment` label.

You are encouraged to open a pull request earlier rather than later (either a `draft pull request` or add `WIP` to the title) so others know what you are working on. 

How you label branches is optional, but we encourage using `iss_<issue-number>_<description_of_issue>` where `<issue-number>` is the github issue number and `<description_of_issue>` is a very short description of the issue. For example `iss_928_add_api_docs`.

### Testing

Writing tests for your code as you develop is strongly recommend.

#### Writing tests

Write tests using [pytest](https://docs.pytest.org/en/latest/).

#### Running tests

Tests should be written where possible before code is accepted into master. Contributing tests to existing code is highly desirable. Tests will also be run on travis (see the [travis configuration](.travis.yml)).

All tests can be found in the [`tests/`](tests) directory. 

```bash
pytest tests
```
