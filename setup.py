from setuptools import setup, find_packages
import io
import os

VERSION = "1.0.0a1"


def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="djangorocket",
    description="CLI tool to add applications and UI templates to any Django website.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ernesto González",
    version=VERSION,
    license="Apache License, Version 2.0",
    packages=find_packages(exclude=["templates"]),
    install_requires=[
        "click",
        "click-default-group>=1.2.3",
        "cookiecutter",
    ],
    entry_points={
        'console_scripts': [
            'djangorocket = djangorocket.cli:cli',
        ]
    },
    url="https://github.com/ernestofgonzalez/djangorocket",
    project_urls={
        "Documentation": "https://djangorocket.com/",
        "Changelog": "https://djangorocket.com/changelog.html",
        "Source code": "https://github.com/ernestofgonzalez/djangorocket",
        "Issues": "https://github.com/ernestofgonzalez/djangorocket/issues",
        "CI": "https://github.com/ernestofgonzalez/djangorocket/actions",
    },
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
    ],
)