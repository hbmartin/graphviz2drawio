from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "graphviz2drawio", "version.py")) as fp:
    exec(fp.read())

setup(
    name="graphviz2drawio",
    version=__version__,  # noqa: F821
    description="Convert graphviz (dot) files to draw.io / lucid (mxGraph) format. "
    "Beautiful and editable graphs in your favorite editor.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hbmartin/graphviz2drawio/",
    author="Harold Martin",
    author_email="harold.martin@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    license="GPLv3",
    keywords="graphviz graph agraph dot convert conversion draw drawio mxgraph maxgraph",
    packages=find_packages(exclude=["doc", "test"]),
    python_requires=">=3.10",
    install_requires=["puremagic", "pygraphviz", "svg.path"],
    tests_require=["pytest"],
    entry_points={"console_scripts": ["graphviz2drawio=graphviz2drawio.__main__:main"]},
    project_urls={
        "Bug Reports": "https://github.com/hbmartin/graphviz2drawio/issues",
        "Source": "https://github.com/hbmartin/graphviz2drawio/",
    },
    include_package_data=True,
    package_data={"graphviz2drawio": ["py.typed"]},
)
