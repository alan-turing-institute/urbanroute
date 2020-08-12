"""routex setup script."""
import setuptools

setuptools.setup(
    name="routex",
    version="0.0.1",
    author="Patrick O'Hara, James Craster, Oscar Giles",
    author_email="pohara@turing.ac.uk, j.craster@warwick.ac.uk",
    description="Routing algorithms.",
    url="https://github.com/alan-turing-institute/urbanroute",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["graph-tool==2.11"],
    python_requires=">=3.6",
)
