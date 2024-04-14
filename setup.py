from setuptools import find_packages, setup

setup(
    name="cs577",
    version="0.1.0",
    description="CS 577 Final Project",
    package_dir={"": "src"},
    packages=find_packages("src"),
)
