"""
    Setup file for dart_dataclasses.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.4.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup, find_packages

if __name__ == "__main__":
    try:
        setup(
            name='dart-dataclasses-engine',
            packages=find_packages(),
            version='0.0.1',
            # use_scm_version={"version_scheme": "no-guess-dev"}
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
