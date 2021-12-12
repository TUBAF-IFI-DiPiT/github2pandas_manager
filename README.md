# github2pandas_manager Introduction

`github2pandas_manager` coordinates data aggregation activities for multiple GitHub-repositories. The user selects a list of repositories by names, name pattern, organizations or individual queries and provides a collection of versions, releases, pull-requests etc. For this purpose `github2pandas_manager` reads a configuration file (yml), collects the referenced repositories and provides the demanded information as Python pandas or csv files. 

Take a view to the documentation of [github2pandas](https://github.com/TUBAF-IFI-DiPiT/github2pandas) for being familiar with the individual aggregation classes.

## Application example

https://user-images.githubusercontent.com/10922356/144754607-fcf170eb-a632-4dbe-875c-fb73e0689928.mp4

## Concept

![Workflow](http://www.plantuml.com/plantuml/svg/fLDDYnD14BtthoZmeg1py9P0P4LPzR0NGJmkbUbAfxG_nghg3OlutqqFSKRSsMYmOPXYfjvxLU_HLseeLbDqs5iH-AGaRa0nxdd0R13OzdNxybXxrDk46SEv3kVHS8jAfy_mPBMwlbwjdDjiu2CDHTcAtCFh48G26fSCcurpJHTUl5gMMuFCo07DIBB2q-uUKtpc5Y1dkG9b4ZG2eM-LrFv6i0OJp9hO_a2SqS2i1vAf_pz6dFQEh3Qw-1OD7_WNInd6xjk-r6nWd4WT7C_uv_kRaXARFeSFgfMExyz5lkvYEHpBhkj-E3YTN9eiXxr1sJqstqt9RIZE0OGIScxLExRtTVjhPuZS1Bk9-DyyM4zupfxls5UCuD5mcMV6pq31mnBYWTGPnkMjrOhGI0sSOP3oXNg3NOcUP2IZx5rxBesx3XwD07_BTC_QKfy3lo49rAA-c3sDoDdEoI3OSIHzdA_ToSbMyjFcg73ogWZqUdVYkQBiQue_0G00)

## Installation

`github2pandas-manager` is available on [pypi](https://pypi.org/project/github2pandas-manager/). Use pip to install the package.

### global

On Linux:

```
sudo pip3 install github2pandas-manager 
sudo pip install github2pandas-manager
```

On Windows as admin or for one user:

```
pip install github2pandas-manager
pip install --user github2pandas-manager
```

### in virtual environment:

```
pipenv install github2pandas-manager
```

In addition a GitHub token is required for authentication. The [website](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) describes how you can generate this for your GitHub account. Add your toke to an hidden `.env` file, an example is given in `.env.example`. 

## Run examples

The [example](https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager/tree/main/examples) folder contains four types of query configurations for different purposes:

| Fokus | Keywords | Example |
| -------| -----------| ----- |
| Repo names | List all relevant repositories by username and repository name - `repo_names` |  [ProjectsByRepoNames.yml](https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager/blob/main/examples/ProjectsByRepoNames.yml)    |
| Repo name patterns       | Describe relevant repositories by white- and black-patterns - `repo_white_pattern`, `repo_black_pattern` | [ProjectsByRepoNamePatterns.yml](https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager/blob/main/examples/ProjectsByRepoNamePatterns.yml)|
| Repos by organizations | Select all repositories of an organization account - `organization_names` | [ProjectsByOrganizations.yml](https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager/blob/main/examples/ProjectsByOrganizations.yml) |
| Repos by a set of query parameter | Select all repositories according to programming languages, stars etc. - `language`,  `start_date`, `end_date`, `star_filter` | [ProjectsByQuery.yml](https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager/blob/main/examples/ProjectsByQuery.yml) |

In order to start the examples just run:

```
pipenv run python -m github2pandas_manager -path ./examples/ProjectsByQuery.yml
```

## YAML-Configuration schema

In addition to the specific configuration parameters mentioned above, each request includes three further definitions - `project_name`, `project_folder` and `content`.

While the first two are used to structure the folders to hold the data, the last parameter describes the repository data to be aggregated:

+ `Repository`
+ `Issues`
+ `Version`
+ `PullRequests`
+ `Workflows`
+ `GitReleases`

An overview of the information contained in each data frame can be found in the [wiki of the gitlab2pandas](https://github.com/TUBAF-IFI-DiPiT/github2pandas/wiki) project.
