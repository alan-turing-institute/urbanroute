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
