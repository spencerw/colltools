# setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CollisionTools",
    version="0.1",
    author="Spencer Wallace",
    author_email="scw7@uw.edu",
    url="https://github.com/spencerw/CollisionTools",
    license="MIT",
    description="Routines for working with collision outputs from ChaNGa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["CollisionTools"]
)
