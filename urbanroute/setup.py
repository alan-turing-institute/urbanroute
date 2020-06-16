"""urbanroute setup script."""
import setuptools

setuptools.setup(
    name="urbanroute",
    version="0.0.1",
    author="Patrick O'Hara, James Craster, Oscar Giles",
    author_email="pohara@turing.ac.uk, j.craster@warwick.ac.uk, ogiles@turing.ac.uk",
    description="Urban graphs and routing.",
    url="https://github.com/alan-turing-institute/urbanroute",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "geopandas==0.7.0",
        "networkx==2.4",
        "osmnx==0.14.1",
    ],
    python_requires=">=3.6",
)