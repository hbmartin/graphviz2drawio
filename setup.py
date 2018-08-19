from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "graphviz2drawio", "version.py")) as fp:
    exec(fp.read())

setup(
    name="graphviz2drawio",
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hbmartin/graphviz2drawio/",
    author="Harold Martin",
    author_email="harold.martin@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="graphviz graph agraph dot convert conversion draw drawio mxgraph xml",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["pygraphviz"],
    entry_points={
        "console_scripts": ["graphviz2drawio=graphviz2drawio.__main__:main"]
    },
    project_urls={
        "Bug Reports": "https://github.com/hbmartin/graphviz2drawio/issues",
        "Say Thanks!": "http://saythanks.io/hbmartin/graphviz2drawio",
        "Source": "https://github.com/hbmartin/graphviz2drawio/",
    },
)
