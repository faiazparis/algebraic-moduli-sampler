"""Setup script for Algebraic Moduli Sampler."""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="moduli_sampler",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
    )
