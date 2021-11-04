# github2pandas_manager Introduction

`github2pandas_manager` coordinates data aggregation activities for multiple GitHub-repositories. The user selects a list of repositories by names, name pattern, organizations or individual queries and provides a collection of versions, releases, pull-requests etc. For this purpose `github2pandas_manager` reads a configuration file (yml), collects the referenced repositories and provides the demanded information as Python pandas files. 

Take a view to the documentation of [github2pandas](https://github.com/TUBAF-IFI-DiPiT/github2pandas) for being familiar with the individual aggregation classes.

## Installation

Still it does not exist a pip based version of `github2pandas_manager`. Hence, it is necessary to clone and to install the dependencies manually.

```
git clone https://github.com/TUBAF-IFI-DiPiT/github2pandas_manager.git
cd github2pandas 
pipenv install
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
pipenv run python src/start_aggregation.py -path ./examples/ProjectsByQuery.yml
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
