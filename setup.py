# use pipenv-setup to generate the requirement list
# https://pypi.org/project/pipenv-setup/

from setuptools import setup
from github2pandas import __version__

with open("README.md", "r") as f:
   long_description = f.read()

setup(
   name="github2pandas",
   version=__version__,
   packages=["github2pandas"],
   license="BSD 2",
   description="Aggregation of github activities on multiple repositories based on github2pandas",
   long_description = long_description,
   long_description_content_type="text/markdown",
   author="Sebastian Zug, Mezekr Weldu, Galina Rudolf",
   url="https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager",
   download_url="https://github.com/user/reponame/archive/v_01.tar.gz",
   keywords=["git", "github", "git mining", "learning analytics"],
   install_requires=[
      "github2pandas",
   ], 
   classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
   ],
   python_requires=">=3.8"
)
