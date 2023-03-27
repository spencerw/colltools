# setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="collisiontools",
    version="0.1",
    author="Spencer Wallace",
    author_email="scw7@uw.edu",
    url="https://github.com/spencerw/collisiontools",
    license="New BSD",
    description="Toolset for working with collision outputs from N-body simulations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["collisiontools"]
)
